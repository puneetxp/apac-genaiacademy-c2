#!/bin/bash

###############################################################################
# SolidJS Frontend Initialization Script
# 
# This script initializes a SolidJS project with Vite (no SolidStart)
# for the Rural Farming & Livestock Management Platform
#
# Usage: ./init_solidjs.sh
###############################################################################

set -e  # Exit on error

echo ""
echo "🌾 Rural Farming Platform - SolidJS Initialization"
echo "================================================================"
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed"
    echo "   Please install Node.js and npm first"
    exit 1
fi

echo "📦 Node.js version: $(node --version)"
echo "📦 npm version: $(npm --version)"
echo ""

# Create solidjs directory structure
echo "📁 Creating solidjs directory structure..."
mkdir -p solidjs

# Navigate to solidjs directory
cd solidjs

echo "🔨 Initializing SolidJS project with Vite..."
echo ""

# Create package.json
cat > package.json << 'EOF'
{
  "name": "farming-platform-frontend",
  "version": "1.0.0",
  "description": "Rural Farming & Livestock Management Platform - SolidJS Frontend",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "solid-js": "^1.8.11",
    "the-solid-router": "^0.0.2",
    "solid-icons": "^1.1.0"
  },
  "devDependencies": {
    "vite": "^5.0.11",
    "vite-plugin-solid": "^2.8.2",
    "typescript": "^5.3.3",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.33",
    "tailwindcss": "^3.4.1"
  }
}
EOF

echo "✅ Created package.json"

# Create vite.config.ts
cat > vite.config.ts << 'EOF'
import { defineConfig } from 'vite';
import solid from 'vite-plugin-solid';

export default defineConfig({
  plugins: [solid()],
  server: {
    port: 3000,
    host: true,
  },
  build: {
    target: 'esnext',
    outDir: 'dist',
  },
});
EOF

echo "✅ Created vite.config.ts"

# Create tsconfig.json
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    "jsx": "preserve",
    "jsxImportSource": "solid-js",
    "types": ["vite/client"],
    "noEmit": true,
    "isolatedModules": true,
    "strict": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "baseUrl": ".",
    "paths": {
      "~/*": ["./src/*"]
    }
  },
  "include": ["src"]
}
EOF

echo "✅ Created tsconfig.json"

# Create Tailwind CSS config
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
      },
    },
  },
  plugins: [],
}
EOF

echo "✅ Created tailwind.config.js"

# Create PostCSS config
cat > postcss.config.js << 'EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

echo "✅ Created postcss.config.js"

# Create src directory structure
echo "📁 Creating src directory structure..."
mkdir -p src/{components,pages,services,stores,types,assets/styles}

# Create index.html
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="Rural Farming & Livestock Management Platform" />
    <meta name="theme-color" content="#22c55e" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <title>CropSense AI - Farming Platform</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
    <script type="module" src="/src/index.tsx"></script>
  </body>
</html>
EOF

echo "✅ Created index.html"

# Create main CSS file
cat > src/assets/styles/index.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gray-50 text-gray-900;
  }
}

@layer components {
  .btn-primary {
    @apply bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors;
  }
  
  .btn-secondary {
    @apply bg-gray-200 text-gray-900 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors;
  }
  
  .card {
    @apply bg-white rounded-lg shadow-md p-6;
  }
}
EOF

echo "✅ Created index.css"

# Create index.tsx
cat > src/index.tsx << 'EOF'
/* @refresh reload */
import { render } from 'solid-js/web';
import { Router } from 'the-solid-router';
import App from './App';
import './assets/styles/index.css';

const root = document.getElementById('root');

if (import.meta.env.DEV && !(root instanceof HTMLElement)) {
  throw new Error(
    'Root element not found. Did you forget to add it to your index.html? Or maybe the id attribute got misspelled?',
  );
}

render(
  () => (
    <Router>
      <App />
    </Router>
  ),
  root!
);
EOF

echo "✅ Created src/index.tsx"

# Create App.tsx
cat > src/App.tsx << 'EOF'
import { Component } from 'solid-js';
import { Route, Routes } from 'the-solid-router';
import Home from './pages/Home';

const App: Component = () => {
  return (
    <div class="min-h-screen">
      <Routes>
        <Route path="/" component={Home} />
      </Routes>
    </div>
  );
};

export default App;
EOF

echo "✅ Created src/App.tsx"

# Create Home page
cat > src/pages/Home.tsx << 'EOF'
import { Component } from 'solid-js';

const Home: Component = () => {
  return (
    <div class="container mx-auto px-4 py-8">
      <div class="text-center">
        <h1 class="text-4xl font-bold text-primary-600 mb-4">
          🌾 CropSense AI
        </h1>
        <h2 class="text-2xl text-gray-700 mb-8">
          Rural Farming & Livestock Management Platform
        </h2>
        <div class="card max-w-2xl mx-auto">
          <p class="text-lg text-gray-600 mb-4">
            Welcome to the AI-powered platform for rural farmers
          </p>
          <p class="text-gray-500">
            Get predictive intelligence for crop management, direct marketplace access,
            and livestock optimization to increase profitability and sustainability.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Home;
EOF

echo "✅ Created src/pages/Home.tsx"

# Create .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/

# Build output
dist/
.solid/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
EOF

echo "✅ Created .gitignore"

# Create types directory with placeholder
cat > src/types/index.ts << 'EOF'
// Generated types will be placed here by setup.php
export {};
EOF

echo "✅ Created src/types/index.ts"

# Create shared directory structure for generated code
mkdir -p src/shared/{Interface/Model,Service,Store}

cat > src/shared/Interface/Model/.gitkeep << 'EOF'
# Generated model interfaces will be placed here
EOF

cat > src/shared/Service/.gitkeep << 'EOF'
# Generated services will be placed here
EOF

cat > src/shared/Store/.gitkeep << 'EOF'
# Generated stores will be placed here
EOF

echo "✅ Created shared directory structure"

echo ""
echo "📦 Installing dependencies..."
echo "   This may take a few minutes..."
echo ""

npm install

echo ""
echo "================================================================"
echo "✅ SolidJS project initialized successfully!"
echo "================================================================"
echo ""
echo "📁 Project structure:"
echo "   solidjs/"
echo "   ├── src/"
echo "   │   ├── assets/styles/     # CSS files"
echo "   │   ├── components/        # Reusable components"
echo "   │   ├── pages/             # Page components"
echo "   │   ├── services/          # API services"
echo "   │   ├── stores/            # State management"
echo "   │   ├── types/             # TypeScript types"
echo "   │   ├── shared/            # Generated code (from setup.php)"
echo "   │   ├── App.tsx            # Main app component"
echo "   │   └── index.tsx          # Entry point"
echo "   ├── index.html             # HTML template"
echo "   ├── package.json           # Dependencies"
echo "   ├── vite.config.ts         # Vite configuration"
echo "   ├── tsconfig.json          # TypeScript configuration"
echo "   └── tailwind.config.js     # Tailwind CSS configuration"
echo ""
echo "🚀 Next steps:"
echo "   1. Run 'php setup.php' to generate code from JSON schemas"
echo "   2. Start development server:"
echo "      cd solidjs && npm run dev"
echo "   3. Open http://localhost:3000 in your browser"
echo ""
echo "📚 Available commands:"
echo "   npm run dev       - Start development server"
echo "   npm run build     - Build for production"
echo "   npm run preview   - Preview production build"
echo "   npm run type-check - Check TypeScript types"
echo ""
