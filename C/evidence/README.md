# Phase 2 Evidence

Evidence remains in its original locations so existing references stay reproducible:

- `logs/` contains browser results, range-server records, inspection output, driver logs, and supporting screenshots.
- `generated-pdfs/` contains the small exported PDFs committed for page-operation, annotation, applied-redaction, bookmark, and save/cancel evidence.

The reviewer-facing mapping is in [`../phase-2/validation-report.md`](../phase-2/validation-report.md). Key structural proof is in `logs/artifact-inspection-final.json`; browser workflow evidence uses the `firefox-phase2-*.json` records; range behavior is recorded in `logs/range-server-final.jsonl`.

The PDFs are reproducible from the repository scripts, and their hashes and parsed facts remain recorded in `logs/artifact-inspection-final.json`. All fixtures and artifacts are synthetic. Do not add private PDFs, credentials, browser profiles, or unredacted user data.
