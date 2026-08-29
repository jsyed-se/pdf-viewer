import { cp, mkdir, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const packageJson = require.resolve('@atlas-pdf/react-sdk/package.json');
const packageRoot = dirname(packageJson);
const consumerRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const publicRoot = resolve(consumerRoot, 'public');

await mkdir(publicRoot, { recursive: true });
await cp(resolve(packageRoot, 'dist-sdk', 'assets'), resolve(publicRoot, 'atlas-pdf-assets'), {
  recursive: true,
  force: true,
});

const onePixelPng = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=',
  'base64',
);
await writeFile(resolve(publicRoot, 'sample-scan.png'), onePixelPng);
