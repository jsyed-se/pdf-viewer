# Atlas PDF SDK

Atlas is a React/TypeScript PDF viewer and transactional document editor. PDF.js provides browser rendering, selectable text, navigation, and HTTP range loading. MuPDF.js runs as WebAssembly in Web Workers for document mutation, annotations, redaction, bookmarks, image-to-PDF conversion, and serialization.

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
```

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

- [`A/`](A/) — MVP application and reusable SDK source
- [`B/architecture-and-design.md`](B/architecture-and-design.md) — required architecture and design document
- [`C/README.md`](C/README.md) — required AI usage and validation records

## SDK integration

```tsx
<PdfViewerSDK
  source={{ kind: 'url', url: 'https://files.example.com/report.pdf' }}
  attachment={{ id: 'report-42', filename: 'report.pdf' }}
  onSave={(request) => persistInHost(request)}
  onDirtyChange={(dirty) => protectHostNavigation(dirty)}
  onCloseRequest={() => closeViewerInHost()}
/>
```

The host owns records, attachment metadata, surrounding navigation, and persistence. The SDK owns PDF loading, viewing, editing, printing, and export. It awaits the host's asynchronous `onSave` result before committing a working document.

## Known limitations

- PDF.js performs viewer rendering; MuPDF WebAssembly performs document processing.
- Signature-field creation and cryptographic signing are not implemented. Existing widgets can be inspected.
- The included persistence API is a local demonstration service with a 25 MB limit and no authentication or cloud storage.
- Browser validation covers Chrome and Firefox; print options remain browser-dependent.
- Annotation resizing is numeric, and direct text selection is page-scoped.

## Licensing

This project is AGPL-3.0-or-later because it uses MuPDF.js. See [`LICENSE`](LICENSE), [`NOTICE-MUPDF.md`](NOTICE-MUPDF.md), and [`A/public/SOURCE_OFFER.txt`](A/public/SOURCE_OFFER.txt). PDF.js is Apache-2.0.
