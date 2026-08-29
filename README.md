# Atlas PDF SDK

Atlas contains a React/TypeScript PDF viewer, transactional document editor, locally distributable SDK package, and demonstration host. The package name is `@atlas-pdf/react-sdk`. It is validated as a local `npm pack` artifact, but it is not published to npm, production-supported, or presented as an official Neubus package. See [`C/validation.md`](C/validation.md) for the packed-consumer evidence.

## Run locally

Requires Node.js 22.13+ or 24+.

```bash
npm install
npm run dev
```

The development server prints its local URL and provides a demonstration records-and-attachments API. No environment variables are required.

```bash
npm run type-check
npm run lint
npm test
npm run build
npm run build:sdk
npm run pack:sdk
```

`npm run build` builds the demonstration application. `npm run build:sdk` creates the library output, declarations, source maps, stylesheet, notices, and runtime assets. `npm run pack:sdk` creates a local `.tgz` with `npm pack`; generated output and tarballs are not committed.

## Features

- High-DPI PDF rendering, thumbnails, page navigation, keyboard navigation, and selectable text
- Zoom in/out, fit-to-width, fit-to-viewport, continuous, single-page, and spread modes
- HTTP byte-range loading for linearized PDFs when the source server supports `206 Partial Content`
- Page rotation, reordering, deletion, import/merge, extraction, keep-selected, copy/paste, and undo/redo
- Browser printing and local export
- PNG/JPEG scan-to-PDF import with progress and cancellation
- Native highlights, notes, rectangle/text redaction, applied redaction, and bookmark editing
- Host-controlled save, upload confirmation, records search, attachment management, and Quick Download

## Repository structure

- [`A/`](A/README.md) — MVP application, SDK source, and public API guide
- [`B/architecture-and-design.md`](B/architecture-and-design.md) — required architecture and design document
- [`C/README.md`](C/README.md) — required AI usage and validation records

## SDK integration

Install the locally generated tarball in the consumer, then import only the public package entries:

```bash
npm install /absolute/path/to/atlas-pdf-react-sdk-1.0.0.tgz
```

```tsx
import { PdfViewerSDK, type PdfDocumentSource } from '@atlas-pdf/react-sdk';
import '@atlas-pdf/react-sdk/styles.css';

const source: PdfDocumentSource = {
  kind: 'url',
  url: 'https://files.example.com/report.pdf',
  filename: 'report.pdf',
};

<PdfViewerSDK
  source={source}
  attachment={{ id: 'report-42', filename: 'report.pdf' }}
  assets={{ baseUrl: '/atlas-pdf-assets/' }}
  onSave={(request) => persistInHost(request)}
  onDirtyChange={(dirty) => protectHostNavigation(dirty)}
  onCloseRequest={() => closeViewerInHost()}
/>
```

Recursively copy the installed package's complete `dist-sdk/assets/` directory to the host's public assets directory and set `assets.baseUrl` to its served URL. Do not copy selected files: worker entry files load hashed chunks and WASM from the same directory. The host owns records, attachment metadata, surrounding navigation, authentication, and persistence. The SDK owns PDF loading, viewing, editing, printing, export, and save initiation. It serializes a candidate, awaits the host's asynchronous `onSave` result, and commits only after success; failure preserves dirty edits for retry or local download. See [`A/README.md`](A/README.md) for the public API and complete integration contract.

## Known limitations

- PDF.js performs viewer rendering; MuPDF WebAssembly performs document processing.
- Signature-field creation and cryptographic signing are not implemented. Existing widgets can be inspected.
- The included persistence API is a local demonstration service with a 25 MB limit and no authentication or cloud storage.
- Browser validation covers Chrome and Firefox; print options remain browser-dependent.
- Annotation resizing is numeric, and direct text selection is page-scoped.

## Licensing

This project is AGPL-3.0-or-later because it uses MuPDF.js. Packaging MuPDF does not remove its license obligations. Distribution or network deployment may require corresponding-source and other AGPL compliance, while proprietary distribution may require a commercial Artifex license. See [`LICENSE`](LICENSE), [`NOTICE-MUPDF.md`](NOTICE-MUPDF.md), and [`A/public/SOURCE_OFFER.txt`](A/public/SOURCE_OFFER.txt). PDF.js is Apache-2.0. This summary is not legal advice.
