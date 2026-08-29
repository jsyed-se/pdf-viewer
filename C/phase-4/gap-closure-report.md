# Phase 4 Gap-Closure Report

## Status

**Nine requested gaps pass in the working candidate; final publication is pending.** Phase 4 began at `7ce08369b9bf2e1bd6713bc590f081965f95cdbe`. Final package revision: `FINAL_COMMIT_PENDING`.

Earlier phase records remain unchanged. The current mapping is in [`../requirements-validation.md`](../requirements-validation.md), and Phase 4 evidence is indexed in [`../evidence/phase-4/README.md`](../evidence/phase-4/README.md).

## Implemented Gap Closures

| Gap | Result | Evidence |
| --- | --- | --- |
| Image scan import | PNG/JPEG and multi-image batches convert in a dedicated MuPDF worker, report read/convert progress, and import atomically | `05-scan-real-progress.png`, `06-scan-cancelled-unchanged.png` |
| Editor zoom | Page-grid zoom is independent and bounded from 18% to 50% | `04-editor-toolbar-zoom.png`; focused state tests |
| Host persistence | The demo host persists PDF-only uploads through a same-origin Vite dev/preview API under ignored `A/.runtime-data/` | `07-upload-in-progress.png`, `09-persisted-attachment-updated.png` |
| Save lifecycle | `onSave` is awaited before commit; failure keeps the editor dirty with retry and local download | `08-upload-success-confirmed.png`, `10-upload-failure-retry.png` |
| Demonstration host | Searchable sample records, expandable attachment metadata, open/back flow, and refreshed persisted metadata | `01-host-search-attachments.png`, `09-persisted-attachment-updated.png` |
| Quick Download | The host downloads persisted bytes without opening the editor | `persisted-and-quick-download.pdf` |
| Toolbar alignment | Viewer and editor controls are compact, grouped, and keep Save/Cancel visible | `02-default-viewer-toolbar-125.png`, `04-editor-toolbar-zoom.png` |
| Viewer rotation | Current-page rotation is temporary, page-scoped, and geometry-aware | `03-viewer-rotation-alignment.png`; focused state tests |
| Opening defaults | Each new source opens in single-page mode at 125% | `02-default-viewer-toolbar-125.png`; focused state tests |

## Browser and Artifact Results

The controlled browser flow opened a 5-page PDF. Two scan images produced 7 pages. Cancelling a 40-image batch at 20/40 kept 7 pages, and an invalid image also kept 7 pages. Upload success returned only after host persistence; reopening the stored attachment returned 7 pages. The two inserted scan pages retained landscape and portrait bounds of 480 × 270 and 270 × 480 PDF points. The final persisted/Quick Download PDF is 34,944 bytes with SHA-256 `6ad8cf387ee6964017e7e95a8467ffb17449ddbd1b4cde511402846aa824c85b`. Upload failure kept the editor available for retry or local download.

The working candidate passes `npm run type-check`, `npm run lint`, `npm test` (3 files, 13 tests), and `npm run build`. Final clean-clone, CI, public revision, and approval checks must be recorded after the commit is frozen.

## Defects and Boundaries

[`defects.md`](defects.md) records two implementation defects, both corrected and revalidated. The SDK remains deployment-neutral: the included persistence API is a local Vite demonstration service, not production storage. A static deployment must provide its own `onSave` host endpoint. The demo accepts only PDFs up to 25 MB and has no authentication, authorization, cloud storage, or production search.
