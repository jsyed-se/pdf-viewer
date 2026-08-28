# Phase 1: Complete Implementation

## Objective

Transform the existing baseline into a complete, reusable, submission-ready PDF Viewer SDK web application.

Start from the current implementation. Inspect it, preserve what is working, correct what is incomplete, and finish the required capabilities. Do not rebuild blindly.

## References

* Current application: https://atlas-pdf-sdk.naidster.chatgpt.site
* Existing source: use the current repository as the baseline
* Reference video: `example_viewer_demo.mov`
* Original written requirements in the assignment
* Existing documentation under `A/`, `B/`, and `C/`

The video is incomplete. Infer missing behavior carefully and document every material inference.

## Phase boundary

This phase covers:

* Baseline analysis
* Architecture decisions
* Complete feature implementation
* Implementation documentation
* Minimal development checks needed to ensure the project compiles and starts

This phase does not cover:

* Final requirement-by-requirement certification
* Screenshot evidence
* Comprehensive browser validation
* Adversarial testing
* Performance benchmarking
* Final test report

Those belong to Phases 2 and 3.

## Required approach

Before implementation:

1. Inspect the existing application, source, documentation, and reference video.
2. Identify what is complete, incomplete, simulated, mislabeled, or architecturally weak.
3. Create and save a concise implementation plan before modifying the application.
4. Separate:

   * Written requirements
   * Behavior observed in the video
   * Inferred requirements
   * Design decisions
   * Bonus capabilities
5. Preserve useful baseline work and unrelated existing changes.

Save the plan under:

```text
C/phase-1-plan.md
```

## Technology direction

Use React and TypeScript.

Use WebAssembly meaningfully, not as a superficial dependency.

Preferred architecture:

* PDF.js for progressive, range-based, and linearized remote loading
* MuPDF.js WebAssembly as the primary document-processing engine
* Run heavy PDF and WASM operations outside the main UI thread
* Retain pdf-lib only where it fills a verified MuPDF.js capability gap

MuPDF.js should support the advanced PDF operations where appropriate:

* High-fidelity processing
* Native annotations
* Actual redaction application
* Page manipulation
* Bookmark operations
* Form and widget inspection
* Final document generation

Because this is a public, noncommercial assessment, comply fully with MuPDF’s AGPL requirements. Include the appropriate license, notices, dependency disclosure, and corresponding source.

Do not claim a capability is WASM-powered unless it actually passes through the WASM engine.

## Functional requirements

### SDK integration

The viewer must be implemented as a reusable SDK component mounted by a demonstration client application.

The client application owns:

* Attachment metadata
* Document source
* Host navigation
* Viewer lifecycle

The SDK owns:

* Loading
* Rendering
* Navigation
* Viewing state
* Editing state
* Annotations
* Printing
* Export

Expose a clear, typed integration interface supporting document input and lifecycle callbacks. The demo must show how a client application integrates the SDK, matching the host-to-viewer flow suggested by the video.

Do not leave host behavior hardcoded inside the PDF engine.

### PDF loading

Support:

* Local files
* PDF URLs
* Raw PDF bytes
* Loading progress
* Cancellation
* Password-protected-document handling
* Actionable network, CORS, malformed-document, and unsupported-file errors

For remote PDFs:

* Use HTTP range and streaming behavior when supported
* Display the first available page without waiting for the complete file
* Avoid duplicate full-document downloads
* Acquire complete bytes only when editing or exporting requires them
* Document the server requirements for true linearized loading

### Viewing and navigation

Implement:

* High-fidelity browser rendering
* High-DPI rendering
* Previous and next page navigation
* Direct page-number navigation
* Thumbnail navigation
* Continuous scrolling
* Single-page mode
* Per-spread mode
* Zoom in and out
* Real fit-to-width
* Real fit-to-viewport
* Current-page tracking
* Keyboard navigation
* Appropriate loading, empty, and error states

Fit calculations must use the actual viewport and PDF page dimensions.

Large documents must not render every page simultaneously. Use an appropriate lazy-rendering, virtualization, or visibility-based strategy.

### Document editor

Implement a complete transactional document-editor mode inspired by the reference video.

Include:

* Page selection
* Select all and select none
* Page rotation
* Page reordering
* Drag-and-drop interaction
* Accessible reorder controls
* Page deletion
* Importing and merging PDFs
* Page extraction
* Keeping only selected pages
* Copying and pasting pages
* Undo and redo
* Save
* Cancel
* Local export

All controls must perform real document operations. Do not ship simulated, decorative, duplicated, or misleading buttons.

Editing behavior must be transactional:

* Cancel restores the last committed document
* Save commits the working version
* Export downloads the current document
* Invalid actions are disabled
* The application must prevent deletion of every page
* Unsaved changes must be protected when leaving, opening another document, or closing editor mode

Preserve page dimensions, rotations, and relevant document structures where technically possible. Document any structures that cannot be preserved.

### Printing

Provide a reliable browser Print action for the current document state.

It must:

* Print the edited document, not the original source
* Avoid popup-blocking problems caused by asynchronous generation
* Wait until the generated PDF is ready before printing
* Clean up temporary resources
* Provide an understandable failure state when printing is blocked or unsupported

