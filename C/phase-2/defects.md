# Phase 2 Defect Record

This log records observed failures before any Phase 2 correction. Evidence and status are updated only after the affected requirement is revalidated.

## P2-D01 — Direct page entry is overridden in continuous mode

- **Blocked requirement:** VIEW-05 — direct page-number navigation.
- **Reproduction:** Open `normal.pdf` in Chromium, leave scroll mode on Continuous, enter `2` in the **Current page** field, and commit the value.
- **Expected result:** Page 2 becomes current and is brought into view.
- **Observed result:** The field returns to page 1. The continuous-view visibility observer reports the still-visible first page before navigation completes and overwrites the requested page.
- **Root cause:** Programmatic navigation used an unscoped selector that found the target page's thumbnail before its document page. The visibility observer could then report the old visible page and overwrite the requested state.
- **Correction:** Scoped the target lookup to the document workspace and added a temporary navigation lock that rejects stale visibility reports until the target page arrives.
- **Revalidation evidence:** Chromium at 1920 × 889: direct entry `1 → 2` ended with page 2 active, workspace `scrollTop` 2195, and page 2 top at 171 px inside a workspace beginning at 170 px. Firefox 154.0.1 kept direct page 2 stable for two seconds, then tracked real workspace scrolling from page 1 to page 2 without oscillation.
- **Final status:** RESOLVED.

## P2-D02 — Documented close callback has no invocation path

- **Blocked requirement:** SDK-03 — documented load, error, dirty-state, save, and close callbacks.
- **Reproduction:** Mount `PdfViewerSDK` with an `onCloseRequest` handler and inspect or exercise every viewer control. The prop exists in `A/src/sdk/types.ts`, but `PdfViewerSDK` neither reads it nor exposes a close control.
- **Expected result:** A viewer close request invokes the host-provided callback while leaving host navigation outside the PDF engine.
- **Observed result:** No viewer action can invoke `onCloseRequest`.
- **Root cause:** The callback was included in the public type but omitted from the component implementation.
- **Correction:** Added an SDK-owned close-request control only when a callback is supplied. The demo callback clears host-owned source and attachment state. Dirty-state confirmation is handled once inside the SDK.
- **Revalidation evidence:** Chromium clean close returned to `No PDF open`; dirty close dismissal preserved an edited native annotation and confirmation discarded it. Firefox 154.0.1 independently created a dirty native bookmark and passed both stay and discard branches.
- **Final status:** RESOLVED.

## P2-D03 — Tablet toolbar labels overlap

- **Blocked requirement:** RESP-01 / A11Y-03 — usable tablet-width layout and reachable controls.
- **Reproduction:** Open `normal.pdf` in Chromium at a 900 × 800 viewport. Keep the toolbar at its initial horizontal position.
- **Expected result:** Toolbar controls remain legible and reachable, using horizontal scrolling where the available width cannot contain every action.
- **Observed result:** The **Toggle thumbnails** and **Edit document** labels overlap because flex items shrink below their text width. The toolbar does expose horizontal scrolling, but the first controls are not visually legible.
- **Root cause:** `.viewer-tool` permits flex shrinking even though its label is `white-space: nowrap`.
- **Correction:** Prevented `.viewer-tool` controls from shrinking below their label width while retaining toolbar horizontal scrolling.
- **Revalidation evidence:** Chromium at 900 × 800 showed complete, non-overlapping labels. Firefox 154.0.1 at 820 × 895 retained the page width, kept the toolbar horizontally scrollable (`798` px client width, `1275` px scroll width), and produced `C/evidence/logs/firefox-phase2-responsive.png`.
- **Final status:** RESOLVED — desktop and tablet-width presentation passed browser review.

## P2-D04 — Continuous mode defeats linearized loading

