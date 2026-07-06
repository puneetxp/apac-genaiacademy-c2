"""
Microsoft Graph API & Hotmail/Outlook Email attachment downloader.
Connects via OAuth 2.0 Device Code Flow, downloads the NDAP pricing CSV attachment,
truncates the PostgreSQL crop_market_data table, and re-seeds it with 384-dimensional vector embeddings.
"""

import sys
import os
import time
import csv
import json
import requests
import hashlib
import html
import zipfile
import io
import re
from datetime import datetime
from sqlalchemy import text

# Add root directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from app.services.bedrock_service import BedrockService

# Custom MailReader App Registration Client ID (Multi-tenant + Personal Accounts enabled)
CLIENT_ID = "824646fe-3d7e-4b1b-b424-fa2475cdd28d"
AUTHORITY = "https://login.microsoftonline.com/common"
SCOPES = ["Mail.Read", "User.Read"]

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "microsoft_token_cache.bin")

def get_msal_cache():
    import msal
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache.deserialize(f.read())
        except Exception:
            pass
    return cache

def save_msal_cache(cache):
    try:
        with open(CACHE_FILE, "w") as f:
            f.write(cache.serialize())
    except Exception:
        pass

def acquire_microsoft_token():
    """
    Acquires Microsoft Graph API OAuth 2.0 Token using Device Code Flow with token caching.
    """
    try:
        import msal
    except ImportError:
        print("❌ 'msal' package is not installed. Run: pip install msal")
        return None
        
    cache = get_msal_cache()
    
    # Try to initialize with the tenant-specific authority, and fall back to 'common' if discovery fails
    try:
        app = msal.PublicClientApplication(
            CLIENT_ID,
            authority=AUTHORITY,
            token_cache=cache
        )
    except Exception as e:
        print(f"⚠️ Failed to init MSAL with authority {AUTHORITY}: {e}")
        return None

    # Check cache silently first
    accounts = app.get_accounts()
    if accounts:
        try:
            result = app.acquire_token_silent(scopes=SCOPES, account=accounts[0])
            if result and "access_token" in result:
                save_msal_cache(cache)
                print("🔑 Reusing cached Microsoft login session.")
                return result["access_token"]
        except Exception:
            pass

    print("\n====================================================")
    print("Microsoft OAuth 2.0 Device Code Login")
    print("====================================================")

    try:
        flow = app.initiate_device_flow(scopes=SCOPES)
    except Exception as e:
        print(f"⚠️ Failed to init MSAL with tenant authority {AUTHORITY}: {e}")
        print("Retrying with Microsoft consumers authority (https://login.microsoftonline.com/consumers)...")
        try:
            app = msal.PublicClientApplication(
                CLIENT_ID,
                authority="https://login.microsoftonline.com/consumers"
            )
            flow = app.initiate_device_flow(scopes=SCOPES)
        except Exception as retry_err:
            print(f"❌ Failed to initiate Device Code Flow with consumers authority: {retry_err}")
            return None

    if "user_code" not in flow:
        print(f"❌ Failed to initiate Device Code Flow: {json.dumps(flow, indent=2)}")
        return None
        
    # 2. Print instruction for user to sign in
    print("\n👉 ACTION REQUIRED:")
    print(flow["message"])
    print("\nWaiting for authentication to complete in your browser...")
    
    # 3. Block and poll until authenticated
    result = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in result:
        print("\n✅ Authentication successful!")
        save_msal_cache(cache)
        return result["access_token"]
    else:
        print(f"\n❌ Authentication failed: {result.get('error_description', 'Unknown Error')}")
        return None

def download_attachment_from_graph(token):
    """
    Connects to Microsoft Graph API, retrieves the latest NDAP 'DOWNLOAD REQUEST' email,
    extracts the 'Download Now' link from the body, downloads the file, and extracts the CSV.
    """
    import re
    import zipfile
    import io

    print("\n====================================================")
    print("Retrieving email from Microsoft Graph API")
    print("====================================================")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
# Database-driven hash tracking and file storage functions
def check_file_stored(file_hash):
    """Checks if the file binary is already stored in the DB."""
    if not file_hash:
        return False
    with engine.connect() as conn:
        try:
            result = conn.execute(text("""
                SELECT id FROM ndap_downloaded_files 
                WHERE file_hash = :file_hash AND enable = 1
                LIMIT 1
            """), {"file_hash": file_hash}).fetchone()
            return result is not None
        except Exception:
            return False

