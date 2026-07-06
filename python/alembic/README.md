# Database Migrations

This directory contains Alembic database migrations for the CropSense AI platform.

## Setup

1. Ensure PostgreSQL is running with pgvector extension installed
2. Set environment variables in `.env` file:
   ```
   POSTGRES_SERVER=localhost
   POSTGRES_USER=your_user
   POSTGRES_PASSWORD=your_password
   POSTGRES_DB=cropsense_db
   POSTGRES_PORT=5432
   ```

## Creating Migrations

### Auto-generate migration from model changes:
```bash
cd crop-intelligence-platform/backend
alembic revision --autogenerate -m "description of changes"
```

### Create empty migration:
```bash
alembic revision -m "description of changes"
```

## Running Migrations

### Upgrade to latest version:
```bash
alembic upgrade head
```

### Upgrade to specific version:
```bash
alembic upgrade <revision_id>
```

### Downgrade one version:
```bash
alembic downgrade -1
```

### Downgrade to specific version:
```bash
alembic downgrade <revision_id>
```

## Viewing Migration History

### Show current version:
```bash
alembic current
```

### Show migration history:
```bash
alembic history
```

### Show pending migrations:
```bash
alembic history --verbose
```

## Initial Setup

To create the initial database schema:

```bash
# Create database (if not exists)
createdb cropsense_db

# Run migrations
alembic upgrade head
```

## Important Notes

- Always review auto-generated migrations before applying them
- Test migrations on a development database first
- Keep migrations small and focused
- Never edit applied migrations - create new ones instead
- Backup your database before running migrations in production

## Migration File Structure

```
alembic/
├── versions/          # Migration files
│   └── 001_initial_schema.py
├── env.py            # Alembic environment configuration
├── script.py.mako    # Template for new migrations
└── README.md         # This file
```

## Troubleshooting

### pgvector extension not found:
```sql
-- Connect to your database and run:
CREATE EXTENSION IF NOT EXISTS vector;
```

### Migration conflicts:
```bash
# Check current state
alembic current

# View history
alembic history

# Resolve conflicts by creating a merge migration
alembic merge -m "merge conflicting revisions" <rev1> <rev2>
```