- **Blocked requirement:** LOAD-10 / LOAD-11 / LOAD-12 / VIEW-16 — range-based first-page loading without idle full acquisition and lazy rendering for large documents.
- **Reproduction:** Open `http://127.0.0.1:8765/slow/large-linearized.pdf` in Chromium. The controlled fixture is 2,492,845 bytes and begins with a PDF `/Linearized` dictionary.
- **Expected result:** Initial `206` ranges provide a usable first page before the complete file is acquired. Remaining bytes stay unfetched until navigation, editing, or export needs them.
- **Observed result:** Before the viewer reported 120 pages ready, the range server recorded four completed `206` responses totaling all 2,492,845 bytes: `0-65535`, `2490368-2492844`, `2424832-2490367`, and `65536-2424831`.
- **Root cause:** Every continuously mounted `PdfPageCanvas` requested its PDF page metadata immediately, including far-off placeholders. The first fixture version also placed its size-generating image on page 1, making the linearization first-page section itself 2,433,157 bytes and unsuitable for proving early display.
- **Correction:** Page canvases now request PDF pages only when their placeholders approach the viewport. The reproducible fixture keeps page 1 small (`/E 2104`) and places the deterministic large image on page 120.
- **Revalidation evidence:** The regenerated 2,492,916-byte fixture rendered page 1 after 100,852 transferred bytes: one aborted speculative 32 KiB response plus ranges `0-65535` and `2490368-2492915`. Three idle seconds added no request. Opening the editor fetched only the missing `65536-2490367` range. `C/evidence/logs/range-server-final.jsonl` records the four-request sequence, and `fixture-inspection.json` confirms the `/Linearized` fixture.
- **Final status:** RESOLVED — the controlled range trace proves early display, no idle full acquisition, and on-demand completion without a second full download.

## P2-D05 — MuPDF worker never answers its first command

- **Blocked requirement:** EDIT-01 through EDIT-12, WASM-01 / WASM-02, annotation/redaction, bookmarks, widgets, edited printing, and edited export.
- **Reproduction:** Open the three-page `merge-alpha.pdf` in Chromium and choose **Edit document**. Repeat against both the Vite development server and the built production preview.
- **Expected result:** The MuPDF module loads in a worker, opens the document, returns its snapshot, and displays the document editor.
- **Observed result:** Both builds remain on `Preparing the WebAssembly document engine…` for more than 25 seconds. The editor never appears, no error is announced, and the worker returns neither a result nor an error.
- **Root cause:** The client posted its first command while the module worker was still evaluating the static MuPDF/WASM import. In the tested Chromium worker lifecycle, the command did not reach the handler that was registered only after that initialization completed.
- **Correction:** Added a tiny bootstrap worker that registers immediately, dynamically loads the MuPDF engine module, and sends an explicit `ready` or `bootstrap-error` message. The client queues calls behind that handshake and applies a 20-second startup bound.
- **Revalidation evidence:** Chromium loaded `merge-alpha.pdf`, reported `MuPDF WebAssembly engine ready.`, and completed import, copy, paste, undo, and redo. Firefox 154.0.1 independently entered the editor, serialized a real 90° rotation, and saved back to the viewer (`C/evidence/logs/firefox-phase2-principal-workflow.json`). The production build contains the bootstrap worker, MuPDF worker, and 10.4 MB WASM asset.
- **Final status:** RESOLVED — worker startup and serialized mutation passed both browser engines and the production build.

## P2-D06 — Undo does not restore structural page changes

- **Blocked requirement:** EDIT-12 — undo and redo for document operations.
- **Reproduction:** In `merge-alpha.pdf`, import the two-page `merge-beta.pdf` (five pages), copy page 4, paste it (six pages), then choose **Undo**.
- **Expected result:** Undo restores the five-page pre-paste document and enables Redo.
- **Observed result:** Redo becomes enabled, but the editor and engine snapshot remain at six pages. Repeating the undo/redo observation produces the same page count.
- **Root cause:** MuPDF's journal flags changed, but its native undo call did not restore the structural graft operation as used by the worker.
- **Correction:** The worker now stores serialized pre-operation states for document mutations and restores those states for undo/redo. Opening, saving, and cancelling reset the bounded session history.
- **Revalidation evidence:** Chromium development build: import changed 3 → 5 pages, paste changed 5 → 6, Undo restored 5 and enabled Redo, and Redo restored 6.
- **Final status:** RESOLVED — corrected Chromium history passed and `combined-working-copy.pdf` independently reopened with the expected five-page order, dimensions, and rotation.

## P2-D07 — Annotation panel omits existing native annotations

