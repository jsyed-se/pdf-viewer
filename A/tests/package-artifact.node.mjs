import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const packageRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const outputRoot = resolve(packageRoot, 'dist-sdk');
const assetsRoot = resolve(outputRoot, 'assets');

function read(path) {
  return readFileSync(resolve(outputRoot, path), 'utf8');
}

test('built SDK contains its public runtime, declarations, maps, and legal files', () => {
  for (const path of [
    'index.js',
    'index.js.map',
    'index.d.ts',
    'index.d.ts.map',
    'styles.css',
    'package-assets.json',
    'LICENSE',
    'NOTICE-MUPDF.md',
    'SOURCE_OFFER.txt',
  ]) assert.equal(existsSync(resolve(outputRoot, path)), true, `${path} is missing`);

  assert.doesNotMatch(read('index.js'), /\/api\/demo|demoRepository|node:fs|CASE-2026|C\/evidence/);
  assert.match(read('index.js'), /from\s*["']react(?:\/jsx-runtime)?["']/);
  assert.match(read('index.js'), /data:text\/javascript;base64,/, 'PDF.js worker is not embedded in the package entry');
});

test('worker bootstrap imports and embedded MuPDF WASM resolve inside packaged assets', () => {
  const manifest = JSON.parse(read('package-assets.json'));
  const actualFiles = readdirSync(assetsRoot).sort();
  assert.deepEqual(manifest.files, actualFiles);

  for (const bootstrap of [manifest.documentWorker, manifest.scanWorker]) {
    const source = readFileSync(resolve(assetsRoot, bootstrap), 'utf8');
    const imported = [...source.matchAll(/import\(["']\.\/([^"']+)["']\)/g)].map((match) => match[1]);
    assert.ok(imported.length > 0, `${bootstrap} does not import a worker implementation`);
    for (const target of imported) assert.equal(existsSync(resolve(assetsRoot, target)), true, `${bootstrap} references missing ${target}`);
    assert.doesNotMatch(source, /\.ts["']/);
  }

  const mupdfChunks = actualFiles.filter((file) => /^mupdf-.*\.js$/.test(file));
  const separateWasm = actualFiles.some((file) => file.endsWith('.wasm'));
  const embeddedWasm = mupdfChunks.some((file) => readFileSync(resolve(assetsRoot, file), 'utf8').includes('data:application/wasm;base64,AGFzbQE'));
  assert.equal(separateWasm || embeddedWasm, true, 'MuPDF WASM is neither emitted nor embedded');

  for (const path of [
    'pdfjs/wasm/jbig2.wasm',
    'pdfjs/wasm/jbig2_nowasm_fallback.js',
    'pdfjs/cmaps/Adobe-Japan1-0.bcmap',
    'pdfjs/standard_fonts/LiberationSans-Regular.ttf',
  ]) assert.equal(existsSync(resolve(assetsRoot, path)), true, `PDF.js runtime asset is missing: ${path}`);
});

test('npm pack allowlist contains only distributable package files', () => {
  const npmCli = process.env.npm_execpath;
  assert.ok(npmCli, 'npm_execpath is required for package validation');
  const result = JSON.parse(execFileSync(process.execPath, [npmCli, 'pack', '--dry-run', '--json', '--ignore-scripts'], {
    cwd: packageRoot,
    encoding: 'utf8',
  }));
  const paths = result[0].files.map((file) => file.path);

  for (const path of paths) {
    assert.ok(path === 'package.json' || path === 'README.md' || path.startsWith('dist-sdk/'), `unexpected tarball path: ${path}`);
  }
  for (const required of [
    'package.json',
    'README.md',
    'dist-sdk/index.js',
    'dist-sdk/index.d.ts',
    'dist-sdk/styles.css',
    'dist-sdk/package-assets.json',
    'dist-sdk/assets/pdfjs/wasm/jbig2.wasm',
    'dist-sdk/assets/pdfjs/cmaps/Adobe-Japan1-0.bcmap',
    'dist-sdk/assets/pdfjs/standard_fonts/LiberationSans-Regular.ttf',
  ]) {
    assert.ok(paths.includes(required), `tarball is missing ${required}`);
  }
  assert.equal(paths.some((path) => /(^|\/)(src|tests|scripts|\.runtime-data|evidence)(\/|$)/.test(path)), false);
});
