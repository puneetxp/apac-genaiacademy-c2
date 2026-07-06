<?php

/**
 * Code generation setup for Rural Farming Platform
 * 
 * This script uses the compile-php library to generate:
 * - FastAPI backend (Python 3.14.3 models, services, routers)
 * - SolidJS frontend (TypeScript interfaces, services, stores)
 * - PostgreSQL migrations with pgvector support
 * 
 * Technology Stack:
 * - Python 3.14.3
 * - FastAPI 0.115.6
 * - SQLAlchemy 2.0.36 with asyncpg 0.30.0
 * - Pydantic 2.10.5
 * - PostgreSQL 14+ with pgvector 0.4.2
 * - SolidJS with TypeScript
 */

require __DIR__ . '/vendor/autoload.php';

use Puneetxp\CompilePhp\setup;

echo "\n";
echo "🌾 Rural Farming & Livestock Management Platform\n";
echo "📦 Code Generator - FastAPI + SolidJS\n";
echo str_repeat("=", 70) . "\n\n";

// Initialize setup with current directory
$setup = new setup(__DIR__);

echo "📋 Configuration:\n";
echo "   - Backend: FastAPI (Python 3.14.3)\n";
echo "   - Frontend: SolidJS (TypeScript)\n";
echo "   - Database: PostgreSQL 14+ with pgvector 0.4.2\n";
echo "   - ORM: SQLAlchemy 2.0.36 (async)\n\n";

// Run code generation
echo "🔨 Generating code from JSON schemas...\n";
echo "   Reading schemas from: database/Model/*.json\n\n";

try {
    $setup->config();
    
    echo "\n✅ Code generation complete!\n\n";
    
    echo "📝 Generated Backend (FastAPI):\n";
    echo "   ├─ Models:      backend/app/models/*.py\n";
    echo "   ├─ Schemas:     backend/app/schemas/*.py\n";
    echo "   ├─ Services:    backend/app/services/*.py\n";
    echo "   ├─ Routers:     backend/app/*.py\n";
    echo "   └─ Database:    backend/app/database/*.py\n\n";
    
    echo "📝 Generated Frontend (SolidJS):\n";
    echo "   ├─ Interfaces:  frontend/solid/src/shared/Interface/Model/*.ts\n";
    echo "   ├─ Services:    frontend/solid/src/shared/Service/*.ts\n";
    echo "   ├─ Stores:      frontend/solid/src/shared/Store/*.ts\n";
    echo "   └─ Types:       frontend/solid/src/types/*.ts\n\n";
    
    echo "📝 Generated Database:\n";
    echo "   ├─ Migrations:  database/migrations/*.sql\n";
    echo "   └─ Schema:      database/schema.sql\n\n";
    
    echo "🚀 Next Steps:\n";
    echo "   1. Review generated code in backend/ and frontend/\n";
    echo "   2. Set up Python virtual environment:\n";
    echo "      cd backend && python3.14 -m venv venv && source venv/bin/activate\n";
    echo "   3. Install Python dependencies:\n";
    echo "      pip install -r requirements.txt\n";
    echo "   4. Set up database:\n";
    echo "      psql -U postgres -d farming_platform -f database/schema.sql\n";
    echo "   5. Run FastAPI server:\n";
    echo "      cd backend && uvicorn app.main:app --reload\n";
    echo "   6. Install frontend dependencies:\n";
    echo "      cd frontend/solid && npm install\n";
    echo "   7. Run SolidJS dev server:\n";
    echo "      cd frontend/solid && npm run dev\n\n";
    
    echo "📚 Documentation:\n";
    echo "   - API Docs: http://localhost:8000/docs\n";
    echo "   - Frontend: http://localhost:3000\n";
    echo "   - Schema Docs: https://the-doc.netlify.app/docs/model/schema/\n\n";
    
} catch (Exception $e) {
    echo "\n❌ Error during code generation:\n";
    echo "   " . $e->getMessage() . "\n\n";
    exit(1);
}

echo str_repeat("=", 70) . "\n";
echo "✨ Happy coding!\n\n";