- **Blocked requirement:** ANN-07 / ANN-08 / ANN-09 — inspect, select, edit, and delete existing annotations.
- **Reproduction:** Open `existing-annotations.pdf` and choose **Annotations**. Independent MuPDF inspection returns `Text` and `Highlight` on page 1.
- **Expected result:** The panel initializes MuPDF metadata and lists both native annotations.
- **Observed result:** The first correction initialized MuPDF, but the worker then failed with `Text annotations have no QuadPoints property`; the panel still listed no annotations.
- **Root cause:** The Annotations toolbar action initially omitted `ensureEngine()`. After that was corrected, metadata extraction called `getQuadPoints()` for every annotation type even though MuPDF does not expose quad points for Text annotations.
- **Correction:** The toolbar now initializes the engine, and metadata extraction falls back to the annotation rectangle when an annotation type has no quad points.
- **Revalidation evidence:** Fresh Chromium and Firefox 154.0.1 sessions listed both native `Text` and `Highlight` annotations and exposed selection, edit, resize, and delete controls. Firefox changed the Text contents, exported, and reopened `C/evidence/generated-pdfs/existing-annotations-edited.pdf`; inspection confirms both native annotations and `Phase 2 updated note` (SHA-256 `ca730f3ea209000e9ab3e7fde4d7fa10483df699c06780bde4c67d4495e88413`).
- **Final status:** RESOLVED — existing native annotations initialize, list, select, edit, export, and reopen correctly. Numeric resize persistence remains a documented bonus limitation.

## P2-D08 — Unsupported local file reports a file-system error

- **Blocked requirement:** LOAD-09 — unsupported/non-PDF files must fail safely with an understandable message.
- **Reproduction:** Open deterministic `unsupported.pdf`, which contains plain text rather than PDF bytes.
- **Expected result:** The viewer explains that the selected file is not a valid or supported PDF.
- **Observed result:** Chromium rejected the file but displayed `A requested file or directory could not be found at the time an operation was processed.`, which misleadingly suggests a missing path.
- **Root cause:** PDF.js reports this byte-input parse failure using a missing-file exception message, and `describeLoadError` did not consider the source kind.
- **Correction:** Local-file and raw-byte missing-file-style parse errors are now classified as invalid/unsupported PDF content; URL errors retain network-specific guidance.
- **Revalidation evidence:** Fresh Chromium upload rejects the fixture, renders no PDF workspace, announces `The file is not a valid or supported PDF`, and delivers the same actionable text through the host `onError` callback.
- **Final status:** RESOLVED — Firefox 154.0.1 also rejected controlled invalid bytes with the same actionable alert/host text and no PDF workspace.

## P2-D09 — Source replacement emits spurious page-change callbacks

- **Blocked requirement:** SDK-03 / VIEW-07 / REL-03 — logical callback ordering, current-page tracking, and safe source replacement.
- **Reproduction:** In the raw-byte dual-instance harness, replace the primary two-page source with `multi-page-text.pdf` without scrolling.
- **Expected result:** The primary reports ready at page 1 without unrelated page changes; the secondary remains unchanged.
- **Observed result:** The primary emitted page callbacks `5, 2, 4, 3, 6, 1` while settling, even though the user did not navigate.
- **Root cause:** Every page observed against the browser viewport with a large preload margin. The visibility observer was also re-created whenever `onVisible` changed, causing nearby pages to compete as the current page.
- **Correction:** Preloading and current-page observation are separated. Current-page observation uses the owning `.page-workspace` with no preload margin and a stable callback ref. The validation harness also constrains each child SDK to `100%` height so its workspace, rather than the browser page, owns scrolling.
- **Revalidation evidence:** Fresh Firefox 154.0.1 evidence in `C/evidence/logs/firefox-phase2-d09-correction.json` shows replacement settling on page 1 with no replacement page callback. The secondary SDK remained unchanged. A deliberate primary-workspace scroll then reported pages 2 and 3 and ended on page 3.
- **Final status:** RESOLVED — Firefox replacement and deliberate-scroll tracking passed with the corrected harness layout.

## P2-D10 — Automated accessibility scan finds semantic and contrast violations

- **Blocked requirement:** A11Y-01 / A11Y-02 / A11Y-04 / A11Y-05.
- **Reproduction:** Run axe-core 4.10.3 in Firefox 154.0.1 at 1440×815 on loaded `normal.pdf`.
- **Expected result:** No known automated semantic, focusability, or contrast violation in the representative viewer.
- **Observed result:** Seven rules failed: prohibited ARIA on generic page/text containers, 3.95:1 host-status contrast, non-focusable scroll region, nested complementary and main landmarks, and no page-level H1.
- **Root cause:** Generic containers carried accessible names without roles; the workspace reused `main`, the thumbnail `aside` implied a nested landmark, the scroll area lacked a tab stop, and the muted host status was too light.
- **Correction:** Add valid grouping roles, a hidden H1, a named region for thumbnails, a focusable section for the page workspace, and darker host-status text.
- **Revalidation evidence:** Firefox 154.0.1 rerun with axe-core 4.10.3 reported zero violation rules, zero affected nodes, 37 passes, and one incomplete check. Chromium accessibility-tree inspection showed the corrected H1, named regions, grouping roles, live status, and focusable PDF workspace. Manual desktop/tablet visual review remains part of the final screenshot gate.
- **Final status:** RESOLVED.

