# Phase 3: Final Conformance, Packaging, and Submission Closure

## Mission

Close the PDF Viewer SDK assignment without expanding product scope.

Phase 3 is not another implementation or exploratory testing phase. Its purpose is to:

1. Check the completed implementation against the original request.
2. Check it against the approved implementation plan.
3. Resolve only submission-blocking discrepancies.
4. Organize the repository into the required `A/`, `B/`, and `C/` structure.
5. Verify the packaged repository works.
6. Complete and publish the final submission.

Repository:

```text
git@github.com:jsyed-se/pdf-viewer.git
```

## Strict scope boundary

Do not add:

* New product features
* New annotation types
* New editing capabilities
* New architecture
* New libraries unless required to repair a mandatory broken requirement
* New performance programs
* New adversarial campaigns
* New browser-support commitments
* Signature-widget creation
* Cryptographic signing
* Features from the “If I had one more day” roadmap

Do not reopen Phase 1 design decisions unless the implementation contradicts the original mandatory requirements.

Signature-widget creation remains an honestly documented bonus limitation.

## Baseline

Start from the latest completed Phase 2 commit.

Before making changes, record:

* Phase 1 baseline commit
* Phase 2 validation commit
* Current branch
* Current working-tree state
* Original assignment requirements
* Approved Phase 1 implementation plan
* Phase 2 validation matrix
* Existing known limitations

Create:

```text
C/phase-3/plan.md
```

Keep the plan concise and focused on closure.

## 1. Final conformance review

Compare three sources:

1. Original assignment
2. Approved implementation plan
3. Actual application behavior and documentation

Create one final matrix containing:

* Requirement
* Mandatory or bonus
* Planned implementation
* Actual implementation
* Phase 2 evidence
* Final status
* Limitation, if applicable

Use only:

```text
PASS
PARTIAL
BLOCKED
NOT APPLICABLE
```

Mandatory requirements must be `PASS` before submission.

Bonus limitations may remain `PARTIAL` or `BLOCKED` if documented honestly.

Do not repeat the complete Phase 2 validation effort. Reuse valid Phase 2 evidence.

## 2. Minimal correction policy

If the conformance review finds a discrepancy:

* Record it before changing code.
* Determine whether it blocks a mandatory requirement.
* Make the smallest correction necessary.
* Run the existing affected tests.
* Refresh only the evidence affected by the correction.
* Update the final matrix.

Do not use Phase 3 to improve working features.

Documentation inconsistencies, broken paths, incorrect commands, missing files, or packaging failures should be corrected.

Optional enhancement requests should be documented as future work and left unchanged.

## 3. Required repository structure

Organize the public repository as follows:

```text
pdf-viewer/
├── README.md
├── REQUIREMENTS.md
├── LICENSE
├── NOTICE-MUPDF.md
├── package.json
├── package-lock.json
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── A/
│   ├── README.md
│   ├── package.json
│   ├── application configuration
│   ├── public/
│   ├── src/
│   └── tests/
│
├── B/
│   ├── README.md
│   └── architecture-and-design.md
│
└── C/
    ├── README.md
    ├── codex-plan.md
    ├── codex-transcript.md
    ├── ai-output-changes.md
    ├── validation.md
    ├── phase-1/
    ├── phase-2/
    ├── phase-3/
    └── evidence/
```

Requirements:

* `A/` contains the complete working MVP and reusable SDK.
* `B/` contains the requested architecture and design document.
* `C/` contains the Codex plan, available transcript record, AI-output changes, validation explanation, screenshots, logs, and phase records.
* Do not leave duplicate application source at the repository root.
* Preserve existing Phase 1 and Phase 2 evidence.
* Update all moved-file links and documentation references.
* Keep the repository easy for a reviewer to navigate.

## 4. Root command contract

From the repository root, the following must work:

```bash
npm install
npm run dev
npm run type-check
npm run lint
npm test
npm run build
```

Root scripts may delegate to `A/`, but the reviewer must not need to change directories.

Verify these commands from a clean clone or equivalent clean environment.

Do not rely on:

* Existing `node_modules`
* Untracked files
* Local environment secrets
* Global packages
* Undocumented setup
* Files outside the repository

## 5. Final mandatory workflow check

Perform one concise final smoke pass covering only the mandatory assignment workflows:

* Open a PDF
* Navigate pages
* Zoom in and out
* Fit to width
* Fit to viewport
* Continuous mode
* Per-spread mode
* Open document-editor mode
* Rotate a page
* Reorder pages
* Import or merge a PDF
* Extract or keep selected pages
* Export the edited PDF
* Reopen the exported PDF
* Save locally
* Trigger browser printing

Confirm the existing Phase 2 evidence still represents the packaged application.

Do not repeat broad adversarial or cross-browser campaigns already completed in Phase 2.

