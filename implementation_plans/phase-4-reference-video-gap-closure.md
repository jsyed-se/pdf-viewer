# Phase 4: Reference-Video Gap Closure

## Mission

Close the nine confirmed gaps between the completed PDF Viewer SDK and the reference video.

This is a bounded correction phase. Do not expand the application beyond the findings listed here.

Repository:

```text
git@github.com:jsyed-se/pdf-viewer.git
```

Preserve the required `A/`, `B/`, and `C/` structure and all previous implementation, validation, testing, and evidence records.

## Authoritative gap list

Phase 4 covers only:

1. Image/PNG scan-to-PDF conversion with progress and cancellation
2. Zoom controls inside the page-grid editor
3. Host-controlled server upload and persistence after editing
4. Upload-success confirmation
5. Demonstration host with record search and attachment management
6. Host-level Quick Download
7. Toolbar arrangement and visual alignment with the video
8. Viewer-level page rotation shortcuts
9. Default single-page, 125% opening state

Do not add unrelated capabilities.

## Starting procedure

Before implementation:

1. Record the current final commit and working-tree state.
2. Reinspect the reference video specifically for these nine findings.
3. Confirm the existing SDK and host boundaries.
4. Identify the smallest changes needed.
5. Save the plan under:

```text
C/phase-4/plan.md
```

Create a traceability table mapping each gap to:

* Video evidence
* Current behavior
* Intended correction
* Implementation location
* Validation method
* Final evidence

## 1. Image scan-to-PDF conversion

Implement the video’s Scan/Import behavior as browser-compatible image-to-PDF conversion.

Support at minimum:

* PNG
* JPEG
* One or multiple images
* Conversion of each image into a PDF page
* Preservation of image aspect ratio
* Appropriate page sizing and orientation
* Insertion into the current document
* Reordering after import
* Progress indication
* Cancellation
* Recovery after an invalid or unsupported image

The UI may use the label `Scan images` or `Import scans`, but documentation must clarify that this is image-based scan import, not direct TWAIN, WIA, or physical-scanner control.

Cancellation must stop remaining conversion work and leave the committed document unchanged.

Do not present simulated progress.

## 2. Editor-grid zoom

Add zoom controls to document-editor page-grid mode.

The controls must:

* Zoom in
* Zoom out
* Display the current editor zoom
* Use practical minimum and maximum limits
* Change thumbnail-grid density and page-preview size
* Preserve selection, ordering, and scroll position where practical
* Remain separate from viewer zoom state

Arrange these controls consistently with the reference video.

## 3. Upload and persistence boundary

Implement real post-edit upload behavior without coupling the reusable SDK to one server.

The SDK must expose an asynchronous host-controlled save or upload callback.

The SDK should provide:

* Edited PDF bytes
* Filename
* MIME type
* Relevant attachment or record identifier
* Save progress state where available
* Success result
* Failure result
* Cancellation signal if supported

The demonstration host must provide a minimal real persistence implementation suitable for running the repository locally.

The demonstrated workflow must prove:

```text
Edit PDF
  → Save
  → Generate final PDF
  → Upload through host callback
  → Persist attachment
  → Return saved attachment metadata
  → Update host record
  → Show success confirmation
```

Do not hardcode a production storage provider, credential, or deployment-specific URL inside the SDK.

The demonstration persistence layer only needs to support the assignment workflow. It is not a general records-management backend.

Include reasonable file-type, filename, and size handling. Do not commit uploaded runtime files.

## 4. Upload-success confirmation

After successful persistence, show a clear confirmation dialog.

Include:

* Successful status
* Saved filename
* Record or attachment context
* Close/return action
* Optional open or download action if already supported

The dialog must appear only after the host confirms successful persistence.

On failure:

* Do not show success
* Preserve the user’s edited state
* Display an actionable error
* Allow retry or local download

## 5. Demonstration host

Add or complete the lightweight host application shown around the SDK in the video.

It should demonstrate:

* Record search
* Search results
* Expandable record or attachment sections
* Opening an attachment in the PDF Viewer SDK
* Returning from the SDK to the host
* Uploading the edited document back to the selected record
* Displaying updated attachment information
* Quick Download

Use safe sample data or locally persisted demonstration records.

Do not build:

* Authentication
* Authorization
* Multi-user collaboration
* Enterprise search infrastructure
* Cloud storage integration
* A production records-management platform

The purpose is to demonstrate SDK integration, not create another product.

## 6. Quick Download

Implement the video’s host-level Quick Download action.

It must:

* Be available from the attachment context shown by the host
* Download the currently persisted attachment
* Use the correct filename and PDF MIME type
* Avoid opening the editor
* Handle missing files and download failures clearly
* Clean up temporary browser resources

Keep SDK-level export and host-level Quick Download as distinct actions.

## 7. Toolbar alignment and styling

Reinspect the video and align the viewer and editor toolbars more closely.

