# Architecture and Design

## Component Diagram

```text
Demo host (`App`)
  owns records, attachment metadata, navigation, persistence
  └─ same-origin Vite demo API ── ignored `A/.runtime-data/`
             │ typed props + lifecycle callbacks
             ▼
`PdfViewerSDK`
  ├─ loading/view state ── PDF.js loading task + PDF.js worker
  │                         range/stream transport, page render, passwords
  ├─ viewer UI ─────────── lazy high-DPI canvases, thumbnails, fit/navigation
  ├─ editor UI ─────────── selection, drag/accessible reorder, transactions
  ├─ scan client ───────── dedicated MuPDF image-conversion worker
  └─ `PdfEngineClient` ─── dedicated document Web Worker
                              └─ MuPDF.js WebAssembly
                                 page mutation, annotations, redaction,
                                 outlines, widget inspection, serialization
```

## SDK Integration Boundary

The host supplies a discriminated `file`, `url`, or `bytes` source plus attachment metadata. It owns surrounding navigation and decides how to react to lifecycle callbacks. `onSave` receives bytes, a safe filename, PDF MIME type, attachment context, and an abort signal, then returns persisted metadata asynchronously. The SDK owns PDF behavior and commits only after host success. This keeps host storage and attachment rules out of both PDF engines.

## Major Modules

- `sdk/PdfViewerSDK.tsx` coordinates lifecycle, viewing state, dirty-state protection, print, and export.
- `components/PdfPageCanvas.tsx` renders visible pages and selectable text at device pixel ratio, then converts region and text-selection coordinates through the PDF.js viewport.
- `components/DocumentEditor.tsx` provides transactional page manipulation and accessible reorder controls.
- `sdk/engineClient.ts` is a request/response bridge with a bounded startup handshake and pending-call cleanup.
- `sdk/scanConversion.ts` stages PNG/JPEG bytes and coordinates progress/cancellation with a dedicated worker.
- `workers/scanConversion.bootstrap.worker.ts` waits for MuPDF initialization before transferring a batch to `scanConversion.worker.ts`.
- `workers/pdfEngine.bootstrap.worker.ts` registers immediately, loads the MuPDF engine module, and reports ready or startup failure.
- `workers/pdfEngine.worker.ts` owns the MuPDF document, journal, clipboard, committed bytes, native PDF structures, and serialization.
- `app/demoRepository.ts` calls the host-owned record/attachment API; `vite.config.ts` supplies its local development and preview implementation.

## State Management

React state holds view mode, page-scoped temporary rotations, current page, zoom policies, panel visibility, loading/save/scan status, errors, and the worker snapshot. The document worker is the authority for committed/working PDF bytes, serialized undo/redo history, clipboard pages, annotations, outlines, and dirty state. The host retains record, attachment, source, and persisted metadata state. A monotonically increasing viewer revision rejects stale loads; worker requests carry unique IDs.

## Document-Loading Lifecycle

For URLs, the SDK passes the URL directly to PDF.js with byte ranges enabled and background stream/autofetch disabled. This prevents an idle viewer from eagerly acquiring the entire file while still allowing available pages to render through HTTP 206 requests. CORS and byte-range support remain server responsibilities; a server without ranges may require a full response. Local files and raw bytes go directly to PDF.js. Cancellation destroys the loading task. Full bytes are requested explicitly only when processing, printing, or export needs them; editing and annotation initialize MuPDF, while unedited print/export can use PDF.js bytes directly.

## Viewing Lifecycle

PDF.js page viewports provide real page dimensions. A `ResizeObserver` measures the actual `.page-workspace` content box after the thumbnail rail or details panel changes it; page-list padding, live gap, and the mounted one- or two-page set feed both fit modes. Canvas backing stores are scaled for high-DPI screens. `IntersectionObserver` renders pages/thumbnails near the viewport and tracks the current page; distant pages remain placeholders. Each new source starts in single-page mode at 125%. Temporary current-page rotation is React view state applied consistently to canvas, text, and annotation coordinates; it never changes worker bytes.

## Editing and Save Lifecycle

