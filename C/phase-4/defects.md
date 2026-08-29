# Phase 4 Defects

## P4-D01 — Scan conversion stalled before WASM was ready

- **Observed:** A two-image scan stayed at 0/2 because conversion messages reached the worker before the MuPDF module was ready.
- **Correction:** Added a lightweight bootstrap worker and an explicit `ready` handshake before transferring image bytes.
- **Revalidation:** Two images advanced through read and convert progress and were inserted as one atomic two-page import. Cancelling a 40-image batch at 20/40 left the original 7-page working document unchanged.
- **Evidence:** [`05-scan-real-progress.png`](../evidence/phase-4/05-scan-real-progress.png) and [`06-scan-cancelled-unchanged.png`](../evidence/phase-4/06-scan-cancelled-unchanged.png).
- **Status:** Corrected and revalidated.

## P4-D02 — Host callbacks reset the active editor

- **Observed:** Inline callbacks created by the demonstration host changed identity during host status updates. The SDK source effect reran and reset the editor.
- **Correction:** Memoized the host callbacks with `useCallback` so status and metadata updates do not look like a new document source.
- **Revalidation:** Scan, editor zoom, upload, persisted reopen, and failure/retry flows completed without an unexpected editor reset.
- **Evidence:** [`04-editor-toolbar-zoom.png`](../evidence/phase-4/04-editor-toolbar-zoom.png), [`08-upload-success-confirmed.png`](../evidence/phase-4/08-upload-success-confirmed.png), and [`10-upload-failure-retry.png`](../evidence/phase-4/10-upload-failure-retry.png).
- **Status:** Corrected and revalidated.

No other Phase 4 defect is recorded. Final publication checks remain separate from behavior revalidation.
