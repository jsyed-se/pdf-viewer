"""Serve generated fixtures with controlled range/CORS behavior and JSONL logs."""

from __future__ import annotations

import argparse
import json
import re
import threading
import time
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

RANGE_PATTERN = re.compile(r"bytes=(\d*)-(\d*)$")


class FixtureHandler(BaseHTTPRequestHandler):
    server_version = "AtlasFixtureRange/1.0"

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Range")
        self.end_headers()

    def do_HEAD(self) -> None:
        self._serve(send_body=False)

    def do_GET(self) -> None:
        self._serve(send_body=True)

    def _serve(self, send_body: bool) -> None:
        parsed = urlsplit(self.path)
        parts = [part for part in unquote(parsed.path).split("/") if part]
        mode = "range"
        if parts and parts[0] in {"range", "no-range", "cors-denied", "slow", "slow-no-range"}:
            mode = parts.pop(0)
        filename = parts[-1] if parts else ""
        root: Path = self.server.fixture_root  # type: ignore[attr-defined]
        candidate = (root / filename).resolve()
        if candidate.parent != root.resolve() or not candidate.is_file():
            self._record(filename, mode, 404, None, 0, 0, 0)
            self.send_error(HTTPStatus.NOT_FOUND, "Controlled fixture not found")
            return

        size = candidate.stat().st_size
        start, end = 0, size - 1
        status = HTTPStatus.OK
        range_header = self.headers.get("Range")
        if mode not in {"no-range", "slow-no-range"} and range_header:
            match = RANGE_PATTERN.fullmatch(range_header.strip())
            if not match:
                self.send_error(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                return
            start = int(match.group(1) or 0)
            end = int(match.group(2) or size - 1)
            end = min(end, size - 1)
            if start > end or start >= size:
                self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return
            status = HTTPStatus.PARTIAL_CONTENT

        length = end - start + 1
        self.send_response(status)
        self.send_header("Content-Type", "application/pdf" if candidate.suffix.lower() == ".pdf" else "text/plain")
        self.send_header("Content-Length", str(length if status == HTTPStatus.PARTIAL_CONTENT else size))
        if mode not in {"no-range", "slow-no-range"}:
            self.send_header("Accept-Ranges", "bytes")
        if status == HTTPStatus.PARTIAL_CONTENT:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        if mode != "cors-denied":
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Expose-Headers", "Accept-Ranges, Content-Length, Content-Range")
        self.end_headers()

        sent = 0
        if send_body:
            with candidate.open("rb") as stream:
                stream.seek(start)
                remaining = length if status == HTTPStatus.PARTIAL_CONTENT else size
                while remaining > 0:
                    chunk = stream.read(min(16 * 1024, remaining))
                    if not chunk:
                        break
                    try:
                        self.wfile.write(chunk)
                    except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
                        break
                    sent += len(chunk)
                    remaining -= len(chunk)
                    if mode in {"slow", "slow-no-range"}:
                        time.sleep(0.03)
        self._record(filename, mode, int(status), range_header, start, end, sent)

    def _record(self, filename: str, mode: str, status: int, requested_range: str | None, start: int, end: int, sent: int) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": self.command,
            "path": filename,
            "mode": mode,
            "requestedRange": requested_range,
            "status": status,
            "start": start,
            "end": end,
            "bytesSent": sent,
        }
        line = json.dumps(entry, separators=(",", ":"))
        lock: threading.Lock = self.server.log_lock  # type: ignore[attr-defined]
        log_path: Path = self.server.log_path  # type: ignore[attr-defined]
        with lock:
            with log_path.open("a", encoding="utf-8") as stream:
                stream.write(line + "\n")
        print(line, flush=True)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("A/tests/fixtures/generated"))
    parser.add_argument("--log", type=Path, default=Path("C/evidence/logs/range-server.jsonl"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.log.write_text("", encoding="utf-8")
    server = ThreadingHTTPServer((args.host, args.port), FixtureHandler)
    server.fixture_root = args.root.resolve()
    server.log_path = args.log.resolve()
    server.log_lock = threading.Lock()
    print(json.dumps({"ready": True, "url": f"http://{args.host}:{args.port}", "root": str(server.fixture_root)}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