### Export and conversion

Support:

* Exporting the complete edited PDF
* Exporting selected pages
* Keeping specified pages
* Importing and merging documents
* Saving locally
* Predictable filenames
* Valid PDF output after combinations of rotation, reordering, duplication, deletion, annotation, and merging

### WASM bonus capabilities

Because the application uses WebAssembly, implement the bonus capabilities as real PDF structures where supported:

* Rectangle-based redaction annotations
* Text-selection/highlighter redaction
* Applying redactions so underlying content is removed
* Text annotations
* Highlight annotations
* Signature form fields
* Widget annotations
* Bookmark reading
* Bookmark creation
* Bookmark editing
* Bookmark deletion

Distinguish clearly between:

* A visual signature field and a cryptographically signed document
* A redaction annotation and an applied redaction
* Native PDF annotations and flattened page graphics

Do not claim cryptographic signing unless it is genuinely implemented and validated.

If a narrow capability requires a secondary library or low-level PDF object work, make the smallest justified addition and document the decision.

### Annotation interaction

Provide usable annotation tools, including:

* Drawing and resizing annotation regions
* Selecting annotations
* Editing annotation properties
* Deleting annotations
* Accurate coordinate conversion across zoom and rotation
* Preserving supported annotations during save and export

Annotations must not exist only as temporary HTML overlays.

### Accessibility and reliability

Implement:

* Semantic controls
* Accessible labels
* Visible keyboard focus
* Keyboard-accessible primary workflows
* Status and error announcements
* Adequate contrast
* Responsive desktop and tablet behavior
* Safe cancellation of stale rendering and loading work
* Cleanup of workers, documents, object URLs, listeners, and temporary resources
* Protection against race conditions when changing documents quickly

## Repository structure

Maintain the required structure:

```text
/
├── A/    Working MVP and SDK source
├── B/    Architecture and design
├── C/    AI usage and implementation records
└── README.md
```

Folder `A` must contain the working MVP and reusable SDK implementation.

The repository root must support:

```bash
npm install
npm run dev
```

Do not require undocumented manual setup.

## Documentation

Keep documentation concise, readable, and evidence-based.

### Architecture document

Update:

```text
B/architecture.md
```

It must contain:

* One component diagram
* SDK integration boundary
* Major modules
* State-management approach
* Document-loading lifecycle
* Viewing lifecycle
* Editing and save lifecycle
* WASM worker responsibilities
* Key design decisions
* Library and licensing decisions
* Performance tradeoffs
* Accessibility tradeoffs
* Privacy and security considerations
* Five to eight “If I had one more day” roadmap items

### Phase 1 implementation record

Create:

```text
C/phase-1-implementation.md
```

Include:

* Baseline findings
* Implemented capabilities
* Important files and modules changed
* Design decisions and their reasons
* How PDF.js and MuPDF.js responsibilities were divided
* Changes made from the baseline AI output
* AGPL compliance actions
* Known limitations
* Honest status of every WASM bonus capability

### AI usage record

Update the existing Codex usage documentation with:

* The Phase 1 plan
* Major prompts or missions
* Material Codex recommendations
* Changes made to AI-generated output and why
* Implementation corrections made after inspection

Do not fabricate a transcript or claim manual decisions that were not made.

### README

Update the root README and `A/README.md` with:

* Product overview
* Supported capabilities
* Technology stack
* Setup instructions
* Development commands
* SDK integration example
* Browser requirements
* Remote-server requirements for range loading
* Licensing
* Known limitations
* Repository layout

Do not add Phase 2 screenshots yet.

## Implementation quality requirements

* No placeholder functionality
* No simulated controls
* No knowingly misleading labels
* No false WebAssembly claims
* No false redaction or signature claims
* No unnecessary architectural rewrite
* No undocumented dependency
* No destructive changes to unrelated work
* No secrets or private documents committed
* No server upload of user PDFs unless explicitly required

Favor a coherent, maintainable implementation over accumulating libraries.

## Phase 1 completion gate

Phase 1 is complete only when:

* All mandatory viewing, navigation, editing, printing, and export capabilities are implemented
* The SDK has a real client-integration boundary
* WebAssembly is genuinely used
* Required WASM bonus capabilities are implemented or explicitly documented with a concrete technical blocker
* Remote loading does not unnecessarily delay initial display
* Fit modes calculate actual scale
* Page operations produce real PDF changes
* Unsaved changes are protected
* The project installs, compiles, type-checks, lints, and starts
* Documentation accurately reflects the implementation
* The repository remains ready for Phase 2 validation

Perform only the minimal smoke checks required to establish that implementation is buildable. Comprehensive testing belongs to Phase 3.

## Completion report

When finished, provide:

1. Implementation summary
2. Major architecture and design decisions
3. WASM integration summary
4. Mandatory feature status
5. Bonus feature status
6. Files and documentation created or updated
7. Commands run
8. Known limitations or blockers
9. Exact starting point for Phase 2

Stop after Phase 1. Do not begin Phase 2 without approval.