Entering the editor initializes MuPDF from complete bytes. Operations mutate only the working document and return serialized bytes that atomically replace the PDF.js view. The worker stores a serialized pre-operation revision for reliable undo/redo. `Cancel` reloads committed bytes; `Export` serializes without changing the commit. `Save` first serializes a candidate and awaits the host's `onSave`; only success commits and closes the editor. Failure keeps dirty state for retry or local download. Host replacement, editor close, and browser unload protect dirty work.

## Scan-Import Lifecycle

The SDK reads one or more PNG/JPEG files, reporting the first half of progress. After the scan worker's MuPDF `ready` handshake, it converts each image into an aspect-aware PDF page and reports the second half. Cancellation terminates that worker. Only a completed batch is sent once to the document worker for atomic import, so cancellation or invalid input cannot partly change the document.

## WASM Worker Responsibilities

MuPDF.js performs rotation, reorder, delete, graft/import, subset extraction, copy/paste, native annotation creation/edit/delete, redaction application, bookmark CRUD, widget inspection, and final serialization. This is meaningful WASM execution rather than dependency presence. PDF.js remains the specialized display/range-loading engine. `pdf-lib` was not added because the verified MuPDF API covers mandatory page operations.

## Decisions and Tradeoffs

- **Two engines:** PDF.js has stronger browser streaming/rendering; MuPDF has stronger document mutation. Atomic serialized revisions cost CPU but prevent split-brain state.
- **Performance:** Lazy rendering, range-only remote acquisition, and capped device scale avoid fetching or rendering every page. `PdfEngineClient` creates the MuPDF worker only on the first processing command, so its ~10 MB WASM payload is not loaded by idle viewing. Unedited print/export can use PDF.js bytes directly.
- **History:** Serialized pre-operation revisions make structural undo reliable but increase worker memory for large documents and long editing sessions. Save, Cancel, and document replacement reset session history.
- **Accessibility:** Semantic toolbars, live regions, visible focus, button-based reorder, and PDF.js text layers support keyboard workflows and selectable page text. Full tagged-PDF reading order still depends on source quality.
- **Annotations:** Region tools and per-page text selection create native PDF structures that survive export. A selected annotation is identified in the panel and outlined on the page; numeric resizing is reliable but less direct than drag handles.
- **Printing:** A synchronously opened placeholder avoids popup timing, but final print controls remain browser-owned.
- **Persistence boundary:** Awaiting the host before commit prevents false success but makes save latency host-dependent. The included Vite API is a local demonstration with a 25 MB PDF-only limit; static and production deployments must supply their own authenticated endpoint.
- **Scan conversion:** A separate worker keeps MuPDF image conversion off the UI thread and makes cancellation safe, at the cost of another WASM worker startup and temporary batch memory.

## Licensing

MuPDF.js 1.28.0 is AGPL-3.0-or-later, so the application uses the same license. The repository carries the full license, dependency notice, exact lock file, deployed source notice, the public application source URL, and the pinned MuPDF 1.28.0 source tag. The built app serves license/source-offer files. PDF.js is Apache-2.0.

## Privacy and Security

Local and remote sources remain inside the SDK until the user chooses the host Save action. The SDK has no fixed upload service; the demonstration host sends saved PDF bytes to its same-origin Vite API, which accepts PDF payloads up to 25 MB and stores them under ignored `A/.runtime-data/`. URLs are restricted to HTTP(S), filenames are sanitized, and the app does not execute embedded PDF JavaScript, collect telemetry, or store passwords. The demo API has no authentication, authorization, cloud storage, or multi-user isolation and is not a production service.

## If I Had One More Day

- Add drag handles for annotation resizing and richer property controls.
- Implement and validate low-level AcroForm signature-widget creation if the browser MuPDF API gains safe support.
- Add bounded worker checkpoints and configurable memory limits for very large edit histories.
- Preserve nested outline placement when adding new child bookmarks.
- Add a production persistence adapter with authentication, authorization, and configurable limits.
- Add automated browser regression coverage for the highest-value viewer and editor workflows.
- Add multi-page text-selection batching and tagged-PDF reading-order audits.

## Validation Status

The implementation and its validation approach are summarized in [`../C/validation.md`](../C/validation.md).
