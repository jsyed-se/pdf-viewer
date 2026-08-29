# Phase 4 Gap-Closure Plan

## Baseline and Scope

- Starting revision: `7ce08369b9bf2e1bd6713bc590f081965f95cdbe` on clean, synchronized `main`.
- Reference recording: `example_viewer_demo.mov`, 44.7 seconds, 2880 × 1444, SHA-256 `4E0DE6A6B24D4A9C5FD1892C6ED4F934056AA0F80B769AE8E80C5CAE80CC2EF5`. The recording is local evidence and will not be committed.
- Authoritative scope: the nine gaps in the supplied Phase 4 brief. Prior phase records and the required `A/`, `B/`, and `C/` structure remain intact.

The recording proves visible controls and sequences only. Persistence, PDF validity, true progress/cancellation, and export isolation require callback, artifact, and browser evidence.

## Video Observations

- `00:00–00:04`: searchable record results open into an attachment table with file metadata and record-level actions.
- `00:06–00:14`: a PNG attachment opens, reports loading, exposes a 125% toolbar, and shows a cancellable scanning state before returning to attachments.
- `00:16–00:24`: a PDF opens in a single-page 125% viewer with Quick Download, page navigation, zoom, rotation, and annotation/edit controls.
- `00:26–00:34`: the page-grid editor exposes Scan, Import, page actions, Undo/Redo, Zoom Out/In, selection/copy/paste, and bottom Cancel/Save actions.
- `00:38–00:44`: upload is invoked, success is confirmed only afterward, and the workflow returns to the attachment list.

## Ownership and Implementation Decisions

The demonstration host owns sample records, search, attachment metadata, attachment selection, Quick Download, and the concrete async save callback. The initial IndexedDB idea was superseded before implementation by the same-origin Vite HTTP API recorded below; persistence remains host-owned. The SDK owns document bytes, rendering, view state, editing, scan conversion/import, PDF generation, local export, and save/upload lifecycle presentation. MuPDF WASM remains the PDF mutation/serialization engine; PDF.js remains the display engine.

- Image conversion is staged before one atomic worker import. Real progress advances after each decoded/converted image; cancellation aborts staging and never mutates the worker document.
- SDK save receives an async host callback with bytes, safe filename, PDF MIME type, record/attachment context, and `AbortSignal`. Worker commit occurs only after host success; failure preserves dirty editor state.
- Viewer rotation is page-scoped view state only. It affects canvas/text/annotation presentation but never dirty state or exported bytes.
- Each new source resets to single-page mode at 125%; later choices remain stable for that source.

## Traceability

| Gap | Video evidence | Current behavior | Intended correction | Implementation location | Validation method | Final evidence |
| --- | --- | --- | --- | --- | --- | --- |
| P4-01 Image scan import | `00:06–00:14`, Scan and cancellable scanning | Editor imports PDF only | PNG/JPEG multi-image staging, aspect-aware PDF pages, progress, cancel, invalid-image recovery | `A/src/sdk/types.ts`, `A/src/sdk/PdfViewerSDK.tsx`, `A/src/components/DocumentEditor.tsx`, `A/src/workers/pdfEngine.worker.ts` | Single/multi-image import, progress event log, cancel invariance, reopened PDF inspection | Pending |
| P4-02 Editor-grid zoom | `00:26–00:34`, Zoom Out/In in editor actions | Fixed `0.28` preview scale | Independent bounded editor zoom with percentage and responsive grid density | `A/src/components/DocumentEditor.tsx`, `A/src/styles.css` | Selection/order/scroll checks across zoom limits | Pending |
| P4-03 Host persistence | `00:38–00:44`, upload then return | Synchronous `onSave` status only | Typed async host save contract and host-owned persistence; the initial IndexedDB idea was superseded by a Vite dev/preview HTTP API | `A/src/sdk/types.ts`, `A/src/sdk/PdfViewerSDK.tsx`, `A/src/app/demoRepository.ts`, `A/src/App.tsx`, `A/vite.config.ts` | Success/failure callbacks, reopen persisted bytes, metadata update | Pending |
| P4-04 Success confirmation | `00:40`, upload success dialog | No confirmation dialog | SDK dialog only after host-confirmed success; failure retains edits with retry/local download | `A/src/sdk/PdfViewerSDK.tsx`, `A/src/styles.css` | Delayed success, rejected save, retry and dirty-state checks | Pending |
| P4-05 Demonstration host | `00:00–00:04`, records and attachments | File/URL launcher only | Safe sample record search, expandable attachments, viewer return, updated attachment metadata | `A/src/App.tsx`, `A/src/app/demoRepository.ts`, `A/src/styles.css` | Search/select/back/persist/reopen workflow | Pending |
| P4-06 Quick Download | `00:16–00:24`, host-level action | SDK export only | Download persisted attachment bytes without opening editor, with MIME/name/error cleanup | `A/src/App.tsx`, `A/src/app/demoRepository.ts` | Download capture and reopened-PDF inspection | Pending |
| P4-07 Toolbar alignment | `00:20–00:38`, compact grouped viewer/editor controls | Functional but differently grouped toolbar | Reorder/group existing and Phase 4 controls; align density, separators, and Save/Cancel placement | `A/src/sdk/PdfViewerSDK.tsx`, `A/src/components/DocumentEditor.tsx`, `A/src/styles.css` | Final screenshots at consistent desktop/tablet viewports | Pending |
| P4-08 Viewer rotation | `00:20–00:24`, left/right rotation controls | Rotation only in editor | Temporary current-page left/right rotation, keyboard accessible and geometry-correct | `A/src/sdk/PdfViewerSDK.tsx`, `A/src/components/PdfPageCanvas.tsx` | Rotate/navigate/zoom/annotation alignment and byte-hash export isolation | Pending |
| P4-09 Opening defaults | `00:12`, `00:20`, 125% single-page view | Continuous fit-width | Reset new sources to single-page custom 125%, with small-viewport fallback documented | `A/src/sdk/PdfViewerSDK.tsx`, `A/src/lib/viewMath.ts` | New-source/reset test and browser observation | Pending |

## Validation and Closure

Add focused unit/integration coverage only for affected logic. Use controlled PNG/JPEG and PDF fixtures. Reopen scan-generated, uploaded, and downloaded PDFs and inspect page count, dimensions, order, MIME type, and visible content. Capture the ten requested Phase 4 screenshots under `C/evidence/phase-4/`. Run `npm run type-check`, `npm run lint`, `npm test`, `npm run build`, and a clean-clone development-server smoke. Record defects before corrections and obtain captain, vice-captain, and documentation approval before publication.

No authentication, authorization, cloud storage, production search, scanner-driver integration, signing, unrelated annotations, broad performance work, or adversarial campaign will be added.

## Recorded Implementation Decision

The initial plan named IndexedDB for local persistence. The implementation audit then reconciled that choice with the authoritative phrase “host-controlled server upload”: the demo instead uses a minimal local HTTP endpoint registered for both Vite development and preview, with ignored filesystem storage under `A/.runtime-data/`. This preserves a real asynchronous upload boundary and keeps persistence outside the SDK. The SDK contract remains deployment-neutral; a static deployment must supply an equivalent host endpoint. This is a bounded correction to the persistence mechanism, not added product scope.
