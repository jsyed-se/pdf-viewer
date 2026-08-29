# Changes to AI-Generated Output

This record explains where generated plans or code were corrected after inspection. A change is not treated as correct until its relevant check passes.

## Phase 1 Corrections

| Change | Why it changed | Validation |
| --- | --- | --- |
| Separated required and bonus scope | Early wording made high-fidelity WebAssembly rendering mandatory | Requirements and documentation review |
| Used PDF.js for display and MuPDF.js in a worker for document changes | Each library has a clearer, verified responsibility | MuPDF spike, build, and browser smoke |
| Added revision checks around document replacement | Older async results could overwrite a newer document | Browser smoke after proxy-race fix |
| Made pages and thumbnails visibility-based | Rendering everything would not scale to large PDFs | Browser smoke; broader performance work remains pending |
| Reworked fit calculations around the measured page workspace | Earlier calculations did not fully represent a mounted spread | Focused unit tests and browser smoke |
| Added selectable PDF.js text and MuPDF quad annotations | Typed search alone did not meet direct-selection behavior | Native highlight serialized and reloaded in smoke testing |
| Deferred creation of the MuPDF worker | The original reset path loaded WASM before document processing | Fresh-load network observation and code review |
| Kept signature-field creation blocked | The browser MuPDF API did not expose a safe helper | Type/API inspection; no false control shipped |

## Phase 2 Findings

| Finding | Required response | Status |
| --- | --- | --- |
| Direct page entry is overwritten in continuous mode | Correct current-page synchronization and rerun `VIEW-03` | Corrected — see `P2-D01` and the final validation report |
| `onCloseRequest` has no invocation path | Add a real close request flow or remove the unsupported contract claim | Corrected — see `P2-D02` and the final validation report |
| Tablet toolbar labels overlap | Prevent control shrinking and retain reachable horizontal scrolling | Corrected — see `P2-D03` and the final validation report |
| Continuous mode eagerly fetches a large linearized file | Defer page metadata/render work until pages approach the viewport | Corrected — see `P2-D04` and the final validation report |
| MuPDF worker misses its first command | Add an explicit bootstrap ready/error handshake and startup bound | Corrected — see `P2-D05` and the final validation report |
| Structural undo leaves the page count unchanged | Restore serialized pre-operation revisions for undo/redo | Corrected — see `P2-D06` and the final validation report |
| Existing annotations do not appear in the panel | Initialize MuPDF on panel open and handle annotation types without quad points | Corrected — see `P2-D07` and the final validation report |

## Phase 4 Corrections

| Change | Why it changed | Validation |
| --- | --- | --- |
| Replaced planned IndexedDB storage with a same-origin Vite host API | The authoritative gap required host-controlled upload and persistence outside the SDK | Persist, return, reopen, and Quick Download browser flow |
| Added a scan-worker bootstrap and `ready` handshake (`P4-D01`) | Image messages could arrive before MuPDF WASM initialization and leave progress at 0/2 | Two-image conversion plus cancel-at-20/40 invariance |
| Memoized demonstration-host callbacks (`P4-D02`) | Inline callback identities retriggered the SDK source effect and reset the editor | Full scan/edit/upload/reopen/failure browser flow |
| Commit only after awaited `onSave` success | A local worker commit before host confirmation could misreport failed persistence | Delayed success and rejected-upload retry/local-download flows |

## Review Rule

Each correction remains traceable to its defect ID and evidence. Phase 2 closure remains in `C/phase-2/validation-report.md`; the current working-candidate result is in `C/phase-4/gap-closure-report.md`. Unsupported bonus work remains explicitly limited.
