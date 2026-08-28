# Requirements Validation Inventory

This ledger maps the detailed Phase 2 test inventory to the accepted closure result. Mandatory rows pass through the grouped evidence in [`validation-report.md`](validation-report.md); bonus limitations and unavailable external environments remain explicit.

## Status and Evidence Rules

- **Mandatory** rows must pass for final acceptance.
- **Bonus** rows may remain unsupported, but implemented claims require validation; blockers must remain explicit.
- **External** rows require artifacts or environments unavailable to the application code.
- Record the exact commit, browser/version, operating system, fixture, steps, and artifact path for each run.
- Store only non-sensitive, redistributable fixtures. Never include private PDFs, credentials, or passwords in evidence.

## SDK Integration and Lifecycle

| ID | Class | Requirement | Implementation location | Validation method | Expected result | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SDK-01 | Mandatory | Reusable SDK component mounted by a demo client | `A/src/sdk/PdfViewerSDK.tsx`; `A/src/App.tsx` | Mount the SDK through the demo and a minimal secondary harness | Both hosts integrate without modifying PDF engine internals | PASS — see grouped evidence |
| SDK-02 | Mandatory | Accept local files, PDF URLs, and raw PDF bytes | `A/src/sdk/types.ts`; `A/src/App.tsx`; `A/src/sdk/PdfViewerSDK.tsx` | Open the same fixture through all three source variants | Each source opens the same page count and content | PASS — see grouped evidence |
| SDK-03 | Mandatory | Typed document input and lifecycle callbacks | `A/src/sdk/types.ts`; `A/README.md` | Capture `onReady`, progress, page, dirty, save, error, and password events | Callbacks fire once, in logical order, with correct values | PASS — see grouped evidence |
| SDK-04 | Mandatory | Client owns metadata, source, host navigation, and viewer lifecycle | `A/src/App.tsx`; `B/architecture-and-design.md` | Trace host back/open/replace flows and inspect ownership boundaries | Host policy remains outside SDK engines; metadata stays host-controlled | PASS — see grouped evidence |
| SDK-05 | Mandatory | SDK owns PDF loading, rendering, navigation, editing, annotations, printing, and export | `A/src/sdk/PdfViewerSDK.tsx`; `A/src/workers/pdfEngine.worker.ts` | Exercise each capability from the SDK surface | No PDF behavior is hardcoded in the host application | PASS — see grouped evidence |
| SDK-06 | Mandatory | Safe source replacement and unmount | `A/src/sdk/PdfViewerSDK.tsx`; `A/src/sdk/engineClient.ts` | Rapidly replace A→B→C during loading/processing, then unmount | Only C wins; no stale callback, worker error, or state leak remains | PASS — see grouped evidence |

## Loading and Error Handling

