# Phase 2: Requirements Validation and Evidence

## Mission

Independently validate the completed PDF Viewer SDK against the original assignment and produce concise, reviewer-ready documentation with screenshots and traceable evidence.

Start from the frozen Phase 1 baseline:

* Repository: `jsyed-se/neubus_pdf_viewer`
* Phase 1 commit: `c33ba71`
* Reference video: `example_viewer_demo.mov`
* Original requirements
* Phase 1 architecture and implementation records

Treat Phase 1 claims as unverified until Phase 2 produces evidence.

## Phase boundary

Phase 2 covers:

* Requirement-by-requirement validation
* Architecture and design-document review
* Controlled browser verification
* Representative fixtures
* Screenshot evidence
* Traceability documentation
* Minimal fixes for defects that block a requirement
* Revalidation of any corrected requirement

Phase 2 does not cover:

* Exhaustive functional testing
* Adversarial testing
* Stress testing
* Long-duration stability testing
* Broad malformed-input campaigns
* Full performance benchmarking
* Security penetration testing

Those belong to Phase 3.

## Operating rules

1. Begin from commit `c33ba71`.
2. Confirm the working tree and baseline before making changes.
3. Review the original requirements, reference video, Phase 1 documentation, and implementation.
4. Save a concise Phase 2 plan before validation begins.
5. Do not assume a feature works because code or a Phase 1 report says it does.
6. Validate observable behavior and produced PDF artifacts.
7. Use controlled, non-sensitive fixtures.
8. Do not fabricate screenshots, browser results, transcripts, or evidence.
9. If validation uncovers a defect:

   * Record the failure first
   * Identify the requirement it blocks
   * Make the smallest appropriate correction
   * Revalidate the affected requirement
   * Capture final evidence from the corrected commit
10. Do not expand product scope or rearchitect working components during this phase.

Create:

```text
C/phase-2-plan.md
```

## Source-of-truth requirements matrix

Create or update a single requirements traceability matrix.

Recommended location:

```text
C/requirements-validation.md
```

Every original requirement must have a row containing:

* Requirement ID
* Requirement text
* Mandatory or bonus classification
* Implementation location
* Validation method
* Expected result
* Observed result
* Evidence reference
* Status: `PASS`, `PARTIAL`, `FAIL`, `BLOCKED`, or `NOT APPLICABLE`
* Limitation or explanation

Do not use `PASS` unless the behavior was directly observed or the generated PDF was inspected.

Signature-widget creation must remain honestly classified according to the final implementation. It is a bonus limitation, not a mandatory failure, unless the implementation changes during Phase 2.

## Controlled validation fixtures

Create or obtain safe fixtures sufficient to demonstrate:

* Small normal PDF
* Multi-page text PDF
* Mixed portrait and landscape pages
* Rotated pages
* Linearized PDF
* Large PDF
* Range-enabled remote PDF
* Password-protected PDF
* PDF with existing annotations
* PDF with bookmarks
* PDF with existing form widgets or signature fields
* Malformed or unsupported file
* Two or more documents suitable for merge and extraction workflows

Keep generated fixtures reproducible. Do not commit oversized files when a script can generate them.

Document each fixture’s purpose and expected behavior.

## Validation scope

### 1. Client integration

Validate that:

* The demonstration client mounts the SDK through its documented interface
* File, URL, and byte-array inputs are supported
* Host navigation remains outside the PDF engine
* Load, error, dirty-state, save, and close callbacks behave as documented
* Multiple viewer instances or repeated document changes do not share unintended state

Capture evidence showing the client application and SDK boundary.

### 2. PDF loading and linearization

Validate:

* Local file loading
* Raw-byte loading
* Remote URL loading
* Loading progress
* Load cancellation
* Password handling
* CORS and network error handling
* Malformed-file handling
* Linearized/range-based loading

For the linearized case, prove that:

* HTTP byte-range requests occur
* The first usable page appears before complete document acquisition
* The document is not downloaded twice
* Complete bytes are acquired only when an editing or export operation requires them

Use browser network evidence, controlled server logs, or application instrumentation. A screenshot of a loaded PDF alone is not proof of linearized loading.

### 3. Viewing and navigation

Validate:

* High-fidelity page rendering
* High-DPI rendering
* Previous and next navigation
* Direct page-number entry
* Thumbnail navigation
* Continuous mode
* Single-page mode
* Per-spread mode
* Current-page tracking
* Zoom in and out
* Fit-to-width
* Fit-to-viewport
* Keyboard navigation
* Selectable text layer
* Lazy rendering or virtualization for large documents

Confirm that fit modes respond to real viewport and page-size changes instead of applying fixed percentages.

### 4. Document editor

Validate real document behavior for:

* Page selection
* Select all and select none
* Rotate left and right
* Reordering by drag and drop
* Accessible reorder controls
* Deleting selected pages
* Preventing deletion of every page
* Importing and merging PDFs
* Extracting selected pages
* Keeping only selected pages
* Copying and pasting pages
* Undo and redo
* Cancel
* Save
* Unsaved-change protection
* Local export

Reopen generated PDFs after combined operations. Verify final page count, page order, dimensions, orientation, and visible content.

Do not validate operations only by observing thumbnail changes.

### 5. Printing and export

Validate:

* Printing the current edited document
* Popup-safe print behavior
* Understandable blocked-print behavior
* Complete-document export
* Selected-page export
* Predictable filenames
* Correct PDF MIME type
* Valid output after combined edits
* Cleanup of temporary URLs and print resources

A browser print dialog is acceptable. Record limitations where operating-system UI prevents full automation.

### 6. WebAssembly evidence

Prove that MuPDF WebAssembly is genuinely used.

Evidence should establish:

* The WASM module loads
* Heavy document operations occur in the worker
* Mutations and serialization pass through MuPDF
* The main interface remains responsive during representative processing
* PDF.js and MuPDF responsibilities match the architecture document

Do not rely only on the dependency appearing in `package.json`.

### 7. Native annotations and redaction

Validate:

* Rectangle redaction annotation
* Selected-text redaction
* Highlight annotation
* Text-note annotation
* Annotation selection
* Annotation editing
* Annotation deletion
* Coordinate accuracy across zoom and rotation
* Persistence after save and reopen
* Applied redaction

For applied redaction, use a fixture containing a unique secret phrase. After applying and saving the redaction:

* The phrase must not render
* Text extraction must not recover it
* Searching the reopened output must not find it

Clearly distinguish native annotations from flattened graphics.

### 8. Bookmarks and widgets

Validate:

* Bookmark reading
* Bookmark creation
* Bookmark editing
* Bookmark deletion
* Bookmark persistence after save and reopen
* Existing widget inspection
* Existing signature-field inspection

Document signature-widget creation as unsupported if the MuPDF.js browser API remains the blocker. Do not imply cryptographic signing.

### 9. Accessibility and responsive behavior

Validate representative workflows using:

* Keyboard-only navigation
* Visible focus
* Accessible names
* Status and error announcements
* Logical focus movement
* Sufficient contrast
* Desktop layout
* Tablet-width layout
* Zoomed browser content

Use an automated accessibility scan as supporting evidence, not as the sole accessibility decision.

### 10. Architecture and documentation review

Verify that the implementation matches `B/architecture.md`.

Check for consistency across:

* Library responsibilities
* State ownership
* Worker boundaries
* Loading lifecycle
* Editing lifecycle
* Save and export behavior
* Licensing
* Privacy claims
* Known limitations
* README setup instructions

Correct inaccurate or stale documentation.

## Screenshot evidence

Create a concise screenshot set under:

```text
C/evidence/screenshots/
```

Capture only screenshots that materially prove requirements. Avoid dozens of redundant images.

