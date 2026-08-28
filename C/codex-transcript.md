# Codex Activity Record

The reviewer approved Codex, or another AI assistant, as an alternative to Cursor. This file is a concise activity record, not a fabricated word-for-word transcript.

## Evidence Sources

- `C/phase-1/plan.md` — saved implementation plan
- `C/ai-usage.md` — Phase 1 missions, recommendations, and checks
- `C/phase-1/implementation.md` — implemented changes and Phase 1 smoke evidence
- `C/phase-2/plan.md` — saved validation plan
- `C/phase-2/defects.md` — failures observed during Phase 2
- Git history — committed implementation and correction record

## Phase 1 Activity

Codex helped turn the assignment into a requirements checklist, inspect the available reference UI, design the PDF.js/MuPDF.js split, implement the SDK and demo, debug runtime issues, and review documentation. Important corrections included stale-load protection, lazy rendering, real fit calculations, selectable text annotations, honest signature-widget limitations, and deferred MuPDF worker loading.

## Phase 2 Activity

Codex prepared a requirement-based validation plan, generated non-sensitive PDF fixtures, added inspection and range-server helpers, and completed the accepted Phase 2 browser and artifact checks. The defect record includes corrections for:

- direct page entry was overwritten in continuous mode;
- `onCloseRequest` had no invocation path;
- tablet toolbar labels overlapped;
- continuous mode eagerly acquired the complete linearized fixture;
- the MuPDF worker did not answer its first command;
- MuPDF journal undo did not restore structural changes; and
- the annotation panel omitted existing native annotations.

The defect record preserves the evidence available for each correction, including later Firefox and reopened-artifact checks. This activity summary is not proof by itself; the accepted result and evidence map are in `C/phase-2/validation-report.md`.

## Integrity Note

No full transcript was available or reconstructed. No private prompts, credentials, browser profiles, or user PDFs are included. This record summarizes material work and points reviewers to saved plans, artifacts, defects, and commits.
