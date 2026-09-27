# CropSense AI

An AI-assisted rural farming platform for crop and livestock management, marketplace trading, and agronomic decision support — covering farm/plot registration, soil and weather data, pest & disease alerts, price prediction, and AI-driven crop and livestock recommendations.

## Feature areas

- **Farm & crop management** — farm/plot registration, crop tracking, expenses, milestones, annual strategy planning, plot analysis & publishing, AI crop recommendations
- **Livestock** — registration, health records, breeding, nutrition, vaccination reminders, ROI calculator, livestock marketplace & transactions
- **Soil & fertilizer** — Soil Health Card (SHC) lookups, soil moisture/test data, land-use classification (SLUSI), fertilizer recommendations & tracking
- **Weather & pest/disease** — weather alerts and severe weather monitoring (incl. IMD, OpenWeatherMap), pest/disease early warning
- **Marketplace & pricing** — crop/livestock marketplace listings, buyer interest, supply matching, MSP rates, market price & price prediction, transport & advance booking, payment milestones, quality verification
- **AI/ML** — Amazon Bedrock and Google Gemini/Vertex AI integration, hybrid AI service, SageMaker model training, vision-based diagnosis, predictive analytics, yield prediction, pgvector-based similarity search
- **Platform** — Cognito authentication, notifications, usage quotas, analytics

## Tech stack

| Layer | Stack |
|---|---|
| Backend | Python 3.14, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL + pgvector, Redis, Celery/APScheduler |
| Frontend | SolidJS, TypeScript, Vite, Tailwind CSS |
| AI/ML | Amazon Bedrock (via boto3), Google Generative AI / Vertex AI, SageMaker |
| Cloud | AWS (Cognito, SNS, S3, RDS, ElastiCache) or GCP (Cloud Run, Cloud SQL, BigQuery, Firestore) — both supported via Terraform |
| Testing | Playwright (E2E), pytest (backend), Vitest (frontend) |

## Repository layout

```
python/            FastAPI backend — API routes, services, SQLAlchemy models, Alembic migrations
solidjs/           SolidJS + TypeScript frontend (Vite, Tailwind)
terraform/         AWS infrastructure as code (VPC, RDS+pgvector, ElastiCache, S3, Cognito, SNS, IAM)
terraform/gcp/     GCP infrastructure as code (Cloud Run, Cloud SQL, BigQuery, Firestore, VPC, IAM)
database/          Legacy/reference SQL schema assets (separate from the Alembic migrations in python/)
e2e/               Playwright end-to-end tests
docs/              Project documentation
schema_generator/  Python code-generation tooling for models/schemas
scripts/           Deployment and operational scripts (EC2, Cognito, DB reset/restore, CI/CD setup)
```

> Note: the root `Resource/`, `composer.json`, `install.sh`, `realtime.sh`, and root `package.json` are leftovers from an unrelated PHP scaffolding template (`puneetxp/the_template_php`) and are not part of the CropSense AI application.

## Getting started

Backend and frontend are set up and run independently.

**Backend** (see [docs/SETUP.md](docs/SETUP.md) and [python/README_SETUP.md](python/README_SETUP.md)):

```bash
cd python
python3.14 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # configure database, Redis, AWS/Cognito, etc.
alembic upgrade head
./start_backend.sh
```

**Frontend**:

```bash
cd solidjs
npm install
cp .env.example .env   # configure VITE_API_URL, Cognito client, etc.
npm run dev
```

**End-to-end tests**: see [e2e/README.md](e2e/README.md).

**Infrastructure**: AWS via [terraform/README.md](terraform/README.md), or GCP via `terraform/gcp/` + `deploy-gcp.sh`.

## Deploying to GCP

`deploy-gcp.sh` deploys two Cloud Run services: `cropsense-backend` (built from `python/`) and `cropsense-frontend` (built from `solidjs/`). By default it only rebuilds the parts that changed.

| Command | What it does | When to use it |
|---|---|---|
| `./deploy-gcp.sh` | **auto** (default): compares `python/` and `solidjs/` with the commit each running service was built from, and rebuilds only the ones that differ. Exits early if nothing changed. | Everyday deploys |
| `./deploy-gcp.sh backend` | Rebuilds and deploys only the API | Only Python changed, or to force a backend redeploy |
| `./deploy-gcp.sh frontend` | Rebuilds and deploys only the web app | Only UI changed |
| `./deploy-gcp.sh app` | Backend + frontend, skips infrastructure | Force both without touching infra |
| `./deploy-gcp.sh infra` | Enables APIs, sets up Artifact Registry, secrets and the upload bucket, runs `terraform apply`, checks the DB schema, and updates Firebase sign-in settings. No image builds. | After changing `terraform/`, secrets or Firebase settings |
| `./deploy-gcp.sh all` | Everything above | First deploy, or when unsure |
| `./deploy-gcp.sh --help` | Prints these options | |

On a first deploy (either service missing), auto mode runs `all`.

**What runs in each mode**

| Step | auto / app / backend / frontend | infra / all |
|---|---|---|
| 1. Check gcloud login, project and billing | ✓ | ✓ |
| 2–5. APIs, Artifact Registry, secrets, `terraform apply`, upload bucket | – (Terraform outputs are only read) | ✓ |
| 6. DB schema check and idempotent migrations | when the backend deploys | ✓ |
| 6b. Read Firebase web config | ✓ | ✓ |
| 7. Build and deploy backend | when `python/` changed | `all` only |
| 8. Build and deploy frontend, then update CORS, sign-in domains and SMS regions | when `solidjs/` changed | `all` (domains and SMS also in `infra`) |
| 9. Health check | ✓ | ✓ |

**Image tags.** Images are tagged with the git commit (e.g. `cropsense-backend:d0637bd`). If a folder has uncommitted changes, the tag gets a suffix (`d0637bd-dirty-20260926171500`), so a local build never overwrites a committed image. Auto mode can't tell what a `-dirty` image contains, so the next run rebuilds that service. **Commit before deploying** to get clean tags and accurate change detection.

**If a deploy hangs at "Creating Revision…"**, the new container is failing to start. Cloud Run keeps traffic on the previous revision and gives up after about 4 minutes. Check why with:

```bash
gcloud run services logs read cropsense-backend --region=us-central1 --project=cropsense-ai-a4d5cf --limit=50
```

## Documentation

- [docs/SETUP.md](docs/SETUP.md) — full local development & production setup guide
- [python/README_SETUP.md](python/README_SETUP.md) — backend quick start
- [python/alembic/README.md](python/alembic/README.md) — database migration commands
- [terraform/README.md](terraform/README.md) — AWS infrastructure overview
- [e2e/README.md](e2e/README.md) — end-to-end test guide

## License

Apache License 2.0 — see [LICENSE](LICENSE).
