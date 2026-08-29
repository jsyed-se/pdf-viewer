export const PDF_ENGINE_WORKER_FILE = 'pdfEngine.bootstrap.worker.js';
export const SCAN_CONVERSION_WORKER_FILE = 'scanConversion.bootstrap.worker.js';

declare const __ATLAS_PDF_PACKAGED__: boolean | undefined;

const packagedBuild = typeof __ATLAS_PDF_PACKAGED__ !== 'undefined' && __ATLAS_PDF_PACKAGED__;

export function resolveRuntimeAsset(baseUrl: string, filename: string): string {
  const trimmed = baseUrl.trim();
  if (!trimmed) throw new Error('PdfViewerSDK assets.baseUrl must not be empty.');
  const normalized = trimmed.endsWith('/') ? trimmed : `${trimmed}/`;
  try {
    return new URL(filename, new URL(normalized, document.baseURI)).href;
  } catch {
    throw new Error('PdfViewerSDK assets.baseUrl must be a valid absolute or document-relative URL.');
  }
}

export function runtimeWorkerUrl(baseUrl: string | undefined, filename: string, sourceUrl: URL): string | URL {
  if (baseUrl) return resolveRuntimeAsset(baseUrl, filename);
  if (packagedBuild) {
    throw new Error(`PdfViewerSDK requires assets.baseUrl before starting ${filename}. Copy the package dist-sdk/assets directory and configure its served URL.`);
  }
  return sourceUrl;
}

export function pdfJsRuntimeOptions(baseUrl: string | undefined) {
  if (baseUrl) {
    return {
      cMapUrl: resolveRuntimeAsset(baseUrl, 'pdfjs/cmaps/'),
      cMapPacked: true,
      standardFontDataUrl: resolveRuntimeAsset(baseUrl, 'pdfjs/standard_fonts/'),
      wasmUrl: resolveRuntimeAsset(baseUrl, 'pdfjs/wasm/'),
    };
  }
  if (packagedBuild) {
    throw new Error('PdfViewerSDK requires assets.baseUrl to load PDF.js runtime assets. Copy the package dist-sdk/assets directory and configure its served URL.');
  }
  return {};
}
