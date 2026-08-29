# Phase 4 Evidence

These artifacts use controlled sample records, synthetic images, and non-sensitive PDFs. They support the working candidate. Final package revision: `FINAL_COMMIT_PENDING`.

| File | What it supports |
| --- | --- |
| `01-host-search-attachments.png` | Searchable records and attachment metadata |
| `02-default-viewer-toolbar-125.png` | Single-page 125% opening default and viewer toolbar |
| `03-viewer-rotation-alignment.png` | Temporary page rotation with aligned rendering |
| `04-editor-toolbar-zoom.png` | Grouped editor toolbar and independent grid zoom |
| `05-scan-real-progress.png` | Multi-image read/convert progress |
| `06-scan-cancelled-unchanged.png` | Cancelled scan leaves the 7-page document unchanged |
| `07-upload-in-progress.png` | Host save pending before SDK commit |
| `08-upload-success-confirmed.png` | Success confirmation after host persistence |
| `09-persisted-attachment-updated.png` | Updated metadata and persisted reopen path |
| `10-upload-failure-retry.png` | Failed upload retains retry and local-download choices |
| `persisted-and-quick-download.pdf` | Host-persisted bytes also retrieved by Quick Download |
| `artifact-inspection.json` | Reopened PDF size, hash, page count, and scan-page bounds |

The controlled browser flow observed 5 initial pages, 7 after two scan images, 7 after cancelling a 40-image batch at 20/40, 7 after invalid input, and 7 after persisted reopen. The inserted pages have 480 × 270 and 270 × 480 PDF-point bounds. `persisted-and-quick-download.pdf` is 34,944 bytes with SHA-256 `6ad8cf387ee6964017e7e95a8467ffb17449ddbd1b4cde511402846aa824c85b`.

Screenshots prove visible state only. The reopened PDF and browser observations support page count, dimensions, persistence, and download behavior. Do not add `A/.runtime-data/`, private records, credentials, raw browser profiles, or user documents.
