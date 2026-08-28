"""Reopen PDF artifacts and emit deterministic structural/content evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
from pathlib import Path
from typing import Any

from pypdf import PdfReader


def outline_items(items: list[Any], depth: int = 0) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, list):
            result.extend(outline_items(item, depth + 1))
        else:
            result.append({"title": getattr(item, "title", str(item)), "depth": depth})
    return result


def inspect(path: Path, password: str | None, secret: str | None) -> dict[str, Any]:
    data = path.read_bytes()
    result: dict[str, Any] = {
        "path": path.name,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "mime": mimetypes.guess_type(path.name)[0],
        "pdfHeader": data.startswith(b"%PDF-"),
        "linearized": b"/Linearized" in data[:2048],
        "valid": False,
    }
    try:
        reader = PdfReader(path, strict=False)
        if reader.is_encrypted:
            result["encrypted"] = True
            if not password or reader.decrypt(password) == 0:
                result["error"] = "password required or incorrect"
                return result
        else:
            result["encrypted"] = False
        pages = []
        all_text = []
        for index, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            all_text.append(text)
            annotations = []
            for annotation_ref in page.get("/Annots", []):
                annotation = annotation_ref.get_object()
                annotations.append(
                    {
                        "subtype": str(annotation.get("/Subtype", "")),
                        "fieldType": str(annotation.get("/FT", "")),
                        "name": str(annotation.get("/T", "")),
                        "contents": str(annotation.get("/Contents", "")),
                        "rect": [float(value) for value in annotation.get("/Rect", [])],
                        "quadPoints": [float(value) for value in annotation.get("/QuadPoints", [])],
                    }
                )
            pages.append(
                {
                    "index": index + 1,
                    "width": round(float(page.mediabox.width), 2),
                    "height": round(float(page.mediabox.height), 2),
                    "rotation": int(page.get("/Rotate", 0) or 0),
                    "textPrefix": " ".join(text.split())[:160],
                    "annotations": annotations,
                }
            )
        fields = reader.get_fields() or {}
        extracted = "\n".join(all_text)
        result.update(
            {
                "valid": True,
                "pageCount": len(pages),
                "pages": pages,
                "outline": outline_items(reader.outline),
                "fields": [
                    {
                        "name": name,
                        "fieldType": str(field.get("/FT", "")),
                        "value": str(field.get("/V", "")),
                    }
                    for name, field in fields.items()
                ],
                "extractedTextLength": len(extracted),
                "secret": secret,
                "secretFound": secret in extracted if secret else None,
            }
        )
    except Exception as error:  # Evidence needs the parser's actual failure.
        result["error"] = f"{type(error).__name__}: {error}"
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--password")
    parser.add_argument("--secret")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = [inspect(path, args.password, args.secret) for path in args.paths]
    payload = json.dumps(report, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
