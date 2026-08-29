# Correctness Validation

## Automated checks

The project is validated from the repository root with:

```bash
npm ci
npm run type-check
npm run lint
npm test
npm run build
npm run dev
```

GitHub Actions runs install, type checking, ESLint, Vitest, and the production build on pushes and pull requests.

## Functional validation

Controlled Chrome and Firefox workflows verified:

- PDF loading, page navigation, thumbnails, every zoom option, and all view modes
- direct page entry, keyboard navigation, viewer rotation, and the 125% single-page default
- editor rotation, reordering, deletion, import/merge, extraction, keep-selected, copy/paste, undo/redo, cancel, save, and export
- browser print launch
- linearized PDF loading through HTTP `206 Partial Content` range requests
- native highlights, text notes, rectangle and selected-text redactions, applied redaction, and bookmark CRUD
- PNG/JPEG scan conversion, progress reporting, cancellation, invalid-input rejection, and atomic insertion
- host upload success, rejected upload recovery, persisted-document reopen, refreshed metadata, and Quick Download

Exported PDFs were reopened and inspected for page count, page order, rotation, annotations, bookmark changes, scan-page geometry, and removal of applied-redaction text. Screenshots from the final workflows are retained in [`screenshots/`](screenshots/).

## Boundaries

- PDF.js, not MuPDF, renders viewer pages.
- Signature-widget creation and cryptographic signing are not claimed.
- The persistence endpoint is a local demonstration service, not production infrastructure.
- Native screen-reader, touch-device, Safari, broad performance, and adversarial-PDF certification are outside the validated scope.