| ID | Class | Requirement | Implementation location | Validation method | Expected result | Status |
| --- | --- | --- | --- | --- | --- | --- |
| LOAD-01 | Mandatory | Local-file loading | `A/src/App.tsx`; `A/src/sdk/PdfViewerSDK.tsx` | Open a controlled local PDF | Correct filename, page count, and first page appear | PASS — see grouped evidence |
| LOAD-02 | Mandatory | Remote-URL loading | `A/src/App.tsx`; `A/src/sdk/PdfViewerSDK.tsx` | Open a controlled CORS-enabled URL | Remote PDF opens without an application proxy/upload | PASS — see grouped evidence |
| LOAD-03 | Mandatory | Raw-byte loading | `A/src/sdk/types.ts`; `A/src/sdk/PdfViewerSDK.tsx` | Mount with a fixture `Uint8Array` | Bytes open with the supplied filename and correct content | PASS — see grouped evidence |
| LOAD-04 | Mandatory | Loading progress | `A/src/sdk/PdfViewerSDK.tsx` | Throttle a large remote fixture and capture UI/callback events | Progress is visible, monotonic, and reported to the host | PASS — see grouped evidence |
| LOAD-05 | Mandatory | Loading cancellation | `A/src/sdk/PdfViewerSDK.tsx` | Cancel a throttled remote load | Work stops safely and no stale document later appears | PASS — see grouped evidence |
| LOAD-06 | Mandatory | Password-protected document handling | `A/src/sdk/PdfViewerSDK.tsx`; `A/src/workers/pdfEngine.worker.ts` | Test required, wrong, cancelled, and correct passwords | Prompt/callback distinguishes states; correct password opens; secrets are not retained | PASS — see grouped evidence |
| LOAD-07 | Mandatory | Actionable network, CORS, and HTTP errors | `A/src/sdk/PdfViewerSDK.tsx` | Use 404, offline, and CORS-denied URLs | Visible error identifies the likely cause and recovery action | PASS — see grouped evidence |
| LOAD-08 | Mandatory | Malformed-document error | `A/src/sdk/PdfViewerSDK.tsx` | Open a truncated/corrupt PDF | Viewer fails safely with an understandable PDF error | PASS — see grouped evidence |
| LOAD-09 | Mandatory | Unsupported/non-PDF error | `A/src/sdk/PdfViewerSDK.tsx` | Open HTML/text renamed as `.pdf` | File is rejected without misleading rendering | PASS — see grouped evidence |
| LOAD-10 | Mandatory | HTTP range and true linearized loading | `A/src/sdk/PdfViewerSDK.tsx`; `A/README.md` | Use a linearized large PDF on a logged HTTP 206 range server; capture HAR/server log | First page appears before full transfer; requests contain valid byte ranges | PASS — see grouped evidence |
| LOAD-11 | Mandatory | No eager or duplicate full-document download while viewing | `A/src/sdk/PdfViewerSDK.tsx` | Leave a range PDF idle and inspect network requests | No background stream/autofetch or duplicate full request occurs | PASS — see grouped evidence |
| LOAD-12 | Mandatory | Full bytes acquired only when processing requires them | `A/src/sdk/PdfViewerSDK.tsx`; `A/src/sdk/engineClient.ts` | Compare idle view with edit, annotation, print, and export network/worker traces | Idle viewing stays ranged; processing explicitly acquires needed bytes | PASS — see grouped evidence |
| LOAD-13 | Mandatory | Server requirements are documented | `README.md`; `A/README.md`; `B/architecture-and-design.md` | Compare docs with controlled range and non-range behavior | CORS, headers, HTTP 206, linearization, and fallback limits are accurate | PASS — see grouped evidence |

## Viewing and Navigation (Original A1)

| ID | Class | Requirement | Implementation location | Validation method | Expected result | Status |
| --- | --- | --- | --- | --- | --- | --- |
| VIEW-01 | Mandatory | Browser PDF rendering | `A/src/components/PdfPageCanvas.tsx` | Open vector, text, image, transparency, and rotated fixtures | Pages render legibly without missing or materially incorrect content | PASS — see grouped evidence |
| VIEW-02 | Bonus | High-fidelity browser rendering through WebAssembly | `A/src/workers/pdfEngine.worker.ts`; `C/phase-1/implementation.md` | Trace claimed high-fidelity operations to WASM and compare serialized output | Only operations actually passing through MuPDF WASM are labeled WASM-powered | PARTIAL — PDF.js renders pages; MuPDF WASM handles worker-side processing and serialization |
| VIEW-03 | Mandatory | High-DPI rendering | `A/src/components/PdfPageCanvas.tsx` | Test DPR 1 and 2+; inspect canvas backing and CSS sizes | Canvas backing scales with DPR while layout size remains correct | PASS — see grouped evidence |
| VIEW-04 | Mandatory | Previous/next navigation | `A/src/sdk/PdfViewerSDK.tsx` | Navigate first, middle, and last pages | Page changes correctly and boundary controls disable | PASS — see grouped evidence |
| VIEW-05 | Mandatory | Direct page-number navigation | `A/src/sdk/PdfViewerSDK.tsx` | Enter valid, fractional, zero, negative, and excessive values | Valid pages open; invalid values clamp safely | PASS — see grouped evidence |
| VIEW-06 | Mandatory | Thumbnail navigation | `A/src/sdk/PdfViewerSDK.tsx` | Select first/middle/last thumbnails | Correct page becomes active and visible | PASS — see grouped evidence |
| VIEW-07 | Mandatory | Current-page tracking | `A/src/components/PdfPageCanvas.tsx`; `A/src/sdk/PdfViewerSDK.tsx` | Scroll at fit width and high zoom | Current page follows the dominant visible page without oscillation | PASS — see grouped evidence |
| VIEW-08 | Mandatory | Continuous scrolling | `A/src/lib/viewMath.ts`; `A/src/sdk/PdfViewerSDK.tsx` | Scroll through a multi-page PDF | Pages remain ordered and navigable in one continuous workspace | PASS — see grouped evidence |
| VIEW-09 | Mandatory | Single-page mode | `A/src/lib/viewMath.ts`; `A/src/sdk/PdfViewerSDK.tsx` | Switch mode and navigate | Only the active page is mounted in the page workspace | PASS — see grouped evidence |
| VIEW-10 | Mandatory | Cover-aware per-spread mode | `A/src/lib/viewMath.ts`; `A/src/sdk/PdfViewerSDK.tsx` | Test cover, odd/even pairs, and final page | Cover stands alone and later pairs remain correct at boundaries | PASS — see grouped evidence |
| VIEW-11 | Mandatory | Zoom in/out | `A/src/sdk/PdfViewerSDK.tsx` | Repeatedly zoom to both limits | Scale changes predictably and stays within documented bounds | PASS — see grouped evidence |
| VIEW-12 | Mandatory | Real fit-to-width | `A/src/lib/viewMath.ts`; `A/src/sdk/PdfViewerSDK.tsx` | Test mixed page sizes, panels, spread mode, and container resize | Mounted page set fits available width using actual dimensions and gap | PASS — see grouped evidence |
| VIEW-13 | Mandatory | Real fit-to-viewport | `A/src/lib/viewMath.ts`; `A/src/sdk/PdfViewerSDK.tsx` | Test portrait/landscape/mixed pages and resized viewports | Entire mounted page set fits both available width and height | PASS — see grouped evidence |
| VIEW-14 | Mandatory | Keyboard navigation and zoom | `A/src/sdk/PdfViewerSDK.tsx` | Use arrows, Page Up/Down, and keyboard zoom outside form controls | Commands work and do not hijack typing controls | PASS — see grouped evidence |
| VIEW-15 | Mandatory | Loading, empty, and error states | `A/src/sdk/PdfViewerSDK.tsx` | Exercise no source, slow source, render failure, and load failure | Each state is distinct, visible, and announced | PASS — see grouped evidence |
| VIEW-16 | Mandatory | Large-document lazy rendering | `A/src/components/PdfPageCanvas.tsx` | Open a 150–300 page fixture and inspect canvases before/after scroll | Distant pages remain placeholders and are not rendered simultaneously | PASS — see grouped evidence |

