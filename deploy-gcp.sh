#!/bin/bash
# =============================================================================
# CropSense AI — Full GCP Deployment Script
# Usage: ./deploy-gcp.sh
# =============================================================================

set -e  # Exit on any error

# ── CONFIGURATION (edit these) ────────────────────────────────────────────────
GCP_PROJECT="project-5449519e-8afb-48ac-b77"
GCP_REGION="us-central1"
GAR_REPO="cropsense-repo"
SERVICE_NAME="cropsense-backend"
FRONTEND_BUCKET="cropsense-frontend-prod"
SA_NAME="cropsense-deployer"
SA_EMAIL="${SA_NAME}@${GCP_PROJECT}.iam.gserviceaccount.com"
DB_PASSWORD="changeme-strong-password"   # ← change this before running
# ─────────────────────────────────────────────────────────────────────────────

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
step() { echo -e "\n${GREEN}▶ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠ $1${NC}"; }
die()  { echo -e "${RED}✗ $1${NC}"; exit 1; }

# ── STEP 1: Auth & project ────────────────────────────────────────────────────
step "1/10  Authenticating & setting project"
gcloud auth login --quiet
gcloud auth application-default login --quiet

# Create project if it doesn't exist
if ! gcloud projects describe "$GCP_PROJECT" &>/dev/null; then
  echo "Project $GCP_PROJECT not found — creating it..."
  gcloud projects create "$GCP_PROJECT" --name="CropSense AI"
  echo ""
  warn "Project created. You MUST enable billing before continuing."
  warn "Open this URL and link a billing account to the project:"
  echo "  https://console.cloud.google.com/billing/linkedaccount?project=${GCP_PROJECT}"
  echo ""
  read -p "Press ENTER once billing is enabled to continue..." 
else
  echo "Project $GCP_PROJECT already exists."
fi

gcloud config set project "$GCP_PROJECT"

# ── STEP 2: Enable APIs ───────────────────────────────────────────────────────
step "2/10  Enabling required GCP APIs"
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  sqladmin.googleapis.com \
  storage.googleapis.com \
  secretmanager.googleapis.com \
  bigquery.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  compute.googleapis.com \
  iam.googleapis.com \
  cloudscheduler.googleapis.com \
  servicenetworking.googleapis.com

# ── STEP 3: Service account ───────────────────────────────────────────────────
step "3/10  Creating service account & IAM roles"
gcloud iam service-accounts create "$SA_NAME" \
  --display-name="CropSense Deployer" 2>/dev/null || warn "Service account already exists, skipping."

for ROLE in roles/run.admin roles/artifactregistry.writer roles/storage.admin \
            roles/iam.serviceAccountUser roles/cloudsql.client \
            roles/secretmanager.secretAccessor; do
  gcloud projects add-iam-policy-binding "$GCP_PROJECT" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="$ROLE" --quiet
done

# Download key for CI/CD (add contents to GitHub Secret GCP_SA_KEY)
gcloud iam service-accounts keys create gcp-sa-key.json \
  --iam-account="$SA_EMAIL" 2>/dev/null || warn "Key may already exist."
warn "gcp-sa-key.json created — add its contents to GitHub Secret GCP_SA_KEY, then delete the file!"

# ── STEP 4: Artifact Registry ─────────────────────────────────────────────────
step "4/10  Creating Artifact Registry repository"
gcloud artifacts repositories create "$GAR_REPO" \
  --repository-format=docker \
  --location="$GCP_REGION" \
  --description="CropSense container images" 2>/dev/null || warn "Artifact Registry repo already exists."

# ── STEP 5: Frontend GCS bucket ───────────────────────────────────────────────
step "5/10  Creating frontend GCS bucket"
gcloud storage buckets create "gs://${FRONTEND_BUCKET}" \
  --location="$GCP_REGION" \
  --uniform-bucket-level-access 2>/dev/null || warn "Bucket already exists."

gcloud storage buckets add-iam-policy-binding "gs://${FRONTEND_BUCKET}" \
  --member=allUsers --role=roles/storage.objectViewer

gcloud storage buckets update "gs://${FRONTEND_BUCKET}" \
  --web-main-page-suffix=index.html \
  --web-error-page=index.html

# ── STEP 6: Terraform infrastructure ─────────────────────────────────────────
step "6/10  Applying Terraform (Cloud Run, Cloud SQL, Firestore, BigQuery, VPC)"
cd "$(dirname "$0")/terraform/gcp"
terraform init -upgrade
terraform apply -auto-approve \
  -var="project_id=${GCP_PROJECT}" \
  -var="region=${GCP_REGION}" \
  -var="db_password=${DB_PASSWORD}" \
  -var="environment=production"
cd - > /dev/null

# ── STEP 7: Build & push backend Docker image ─────────────────────────────────
step "7/10  Building & pushing backend Docker image"
gcloud auth configure-docker "${GCP_REGION}-docker.pkg.dev" --quiet
IMAGE="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${GAR_REPO}/${SERVICE_NAME}"
docker build -t "${IMAGE}:latest" ./python
docker push "${IMAGE}:latest"

# ── STEP 8: Deploy backend to Cloud Run ──────────────────────────────────────
step "8/10  Deploying backend to Cloud Run"
gcloud run deploy "$SERVICE_NAME" \
  --image="${IMAGE}:latest" \
  --region="$GCP_REGION" \
  --allow-unauthenticated \
  --port=8000 \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${GCP_PROJECT},GOOGLE_CLOUD_REGION=${GCP_REGION},ENVIRONMENT=production"

BACKEND_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region="$GCP_REGION" --format="value(status.url)")
echo -e "${GREEN}Backend URL: ${BACKEND_URL}${NC}"

# ── STEP 9: Build & deploy frontend ──────────────────────────────────────────
step "9/10  Building & uploading frontend to GCS"
cd "$(dirname "$0")/solidjs"
npm ci
VITE_API_URL="$BACKEND_URL" VITE_ENV=production npm run build
gsutil -m rsync -r -d dist/ "gs://${FRONTEND_BUCKET}"
gsutil setmeta -h "Cache-Control:public, max-age=0, must-revalidate" \
  "gs://${FRONTEND_BUCKET}/index.html"
cd - > /dev/null

# ── STEP 10: Smoke test ───────────────────────────────────────────────────────
step "10/10  Running health check"
curl -f "${BACKEND_URL}/health" && echo -e "\n${GREEN}✓ Health check passed${NC}" \
  || die "Health check failed — check Cloud Run logs: gcloud run logs read --service=${SERVICE_NAME} --region=${GCP_REGION}"

# ── Summary ───────────────────────────────────────────────────────────────────
echo -e "\n${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ CropSense AI deployed successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "  Backend  : ${BACKEND_URL}"
echo -e "  Frontend : https://storage.googleapis.com/${FRONTEND_BUCKET}/index.html"
echo -e "\n  Next: Add ${BACKEND_URL} as GCP_BACKEND_URL in GitHub Secrets"
echo -e "        Then push to 'google-cloud' branch for CI/CD auto-deploys.\n"
warn "Remember to delete gcp-sa-key.json after adding it to GitHub Secrets!"
