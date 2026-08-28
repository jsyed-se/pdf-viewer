# Validation

Phase 2 is closed at `phase-2-complete`. The authoritative result is the [`Phase 2 validation report`](phase-2/validation-report.md); Phase 3 packaging is tracked in the [`conformance matrix`](phase-3/conformance-matrix.md) and [`closure report`](phase-3/closure-report.md).

## How Correctness Was Checked

- Phase 3 candidate `6ab29a7f06535ef616779c7aea1d5c4fbef52de0` passed `npm install`, `npm run type-check`, `npm run lint`, `npm test`, `npm run build`, and `npm run dev` from a clean public clone. The server returned HTTP 200, the clone remained clean, and GitHub CI passed.
- Synthetic fixtures from `A/tests/fixtures/` cover normal, mixed-size/rotation, large linearized, encrypted, corrupt, annotation, bookmark, widget, and import cases. They contain no private data.
- Controlled Chrome and Firefox workflows exercised loading, navigation, fit/modes, editing, dirty-state protection, print launch, accessibility, responsive layout, and source replacement. Safari was not available and is not certified.
- Exported PDFs in [`evidence/generated-pdfs/`](evidence/generated-pdfs/) were reopened and structurally inspected for page order, rotation, annotations, applied redaction, bookmarks, and save/cancel behavior.
- Range-server records prove HTTP `206` requests and early display for the linearized fixture. PDF.js performs page rendering; traces and serialized output prove on-demand MuPDF WASM processing in its worker.
- Applied-redaction inspection reports that the controlled secret is absent. Screenshots show visible results but are not used alone to prove PDF structure, byte ranges, WASM execution, or content removal.

Evidence is indexed in [`evidence/README.md`](evidence/README.md), with detailed defects in [`phase-2/defects.md`](phase-2/defects.md). Boundaries remain explicit: signature/widget creation and signing are unsupported; native screen-reader/touch, broad performance/adversarial testing, and Safari were not executed; the original source baseline was not treated as evidence.
