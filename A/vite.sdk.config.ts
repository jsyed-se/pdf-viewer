import { resolve } from 'node:path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: './',
  define: { __ATLAS_PDF_PACKAGED__: 'true' },
  plugins: [react()],
  worker: {
    format: 'es',
    rolldownOptions: {
      output: {
        entryFileNames: 'assets/[name].js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name][extname]',
      },
    },
  },
  build: {
    target: 'es2022',
    outDir: 'dist-sdk',
    emptyOutDir: true,
    sourcemap: true,
    copyPublicDir: false,
    lib: {
      entry: resolve(import.meta.dirname, 'src/sdk/index.ts'),
      formats: ['es'],
      fileName: () => 'index.js',
      cssFileName: 'styles',
    },
    rolldownOptions: {
      external: ['react', 'react-dom', 'react/jsx-runtime'],
    },
  },
});
