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

## Review Rule

Each correction remains traceable to its defect ID and evidence. The accepted closure status is recorded in `C/phase-2/validation-report.md`; unsupported bonus work remains explicitly limited there.