## Transactional Document Editor (Original A2/A4)

| ID | Class | Requirement | Implementation location | Validation method | Expected result | Status |
| --- | --- | --- | --- | --- | --- | --- |
| EDIT-01 | Mandatory | Document-editor mode and real toolbar | `A/src/components/DocumentEditor.tsx` | Enter editor and invoke every enabled control | No decorative, duplicated, simulated, or mislabeled control exists | PASS — see grouped evidence |
| EDIT-02 | Mandatory | Page selection, select all, and select none | `A/src/components/DocumentEditor.tsx` | Toggle pages and bulk selection | Selection state and enabled actions remain accurate | PASS — see grouped evidence |
| EDIT-03 | Mandatory | Rotate pages left/right | `A/src/workers/pdfEngine.worker.ts` | Rotate selected pages and reopen exported output | Rotation is serialized and unselected pages remain unchanged | PASS — see grouped evidence |
| EDIT-04 | Mandatory | Drag-and-drop page reorder | `A/src/components/DocumentEditor.tsx`; `A/src/workers/pdfEngine.worker.ts` | Drag first/middle/last pages | Visual order and exported page identity match | PASS — see grouped evidence |
| EDIT-05 | Mandatory | Accessible reorder controls | `A/src/components/DocumentEditor.tsx` | Reorder using keyboard-focusable left/right buttons | Same serialized result as drag reorder | PASS — see grouped evidence |
| EDIT-06 | Mandatory | Page deletion | `A/src/workers/pdfEngine.worker.ts` | Delete selected pages and export/reopen | Only selected pages are removed | PASS — see grouped evidence |
| EDIT-07 | Mandatory | Prevent deleting every page | `A/src/components/DocumentEditor.tsx`; `A/src/workers/pdfEngine.worker.ts` | Select all and attempt deletion through UI/protocol | UI disables action and engine rejects invalid request | PASS — see grouped evidence |
| EDIT-08 | Mandatory | Import and merge PDFs | `A/src/components/DocumentEditor.tsx`; `A/src/workers/pdfEngine.worker.ts` | Import a distinct mixed-size fixture at selected/default insertion points | Imported pages appear once, in order, at the expected location | PASS — see grouped evidence |
| EDIT-09 | Mandatory | Page extraction | `A/src/workers/pdfEngine.worker.ts`; `A/src/sdk/PdfViewerSDK.tsx` | Extract a non-contiguous selection | Download contains exactly selected pages in source order | PASS — see grouped evidence |
| EDIT-10 | Mandatory | Keep only selected pages | `A/src/workers/pdfEngine.worker.ts` | Keep a non-contiguous selection | Working document contains exactly selected pages | PASS — see grouped evidence |
| EDIT-11 | Mandatory | Copy and paste pages | `A/src/workers/pdfEngine.worker.ts`; `A/src/components/DocumentEditor.tsx` | Copy multiple pages and paste at boundaries | Duplicates retain content/dimensions and appear at expected index | PASS — see grouped evidence |
| EDIT-12 | Mandatory | Undo and redo | `A/src/workers/pdfEngine.worker.ts` | Undo/redo rotate, reorder, delete, import, and annotation actions | State reverses/reapplies one journal operation at a time | PASS — see grouped evidence |
| EDIT-13 | Mandatory | Invalid actions disabled | `A/src/components/DocumentEditor.tsx` | Inspect selection, clipboard, busy, history, and boundary states | Unavailable actions are disabled and cannot mutate the PDF | PASS — see grouped evidence |
| TXN-01 | Mandatory | Cancel restores last committed document | `A/src/workers/pdfEngine.worker.ts`; `A/src/sdk/PdfViewerSDK.tsx` | Save baseline, perform several edits, then Cancel | Viewer bytes/page state exactly match last commit | PASS — see grouped evidence |
| TXN-02 | Mandatory | Save commits working document | `A/src/workers/pdfEngine.worker.ts`; `A/src/sdk/PdfViewerSDK.tsx` | Edit, Save, edit again, then Cancel | Cancel restores the saved revision, not original source | PASS — see grouped evidence |
| TXN-03 | Mandatory | Export downloads current state without committing | `A/src/sdk/PdfViewerSDK.tsx` | Edit, Export, then Cancel | Download contains edits; viewer returns to prior commit | PASS — see grouped evidence |
| TXN-04 | Mandatory | Protect dirty state on editor close | `A/src/sdk/PdfViewerSDK.tsx` | Close with dirty state; test stay/discard choices | Stay preserves work; discard restores commit | PASS — see grouped evidence |
| TXN-05 | Mandatory | Protect dirty state on host navigation or document replacement | `A/src/App.tsx`; `A/src/sdk/PdfViewerSDK.tsx` | Use Back, local open, URL open, and browser unload while dirty | Navigation requires confirmation and follows the chosen outcome | PASS — see grouped evidence |
| EDIT-14 | Mandatory | Preserve page dimensions, rotations, and relevant structures where possible | `A/src/workers/pdfEngine.worker.ts`; `C/phase-1/implementation.md` | Reopen compound-edit output and compare page/outline/annotation/widget metadata | Supported structures persist; unavoidable loss is documented precisely | PASS — see grouped evidence |