## P2-D11 — Cancelled loading remains stuck in the loading UI

- **Blocked requirement:** LOAD-05 / VIEW-15 — load cancellation and distinct loading states.
- **Reproduction:** Open `/slow-no-range/large-linearized.pdf`, wait for visible progress, and choose **Cancel loading**.
- **Expected result:** The request is aborted, loading controls disappear, and the viewer reports cancellation without later installing the document.
- **Observed result:** The connection was aborted, but the SDK remained indefinitely on `Preparing document` with the Cancel button still present.
- **Root cause:** The button destroyed the PDF.js loading task but did not invalidate the active revision or update React loading/progress/status state; the task promise did not settle promptly enough to run `finally`.
- **Correction:** Cancellation now advances the document revision, clears the active task reference, destroys the task, and immediately resets loading/progress with an announced `Loading cancelled.` status.
- **Revalidation evidence:** Fresh Chromium cancelled the controlled slow no-range response, immediately removed loading controls, announced `Loading cancelled.`, and did not install the document; the server recorded the abort. Firefox 154.0.1 repeated the flow with 87.2 ms cancellation latency and no document after four seconds (`C/evidence/logs/firefox-phase2-postfix.json`).
- **Final status:** RESOLVED — cancellation passed in Chromium and Firefox.

## P2-D12 — Firefox logs stale PDF.js worker calls during source replacement

- **Blocked requirement:** SDK-06 / REL-01 / REL-03 — safe source replacement and cancellation of stale rendering work.
- **Reproduction:** In Firefox, replace loaded PDFs while canvas/text-layer work is active and inspect the browser driver log.
- **Expected result:** The latest document wins without stale PDF.js worker calls or console errors.
- **Observed result:** Visible replacement succeeded, but Firefox logged repeated `TypeError: can't access property "sendWithPromise", this.messageHandler is null` from PDF.js.
- **Root cause:** Canvas rendering, text-layer rendering, and current-page sizing share PDF page proxies, but each effect called `page.cleanup()` independently. One task could release page resources while another still used the proxy, especially as the document worker was retired.
- **Correction:** Per-effect page cleanup calls are removed; cancellation remains task-specific, and document-level cleanup owns shared PDF.js resources during replacement/unmount.
- **Revalidation evidence:** `C/evidence/logs/firefox-phase2-d09-correction.json` records a fresh loaded-to-loaded Firefox sequence ending on page 1 with no captured application errors. Its combined driver-log summary contains zero `sendWithPromise` failures and zero application JavaScript errors.
- **Final status:** RESOLVED — the Firefox replacement smoke completed cleanly.

## P2-D13 — Controlled-fixture border crosses body text

- **Blocked requirement:** Screenshot evidence quality / UI presentation review.
- **Reproduction:** Open any identity fixture such as `normal.pdf` or `bookmarks.pdf`; inspect the first body line.
- **Expected result:** The controlled fixture's vector border frames its body without obscuring text, so presentation screenshots remain legible.
- **Observed result:** The blue top border crosses the first body line in both Chromium and Firefox screenshots.
- **Root cause:** The first text baseline is `height - 135`, while the 3-point rectangle stroke tops out at `height - 132`; the PDF itself encodes the overlap.
- **Correction:** Lower the fixture rectangle top to `height - 190`, leaving clear space below both body lines. This is a fixture correction; no viewer rendering code changes.
- **Revalidation evidence:** The fixtures were regenerated and independently rendered with Poppler. The corrected border no longer crosses the body text. The current `normal.pdf` SHA-256 is `0aef592720013371bb2c38e0e9ab1d526d6ee81481a2b8a2533c91e47267b77e`.
- **Final status:** RESOLVED — the overlap was fixture-authored and the regenerated fixture renders cleanly; no viewer change was required.
