"""Generate deterministic, non-sensitive PDFs for Phase 2 validation."""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

import pikepdf
from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Highlight, Text
from pypdf.generic import (
    ArrayObject,
    BooleanObject,
    DictionaryObject,
    NameObject,
    NumberObject,
    RectangleObject,
    TextStringObject,
)
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tests" / "fixtures" / "generated"
PASSWORD = "viewerpass"
SECRET = "PHASE2_SECRET_7F3A9"


def draw_identity_page(
    pdf: canvas.Canvas,
    label: str,
    body: str,
    page_size: tuple[float, float],
    image_path: Path | None = None,
) -> None:
    width, height = page_size
    pdf.setPageSize(page_size)
    pdf.setFillColorRGB(0.05, 0.24, 0.34)
    pdf.rect(0, height - 92, width, 92, fill=1, stroke=0)
    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 25)
    pdf.drawString(42, height - 55, label)
    pdf.setFillColorRGB(0.08, 0.12, 0.15)
    pdf.setFont("Helvetica", 13)
    for index, line in enumerate(body.splitlines()):
        pdf.drawString(48, height - 135 - index * 22, line)
    pdf.setStrokeColorRGB(0.1, 0.55, 0.72)
    pdf.setLineWidth(3)
    pdf.rect(42, 48, width - 84, height - 238, fill=0, stroke=1)
    if image_path:
        pdf.drawImage(str(image_path), 64, 72, width=min(300, width - 128), height=min(300, height - 220), preserveAspectRatio=True)
    pdf.showPage()


def create_pages(path: Path, pages: list[dict], image_path: Path | None = None) -> None:
    pdf = canvas.Canvas(str(path), pagesize=letter, pageCompression=1, invariant=1)
    for page in pages:
        pdf.setPageRotation(page.get("rotation", 0))
        draw_identity_page(pdf, page["label"], page["body"], page.get("size", letter), image_path if page.get("image") else None)
        pdf.setPageRotation(0)
    pdf.save()


def encrypted_copy(source: Path, target: Path) -> None:
    reader = PdfReader(source)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer.encrypt(user_password=PASSWORD, owner_password="phase2-owner", algorithm="AES-256")
    with target.open("wb") as stream:
        writer.write(stream)


def add_annotations(source: Path, target: Path) -> None:
    reader = PdfReader(source)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer.add_annotation(0, Text(rect=(72, 500, 110, 538), text="Existing Phase 2 text note", open=False))
    writer.add_annotation(
        0,
        Highlight(
            rect=(72, 430, 330, 454),
            quad_points=ArrayObject([NumberObject(value) for value in [72, 454, 330, 454, 72, 430, 330, 430]]),
            highlight_color="ffd323",
            printing=True,
        ),
    )
    with target.open("wb") as stream:
        writer.write(stream)


def add_bookmarks(source: Path, target: Path) -> None:
    reader = PdfReader(source)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    root = writer.add_outline_item("Phase 2 Root", 0)
    writer.add_outline_item("Nested page 2", 1, parent=root)
    writer.add_outline_item("Final page", len(writer.pages) - 1)
    with target.open("wb") as stream:
        writer.write(stream)


