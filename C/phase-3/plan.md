# Phase 3 Closure Plan

## Baseline

- Phase 1 completed baseline: `c33ba71bc845ce022366fa15656a746efc6f92a6`.
- Phase 2 completed validation: `51e2dca61c40be5f9b713a3bf7da51af9b25f4ee` (`phase-2-complete`).
- Starting branch and state: `main`, clean, synchronized with `origin/main`.
- Sources of truth: `REQUIREMENTS.md`, `C/phase-1/plan.md`, `C/phase-2/requirements-validation.md`, and the Phase 2 evidence catalog.
- Accepted limitations: PDF.js, not WASM, renders pages; signature/widget creation and cryptographic signing are unsupported; Safari and native assistive-technology/touch certification were not executed.

## Closure Steps

1. Compare the original requirements, approved Phase 1 plan, actual package, and reusable Phase 2 evidence; then run one concise mandatory smoke and create one final conformance matrix.
2. Record discrepancies before correction and fix only mandatory submission, packaging, command, path, or documentation blockers. The known root command discrepancy is the missing `npm run type-check` alias; adding that alias is packaging-only and does not change application behavior.
3. Confirm the required `A/`, `B/`, and `C/` structure, reviewer documentation, evidence links, licensing, secret/private-file hygiene, and absence of duplicate source or tracked dependencies/build output. The final documentation set is `A/README.md`, `B/architecture-and-design.md`, `C/codex-plan.md`, `C/codex-transcript.md`, `C/ai-output-changes.md`, `C/validation.md`, `C/phase-3/conformance-matrix.md`, and `C/phase-3/closure-report.md`.
4. From a clean public clone, run the exact contract: `npm install`, `npm run dev`, `npm run type-check`, `npm run lint`, `npm test`, and `npm run build`. Development-server success requires HTTP 200 followed by a clean shutdown.
5. Complete the closure report, commit and publish, then confirm public `main`, default-branch `A/`/`B/`/`C/` contents, rendered root README, matching CI commands, and final CI status.
6. Publish a stable Phase 3 completion tag and obtain captain, vice-captain, and documentation approval.

## Scope Boundary

No new product features, architecture, libraries, browser commitments, broad test campaigns, signature creation, signing, performance programs, or roadmap work will be added. Application code changes are permitted only for a newly observed mandatory blocker. Phase 2 evidence will be refreshed only if application behavior changes.