Match the observable:

* Control order
* Functional grouping
* Labels
* Icons
* Separators
* Page-navigation placement
* Zoom placement
* Rotation placement
* Editor actions
* Save and Cancel placement
* General density, colors, and visual hierarchy

The result should clearly resemble the reference application while remaining responsive and accessible.

Do not pursue speculative pixel-perfect recreation where the video is incomplete or unclear.

Document material differences that remain intentional.

## 8. Viewer-level rotation

Add rotation controls to normal viewer mode.

Support:

* Rotate current view left
* Rotate current view right
* Keyboard-accessible operation
* Correct rendering at all zoom modes
* Correct text and annotation alignment
* Predictable behavior when navigating between pages

Keep viewer rotation conceptually separate from committed document-editor rotation unless the existing product design explicitly chooses otherwise.

Document whether viewer rotation is:

* Temporary view state, or
* A committed document mutation

Do not silently modify exported pages through a view-only action.

## 9. Default opening state

For newly opened documents on normal desktop view, use:

* Single-page mode
* 125% zoom

This default should match the reference video.

Rules:

* Apply it predictably when a new document opens
* Do not override an active user choice unexpectedly during the same document session
* Preserve responsive usability on smaller viewports
* Keep fit-to-width and fit-to-viewport available
* Document any responsive fallback

## State and architecture requirements

Maintain clear ownership:

### Demonstration host owns

* Records
* Attachment metadata
* Search
* Persistence
* Quick Download
* Navigation into and out of the SDK
* The concrete save/upload callback

### SDK owns

* PDF loading
* Rendering
* Navigation
* Viewing state
* Editing
* Image-to-PDF import
* Annotations
* PDF generation
* Print
* Local export
* Save/upload lifecycle presentation

Do not move host-specific persistence logic into the reusable PDF engine.

Update the architecture documentation if the host/persistence lifecycle was not previously represented.

## Documentation

Create:

```text
C/phase-4/plan.md
C/phase-4/gap-closure-report.md
C/phase-4/defects.md
```

Update as necessary:

```text
README.md
REQUIREMENTS.md
A/README.md
B/architecture-and-design.md
C/validation.md
C/requirements-validation.md
C/ai-output-changes.md
C/evidence/README.md
```

The gap-closure report must include:

* Starting commit
* Final commit
* The nine findings
* Implementation decision for each
* Files changed
* Evidence
* Corrections discovered during validation
* Remaining intentional differences
* Final submission impact

Do not rewrite or erase previous phase records.

## Targeted validation

Validate only the Phase 4 gaps and affected regression paths.

At minimum, verify:

* PNG import creates a valid PDF page
* Multiple-image import reports real progress
* Cancellation preserves the document
* Editor zoom works without losing selection or order
* Save uploads through the host callback
* The persisted attachment can be reopened
* Success dialog appears only after confirmed persistence
* Failed upload preserves edited state
* Record search finds the expected sample record
* Attachment selection opens the correct PDF
* Quick Download returns the persisted PDF
* Viewer rotation does not corrupt export behavior
* New documents open in single-page mode at 125%
* Viewer and editor toolbars align with the video
* Existing mandatory tests, type checking, lint, and production build still pass

Reopen uploaded and downloaded PDFs to confirm validity.

Use final screenshots for:

* Host search and attachments
* Quick Download
* Default viewer state
* Updated viewer toolbar
* Editor toolbar with zoom
* Scan/import progress
* Scan cancellation
* Upload in progress
* Upload success
* Persisted attachment after editing

Store evidence under:

```text
C/evidence/phase-4/
```

## Correction policy

If a Phase 4 change breaks an existing mandatory capability:

* Record the defect
* Apply the smallest correction
* Add or update regression coverage
* Revalidate the affected workflow

Do not expand scope to unrelated defects or enhancements.

## Completion gate

Phase 4 is complete only when:

* All nine gaps are implemented or resolved through the documented SDK/host boundary
* Image-to-PDF conversion is real
* Progress and cancellation are real
* Editor-grid zoom works
* Host persistence works locally
* Success confirmation depends on actual persistence success
* Record search and attachment management demonstrate integration
* Quick Download works
* Toolbar organization materially matches the video
* Viewer rotation works
* Default opening state is single-page at 125%
* Generated, uploaded, and downloaded PDFs reopen successfully
* Existing mandatory requirements remain passing
* Required A/B/C structure remains intact
* Documentation and evidence are updated
* Final repository commands pass
* Final commit is pushed publicly

Do not prepare or send the delivery email until Phase 4 is complete.

## Completion response

Report:

1. Starting and final commit
2. Status of each of the nine gaps
3. Host and SDK boundary implemented
4. Persistence result
5. Targeted validation result
6. Screenshots and evidence created
7. Regression status
8. Remaining intentional differences
9. Final delivery readiness
