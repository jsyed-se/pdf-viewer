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

## SDK Packaging Validation

Validated implementation commit: `7d005d768b8f4a2c9f754f5e36bbab14ae0f4ff1` on `feature/sdk`. Validation ran on Windows 11 with Node.js 24.14.1, npm 11.11.0, and Chromium 151. The local package is `@atlas-pdf/react-sdk`; it is not published to npm or presented as a production-supported package.

```bash
npm ci
npm run type-check
npm run lint
npm test
npm run build
npm run test:package
npm run test:consumer-package
```

Results: install completed with zero vulnerabilities; type checking and linting passed; Vitest passed 29 tests in 10 files; the demonstration production build passed; and all 3 packed-artifact tests passed. The repeatable clean-consumer gate packed the package, installed its tarball into a fresh temporary React application, type-checked it, recursively copied its installed asset tree, and completed a production build.

The inspected tarball contained 226 intended files (9.4 MB packed, 23.3 MB unpacked): ESM, declarations, source maps, scoped CSS, deterministic worker bootstraps and chunks, MuPDF code with embedded WASM, PDF.js CMaps/fonts/decoder WASM, package metadata, README, license, notice, and source offer. It excluded application source, tests, fixtures, demo files, screenshots, evidence, and transcripts.

Controlled Chromium checks exercised the installed tarball in both Vite development and production-preview modes. The consumer rendered a five-page PDF and navigated to page 2. Production validation loaded the MuPDF editor, rotated a page, converted and inserted a PNG through the scan worker, saved successfully through the host callback with dirty state cleared and no SDK-owned success dialog, then performed another mutation and confirmed an intentional host rejection left the editor open and dirty. DevTools recorded a dedicated `data:text/javascript;base64,...` PDF.js worker target with HTTP 200 and no `Setting up fake worker` console warning. Hosted MuPDF/scan bootstraps and chunks loaded successfully; direct browser fetches of the packaged PDF.js JBIG2 WASM, representative CMap, and standard font returned HTTP 200 with nonzero content. MuPDF WASM remained embedded in its loaded chunk. No SDK runtime asset request returned 404.

## SDK Packaging Conformance

| Requirement | Evidence | Status |
| --- | --- | --- |
| Public package-only import | Explicit root exports plus clean consumer importing only `@atlas-pdf/react-sdk` and its stylesheet | PASS |
| Independent ESM, declarations, maps, and scoped CSS | `build:sdk` output and packed-artifact assertions | PASS |
| Host-provided React runtime | React and React DOM peer dependencies; artifact import assertion | PASS |
| Intentional tarball contents | npm pack allowlist test; 226-file inventory | PASS |
| Clean install, typecheck, and build | `test:consumer-package` temporary-consumer gate | PASS |
| Reliable PDF.js, MuPDF, and scan runtime assets | Asset-resolution and document-worker handshake/correlation tests, artifact path checks, and Chromium worker/network checks | PASS |
| Real document mutation | MuPDF editor rotation observed in the installed consumer | PASS |
| Transactional save success and failure | Automated save tests and installed-consumer success/rejection workflows | PASS |
| Host/SDK responsibility boundary | Package API contracts, host callback example, default host-owned confirmation | PASS |
| Documentation, license, and A/B/C preservation | Root/A/B/C guides, AGPL notice/source offer, unchanged deliverable layout | PASS |

Generated SDK output, tarballs, temporary consumers, copied runtime assets, and `node_modules` remain untracked. This exact implementation commit contains the validated package contents; the subsequent record-only commit changes only this validation file.