def get_stored_file_content(file_hash):
    """Retrieves the stored file binary from the DB."""
    if not file_hash:
        return None
    with engine.connect() as conn:
        try:
            result = conn.execute(text("""
                SELECT file_content FROM ndap_downloaded_files 
                WHERE file_hash = :file_hash AND enable = 1
                LIMIT 1
            """), {"file_hash": file_hash}).fetchone()
            # In SQLAlchemy, BYTEA is returned as bytes or memoryview
            if result and result[0]:
                return bytes(result[0])
            return None
        except Exception as e:
            print(f"⚠️ Failed to retrieve stored file content from DB: {e}")
            return None

def save_file_to_db(file_name, file_hash, file_content):
    """Saves the raw downloaded file content directly to ndap_downloaded_files table."""
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            # Check if this hash already exists in file storage
            existing = conn.execute(text("""
                SELECT id FROM ndap_downloaded_files WHERE file_hash = :file_hash LIMIT 1
            """), {"file_hash": file_hash}).fetchone()
            
            if not existing:
                conn.execute(text("""
                    INSERT INTO ndap_downloaded_files (file_name, file_hash, file_content, enable)
                    VALUES (:file_name, :file_hash, :file_content, 1)
                """), {
                    "file_name": file_name,
                    "file_hash": file_hash,
                    "file_content": file_content
                })
            transaction.commit()
            print("  💾 Raw file successfully stored in the database.")
        except Exception as e:
            transaction.rollback()
            print(f"⚠️ Failed to save downloaded file in DB storage: {e}")

def check_hash_processed(file_hash):
    """Checks if a file ETag or content hash has already been successfully completed in the DB."""
    if not file_hash:
        return False
    with engine.connect() as conn:
        try:
            result = conn.execute(text("""
                SELECT id FROM ndap_ingestion_runs 
                WHERE file_hash = :file_hash AND status = 'completed'
                LIMIT 1
            """), {"file_hash": file_hash}).fetchone()
            return result is not None
        except Exception:
            return False

def log_ingestion_start(file_name, file_hash):
    """Logs the start of an ingestion run in the database."""
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            existing = conn.execute(text("""
                SELECT id FROM ndap_ingestion_runs WHERE file_hash = :file_hash LIMIT 1
            """), {"file_hash": file_hash}).fetchone()
            
            if existing:
                conn.execute(text("""
                    UPDATE ndap_ingestion_runs 
                    SET status = 'running', started_at = :now, completed_at = NULL, error_message = NULL, file_name = :file_name
                    WHERE id = :id
                """), {"id": existing[0], "now": datetime.now(), "file_name": file_name})
                run_id = existing[0]
            else:
                res = conn.execute(text("""
                    INSERT INTO ndap_ingestion_runs (file_name, file_hash, started_at, status, enable)
                    VALUES (:file_name, :file_hash, :now, 'running', 1)
                    RETURNING id
                """), {"file_name": file_name, "file_hash": file_hash, "now": datetime.now()})
                run_id = res.fetchone()[0]
            transaction.commit()
            return run_id
        except Exception as e:
            transaction.rollback()
            print(f"⚠️ Failed to log ingestion start in DB: {e}")
            return None

def log_ingestion_finish(run_id, file_hash, records_ingested, status='completed', error_message=None):
    """Updates the ingestion run with the outcome status and record count."""
    if run_id is None:
        # Fallback to record as new run to ensure durability
        with engine.connect() as conn:
            transaction = conn.begin()
            try:
                conn.execute(text("""
                    INSERT INTO ndap_ingestion_runs (file_name, file_hash, started_at, completed_at, status, records_ingested, error_message, enable)
                    VALUES ('direct_import', :file_hash, :now, :now, :status, :records_ingested, :error_message, 1)
                """), {
                    "file_hash": file_hash,
                    "status": status,
                    "records_ingested": records_ingested,
                    "error_message": error_message,
                    "now": datetime.now()
                })
                transaction.commit()
            except Exception as e:
                transaction.rollback()
                print(f"⚠️ Failed to log new ingestion run in DB: {e}")
        return
        
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            conn.execute(text("""
                UPDATE ndap_ingestion_runs 
                SET status = :status, completed_at = :now, records_ingested = :records_ingested, error_message = :error_message, updated_at = :now
                WHERE id = :id
            """), {
                "id": run_id,
                "status": status,
                "records_ingested": records_ingested,
                "error_message": error_message,
                "now": datetime.now()
            })
            transaction.commit()
        except Exception as e:
            transaction.rollback()
            print(f"⚠️ Failed to update ingestion run {run_id} in DB: {e}")