If Phase 3 changes application code, rerun the affected Phase 2 checks. If Phase 3 only changes repository organization and documentation, record that the Phase 2 application evidence remains valid for the unchanged implementation.

## 6. Final bonus-status check

Confirm and document the existing bonus status:

* WebAssembly processing
* Rectangle redaction
* Selected-text redaction
* Applied redaction
* Text annotations
* Highlights
* Bookmark read/write
* Existing widget inspection
* Existing signature-field inspection
* Signature-widget creation limitation

Do not attempt to close the signature-widget creation limitation during Phase 3.

Do not claim cryptographic signing.

## 7. Final documentation package

Ensure the following are complete and readable:

### `A/README.md`

Include:

* MVP overview
* Features
* Technology stack
* Setup
* Development commands
* SDK integration example
* Browser requirements
* Known limitations

### `B/architecture-and-design.md`

Include:

* One component diagram
* Modules
* State-management approach
* PDF.js and MuPDF responsibilities
* Loading and editing lifecycle
* Key design decisions
* Performance, accessibility, licensing, and privacy tradeoffs
* Five to eight “If I had one more day” items

Do not expand this into a long engineering specification.

### `C/codex-plan.md`

Provide the saved Codex plan equivalent requested by the reviewer.

### `C/codex-transcript.md`

Include the available Codex activity or transcript record. Do not fabricate hidden reasoning or an unavailable platform export.

### `C/ai-output-changes.md`

Explain:

* What changed from the initial AI output
* Why those changes were necessary
* Major human or engineering decisions
* Corrections made after validation

### `C/validation.md`

Explain:

* How correctness was validated
* Commands executed
* Fixtures used
* Browser evidence
* Generated-PDF reopening
* Linearization evidence
* WASM evidence
* Redaction evidence
* Known validation boundaries

### `C/phase-3/closure-report.md`

Include:

* Baseline commit
* Final commit
* Conformance result
* Repository structure result
* Commands executed
* Final smoke result
* Corrections made
* Mandatory status
* Bonus status
* Remaining limitations
* Submission recommendation

## 8. Root README

The root `README.md` must act as the reviewer’s entry point.

Include:

* Short project description
* Quick start
* Required Node version
* Direct links to `A/`, `B/`, and `C/`
* Requirement-to-deliverable mapping
* Test commands
* Public repository information
* License summary
* Known bonus limitation

The reviewer should understand the entire submission structure within one minute.

## 9. Evidence handling

Keep existing Phase 2 evidence under:

```text
C/evidence/
```

Every screenshot or technical artifact must remain linked from the validation documents.

Do not generate unnecessary new screenshots.

Refresh evidence only when:

* Application behavior changed
* A screenshot references an obsolete path or interface
* Existing evidence does not support a mandatory requirement
* Packaging changed the visible application

Do not edit screenshots to fabricate success.

## 10. Licensing and repository hygiene

Confirm:

* AGPL license is present
* MuPDF notice and source disclosure are present
* Dependency licenses are accurately described
* No secrets are committed
* No private PDFs are committed
* No `node_modules` directories are committed
* No unnecessary build output is committed
* No temporary files or obsolete duplicate source remain
* Documentation links resolve
* Git working tree is clean

## 11. Final verification

Run the existing project gates against the final packaged structure:

```bash
npm install
npm run type-check
npm run lint
npm test
npm run build
```

Start the development server using the documented root command and perform the final mandatory smoke pass.

Confirm CI uses the same supported commands.

Do not add new test categories unless required to reproduce a submission-blocking defect.

## 12. Publish final repository

After all closure checks pass:

1. Commit the final structure and documentation.
2. Push to:

```text
git@github.com:jsyed-se/pdf-viewer.git
```

3. Confirm the public repository contains the final commit.
4. Confirm the default branch shows the required `A/`, `B/`, and `C/` folders.
5. Confirm the root README renders correctly.
6. Confirm CI passes on the final commit.

Do not rewrite published history unnecessarily.

## Completion gate

Phase 3 is complete only when:

* Every mandatory requirement is `PASS`
* The implementation matches the approved plan
* The repository has the required `A/`, `B/`, and `C/` structure
* Root installation and development commands work
* Existing tests and build pass
* Final mandatory smoke workflow passes
* Documentation matches the implementation
* Bonus limitations are honest
* Evidence is linked and readable
* Licensing is correct
* Repository is clean
* Final commit is pushed publicly
* CI passes

If a mandatory requirement fails, stop and report the specific blocker.

Do not certify the submission by hiding or reclassifying a mandatory failure.

## Final response

Report only:

1. Final commit
2. Public repository URL
3. Mandatory requirements result
4. Bonus requirements result
5. Repository structure result
6. Commands and checks passed
7. Corrections made during closure
8. Remaining documented limitations
9. Final submission recommendation