## Printing and Export (Original A3/A4)

| ID | Class | Requirement | Implementation location | Validation method | Expected result | Status |
| --- | --- | --- | --- | --- | --- | --- |
| PRINT-01 | Mandatory | Browser Print action | `A/src/sdk/PdfViewerSDK.tsx` | Print an unedited document in each target browser | Browser print flow opens with the current PDF | PASS — see grouped evidence |
| PRINT-02 | Mandatory | Print edited state, not original source | `A/src/sdk/PdfViewerSDK.tsx` | Make a visible edit, then inspect print preview | Preview contains the edit and correct page order/count | PASS — see grouped evidence |
| PRINT-03 | Mandatory | Avoid asynchronous popup blocking | `A/src/sdk/PdfViewerSDK.tsx` | Invoke with normal popup policy | Synchronous placeholder opens before PDF preparation | PASS — see grouped evidence |
| PRINT-04 | Mandatory | Wait for generated PDF before printing | `A/src/sdk/PdfViewerSDK.tsx` | Throttle preparation and observe print invocation | Print starts only after iframe/PDF load | PASS — see grouped evidence |
| PRINT-05 | Mandatory | Print cleanup and failure state | `A/src/sdk/PdfViewerSDK.tsx` | Test successful, blocked, unsupported, and closed-window paths | Object URLs are revoked and failure guidance is visible | PASS — see grouped evidence |
| EXP-01 | Mandatory | Export complete edited PDF | `A/src/sdk/PdfViewerSDK.tsx`; `A/src/workers/pdfEngine.worker.ts` | Export and reopen a visibly edited document | Output is valid and contains the complete current state | PASS — see grouped evidence |
| EXP-02 | Mandatory | Export selected pages | `A/src/sdk/PdfViewerSDK.tsx`; `A/src/workers/pdfEngine.worker.ts` | Extract selected non-contiguous pages and reopen | Output contains only selected pages | PASS — see grouped evidence |
| EXP-03 | Mandatory | Keep specified pages and export | `A/src/workers/pdfEngine.worker.ts` | Keep pages, export, and parse identity/order | Output contains only kept pages in expected order | PASS — see grouped evidence |
| EXP-04 | Mandatory | Import/merge and export | `A/src/workers/pdfEngine.worker.ts` | Merge two fixtures, export, and parse page identities | Both documents appear once in the requested order | PASS — see grouped evidence |
| EXP-05 | Mandatory | Save locally with predictable safe filenames | `A/src/sdk/PdfViewerSDK.tsx` | Export sources with normal and unsafe filenames | Browser download occurs locally with sanitized suffix/name | PASS — see grouped evidence |
| EXP-06 | Mandatory | Valid output after compound edits | `A/src/workers/pdfEngine.worker.ts` | Rotate, reorder, duplicate, delete, annotate, merge, export, and reopen in both engines | Output parses/renders with correct page state and supported structures | PASS — see grouped evidence |

