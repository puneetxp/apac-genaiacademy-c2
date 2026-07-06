"""
Outlook/Hotmail Email Fetcher & Dataset Ingester
Retrieves the NDAP dataset download link via IMAP from Hotmail and ingests it into PostgreSQL.
"""

import sys
import os
import imaplib
import email
from email.header import decode_header
import re
import urllib.request
import zipfile
import io
import pandas as pd
from datetime import datetime

# Add root directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.orm.crop_market_data import CropMarketData

# IMAP Configuration
IMAP_SERVER = "imap-mail.outlook.com"
IMAP_PORT = 993

def get_outlook_credentials():
    """Read Outlook credentials from environment or prompt user"""
    email_addr = os.getenv("HOTMAIL_EMAIL", "puneetsharma9@hotmail.com")
    password = os.getenv("HOTMAIL_PASSWORD")
    
    if not password:
        print("\n⚠️  Microsoft accounts require an 'App Password' if Multi-Factor Authentication is enabled.")
        print("Create one at: https://account.microsoft.com/security -> Advanced security options -> App passwords\n")
        password = input(f"Enter password/app-password for {email_addr}: ")
        
    return email_addr, password

def fetch_download_link(email_addr, password):
    """Connects to Hotmail IMAP and searches for the NDAP download link"""
    print(f"Connecting to {IMAP_SERVER}...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    
    try:
        mail.login(email_addr, password)
        print("Logged in successfully.")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

    # Search in INBOX
    mail.select("inbox")
    
    # Search for emails from niti.gov.in or containing NDAP
    print("Searching for NDAP download emails...")
    status, messages = mail.search(None, '(BODY "ndap.niti.gov.in")')
    
    if status != "OK" or not messages[0]:
        # Try searching junk folder as well
        print("Link not found in Inbox, searching Junk folder...")
        mail.select("Junk")
        status, messages = mail.search(None, '(BODY "ndap.niti.gov.in")')
        
        if status != "OK" or not messages[0]:
            print("❌ No emails containing NDAP download links found.")
            mail.logout()
            return None

    # Get the latest message ID
    msg_ids = messages[0].split()
    latest_msg_id = msg_ids[-1]
    
    # Fetch email body
    status, data = mail.fetch(latest_msg_id, "(RFC822)")
    raw_email = data[0][1]
    
    # Parse email content
    msg = email.message_from_bytes(raw_email)
    
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8")
    print(f"Found Email Subject: {subject}")
    
    # Extract body
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/html" and "attachment" not in content_disposition:
                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                break
            elif content_type == "text/plain" and "attachment" not in content_disposition:
                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
    else:
        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
        
    mail.logout()
    
    # Extract URLs from email body
    urls = re.findall(r'(https?://[^\s<>"]+|https?://ndap\.niti\.gov\.in/download/[^\s<>"]+)', body)
    
    download_urls = [url for url in urls if "/download" in url or "ndap" in url]
    if download_urls:
        # Return unique, cleaned URL
        url = download_urls[0].replace("&amp;", "&")
        print(f"🎉 Extracted Download Link: {url}")
        return url
        
    print("❌ Could not extract download link from the email body.")
    return None

import csv

def download_and_ingest(url):
    """Downloads the zip file, extracts CSV, and inserts it into PostgreSQL"""
    print(f"Downloading dataset from: {url} ...")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            zip_data = response.read()
    except Exception as e:
        print(f"❌ Failed to download file: {e}")
        return
        
    print("Download completed. Unzipping data...")
    
    try:
        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            # Find the CSV file in the zip
            csv_files = [f for f in z.namelist() if f.endswith('.csv')]
            if not csv_files:
                print("❌ No CSV file found in the downloaded zip archive.")
                return
                
            csv_filename = csv_files[0]
            print(f"Extracting: {csv_filename}")
            
            with z.open(csv_filename) as f:
                # Read CSV using standard library csv module
                content = f.read().decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(content))
                rows = list(csv_reader)
    except Exception as e:
        print(f"❌ Failed to unzip/parse CSV: {e}")
        return

    print(f"Successfully loaded {len(rows)} rows from CSV.")
    if rows:
        print("Preview of columns:", list(rows[0].keys()))
    
    # Ingest rows into local PostgreSQL
    print("Ingesting crop prices into PostgreSQL...")
    success_count = 0
    
    for row in rows:
        try:
            # Convert wholesale price (usually per quintal) to per kg
            price_raw = row.get('Wholesale prices of crops', row.get('price_per_kg', 0))
            if not price_raw or str(price_raw).strip() == "":
                price_per_kg = 0
            else:
                price_per_kg = int(float(price_raw) / 100)
            
            crop_name = row.get('Commodity name', row.get('crop_name', 'Unknown'))
            state = row.get('State/UT', row.get('state', 'Unknown'))
            district = row.get('Commodity market', row.get('district', ''))
            
            # Map demand levels (simple mock rule)
            demand_level = "high" if price_per_kg > 40 else ("medium" if price_per_kg > 20 else "low")
            
            price_record = {
                "enable": 1,
                "crop_name": crop_name,
                "state": state,
                "district": district,
                "price_per_kg": price_per_kg,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "season": (row.get('Month') or row.get('season') or 'rabi').lower()[:10],
                "yoy_growth": 0,
                "demand_level": demand_level
            }
            
            CropMarketData.create(price_record)
            success_count += 1
            if success_count % 1000 == 0:
                print(f"Ingested {success_count} records...")
                
        except Exception as e:
            # Keep log quiet for bulk ingestion
            pass
            
    print(f"✅ Completed! Ingested {success_count} crop market price records into PostgreSQL.")

def main():
    print("====================================================")
    print("NDAP Hotmail Automated Email Link Fetcher & Ingester")
    print("====================================================")
    
    email_addr, password = get_outlook_credentials()
    if not password:
        print("❌ Password cannot be empty.")
        return
        
    url = fetch_download_link(email_addr, password)
    if url:
        download_and_ingest(url)

if __name__ == "__main__":
    main()
