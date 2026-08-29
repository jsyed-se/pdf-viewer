import { describe, expect, it } from 'vitest';
import packageManifest from '../../package.json';

interface PackageManifest {
  name?: string;
  private?: boolean;
  type?: string;
  main?: string;
  module?: string;
  types?: string;
  files?: string[];
  exports?: Record<string, unknown>;
  dependencies?: Record<string, string>;
  peerDependencies?: Record<string, string>;
  scripts?: Record<string, string>;
}

const manifest = packageManifest as PackageManifest;

describe('SDK package metadata', () => {
  it('defines the local ESM package and its supported entry points', () => {
    expect(manifest).toMatchObject({
      name: '@atlas-pdf/react-sdk',
      private: true,
      type: 'module',
      main: './dist-sdk/index.js',
      module: './dist-sdk/index.js',
      types: './dist-sdk/index.d.ts',
      files: ['dist-sdk', 'README.md'],
    });
    expect(manifest.exports).toEqual({
      '.': {
        types: './dist-sdk/index.d.ts',
        import: './dist-sdk/index.js',
      },
      './styles.css': './dist-sdk/styles.css',
      './package.json': './package.json',
    });
  });

  it('externalizes React through peer dependencies', () => {
    expect(manifest.peerDependencies).toEqual({
      react: '>=19.0.0',
      'react-dom': '>=19.0.0',
    });
    expect(manifest.dependencies?.react).toBeUndefined();
    expect(manifest.dependencies?.['react-dom']).toBeUndefined();
  });

  it('has explicit SDK build and pack commands', () => {
    expect(manifest.scripts?.['build:sdk']).toContain('vite.sdk.config.ts');
    expect(manifest.scripts?.['build:sdk']).toContain('tsconfig.sdk.json');
    expect(manifest.scripts?.['pack:sdk']).toContain('npm pack');
  });
});