## WASM, Annotations, Signatures, and Bookmarks (Original A5 Bonus)

| ID | Class | Requirement | Implementation location | Validation method | Expected result | Status |
| --- | --- | --- | --- | --- | --- | --- |
| WASM-01 | Mandatory in Phase 1 architecture | WebAssembly used meaningfully and off the main UI thread | `A/src/sdk/engineClient.ts`; `A/src/workers/pdfEngine.worker.ts` | Capture network/worker trace and perform a mutation | MuPDF WASM loads on demand in a worker and serialized bytes change | PASS — see grouped evidence |
| WASM-02 | Mandatory quality rule | No false WASM claim | `B/architecture-and-design.md`; `C/phase-1/implementation.md` | Trace each claimed WASM capability to worker code and output | Every claim has an actual worker/WASM call path | PASS — see grouped evidence |
| ANN-01 | Bonus | Rectangle redaction annotation | `A/src/components/PdfPageCanvas.tsx`; `A/src/workers/pdfEngine.worker.ts` | Draw at zoom levels and rotations 0/90/180/270; reopen output | Native Redact annotation matches selected region | PASS — see grouped evidence |
| ANN-02 | Bonus | Text-selection/highlighter redaction | `A/src/components/PdfPageCanvas.tsx`; `A/src/workers/pdfEngine.worker.ts` | Select known text at each rotation/zoom and inspect quads | Native Redact quads align with selected text | PASS — see grouped evidence |
| ANN-03 | Bonus | Applied redaction removes underlying content | `A/src/workers/pdfEngine.worker.ts` | Apply, export, reopen, render, and search/extract redacted text | Covered content is absent visually and from extraction/search | PASS — see grouped evidence |
| ANN-04 | Bonus | Native text annotation | `A/src/workers/pdfEngine.worker.ts` | Create/edit/export/reopen a text note | Native Text annotation and contents persist | PASS — see grouped evidence |
| ANN-05 | Bonus | Native highlight annotation | `A/src/components/PdfPageCanvas.tsx`; `A/src/workers/pdfEngine.worker.ts` | Test region, text match, and direct text selection | Native Highlight quads persist and align | PASS — see grouped evidence |
| ANN-06 | Bonus | Draw annotation regions | `A/src/components/PdfPageCanvas.tsx` | Draw across page edges, zooms, and rotations | Region remains bounded and maps accurately to PDF coordinates | PASS — see grouped evidence |
| ANN-07 | Bonus | Select annotation and show page location | `A/src/sdk/PdfViewerSDK.tsx`; `A/src/components/PdfPageCanvas.tsx` | Select each annotation row | Selected state is announced and correct region is outlined | PASS — see grouped evidence |
| ANN-08 | Bonus | Edit annotation properties and size | `A/src/sdk/PdfViewerSDK.tsx`; `A/src/workers/pdfEngine.worker.ts` | Change contents and numeric dimensions, then reopen | Updated native properties persist at the intended coordinates | PASS — see grouped evidence |
| ANN-09 | Bonus | Delete annotation | `A/src/sdk/PdfViewerSDK.tsx`; `A/src/workers/pdfEngine.worker.ts` | Delete selected annotation and reopen | Annotation is absent from metadata and rendering | PASS — see grouped evidence |
| ANN-10 | Bonus | Preserve annotations during save/export and page edits | `A/src/workers/pdfEngine.worker.ts` | Annotate, rotate/reorder/merge, save/export, and reopen | Supported annotations remain native and attached to the correct content | PASS — see grouped evidence |
| SIG-01 | Bonus | Signature form-field creation | `A/src/sdk/PdfViewerSDK.tsx`; `C/phase-1/implementation.md` | Review blocker against MuPDF API and inspect UI claims | Unsupported creation remains clearly blocked; no decorative control exists | PARTIAL — creation unsupported and not claimed |
| SIG-02 | Bonus | Widget annotation inspection/creation status | `A/src/workers/pdfEngine.worker.ts`; `A/src/sdk/PdfViewerSDK.tsx` | Open an AcroForm fixture and inspect widget metadata | Existing widgets are reported accurately; creation is not falsely claimed | PARTIAL — inspection supported; creation unsupported |
| SIG-03 | Bonus quality rule | Distinguish visual signature field from cryptographic signing | `A/README.md`; `C/phase-1/implementation.md` | Inspect UI/docs and exported sample | No cryptographic-signing claim appears without implementation proof | PASS — see grouped evidence |
| BMK-01 | Bonus | Read bookmarks | `A/src/workers/pdfEngine.worker.ts`; `A/src/sdk/PdfViewerSDK.tsx` | Open nested-outline fixture and navigate each destination | Titles, hierarchy, and destinations are represented correctly | PASS — see grouped evidence |
| BMK-02 | Bonus | Create bookmarks | `A/src/workers/pdfEngine.worker.ts` | Create at multiple pages and reopen | New native outline entries persist with correct destinations | PASS — see grouped evidence |
| BMK-03 | Bonus | Edit bookmarks | `A/src/workers/pdfEngine.worker.ts` | Change title/destination and reopen | Updated native outline data persists | PASS — see grouped evidence |
| BMK-04 | Bonus | Delete bookmarks | `A/src/workers/pdfEngine.worker.ts` | Delete root and nested entries, then reopen | Intended outline entry is removed without corrupting siblings | PASS — see grouped evidence |

