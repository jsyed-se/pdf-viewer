import { copyFile, cp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const packageRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const repositoryRoot = resolve(packageRoot, '..');
const outputRoot = resolve(packageRoot, 'dist-sdk');
const declarationRoot = resolve(outputRoot, '.types', 'sdk');

const declarations = [
  ['index.d.ts', 'index.d.ts'],
  ['index.d.ts.map', 'index.d.ts.map'],
  ['PdfViewerSDK.d.ts', 'PdfViewerSDK.d.ts'],
  ['PdfViewerSDK.d.ts.map', 'PdfViewerSDK.d.ts.map'],
  ['publicTypes.d.ts', 'publicTypes.d.ts'],
  ['publicTypes.d.ts.map', 'publicTypes.d.ts.map'],
];

for (const [source, destination] of declarations) {
  await copyFile(resolve(declarationRoot, source), resolve(outputRoot, destination));
}
await rm(resolve(outputRoot, '.types'), { recursive: true, force: true });

await copyFile(resolve(repositoryRoot, 'LICENSE'), resolve(outputRoot, 'LICENSE'));
await copyFile(resolve(repositoryRoot, 'NOTICE-MUPDF.md'), resolve(outputRoot, 'NOTICE-MUPDF.md'));
await copyFile(resolve(packageRoot, 'public', 'SOURCE_OFFER.txt'), resolve(outputRoot, 'SOURCE_OFFER.txt'));

const pdfJsRoot = resolve(repositoryRoot, 'node_modules', 'pdfjs-dist');
for (const directory of ['cmaps', 'standard_fonts', 'wasm']) {
  await cp(resolve(pdfJsRoot, directory), resolve(outputRoot, 'assets', 'pdfjs', directory), {
    recursive: true,
    force: true,
  });
}

const entryPath = resolve(outputRoot, 'index.js');
const entry = await readFile(entryPath, 'utf8');
if (/from\s*["']react(?:-dom|\/jsx-runtime)?["']/.test(entry) === false) {
  throw new Error('The SDK entry does not retain the expected external React import.');
}
if (/\/api\/demo|demoRepository|node:fs|CASE-2026/.test(entry)) {
  throw new Error('Demo-only implementation leaked into the SDK entry.');
}

const manifest = {
  generatedAt: new Date().toISOString(),
  assetStrategy: 'hosted copy configured through PdfViewerSDK assets.baseUrl',
  entry: 'index.js',
  stylesheet: 'styles.css',
  copyFrom: 'dist-sdk/assets',
  requiredBaseUrl: true,
  documentWorker: 'pdfEngine.bootstrap.worker.js',
  scanWorker: 'scanConversion.bootstrap.worker.js',
  pdfJsAssets: 'pdfjs/',
  files: (await readdir(resolve(outputRoot, 'assets'))).sort(),
};
await mkdir(outputRoot, { recursive: true });
await writeFile(resolve(outputRoot, 'package-assets.json'), `${JSON.stringify(manifest, null, 2)}\n`);
