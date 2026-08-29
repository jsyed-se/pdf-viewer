# Atlas PDF SDK Application

## Capabilities

The SDK accepts local files, remote URLs, or raw bytes. PDF.js provides progressive/range loading and high-DPI lazy canvas rendering. MuPDF.js runs in a dedicated Web Worker for real page mutations, native annotations, applied redaction, bookmarks, and final PDF serialization.

Phase 4 adds PNG/JPEG scan import, independent 18%–50% editor zoom, page-scoped temporary viewer rotation, and a single-page 125% default for each new source. Its demonstration host provides record search, attachment metadata, Quick Download, and asynchronous persistence.

Phase 2 browser and persistence validation passed and is closed. See [`../C/phase-2/validation-report.md`](../C/phase-2/validation-report.md) for the tested scope and explicit limits.

The Phase 4 working-candidate result is in [`../C/phase-4/gap-closure-report.md`](../C/phase-4/gap-closure-report.md). Earlier accepted status remains in the Phase 3 conformance matrix.

Implemented viewing features include thumbnails, previous/next/direct navigation, current-page tracking, continuous/single/cover-aware spread modes, keyboard navigation, custom zoom, and fit-to-width/fit-to-viewport calculated from the live container and page dimensions.

The transactional editor supports select all/none, rotation, drag or accessible-button reordering, deletion, import/merge, extraction, keep-selected, copy/paste, undo/redo, save, cancel, and local export. It blocks deletion of every page and protects dirty work during editor close, document replacement, and browser unload.

Native `Text`, `Highlight`, and `Redact` annotations are saved into the PDF. Highlight/redaction can use a drawn rectangle, typed text match, or direct selection in the PDF.js text layer. Redactions can remain annotations or be applied to remove covered content. Annotations can be selected in the panel, outlined on-page, edited, resized numerically, and deleted. Bookmarks can be read, created, edited, and deleted. Existing form widgets are inspected; creation of signature widgets is not claimed.

## SDK Integration

```tsx
import { PdfViewerSDK } from './src/sdk/PdfViewerSDK';
import type { PdfDocumentSource } from './src/sdk/types';

const source: PdfDocumentSource = {
  kind: 'url',
  url: 'https://files.example.com/report.pdf',
  filename: 'report.pdf',
};

<PdfViewerSDK
  source={source}
  attachment={{ id: 'report-42', filename: 'report.pdf' }}
  onReady={({ pageCount }) => console.log(pageCount)}
  onPageChange={(page) => console.log(page)}
  onDirtyChange={(dirty) => protectHostNavigation(dirty)}
  onSave={(request) => persistInHost(request)}
  onError={(error) => reportToHost(error)}
  onCloseRequest={() => closeViewerInHost()}
/>
```

The host owns the source, attachment metadata, surrounding navigation, persistence, and component lifecycle. The SDK owns PDF state and awaits the host's `onSave(request)` promise before it commits a working edit. Success closes the editor and shows confirmation only after the host responds; failure leaves the editor dirty for retry or local download. Password handling can be customized with `onPasswordRequest`; an optional `onCloseRequest` lets the host respond to the SDK's close control.

## Scan Import and View Controls

The editor accepts one or more PNG/JPEG images. A dedicated MuPDF worker reads and converts them with visible progress; cancellation terminates that worker before the converted pages are imported atomically. Invalid input leaves the working document unchanged. Editor-grid zoom is independent of PDF content and ranges from 18% to 50%.

Viewer rotation applies only to the current page presentation and keeps canvas, text, and annotation geometry aligned. It does not dirty the document or alter saved bytes. Every new source opens in single-page mode at 125%; users can then choose another mode or zoom.

## Demonstration Persistence

During Vite development and preview, the sample host exposes a same-origin API for record metadata, persisted attachment bytes, and Quick Download. It accepts only `application/pdf` payloads up to 25 MB and writes ignored state to `A/.runtime-data/`. This is not production storage: there is no authentication, authorization, cloud service, or multi-user isolation. A static deployment must supply an equivalent host endpoint; the SDK itself remains deployment-neutral.

## Commands

Run from the repository root:

```bash
npm install
npm run dev
npm run build
npm run type-check
npm run lint
npm test
```

## Browser and Remote-Server Requirements

Phase 2 browser evidence covers current Chrome and Firefox. Other browsers are not certified; they require JavaScript, Web Workers, WebAssembly, canvas, `ResizeObserver`, and `IntersectionObserver`.

For progressive and linearized remote loading, the PDF server must:

- allow the application origin through CORS;
- expose `Content-Length`, `Accept-Ranges`, and `Content-Range` as needed;
- answer `Range: bytes=…` requests with HTTP `206 Partial Content`;
- serve a genuinely linearized PDF for fastest first-page display.

PDF.js receives the URL directly with ranges enabled and background stream/autofetch disabled. Full bytes are explicitly requested only when editing, annotating, printing, or exporting requires them; a server without byte ranges may still need to return the full PDF for viewing. Source bytes remain local to the browser until the user explicitly chooses Save through a host callback. The included demonstration callback then sends the edited PDF to its same-origin local API; another host controls its own persistence policy.

## Repository Layout

- `src/sdk/` — typed SDK boundary, viewer orchestration, and worker client
- `src/components/` — page canvas/text layer and transactional editor UI
- `src/workers/` — MuPDF WebAssembly document and scan-conversion workers
- `src/app/` — demonstration-host persistence client
- `src/lib/` and `src/tests/` — deterministic view math and focused tests
- `public/` — deployed AGPL license and corresponding-source notice

## Printing and Export

Print uses the current serialized document, opens a synchronous placeholder window to avoid popup blocking, waits for the PDF URL to load, invokes browser print, and revokes temporary resources. Exports use sanitized predictable filenames such as `report-edited.pdf` and `report-selected-pages.pdf`.

## Accessibility

Controls use semantic buttons, labels, pressed/disabled states, visible focus, status/error live regions, and keyboard page navigation. Page reordering has left/right buttons in addition to drag-and-drop. The layout adapts to desktop and tablet widths.

## Known Limitations

- Direct text selection creates annotations one page at a time; multi-page selections are not batched.
- Annotation resizing uses explicit PDF-point dimensions instead of drag handles.
- MuPDF.js 1.28 exposes browser widget inspection but not a safe signature-field creation helper; signature/widget creation and cryptographic signing are not claimed.
- Browser print UI and supported options remain browser-dependent.
- Phase 2 evidence covers the accepted Chrome/Firefox workflows. Phase 4 adds a controlled working-candidate browser flow but does not expand browser certification. Native print appearance, screen-reader/touch certification, broad performance testing, and unsupported signature/widget creation remain outside the validated claim.

## License

AGPL-3.0-or-later. The built app serves `/LICENSE.txt` and `/SOURCE_OFFER.txt`; corresponding source is at <https://github.com/jsyed-se/pdf-viewer>. See the repository root notices for complete dependency details.