def add_widgets(target: Path) -> None:
    pdf = canvas.Canvas(str(target), pagesize=letter, pageCompression=1, invariant=1)
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(72, 720, "WIDGETS-01 Existing form controls")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(72, 675, "Reviewer name")
    pdf.acroForm.textfield(name="reviewer_name", tooltip="Reviewer name", x=72, y=630, width=240, height=28)
    pdf.drawString(72, 590, "Approved")
    pdf.acroForm.checkbox(name="approved", tooltip="Approved", x=140, y=580, buttonStyle="check")
    pdf.drawString(72, 525, "Signature field below is intentionally empty.")
    pdf.showPage()
    pdf.save()

    reader = PdfReader(target)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    page = writer.pages[0]
    signature = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Widget"),
            NameObject("/FT"): NameObject("/Sig"),
            NameObject("/T"): TextStringObject("approval_signature"),
            NameObject("/TU"): TextStringObject("Approval signature"),
            NameObject("/Rect"): RectangleObject([72, 455, 320, 495]),
            NameObject("/F"): NumberObject(4),
            NameObject("/P"): page.indirect_reference,
        }
    )
    signature_ref = writer._add_object(signature)
    annotations = page.get("/Annots")
    if annotations is None:
        annotations = ArrayObject()
        page[NameObject("/Annots")] = annotations
    else:
        annotations = annotations.get_object()
    annotations.append(signature_ref)

    acro_form = writer._root_object.get("/AcroForm")
    if acro_form is None:
        acro_form = DictionaryObject({NameObject("/Fields"): ArrayObject()})
        writer._root_object[NameObject("/AcroForm")] = writer._add_object(acro_form)
    else:
        acro_form = acro_form.get_object()
    fields = acro_form.get("/Fields")
    if fields is None:
        fields = ArrayObject()
        acro_form[NameObject("/Fields")] = fields
    else:
        fields = fields.get_object()
    fields.append(signature_ref)
    acro_form[NameObject("/SigFlags")] = NumberObject(3)
    acro_form[NameObject("/NeedAppearances")] = BooleanObject(True)
    temporary = target.with_suffix(".widgets.tmp.pdf")
    with temporary.open("wb") as stream:
        writer.write(stream)
    temporary.replace(target)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for path in OUTPUT.iterdir():
        if path.is_file():
            path.unlink()

    create_pages(
        OUTPUT / "normal.pdf",
        [
            {"label": "NORMAL-01 PAGE 1", "body": "Small controlled PDF\nVector border and selectable text"},
            {"label": "NORMAL-02 PAGE 2", "body": "Second page marker\nUsed for navigation and print"},
        ],
    )
    create_pages(
        OUTPUT / "multi-page-text.pdf",
        [
            {"label": f"TEXT-{index:02d} PAGE {index}", "body": f"Selectable sentence for page {index}\nIdentity token TEXT_TOKEN_{index:02d}"}
            for index in range(1, 17)
        ],
    )
    create_pages(
        OUTPUT / "mixed-pages.pdf",
        [
            {"label": "MIXED-PORTRAIT", "body": "612 x 792 points\nPortrait reference", "size": letter},
            {"label": "MIXED-LANDSCAPE", "body": "792 x 612 points\nLandscape reference", "size": landscape(letter)},
            {"label": "MIXED-A4-ROTATED", "body": "A4 page with 90 degree rotation\nRotation reference", "size": A4, "rotation": 90},
            {"label": "MIXED-SQUARE", "body": "540 x 540 points\nCustom-size reference", "size": (540, 540)},
        ],
    )
    create_pages(
        OUTPUT / "merge-alpha.pdf",
        [
            {"label": "ALPHA-A1", "body": "Merge source alpha\nIdentity ALPHA_A1"},
            {"label": "ALPHA-A2", "body": "Merge source alpha\nIdentity ALPHA_A2", "size": landscape(letter)},
            {"label": "ALPHA-A3", "body": "Merge source alpha\nIdentity ALPHA_A3"},
        ],
    )
    create_pages(
        OUTPUT / "merge-beta.pdf",
        [
            {"label": "BETA-B1", "body": "Merge source beta\nIdentity BETA_B1", "size": A4},
            {"label": "BETA-B2", "body": "Merge source beta\nIdentity BETA_B2"},
        ],
    )
    create_pages(
        OUTPUT / "secret-redaction.pdf",
        [
            {"label": "REDACTION-SECRET", "body": f"Public prefix {SECRET} public suffix\nThe unique phrase must disappear after applied redaction."},
            {"label": "REDACTION-CONTROL", "body": "Control page without the secret\nThis content must remain extractable."},
        ],
    )
    create_pages(
        OUTPUT / "bookmarks-base.pdf",
        [
            {"label": f"BOOKMARK-{index}", "body": f"Outline destination page {index}\nBOOKMARK_TOKEN_{index}"}
            for index in range(1, 5)
        ],
    )
    add_bookmarks(OUTPUT / "bookmarks-base.pdf", OUTPUT / "bookmarks.pdf")
    (OUTPUT / "bookmarks-base.pdf").unlink()
    add_annotations(OUTPUT / "normal.pdf", OUTPUT / "existing-annotations.pdf")
    add_widgets(OUTPUT / "widgets.pdf")
    encrypted_copy(OUTPUT / "normal.pdf", OUTPUT / "password-protected.pdf")

    random_source = random.Random(20260828)
    noise = bytes(random_source.randrange(256) for _ in range(900 * 900 * 3))
    noise_path = OUTPUT / "large-noise.png"
    Image.frombytes("RGB", (900, 900), noise).save(noise_path, format="PNG", compress_level=6)
    large_base = OUTPUT / "large-base.pdf"
    create_pages(
        large_base,
        [
            {
                "label": f"LARGE-{index:03d}",
                "body": f"Large linearized fixture page {index} of 120\nLARGE_TOKEN_{index:03d}",
                # Keep page 1 small so the linearization test can prove that it
                # becomes usable before the deliberately large tail is fetched.
                "image": index == 120,
            }
            for index in range(1, 121)
        ],
        image_path=noise_path,
    )
    with pikepdf.open(large_base) as document:
        document.save(
            OUTPUT / "large-linearized.pdf",
            linearize=True,
            deterministic_id=True,
            compress_streams=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
        )
    large_base.unlink()
    noise_path.unlink()

    (OUTPUT / "malformed.pdf").write_bytes(b"%PDF-1.7\n1 0 obj << /Type /Catalog >>\ntruncated-without-xref")
    (OUTPUT / "unsupported.txt").write_text("This is controlled plain text, not a PDF.\n", encoding="utf-8")

    purposes = {
        "normal.pdf": "small local, bytes, navigation, print",
        "multi-page-text.pdf": "navigation, selection, thumbnails, extraction",
        "mixed-pages.pdf": "mixed dimensions and rotation",
        "large-linearized.pdf": "linearized range and lazy rendering",
        "password-protected.pdf": "password handling",
        "existing-annotations.pdf": "existing native annotations",
        "bookmarks.pdf": "nested bookmarks",
        "widgets.pdf": "text, checkbox, and signature widgets",
        "merge-alpha.pdf": "primary edit and merge identity",
        "merge-beta.pdf": "import and merge identity",
        "secret-redaction.pdf": "irreversible redaction extraction check",
        "malformed.pdf": "malformed PDF error",
        "unsupported.txt": "unsupported file error",
    }
    manifest = {
        "generatedBy": "A/scripts/generate_fixtures.py",
        "passwords": {"password-protected.pdf": PASSWORD},
        "secretPhrase": SECRET,
        "files": [
            {
                "name": path.name,
                "purpose": purposes[path.name],
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "linearized": path.read_bytes()[:2048].find(b"/Linearized") >= 0,
            }
            for path in sorted(OUTPUT.iterdir())
            if path.name in purposes
        ],
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