The evidence set should demonstrate:

* Host application and SDK integration
* Normal viewer with thumbnails
* Continuous, single-page, and spread behavior
* Fit-to-width or fit-to-viewport
* Document-editor page organization
* Selection and page manipulation
* Merge or import result
* Annotation tools
* Applied redaction result
* Bookmark management
* Widget inspection
* Dirty-state protection
* Loading or range-request evidence
* Representative error handling
* Responsive or keyboard-focused state

Requirements for screenshots:

* Use the final Phase 2 commit
* Use controlled fixtures
* Exclude private data
* Show enough surrounding interface to establish context
* Use consistent browser dimensions where practical
* Use descriptive filenames
* Do not modify screenshots to fabricate state
* Crop only when it improves readability without removing necessary context

Create:

```text
C/evidence/screenshots/README.md
```

For every screenshot, record:

* Filename
* Requirement IDs supported
* Fixture used
* Browser and viewport
* What the screenshot proves
* What it does not prove
* Final commit hash

Where a screenshot cannot prove a technical claim, attach the relevant log, generated artifact, or structured inspection result.

## Browser coverage

Use at least:

* Current Chromium-based browser
* Current Firefox

Validate the principal viewing and editing workflow in both. Record any browser-specific behavior.

Safari may be documented as not executed if the environment does not provide it. Do not claim Safari compatibility without running it.

## Documentation deliverables

Create or update:

```text
C/phase-2-plan.md
C/requirements-validation.md
C/phase-2-validation.md
C/phase-2-defects.md
C/validation.md
C/ai-output-changes.md
C/codex-transcript.md
C/evidence/screenshots/README.md
B/architecture.md
README.md
A/README.md
```

### Phase 2 validation report

`C/phase-2-validation.md` must concisely include:

* Baseline commit
* Final validation commit
* Environment
* Browsers
* Fixtures
* Requirements summary
* Evidence summary
* Defects discovered
* Corrections made
* Revalidation results
* Mandatory requirement status
* Bonus requirement status
* Remaining limitations
* Exact Phase 3 starting point

### Defect record

`C/phase-2-defects.md` must record each defect with:

* Identifier
* Blocked requirement
* Reproduction
* Expected result
* Observed result
* Root cause
* Correction
* Revalidation evidence
* Final status

If no defects are discovered, say so explicitly rather than inventing entries.

### AI documentation correction

The reviewer approved Codex or another AI tool instead of requiring Cursor specifically.

Update the submission documentation to consistently use Codex equivalents:

* Saved plan
* Available Codex transcript or activity export
* Explanation of changes made from AI output
* Explanation of correctness validation

Do not leave misleading statements that Cursor artifacts are still required. Do not fabricate a full transcript if the platform cannot export one; document the available evidence and any external upload step accurately.

## Phase 2 completion gate

Phase 2 is complete only when:

* Every original requirement appears in the traceability matrix
* Every mandatory requirement has direct evidence
* Any mandatory failure is corrected and revalidated, or clearly reported as blocking completion
* Bonus capabilities are classified honestly
* Screenshots come from the final validated commit
* Generated PDFs have been reopened and inspected
* Linearized loading and WASM usage have technical evidence
* Applied redaction has content-removal evidence
* Documentation matches actual behavior
* Phase 1 design claims have been independently checked
* The repository is clean and published
* Phase 3 has not been started

Do not declare Phase 2 successful if any mandatory requirement remains `FAIL`, `PARTIAL`, or `BLOCKED`.

## Completion report

At completion, report:

1. Baseline and final commit
2. Mandatory requirements passed
3. Bonus requirements passed, partial, or blocked
4. Evidence and screenshot inventory
5. Defects found and fixed
6. Cross-browser result
7. Documentation updated
8. Remaining limitations
9. Exact starting point and risk list for Phase 3

Stop after Phase 2 and wait for approval before beginning Phase 3.


