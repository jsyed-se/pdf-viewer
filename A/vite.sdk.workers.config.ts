import { resolve } from 'node:path';
import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  build: {
    target: 'es2022',
    outDir: 'dist-sdk/assets',
    emptyOutDir: false,
    sourcemap: true,
    copyPublicDir: false,
    lib: {
      entry: {
        'pdfEngine.bootstrap.worker': resolve(import.meta.dirname, 'src/workers/pdfEngine.bootstrap.worker.ts'),
        'scanConversion.bootstrap.worker': resolve(import.meta.dirname, 'src/workers/scanConversion.bootstrap.worker.ts'),
      },
      formats: ['es'],
      fileName: (_format, entryName) => `${entryName}.js`,
    },
    rolldownOptions: {
      output: {
        chunkFileNames: '[name]-[hash].js',
        assetFileNames: '[name]-[hash][extname]',
      },
    },
  },
});
