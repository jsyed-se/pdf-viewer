import assert from 'node:assert/strict';
import { access, cp, mkdir, mkdtemp, readFile, readdir, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const npmCli = process.env.npm_execpath;
assert(npmCli, 'npm_execpath is required to run the packed-consumer validation');
const testsRoot = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(testsRoot, '..', '..');
const exampleRoot = resolve(repositoryRoot, 'examples', 'sdk-consumer');
const temporaryRoot = await mkdtemp(join(tmpdir(), 'atlas-sdk-consumer-test-'));
const packRoot = join(temporaryRoot, 'pack');
const consumerRoot = join(temporaryRoot, 'consumer');

function run(args, cwd) {
  execFileSync(process.execPath, [npmCli, ...args], { cwd, stdio: 'inherit' });
}

try {
  await mkdir(packRoot, { recursive: true });
  await cp(exampleRoot, consumerRoot, {
    recursive: true,
    filter: (source) =>
      !source.includes(`${join('node_modules')}`) &&
      !source.includes(`${join('dist')}`) &&
      !source.includes(`${join('public', 'atlas-pdf-assets')}`) &&
      !source.endsWith(join('public', 'sample-scan.png')),
  });

  const source = await readFile(join(consumerRoot, 'src', 'App.tsx'), 'utf8');
  assert.match(source, /from '@atlas-pdf\/react-sdk'/);
  assert.doesNotMatch(source, /A\/src|\.\.\/\.\.\/A/);

  run(['pack', '--workspace', '@atlas-pdf/react-sdk', '--pack-destination', packRoot], repositoryRoot);
  const tarballs = (await readdir(packRoot)).filter((name) => name.endsWith('.tgz'));
  assert.equal(tarballs.length, 1, 'expected one packed SDK tarball');

  run(['install', '--no-audit', '--no-fund'], consumerRoot);
  run(['install', '--no-save', '--no-audit', '--no-fund', join(packRoot, tarballs[0])], consumerRoot);
  run(['run', 'typecheck'], consumerRoot);
  run(['run', 'build'], consumerRoot);

  const emittedAssets = await readdir(join(consumerRoot, 'dist', 'atlas-pdf-assets'));
  assert(emittedAssets.includes('pdfEngine.bootstrap.worker.js'));
  assert(emittedAssets.includes('scanConversion.bootstrap.worker.js'));
  assert(emittedAssets.some((name) => name.startsWith('mupdf-') && name.endsWith('.js')));
  await access(join(consumerRoot, 'dist', 'atlas-pdf-assets', 'pdfjs', 'wasm', 'jbig2.wasm'));
  await access(join(consumerRoot, 'dist', 'atlas-pdf-assets', 'pdfjs', 'cmaps', 'Adobe-Japan1-0.bcmap'));
  await access(join(consumerRoot, 'dist', 'atlas-pdf-assets', 'pdfjs', 'standard_fonts', 'LiberationSans-Regular.ttf'));
  console.log('Packed consumer install, typecheck, production build, and asset copy passed.');
} finally {
  await rm(temporaryRoot, { recursive: true, force: true });
}
