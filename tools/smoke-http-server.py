#!/usr/bin/env python3
import argparse
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


class SmokeHandler(SimpleHTTPRequestHandler):
    sdk_delay_seconds = 15.0

    def do_GET(self):
        path = urlsplit(self.path).path
        referer = self.headers.get("Referer", "")

        if path == "/sdk.js" and "sdkScript=delay" in referer:
            print(
                f"[smoke-http] delaying /sdk.js by {self.sdk_delay_seconds:.1f}s",
                flush=True,
            )
            time.sleep(self.sdk_delay_seconds)

        super().do_GET()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--directory", default="dist")
    parser.add_argument("--sdk-delay-seconds", type=float, default=15.0)
    args = parser.parse_args()

    SmokeHandler.sdk_delay_seconds = max(0.0, args.sdk_delay_seconds)
    handler = partial(SmokeHandler, directory=args.directory)
    server = ThreadingHTTPServer((args.bind, args.port), handler)
    print(
        f"[smoke-http] serving {args.directory} on "
        f"http://{args.bind}:{args.port}",
        flush=True,
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