## Accessibility, Responsiveness, Reliability, and Privacy

| ID | Class | Requirement | Implementation location | Validation method | Expected result | Status |
| --- | --- | --- | --- | --- | --- | --- |
| A11Y-01 | Mandatory | Semantic controls and accessible names | `A/src/**/*.tsx` | Inspect accessibility tree and run axe | Interactive controls have correct roles, names, and states | PASS — see grouped evidence |
| A11Y-02 | Mandatory | Visible keyboard focus | `A/src/styles.css` | Tab through all primary workflows | Focus is never lost or visually hidden | PASS — see grouped evidence |
| A11Y-03 | Mandatory | Keyboard-accessible primary workflows | `A/src/sdk/PdfViewerSDK.tsx`; `A/src/components/DocumentEditor.tsx` | Complete open/view/navigate/reorder/save/cancel without a mouse | Required primary actions are operable by keyboard | PASS — see grouped evidence |
| A11Y-04 | Mandatory | Status and error announcements | `A/src/sdk/PdfViewerSDK.tsx` | Inspect live regions during loading, operations, and failures | Important state changes are announced once and understandably | PASS — see grouped evidence |
| A11Y-05 | Mandatory | Adequate contrast | `A/src/styles.css` | Automated contrast scan plus focus/error visual review | Text, controls, states, and focus meet applicable WCAG contrast | PASS — see grouped evidence |
| A11Y-06 | Mandatory | Selectable text and source-dependent reading order documented honestly | `A/src/components/PdfPageCanvas.tsx`; `A/README.md` | Test tagged and untagged fixtures with accessibility tree/screen reader | Selectable text works; unsupported reading-order behavior is not overclaimed | PASS — see grouped evidence |
| RESP-01 | Mandatory | Responsive desktop and tablet behavior | `A/src/styles.css` | Test 1440×900, 1024×768, and 768×1024 with touch emulation | Primary controls remain visible, reachable, and usable without destructive clipping | PASS — see grouped evidence |
| REL-01 | Mandatory | Cancel stale render/loading work | `A/src/components/PdfPageCanvas.tsx`; `A/src/sdk/PdfViewerSDK.tsx` | Rapid scroll, zoom, cancel, and source replacement under throttling | Cancelled work does not surface stale content/errors | PASS — see grouped evidence |
| REL-02 | Mandatory | Cleanup workers, documents, object URLs, listeners, and temporary resources | `A/src/sdk/engineClient.ts`; `A/src/sdk/PdfViewerSDK.tsx`; `A/src/components/PdfPageCanvas.tsx` | Repeat open/edit/export/print/unmount cycles and inspect resources | Worker/listener/object-URL counts return to baseline | PASS — see grouped evidence |
| REL-03 | Mandatory | Protect against rapid document-change races | `A/src/sdk/PdfViewerSDK.tsx` | Switch sources during PDF.js load and MuPDF mutation | Latest revision wins and UI/metadata never mix documents | PASS — see grouped evidence |
| PRIV-01 | Mandatory quality rule | No server upload of user PDFs | `A/src/App.tsx`; `A/src/sdk/PdfViewerSDK.tsx`; `B/architecture-and-design.md` | Inspect network during local open/edit/export | No PDF bytes leave the browser except user-requested remote-origin fetches | PASS — see grouped evidence |
| PRIV-02 | Mandatory quality rule | No secrets, private documents, telemetry, or undocumented dependency | Repository; `package-lock.json`; `NOTICE-MUPDF.md` | Secret scan, dependency review, network inspection, fixture provenance review | No prohibited material or hidden network/dependency behavior is found | PASS — see grouped evidence |

