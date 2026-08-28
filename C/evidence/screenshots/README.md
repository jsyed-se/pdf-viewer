# Final Screenshot Evidence

All screenshots were captured from validated application commit `d778c24b1ef09d777eadcdd6eb336984a1d6fc23` using Firefox 154.0.1 on Windows 11. The desktop viewport was 1440 × 900; the tablet viewport was 820 × 900. Fixtures and committed output PDFs contain no private data.

| Filename | Requirement IDs | Fixture | What it proves | What it does not prove |
| --- | --- | --- | --- | --- |
| `01-firefox-desktop-continuous.png` | SDK-01, VIEW-01, VIEW-06 | `normal.pdf` | Host/SDK boundary, thumbnails, continuous layout, and corrected text/border alignment | PDF structure, range requests, or WASM execution |
| `02-firefox-single-page.png` | VIEW-09 | `normal.pdf` | Single-page selection and centered presentation | Navigation history or export correctness |
| `03-firefox-spread.png` | VIEW-10, VIEW-13 | `multi-page-text.pdf` | Pages 2–3 displayed as a fitted spread with legible spacing | Serialized page order or editing |
| `04-firefox-editor-page-organization.png` | EDIT-01, EDIT-02, EDIT-03 | `merge-alpha.pdf` | Editor toolbar, selection, three page cards, and visible 90° rotation | Reopened output; see `../logs/artifact-inspection-final.json` |
| `05-firefox-native-annotations.png` | ANN-03, ANN-07, ANN-08 | `existing-annotations-edited.pdf` | Native Text/Highlight listing, edited note, selection controls, and page rendering | Annotation resize persistence or signature creation |
| `06-firefox-bookmark-management.png` | BMK-01 through BMK-04 | `bookmarks-edited.pdf` | Reopened edited bookmark plus add/edit/delete controls | Exhaustive nested-outline combinations |
| `07-firefox-applied-redaction.png` | ANN-03 | `applied-redaction.pdf` | Reopened output visibly replaces the secret with a black redaction | Content removal by itself; inspection separately reports `secretFound: false` |
| `08-firefox-error-guidance.png` | LOAD-09, A11Y-04 | `unsupported.txt` | Understandable visible error and host status after unsupported input | CORS, HTTP, or password branches |
| `09-firefox-tablet-focus.png` | RESP-01, A11Y-02, A11Y-03 | `normal.pdf` | Tablet alignment, reachable horizontal toolbar, and visible keyboard focus | Touch-device or screen-reader certification |

`manifest.json` records capture time, browser, viewports, SHA, and file sizes. Technical range, redaction-removal, export, and WASM claims use the linked logs and inspected PDFs because screenshots alone cannot prove them.
