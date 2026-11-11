#!/usr/bin/env python3
"""Minimal stand-in for the Cursor download API used by the role tests.

A HEAD request to ``/<base>/<platform>/cursor/<version>`` answers with a 302
redirect whose filename carries the resolved version, mirroring the real API.
The redirect target serves a small shell script in place of the AppImage so the
download path can be exercised without internet access.
"""

import argparse
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DOWNLOAD_REQUEST = re.compile(r"/download/Cursor-(?P<version>[0-9.]+)-[^/]+\.AppImage$")


class CursorApiHandler(BaseHTTPRequestHandler):
    server_version = "FakeCursorApi/0.1"

    def _resolve_version(self) -> str:
        return self.server.resolved_version

    def _redirect(self) -> None:
        version = self._resolve_version()
        host, port = self.server.server_address[:2]
        location = f"http://{host}:{port}/download/Cursor-{version}-x86_64.AppImage"
        self.send_response(302)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _download(self, include_body: bool) -> None:
        match = DOWNLOAD_REQUEST.search(self.path)
        if not match:
            self.send_error(404, "unknown download path")
            return
        body = f"#!/bin/sh\n# fake Cursor {match.group('version')} AppImage\nexit 0\n".encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if DOWNLOAD_REQUEST.search(self.path):
            self._download(include_body=True)
        else:
            self._redirect()

    def do_HEAD(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if DOWNLOAD_REQUEST.search(self.path):
            self._download(include_body=False)
        else:
            self._redirect()

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"{self.address_string()} {fmt % args}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18080)
    parser.add_argument("--version", default="3.0.16")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), CursorApiHandler)
    server.resolved_version = args.version
    print(f"fake Cursor API on http://{args.host}:{args.port} (version {args.version})", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