## Architecture, AI Records, Repository, and Delivery (Original B–D)

| ID | Class | Requirement | Implementation location | Validation method | Expected result | Status |
| --- | --- | --- | --- | --- | --- | --- |
| DOC-B01 | Mandatory | Short architecture/design document with one diagram | `B/architecture-and-design.md` | Compare diagram/modules with current code | Diagram exists and accurately represents current architecture | PASS — see grouped evidence |
| DOC-B02 | Mandatory | State-management approach and state locations | `B/architecture-and-design.md` | Trace React, host, PDF.js, and worker state | Document names the authoritative owner of each state category | PASS — see grouped evidence |
| DOC-B03 | Mandatory | Loading, viewing, editing/save, and WASM worker lifecycles | `B/architecture-and-design.md` | Compare each lifecycle with runtime traces | Documented sequence matches observed execution | PASS — see grouped evidence |
| DOC-B04 | Mandatory | Performance, accessibility, library, license, privacy, and security tradeoffs | `B/architecture-and-design.md` | Review against dependencies and observed limitations | Decisions and tradeoffs are concise, accurate, and complete | PASS — see grouped evidence |
| DOC-B05 | Mandatory | Five to eight one-more-day roadmap bullets | `B/architecture-and-design.md` | Count and review roadmap items | Between five and eight concrete items are present | PASS — see grouped evidence |
| DOC-C01 | Mandatory | Phase plan saved before implementation | `C/phase-1/plan.md`; `C/ai-usage.md` | Review history/timestamps and content | Plan is concise, predates implementation, and separates requirement classes | PASS — see grouped evidence |
| DOC-C02 | Mandatory | AI changes, reasons, recommendations, corrections, and correctness validation | `C/ai-usage.md`; `C/phase-1/implementation.md` | Compare records with git/code history | Material AI influence and corrections are evidence-based and not fabricated | PASS — see grouped evidence |
| CODEX-C03 | Mandatory | Approved Codex plan saved before work | `C/phase-1/plan.md`; `C/phase-2/plan.md` | Compare plans with commit history and implementation records | Saved plans precede their corresponding implementation/validation work | PASS — see grouped evidence |
| CODEX-C04 | Mandatory | Available Codex activity evidence recorded without fabrication | `C/codex-transcript.md`; `C/ai-output-changes.md` | Reconcile activity summary, changes, and correctness evidence with repository history | Available evidence is truthful; unavailable full export and external upload are stated accurately | PASS — see grouped evidence |
| DEL-D01 | Mandatory | Public GitHub repository or shared private repository | `README.md`; git remote | Open repository anonymously or as designated reviewer | Reviewer can access exact submitted source and history | PASS — see grouped evidence |
| DEL-D02 | Mandatory | Clean root setup with `npm install && npm run dev` | `package.json`; `README.md` | Fresh-clone into a temporary directory and run exact commands | Install succeeds without undocumented setup and dev server starts | PASS — see grouped evidence |
| DEL-D03 | Mandatory | Top-level `A/`, `B/`, and `C/` deliverables | Repository root | Inspect clean clone | `A/` has MVP/SDK, `B/` architecture, `C/` AI/evidence records | PASS — see grouped evidence |
| DEL-D04 | Mandatory | Build, type-check, lint, and focused tests | Root and `A/package.json` | Run root build/typecheck/lint/test commands at exact commit | Every command exits zero with recorded output | PASS — see grouped evidence |
| DEL-D05 | Mandatory | AGPL license, notices, dependency disclosure, and corresponding source | `LICENSE`; `NOTICE-MUPDF.md`; `A/public/*` | Build/start app; request notice files and follow source links | License/source notices are served and exact corresponding source is accessible | PASS — see grouped evidence |
| DEL-D06 | Mandatory | Documentation matches tested implementation | `README.md`; `A/README.md`; `B/`; `C/` | Reconcile every claim with validation results | No unsupported capability, command, browser, or WASM claim remains | PASS — see grouped evidence |

