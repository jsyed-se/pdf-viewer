# Controlled PDF Fixtures

Generate the non-sensitive Phase 2 fixtures from the repository root:

```powershell
python -m pip install -r A/scripts/requirements.txt
python A/scripts/generate_fixtures.py
```

Output is written to `A/tests/fixtures/generated/` and is intentionally ignored. The generator uses deterministic content and writes `manifest.json` with SHA-256 hashes, sizes, purposes, passwords, and expected facts.

| Fixture | Purpose |
| --- | --- |
| `normal.pdf` | Small local/byte-array viewing and print flow |
| `multi-page-text.pdf` | Navigation, text selection, thumbnails, and extraction |
| `mixed-pages.pdf` | Portrait, landscape, custom-size, and rotated pages |
| `large-linearized.pdf` | Large document, lazy rendering, HTTP range, and linearization evidence |
| `password-protected.pdf` | Correct, incorrect, and cancelled password flows; password is `viewerpass` |
| `existing-annotations.pdf` | Native text and highlight annotation reading |
| `bookmarks.pdf` | Nested outline reading and bookmark CRUD |
| `widgets.pdf` | Existing text, checkbox, and empty signature-field inspection |
| `merge-alpha.pdf`, `merge-beta.pdf` | Merge, reorder, copy, keep, and extraction identity checks |
| `secret-redaction.pdf` | Applied-redaction removal check using `PHASE2_SECRET_7F3A9` |
| `malformed.pdf`, `unsupported.txt` | Actionable invalid/unsupported-file errors |

These fixtures contain no private or production data.
