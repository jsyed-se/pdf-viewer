# Atlas React PDF SDK

## Packaging Status

`@atlas-pdf/react-sdk` is the local package name for the reusable viewer. Its packed artifact has been installed and exercised in an independent consumer in development and production modes. It is not published to npm, production-supported, or an official Neubus package.

## Public API

Consumers use one package entry. The supported exports are intentionally limited to:

- `PdfViewerSDK` and `PdfViewerSDKProps`
- `PdfDocumentSource`
- `AttachmentMetadata`
- `PdfSaveRequest` and `PdfSaveResult`
- `PdfViewerAssetConfig`
- `PdfReadyDetails`, `PdfPasswordReason`, `PdfProgressCallback`, and `PdfErrorCallback`
- `ViewerLifecycleCallbacks`

Worker messages, engine clients, state helpers, reducers, hooks, and internal UI components are not public API. Importing from `A/src/` or another package subpath is unsupported.

## Local Consumer Example

Build and pack from the repository root, then install the generated tarball in a consumer. The completed acceptance evidence is recorded in [`../C/validation.md`](../C/validation.md).

```bash
npm run build:sdk
npm run pack:sdk
npm install /absolute/path/to/atlas-pdf-react-sdk-1.0.0.tgz
```

Import only the public package entries:

```tsx
import { PdfViewerSDK } from '@atlas-pdf/react-sdk';
import type {
  PdfDocumentSource,
  PdfSaveRequest,
  PdfSaveResult,
} from '@atlas-pdf/react-sdk';
import '@atlas-pdf/react-sdk/styles.css';

const source: PdfDocumentSource = {
  kind: 'url',
  url: 'https://files.example.com/report.pdf',
  filename: 'report.pdf',
};

async function savePdf(request: PdfSaveRequest): Promise<PdfSaveResult> {
  const attachment = await persistPdfInHost(request);
  return { attachment, savedAt: new Date().toISOString() };
}

export function DocumentView() {
  return (
    <PdfViewerSDK
      source={source}
      attachment={{ id: 'report-42', filename: 'report.pdf' }}
      assets={{ baseUrl: '/atlas-pdf-assets/' }}
      onProgress={(loaded, total) => reportProgress(loaded, total)}
      onDirtyChange={(dirty) => protectHostNavigation(dirty)}
      onSave={savePdf}
      onError={(error) => reportError(error)}
      onCloseRequest={() => closeViewerInHost()}
    />
  );
}
```

React and React DOM are peer dependencies and must be installed by the host. No consumer should resolve a second React runtime through the SDK.

## Source and Callback Contracts

`PdfDocumentSource` accepts a browser `File`, an HTTP(S) URL with an optional filename, or a `Uint8Array` with a filename. Equivalent source values must not reset the active document merely because a parent creates a new object or callback during rendering.

The host owns records, attachment metadata, authentication, navigation, persistence, and host-specific save confirmation. The SDK owns PDF loading, viewing, editing, processing, printing, export, and save initiation. Status callbacks report readiness, transfer progress, active page, dirty state, errors, password requests, and close requests. `showSaveConfirmation` optionally enables the SDK's generic post-save dialog; it is off by default, while the included legacy demo opts in.

Save is transactional:

1. The SDK serializes candidate PDF bytes.
2. It calls `onSave(request)` with the bytes, filename, PDF MIME type, attachment context, and abort signal.
3. It waits for the host promise.
4. It commits and clears dirty state only after success.
5. A rejection keeps edits dirty and available for retry or local download.

The SDK never embeds a demo persistence endpoint. A production host must implement its own authenticated `onSave` behavior.

## Runtime Assets

The host must recursively copy the installed package's entire `dist-sdk/assets/` directory to a public directory and pass its served URL as `assets.baseUrl`. For example, copy it to `public/atlas-pdf-assets/` and configure `assets={{ baseUrl: '/atlas-pdf-assets/' }}`. Copy the directory as a unit: the MuPDF document worker, scan worker, embedded WebAssembly, hashed worker chunks, and PDF.js CMaps, standard fonts, and decoder WASM must stay together. The PDF.js worker itself is embedded as a data URL in the package entry. The example consumer automates the hosted copy in `examples/sdk-consumer/scripts/copy-sdk-assets.mjs`.

An empty or invalid base URL is rejected, and a packaged MuPDF/scan operation reports an actionable error when the configuration is missing. The installed tarball was validated in clean development and production consumers with successful document-worker, scan-worker, shared-chunk, and embedded-WASM loading.

## Browser Support and Limits

The browser must support Web Workers, WebAssembly, canvas, `ResizeObserver`, and `IntersectionObserver`. Existing validation covers Chrome and Firefox; Safari, native screen-reader/touch behavior, and broad performance or adversarial-PDF testing are not certified. PDF.js renders viewer pages. MuPDF performs document processing. Signature-field creation and cryptographic signing remain unsupported.

## License

The SDK and demonstration application are AGPL-3.0-or-later because they include MuPDF.js. Packaging does not remove AGPL obligations. Distribution or network use may require corresponding-source availability and other compliance steps; proprietary distribution may require a commercial Artifex license. See the repository `LICENSE`, `NOTICE-MUPDF.md`, and `A/public/SOURCE_OFFER.txt`. This summary is not legal advice.
