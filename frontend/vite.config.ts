import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5600',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://127.0.0.1:5600',
        ws: true,
      },
      '/static': {
        target: 'http://127.0.0.1:5600',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: path.resolve(__dirname, '../apps/football_pool/static/dist'),
    emptyOutDir: true,
  },
});
