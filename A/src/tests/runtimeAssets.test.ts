import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  PDF_ENGINE_WORKER_FILE,
  pdfJsRuntimeOptions,
  resolveRuntimeAsset,
  runtimeWorkerUrl,
  SCAN_CONVERSION_WORKER_FILE,
} from '../sdk/runtimeAssets';

describe('packaged runtime asset resolution', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('resolves documented worker names beneath a document-relative base URL', () => {
    vi.stubGlobal('document', { baseURI: 'https://consumer.example/app/index.html' });

    expect(resolveRuntimeAsset('/vendor/atlas-assets', PDF_ENGINE_WORKER_FILE))
      .toBe('https://consumer.example/vendor/atlas-assets/pdfEngine.bootstrap.worker.js');
    expect(resolveRuntimeAsset('./sdk-assets/', SCAN_CONVERSION_WORKER_FILE))
      .toBe('https://consumer.example/app/sdk-assets/scanConversion.bootstrap.worker.js');
  });

  it('uses configured package assets without exposing source-relative worker paths', () => {
    vi.stubGlobal('document', { baseURI: 'https://consumer.example/' });
    const sourceUrl = new URL('https://source.invalid/workers/pdfEngine.bootstrap.worker.ts');

    expect(runtimeWorkerUrl('/assets/pdf-sdk', PDF_ENGINE_WORKER_FILE, sourceUrl))
      .toBe('https://consumer.example/assets/pdf-sdk/pdfEngine.bootstrap.worker.js');
  });

  it('resolves PDF.js support data beneath the configured package asset base', () => {
    vi.stubGlobal('document', { baseURI: 'https://consumer.example/app/' });

    expect(pdfJsRuntimeOptions('/assets/pdf-sdk')).toEqual({
      cMapUrl: 'https://consumer.example/assets/pdf-sdk/pdfjs/cmaps/',
      cMapPacked: true,
      standardFontDataUrl: 'https://consumer.example/assets/pdf-sdk/pdfjs/standard_fonts/',
      wasmUrl: 'https://consumer.example/assets/pdf-sdk/pdfjs/wasm/',
    });
  });

  it('rejects an empty configured asset base', () => {
    vi.stubGlobal('document', { baseURI: 'https://consumer.example/' });
    expect(() => resolveRuntimeAsset('  ', PDF_ENGINE_WORKER_FILE))
      .toThrow('assets.baseUrl must not be empty');
  });
});
