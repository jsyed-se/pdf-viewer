# Changes from AI Output and Why

AI-generated plans and code were treated as proposals, not proof of correctness. The following material corrections were made after inspection and testing:

- Split browser display and document mutation between PDF.js and MuPDF.js after verifying that each library was better suited to a different responsibility.
- Added revision guards so stale asynchronous loads cannot replace a newer document.
- Changed pages and thumbnails to visibility-based rendering to reduce large-document work.
- Replaced approximate zoom fitting with calculations based on the measured workspace and actual page dimensions.
- Added selectable PDF.js text layers and native MuPDF quad annotations because typed text search did not satisfy direct-selection behavior.
- Deferred MuPDF worker creation until a processing operation requires it, avoiding the WASM download during viewing-only sessions.
- Replaced unreliable journal-only structural undo with serialized pre-operation revisions.
- Added explicit worker-ready handshakes after initial commands could arrive before WASM initialization.
- Made save transactional: the SDK serializes a candidate, awaits host persistence, and commits only after success. Failure preserves dirty edits for retry or local download.
- Converted scan images in a separate worker and imported only a completed batch so cancellation or invalid input cannot partially modify the PDF.
- Kept signature-field creation explicitly unsupported rather than shipping a decorative or false implementation.

The SDK packaging correction also narrows consumer access to one explicit `@atlas-pdf/react-sdk` entry, keeps React and React DOM as host-provided peers, and separates the library build from the demonstration build. Runtime files use a typed `assets.baseUrl`; consumers recursively copy the complete packaged asset directory so MuPDF workers, hashed dependencies, embedded MuPDF WASM, and PDF.js support data remain together, while the PDF.js worker stays embedded in the package entry. Host-specific success presentation remains with the host by default, with an explicit opt-in generic SDK confirmation retained for the legacy demo. A clean consumer imports only the package and explicit stylesheet. The packed-artifact, clean-consumer, automated, and browser results are recorded in `C/validation.md`.

The earlier PDF behavior corrections were retained only after their relevant static, automated, browser, or exported-artifact checks passed. Packaging was accepted only after the separate package-boundary and browser checks passed.