## Required Cross-Feature Flows

| ID | Class | Flow | Validation method | Expected result | Status |
| --- | --- | --- | --- | --- | --- |
| FLOW-01 | Mandatory | Linearized URL load → early page → navigation/modes/fits → edit → export/reopen | Capture HAR, screenshots, event log, download, and parsed metadata | Ranged viewing stays correct and exported edits reopen successfully | PASS — see grouped evidence |
| FLOW-02 | Mandatory | Mixed-page local PDF → rotate/reorder/copy/delete/import → undo/redo → Save → more edits → Cancel | Use visible page-identity fixtures and compare final parsed state | Save establishes commit; Cancel restores it; all operations serialize correctly | PASS — see grouped evidence |
| FLOW-03 | Bonus | Rotated/zoomed text selection → native highlight/redact → select/edit/resize → apply → export/reopen | Capture before/after screenshots and search/extraction results | Coordinates remain correct; annotations persist; applied content is removed | PASS — see grouped evidence |
| FLOW-04 | Bonus | Existing bookmarks/widgets → page edits/merge → bookmark CRUD/widget inspection → export/reopen | Compare outline/widget/page metadata before and after | Supported structures persist or exact losses are documented | PASS — see grouped evidence |
| FLOW-05 | Mandatory | Dirty document → Back/new local/new URL/browser close → stay/discard outcomes | Record each confirmation branch and resulting document identity | Dirty work is never silently lost | PASS — see grouped evidence |
| FLOW-06 | Mandatory | Edited document → Print → preview → cleanup | Capture edited page identity in preview and resource lifecycle | Preview uses edited bytes and temporary resources are reclaimed | PASS — see grouped evidence |
| FLOW-07 | Mandatory | Rapid remote A→B→C with cancellation and a processing race | Throttle network, capture callbacks/console/workers | Only C remains active; no stale state, unhandled error, or leaked worker | PASS — see grouped evidence |

## Browser and Fixture Coverage

| ID | Class | Coverage requirement | Validation method | Expected result | Status |
| --- | --- | --- | --- | --- | --- |
| BROWSER-01 | Mandatory | Exhaustive current Chromium/Chrome validation | Run every applicable mandatory row and claimed bonus row | Evidence includes browser version and artifacts for each result | PASS — see grouped evidence |
| BROWSER-03 | Mandatory | Current Firefox compatibility smoke | Run load/render/modes/fit/editor/annotation/responsive flows | Principal workflows work without a Firefox-specific blocker | PASS — see grouped evidence |
| BROWSER-04 | Optional external | Safari compatibility | Run on a current macOS Safari environment | Not executed because this Windows environment does not provide Safari; no compatibility claim is made | NOT APPLICABLE — environment unavailable |
| FIX-01 | Mandatory | Controlled redistributable fixture suite | Create/gather fixtures with provenance and deterministic expectations | Includes basic, mixed-size/rotation, large, linearized, encrypted, corrupt, annotated, outlined, widget, and import PDFs | PASS — see grouped evidence |
| FIX-02 | Mandatory | Controlled HTTP range/fallback test server | Run with request logging, CORS, range, throttle, and failure modes | Server can prove 206/range behavior and reproduce error/fallback cases | PASS — see grouped evidence |
| EVID-01 | Mandatory | Evidence tied to exact source revision | Record commit, clean status, browser, OS, fixture hash, steps, and artifact links | Every result is reproducible and attributable to one commit | PASS — see grouped evidence |
| EVID-02 | Mandatory | No Phase 2 result is inferred from code presence | Review completed matrix rows | PASS is used only when direct evidence exists; limitations remain explicit | PASS — see grouped evidence |