def download_and_process_emails(token, limit=None, reset_db=False):
    """
    Finds ALL emails from 'ndapadm@gmail.com' in Inbox and Junk folder,
    downloads each dataset, calculates its SHA-256 hash, filters duplicates,
    and seeds new datasets into the database.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    print("\n====================================================")
    print("Retrieving emails from Microsoft Graph API")
    print("====================================================")
    
    # 1. Fetch messages from Inbox (with paging support to retrieve all historic emails)
    inbox_url = "https://graph.microsoft.com/v1.0/me/messages?$filter=from/emailAddress/address eq 'ndapadm@gmail.com'&$select=id,subject,receivedDateTime"
    inbox_messages = []
    while inbox_url:
        try:
            response = requests.get(inbox_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                inbox_messages.extend(data.get("value", []))
                inbox_url = data.get("@odata.nextLink")
            else:
                break
        except Exception as e:
            print(f"⚠️ Inbox query failed: {e}")
            break
        
    # 2. Fetch messages from Junk Folder (with paging support to retrieve all historic emails)
    junk_url = "https://graph.microsoft.com/v1.0/me/mailFolders/junkemail/messages?$filter=from/emailAddress/address eq 'ndapadm@gmail.com'&$select=id,subject,receivedDateTime"
    junk_messages = []
    while junk_url:
        try:
            response = requests.get(junk_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                junk_messages.extend(data.get("value", []))
                junk_url = data.get("@odata.nextLink")
            else:
                break
        except Exception as e:
            print(f"⚠️ Junk folder query failed: {e}")
            break
        
    # Combine and deduplicate messages by ID, sorted newest first
    messages_map = {}
    for m in inbox_messages:
        messages_map[m["id"]] = m
    for m in junk_messages:
        messages_map[m["id"]] = m
        
    messages = sorted(messages_map.values(), key=lambda x: x.get("receivedDateTime", ""), reverse=True)
    
    if not messages:
        print("⚠️ No emails found from 'ndapadm@gmail.com' in Inbox or Junk Email folders.")
        return False
        
    print(f"Found {len(messages)} emails from 'ndapadm@gmail.com'.")
    
    # Track if any database seed was performed
    any_seeded = False
    is_first = True
    
    for idx, message in enumerate(messages):
        message_id = message["id"]
        subject = message.get("subject", "No Subject")
        received_date = message.get("receivedDateTime", "Unknown Date")
        
        print(f"\n[{idx+1}/{len(messages)}] Checking email '{subject}' received at {received_date}...")
        
        # Get full message content (including HTML body)
        msg_url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}?$select=body"
        msg_response = requests.get(msg_url, headers=headers)
        if msg_response.status_code != 200:
            print(f"  ❌ Failed to retrieve message body: {msg_response.status_code}")
            continue
            
        body_content = msg_response.json().get("body", {}).get("content", "")
        if not body_content:
            print("  ⚠️ Email body is empty.")
            continue
            
        # Parse the HTML body to find the Download link
        all_links = re.findall(r'href="([^"]+)"', body_content)
        
        url_match = re.search(r'<a\s+[^>]*href="([^"]+)"[^>]*>(?:<[^>]+>)*\s*Download\s+Now\s*(?:</[^>]+>)*\s*</a>', body_content, re.IGNORECASE)
        if not url_match:
            url_match = re.search(r'href="([^"]*amazonaws\.com[^"]*)"', body_content, re.IGNORECASE)
        if not url_match:
            url_match = re.search(r'href="([^"]*ndap[^"]*)"', body_content, re.IGNORECASE)
        if not url_match:
            url_match = re.search(r'href="([^"]*download[^"]*)"', body_content, re.IGNORECASE)
            
        if not url_match:
            for l in all_links:
                if l.startswith("http") and not any(x in l.lower() for x in ["apple.com", "microsoft.com", "office.com", "live.com", "outlook.com"]):
                    url_match = re.match(r'(.*)', l)
                    break
                    
        if not url_match:
            print("  ⚠️ Could not find download link inside the email body.")
            continue
            
        download_url = html.unescape(url_match.group(1))
        
        # Decode Outlook Safe Links
        if "safelinks.protection.outlook.com" in download_url:
            from urllib.parse import urlparse, parse_qs
            try:
                parsed = urlparse(download_url)
                qs = parse_qs(parsed.query)
                if "url" in qs:
                    download_url = qs["url"][0]
            except Exception as parse_err:
                print(f"  ⚠️ Failed to decode Outlook Safe Link: {parse_err}")
                
        # Check ETag of target URL using HEAD request before downloading
        try:
            head_response = requests.head(download_url)
            etag = head_response.headers.get("ETag", "").replace('"', '').strip()
            
            # 1. If ETag is already completed successfully in DB, skip the entire email!
            if etag and check_hash_processed(etag):
                print(f"  ℹ️ File ETag '{etag}' has already been successfully ingested. Skipping email...")
                continue
                
            content_bytes = None
            
            # 2. Check if the file is already stored in the DB
            if etag and check_file_stored(etag):
                print(f"  💾 File ETag '{etag}' found in database storage. Loading from DB...")
                content_bytes = get_stored_file_content(etag)
                
            # 3. Download the file if not loaded from DB
            if not content_bytes:
                print("  Downloading file from link...")
                file_response = requests.get(download_url, stream=True)
                if file_response.status_code != 200:
                    print(f"  ❌ Failed to download file from link: {file_response.status_code}")
                    continue
                content_bytes = file_response.content
                
                # Save downloaded file to DB storage
                if etag:
                    save_file_to_db(subject, etag, content_bytes)
            
            # Decompress ZIP if needed
            is_zip = content_bytes.startswith(b"PK\x03\x04")
            csv_content = None
            
            if is_zip:
                with zipfile.ZipFile(io.BytesIO(content_bytes)) as z:
                    csv_files = [f for f in z.namelist() if f.lower().endswith(".csv")]
                    if csv_files:
                        csv_content = z.read(csv_files[0])
            else:
                csv_content = content_bytes
                
            if not csv_content:
                print("  ❌ Could not retrieve valid CSV content.")
                continue
                
            # Verify it's not an HTML page redirect
            first_line = csv_content[:200].lower()
            if b"<!doctype html>" in first_line or b"<html" in first_line:
                print("  ❌ Downloaded file is an HTML redirect/login page, not a CSV.")
                continue
                
            # Compute SHA-256 hash of the CSV content
            file_hash = hashlib.sha256(csv_content).hexdigest()
            print(f"  SHA-256 Hash: {file_hash}")
            
            # 4. Check if the content hash has already been successfully completed
            if check_hash_processed(file_hash):
                print("  ℹ️ File with this SHA-256 has already been successfully ingested. Skipping...")
                # Log ETag run if different and skip
                if etag and etag != file_hash:
                    log_ingestion_start(subject, etag)
                    log_ingestion_finish(None, etag, 0, 'completed')
                continue
                
            # Save the raw file content under the content hash to DB storage if not already there
            if not check_file_stored(file_hash):
                save_file_to_db(subject, file_hash, content_bytes)
                
            # Start DB log run using content hash
            run_id = log_ingestion_start(subject, file_hash)
            
            # Save the new CSV content to a temporary file for ingestion
            temp_filename = f"temp_ndap_{message_id}.csv"
            with open(temp_filename, "wb") as f:
                f.write(csv_content)
                
            print(f"  New dataset found! Ingesting {temp_filename}...")
            
            # Truncate only on the very first successful database write, if reset_db is requested
            should_truncate = reset_db and is_first
            seeded_count = truncate_and_seed_database(temp_filename, limit=limit, reset_db=should_truncate)
            
            # Clean up temp file
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
            # Update DB log run to completed status
            if seeded_count > 0:
                log_ingestion_finish(run_id, file_hash, seeded_count, 'completed')
                if etag and etag != file_hash:
                    etag_run = log_ingestion_start(subject, etag)
                    log_ingestion_finish(etag_run, etag, seeded_count, 'completed')
                any_seeded = True
                is_first = False
            else:
                log_ingestion_finish(run_id, file_hash, 0, 'failed', "Ingestion returned 0 seeded records (failed or empty)")
            
        except Exception as file_err:
            print(f"  ❌ Failed to process file: {file_err}")
            if 'file_hash' in locals() and 'run_id' in locals():
                log_ingestion_finish(run_id, file_hash, 0, 'failed', str(file_err))
            continue
            
    return any_seeded

def parse_date_from_csv(year_str, month_str):
    """
    Parses year and month strings from NDAP CSV and returns a 'YYYY-MM-DD' formatted string.
    Example: 
      year_str = "Calendar Year (Jan - Dec), 2021"
      month_str = "December, 2021"
      returns: "2021-12-01"
    """
    import re
    year = 2021
    if year_str:
        year_match = re.search(r'\b(19|20)\d{2}\b', str(year_str))
        if year_match:
            year = int(year_match.group(0))
            
    month = 1
    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    if month_str:
        month_str_lower = str(month_str).lower()
        for name, num in month_map.items():
            if name in month_str_lower:
                month = num
                break
                
    return f"{year}-{month:02d}-01"

def truncate_and_seed_database(csv_path, limit=50, reset_db=False):
    """
    Seeds the crop_market_data table with unique CSV records.
    """
    print("\n====================================================")
    print("Database Incremental Vector Seeding")
    print("====================================================")
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found at {csv_path}")
        return 0
        
    # Initialize BedrockService for embeddings
    bedrock = BedrockService()
    
    # 1. Truncate table if reset flag is active
    if reset_db:
        print("⚠️ WARNING: Truncating 'crop_market_data' table (clearing old records)...")
        with engine.connect() as conn:
            transaction = conn.begin()
            try:
                conn.execute(text("TRUNCATE TABLE crop_market_data RESTART IDENTITY CASCADE;"))
                transaction.commit()
                print("✅ crop_market_data table cleared successfully.")
            except Exception as e:
                transaction.rollback()
                print(f"❌ Truncation failed: {e}")
                return 0
            
    # Check if the downloaded file is HTML (login or error page) instead of CSV
    try:
        with open(csv_path, "r", encoding="utf-8-sig", errors="ignore") as f:
            first_line = f.readline()
            if "<!doctype html>" in first_line.lower() or "<html" in first_line.lower():
                print("\n❌ ERROR: The downloaded file is an HTML web page, NOT a CSV dataset.")
                print("This usually happens because NITI Aayog redirected the request to a Login/Sign-in screen.")
                print("Please log in to your NDAP account in your browser, trigger a download, and save the CSV file as 'ndap_data.csv' in this folder.")
                return
    except Exception as e:
        print(f"⚠️ Failed to pre-verify file format: {e}")
        
    # 2. Parse CSV and seed records
    print(f"Reading CSV from {csv_path}...")
    records_to_seed = []
    
    try:
        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            
            # Map CSV headers dynamically to support various NDAP formats case-insensitively
            for row in reader:
                crop_name = "Unknown"
                state = "Unknown"
                district = "Unknown"
                price_per_kg = 20
                season = "current"
                demand = "medium"
                year_val = ""
                month_val = ""
                
                # Check each key for partial case-insensitive matches
                for key, val in row.items():
                    if not key or not val:
                        continue
                    key_lower = key.lower().strip()
                    val_str = str(val).strip()
                    
                    # 1. Price Column (must check first to avoid matching "crops" in price header)
                    if "price" in key_lower:
                        try:
                            # Convert quintal pricing (common in Mandi data) to kg pricing
                            price_per_kg = int(float(val_str))
                            if price_per_kg > 100:
                                price_per_kg = int(price_per_kg / 100)
                        except ValueError:
                            pass
                    # 2. State Column
                    elif "state" in key_lower:
                        state = val_str
                    # 3. Market / District Column
                    elif "market" in key_lower or "district" in key_lower:
                        district = val_str
                    # 4. Crop / Commodity Name Column
                    elif "commodity name" in key_lower or "crop name" in key_lower or key_lower == "commodity" or key_lower == "crop":
                        crop_name = val_str
                    # 5. Season
                    elif "season" in key_lower:
                        season = val_str
                    # 6. Demand
                    elif "demand" in key_lower:
                        demand = val_str
                    # 7. Year
                    elif "year" in key_lower:
                        year_val = val_str
                    # 8. Month
                    elif "month" in key_lower:
                        month_val = val_str
                
                parsed_date = parse_date_from_csv(year_val, month_val)
                
                records_to_seed.append({
                    "crop_name": crop_name,
                    "state": state,
                    "district": district,
                    "price_per_kg": price_per_kg,
                    "date": parsed_date,
                    "season": season,
                    "demand_level": demand
                })
                
                if limit is not None and len(records_to_seed) >= limit:
                    break
    except Exception as e:
        print(f"❌ Failed to parse CSV file: {e}")
        return 0
        
    # 2. Filter unique records against the database to avoid duplicate historical records
    unique_records = []
    duplicate_count = 0
    
    # If reset_db is requested, skip DB check entirely because the table is cleared/truncated
    if reset_db:
        unique_records = records_to_seed
    else:
        print("Checking for existing duplicate records in database...")
        for rec in records_to_seed:
            with engine.connect() as conn:
                dup = conn.execute(text("""
                    SELECT id FROM crop_market_data 
                    WHERE crop_name = :crop_name 
                      AND state = :state 
                      AND district = :district 
                      AND season = :season
                      AND date = :date
                    LIMIT 1
                """), {
                    "crop_name": rec["crop_name"],
                    "state": rec["state"],
                    "district": rec["district"],
                    "season": rec["season"],
                    "date": rec["date"]
                }).fetchone()
                
                if dup:
                    duplicate_count += 1
                else:
                    unique_records.append(rec)
                    
    print(f"Duplicates found in DB: {duplicate_count}. Unique records to process: {len(unique_records)}.")
    
    if not unique_records:
        print(f"\n✨ Database refresh completed! Seeded 0 unique crops. Ignored {duplicate_count} duplicates.")
        return 0
        
    # 3. Extract unique (crop_name, state, district) combinations for embedding generation.
    # This prevents redundant API calls: multiple historical entries of the same crop-market share the same vector!
    unique_embedding_keys = set()
    for rec in unique_records:
        c_name = rec["crop_name"].strip().upper()
        state_name = rec["state"].strip().upper()
        dist_name = rec["district"].strip().upper()
        unique_embedding_keys.add((c_name, state_name, dist_name))
        
    unique_keys_list = list(unique_embedding_keys)
    
    # Generate embeddings in batches of 250 (Vertex AI maximum limit) concurrently to optimize performance
    batch_size = 250
    batches = [unique_keys_list[i : i + batch_size] for i in range(0, len(unique_keys_list), batch_size)]
    
    print(f"Generating embeddings for {len(unique_keys_list)} unique crop-markets across {len(batches)} batches concurrently...")
    
    from vertexai.language_models import TextEmbeddingModel
    try:
        model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    except Exception as e:
        print(f"❌ Failed to load Vertex AI TextEmbeddingModel: {e}")
        return 0
        
    from concurrent.futures import ThreadPoolExecutor
    
    def process_batch(batch_idx):
        batch = batches[batch_idx]
        texts = [
            f"crop:{k[0]} state:{k[1]} district:{k[2]}"
            for k in batch
        ]
        
        # Generate vectors in batch with retry/backoff logic to handle rate limits
        retries = 5
        backoff_sec = 2
        for attempt in range(retries):
            try:
                embeddings = model.get_embeddings(texts, output_dimensionality=384)
                if len(embeddings) == len(batch):
                    return batch, embeddings
                else:
                    raise ValueError("Batch response size mismatch.")
            except Exception as e:
                if attempt == retries - 1:
                    print(f"❌ Batch {batch_idx+1} embedding generation failed after {retries} attempts: {e}")
                    raise e
                print(f"⚠️ Vertex AI rate limit hit on batch {batch_idx+1}: {e}. Retrying in {backoff_sec} seconds...")
                time.sleep(backoff_sec)
                backoff_sec *= 2

    # Execute requests in parallel
    embeddings_map = {}
    try:
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(process_batch, range(len(batches))))
            for batch, embeddings in results:
                for key, emb in zip(batch, embeddings):
                    vector = emb.values
                    if all(v == 0.0 for v in vector):
                        print(f"\n❌ ERROR: Vertex AI returned a mock/all-zero vector for key '{key}'.")
                        return 0
                    embeddings_map[key] = vector
    except Exception as parallel_err:
        print(f"❌ Parallel embedding generation failed: {parallel_err}")
        return 0
        
    print(f"✅ Generated {len(embeddings_map)} embeddings successfully.")
    
    # 4. Map embeddings back to all records
    all_insert_data = []
    for rec in unique_records:
        c_name = rec["crop_name"].strip().upper()
        state_name = rec["state"].strip().upper()
        dist_name = rec["district"].strip().upper()
        
        vector = embeddings_map.get((c_name, state_name, dist_name))
        if vector:
            all_insert_data.append({
                "crop_name": rec["crop_name"],
                "state": rec["state"],
                "district": rec["district"],
                "price_per_kg": rec["price_per_kg"],
                "date": rec["date"],
                "season": rec["season"],
                "demand_level": rec["demand_level"],
                "rag_embedding": vector
            })
            
    # Commit all data in a single unified database transaction (inserted in chunks of 5000)
    print(f"\nCommitting {len(all_insert_data)} records to database...")
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            if reset_db:
                print("⚠️ Truncating 'crop_market_data' table (clearing old records)...")
                conn.execute(text("TRUNCATE TABLE crop_market_data RESTART IDENTITY CASCADE;"))
                
            chunk_size = 5000
            for idx in range(0, len(all_insert_data), chunk_size):
                chunk = all_insert_data[idx : idx + chunk_size]
                conn.execute(text("""
                    INSERT INTO crop_market_data (enable, crop_name, state, district, price_per_kg, date, season, yoy_growth, demand_level, rag_embedding)
                    VALUES (1, :crop_name, :state, :district, :price_per_kg, :date, :season, 0, :demand_level, :rag_embedding)
                """), chunk)
                
            transaction.commit()
            print(f"✅ Transaction committed successfully! Seeded {len(all_insert_data)} crops.")
            return len(all_insert_data)
        except Exception as db_err:
            transaction.rollback()
            print(f"❌ Database commit failed: {db_err}")
            return 0

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="CropSense AI: Email NDAP Vector Seeding Pipeline")
    parser.add_argument("--reset", action="store_true", help="Truncate database table before seeding the first new dataset")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of records to seed per file (default: 0 for unlimited)")
    args = parser.parse_args()

    print("====================================================")
    print("CropSense AI: Email NDAP Vector Seeding Pipeline")
    print("====================================================")
    
    # Ensure database tables exist
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS ndap_ingestion_runs (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    enable SMALLINT DEFAULT 1,
                    file_name VARCHAR(255),
                    file_hash VARCHAR(255) UNIQUE,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    status VARCHAR(50),
                    records_ingested INT,
                    error_message TEXT
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS ndap_downloaded_files (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    enable SMALLINT DEFAULT 1,
                    file_name VARCHAR(255) NOT NULL,
                    file_hash VARCHAR(255) UNIQUE NOT NULL,
                    file_content BYTEA NOT NULL
                );
            """))
            transaction.commit()
        except Exception as table_err:
            transaction.rollback()
            print(f"⚠️ Could not verify/create database tables: {table_err}")

    # 1. Get access token
    token = acquire_microsoft_token()
    if not token:
        print("❌ Authentication failed. Could not retrieve Microsoft access token.")
        sys.exit(1)
        
    # 2. Retrieve, download, hash-verify, and seed all matching emails
    limit_val = None if args.limit <= 0 else args.limit
    success = download_and_process_emails(token, limit=limit_val, reset_db=args.reset)
    
    if success:
        print("\n✨ All new datasets have been successfully processed and seeded!")
    else:
        print("\nℹ️ No new datasets to process (all emails are either duplicates or unreadable).")

if __name__ == "__main__":
    main()
