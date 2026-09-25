#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

AUTHORED_RUNTIME = (
    "index.html",
    "styles.css",
    "src/main.js",
    "src/yandex.js",
)

GENERATED_RUNTIME = (
    "game/powder.js",
    "game/powder.wasm",
)

# The game itself must be self-contained. The Yandex platform SDK is loaded
# only through the required same-origin /sdk.js path and therefore does not
# appear as an external destination here.
ABSOLUTE_NETWORK_URL = re.compile(
    rb"(?i)(?:https?|wss?)://[^\x00-\x20\"'<>]+"
)
PROTOCOL_RELATIVE_HOST = re.compile(
    rb"(?i)(?<!:)//(?:[a-z0-9-]+\.)+[a-z]{2,}(?:[:/]|$)"
)

# Upstream/community/network-service hosts that must never survive into the
# no-HTTP Yandex runtime, even if they are not written as a full URL.
FORBIDDEN_AUTHORED_NETWORK_PRIMITIVES = (
    b"fetch(",
    b"XMLHttpRequest",
    b"WebSocket",
    b"EventSource",
    b"sendBeacon",
    b"window.open",
    b"location.assign",
    b"location.replace",
    b"document.location",
)

FORBIDDEN_SERVICE_MARKERS = (
    b"powdertoy.co.uk",
    b"www.powdertoy.co.uk",
    b"tpt.io",
    b"starcatcher.us",
    b"irc.libera.chat",
    b"discord.gg",
    b"discord.com",
)

# URL-like strings used only as XML namespace identifiers are not network
# destinations and may legitimately be emitted by browser libraries.
NON_NETWORK_NAMESPACE_PREFIXES = (
    b"http://www.w3.org/",
    b"https://www.w3.org/",
)


def find_external_url_literals(data: bytes):
    findings = []
    for regex in (ABSOLUTE_NETWORK_URL, PROTOCOL_RELATIVE_HOST):
        for match in regex.finditer(data):
            value = match.group(0)
            if value.startswith(NON_NETWORK_NAMESPACE_PREFIXES):
                continue
            findings.append(value)
    return findings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dist", nargs="?", default="dist")
    args = parser.parse_args()

    root = Path(args.dist)
    failures = []

    for rel in AUTHORED_RUNTIME:
        path = root / rel
        if not path.is_file():
            failures.append(f"{rel}: missing runtime file")
            continue

        data = path.read_bytes()
        for value in find_external_url_literals(data):
            failures.append(
                f"{rel}: external URL literal {value.decode('utf-8', 'replace')}"
            )
        lower = data.lower()
        for primitive in FORBIDDEN_AUTHORED_NETWORK_PRIMITIVES:
            if primitive.lower() in lower:
                failures.append(
                    f"{rel}: forbidden network/navigation primitive "
                    f"{primitive.decode()}"
                )
        for marker in FORBIDDEN_SERVICE_MARKERS:
            if marker in lower:
                failures.append(
                    f"{rel}: forbidden service marker {marker.decode()}"
                )

    # Generated Emscripten output may contain browser-library documentation
    # strings, so for it enforce the service-host ban rather than treating
    # every diagnostic URL as a network destination.
    for rel in GENERATED_RUNTIME:
        path = root / rel
        if not path.is_file():
            failures.append(f"{rel}: missing runtime file")
            continue

        lower = path.read_bytes().lower()
        for marker in FORBIDDEN_SERVICE_MARKERS:
            if marker in lower:
                failures.append(
                    f"{rel}: forbidden service marker {marker.decode()}"
                )

    if failures:
        raise SystemExit(
            "Third-party runtime network audit failed:\n- "
            + "\n- ".join(failures)
        )

    print("Third-party runtime network audit: OK")
    print("Checked authored runtime for external URL literals and direct network/navigation primitives.")
    print("Checked JS/WASM runtime for upstream/community service hosts.")
    print("Only the same-origin Yandex SDK path /sdk.js is permitted by the port.")


if __name__ == "__main__":
    main()
