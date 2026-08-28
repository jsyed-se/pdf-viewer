# Atlas PDF SDK

Atlas is a reusable React/TypeScript PDF viewer and transactional document editor. The demonstration host in `A/` supplies attachment metadata and document sources to the SDK; the SDK owns loading, rendering, navigation, editing, annotations, printing, and export.

## Capabilities and Stack

PDF.js provides lazy high-DPI rendering, selectable text, navigation, and byte-range URL loading. MuPDF.js 1.28.0 runs in an on-demand Web Worker for transactional page operations, native notes/highlights/redactions, applied redaction, bookmark editing, widget inspection, and final serialization. The editor supports rotation, reorder, delete, import/merge, extraction, keep-selected, copy/paste, undo/redo, save/cancel, print, and local export.

## Validation Status

**Phase 2 passed and is closed.** Controlled browser runs, reopened exported PDFs, range-server logs, accessibility checks, and final screenshots support the result. See [`C/phase-2/validation-report.md`](C/phase-2/validation-report.md). Validated application revision: `d778c24b1ef09d777eadcdd6eb336984a1d6fc23`.

**Phase 3 passed and the submission is closed.** Use its [`conformance matrix`](C/phase-3/conformance-matrix.md) and [`closure report`](C/phase-3/closure-report.md). The validated package revision is `6ab29a7f06535ef616779c7aea1d5c4fbef52de0`; the published `phase-3-complete` tag adds only the final closure record.

## Setup

Prerequisite: Node.js 22.13+ or 24+.

```bash
npm install
npm run dev
```

The development server prints its local URL. No environment variables or manual asset copying are required.

```bash
npm run build       # Type-check and create A/dist
npm run type-check  # Check TypeScript
npm run lint        # Run ESLint
npm test            # Run focused Phase 1 unit tests
```

## SDK Integration

```tsx
import { PdfViewerSDK } from './src/sdk/PdfViewerSDK';

<PdfViewerSDK
  source={{ kind: 'url', url: 'https://files.example.com/report.pdf' }}
  attachment={{ id: 'report-42', filename: 'report.pdf' }}
  onReady={({ pageCount }) => console.log(pageCount)}
  onDirtyChange={(dirty) => protectHostNavigation(dirty)}
  onSave={(bytes, filename) => persistInHost(bytes, filename)}
  onCloseRequest={() => closeViewerInHost()}
/>
```

The host owns source metadata, navigation, persistence, and the response to a close request. The SDK also accepts local `File` objects or raw `Uint8Array` bytes and exposes progress, page, error, password, dirty, save, and close-request callbacks.

## Browser and Range-Server Requirements

Phase 2 browser evidence covers current Chrome and Firefox. Other browsers are not certified; they require Web Workers, WebAssembly, canvas, `ResizeObserver`, and `IntersectionObserver`. For fast first-page URL display, the origin must allow CORS, expose range headers, return `206 Partial Content`, and serve a linearized PDF. Background stream/autofetch is disabled so complete bytes are only requested explicitly for processing; servers without range support may require a full viewing response.

## Repository Layout

- [`A/`](A/README.md) — working MVP, reusable SDK, demonstration host, and app instructions
- [`B/`](B/README.md) — architecture and design
- [`C/`](C/README.md) — phase plans, final conformance, validation, evidence, defects, and approved Codex records

The assignment checklist remains in [`REQUIREMENTS.md`](REQUIREMENTS.md).

| Requirement | Reviewer location |
| --- | --- |
| A. Working MVP | [`A/`](A/README.md) |
| B. Architecture and design | [`B/`](B/README.md) |
| C. Approved AI record and validation | [`C/`](C/README.md) |
| D. Repository setup and delivery | This README, `package.json`, and the top-level A/B/C folders |

## Licensing

The project is AGPL-3.0-or-later because it uses MuPDF.js WebAssembly. See [`LICENSE`](LICENSE), [`NOTICE-MUPDF.md`](NOTICE-MUPDF.md), and [`A/public/SOURCE_OFFER.txt`](A/public/SOURCE_OFFER.txt). PDF.js is Apache-2.0. Corresponding application source is public at <https://github.com/jsyed-se/pdf-viewer>; deployed copies must retain the source-and-license notice.

## Known Limitations

The referenced video was unavailable. Text-selection annotation is per page, annotation resize is numeric rather than handle-based, and signature/widget creation and cryptographic signing are not claimed. The reviewer approved Codex plan and activity evidence as the AI-tool equivalent; the repository provides an honest activity summary and does not fabricate a word-for-word transcript.
