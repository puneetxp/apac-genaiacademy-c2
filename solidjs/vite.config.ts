import { defineConfig } from 'vite';
import solid from 'vite-plugin-solid';
import path from 'path';

export default defineConfig({
  plugins: [solid()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
    transformMode: {
      web: [/\.[jt]sx?$/],
    },
    deps: {
      inline: [/solid-js/, /@solidjs\/router/],
    },
  },
  resolve: {
    alias: {
      '~': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    target: 'es2015', // Support older Android devices (Android 8.0+)
    outDir: 'dist',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console logs in production
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // Split vendor code for better caching
          if (id.includes('node_modules')) {
            if (id.includes('solid-js')) {
              return 'vendor-solid';
            }
            if (id.includes('@solidjs/router')) {
              return 'vendor-router';
            }
            if (id.includes('solid-icons')) {
              return 'vendor-icons';
            }
            return 'vendor';
          }
          
          // Split by feature for lazy loading
          if (id.includes('/components/dashboard/')) {
            return 'dashboard';
          }
          if (id.includes('/components/strategy/')) {
            return 'strategy';
          }
          if (id.includes('/components/marketplace/')) {
            return 'marketplace';
          }
          if (id.includes('/components/farm/')) {
            return 'farm';
          }
          if (id.includes('/components/auth/')) {
            return 'auth';
          }
        },
      },
    },
    chunkSizeWarningLimit: 500, // Warn if chunks exceed 500KB
    cssCodeSplit: true, // Split CSS for better loading
  },
  publicDir: 'public',
  // Optimize dependencies
  optimizeDeps: {
    include: ['solid-js', 'solid-icons'],
  },
});
