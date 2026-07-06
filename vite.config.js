// vite.config.js
import { defineConfig } from 'vite'
export default defineConfig({
  plugins: [],
  esbuild: "",
  build: {
    rollupOptions: {
      output: {
        dir: "public/assets/js",
        entryFileNames: '[name].js',
      },
      input: {
        index: 'Resource/Js/index.js'
      }
    },
  },
})
