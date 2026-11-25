#!/usr/bin/env python3
"""The 3 AM Excuse: one line, delivered to entry.txt.

A hardware wallet explains why it will not sign. This module keeps
that explanation in EXCUSE, sanity-checks it, and drops it into the
folder the harness names (MAKEFUN_OUTPUT_DIR, else /output).
"""

import os
import sys
import tempfile
from pathlib import Path

EXCUSE = "Denied: at 3 AM the scammers clock in, your brain clocks out, and I'm the only one on shift still reading the whole destination address."
LIMIT = 200


def problems_with(text):
    """List everything wrong with the candidate line; [] means fine."""
    found = []
    if not isinstance(text, str):
        return ["excuse is not text"]
    if not 1 <= len(text) <= LIMIT:
        found.append("excuse must be 1 to %d characters" % LIMIT)
    if text.strip() == "":
        found.append("excuse must not be blank")
    for mark in ("\n", "\r"):
        if mark in text:
            found.append("excuse must stay on one line")
            break
    return found


def destination():
    """Where entry.txt goes; a blank override means the default."""
    named = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    return Path(named) if named else Path("/output")


def deliver():
    issues = problems_with(EXCUSE)
    if issues:
        for issue in issues:
            print("refusing to write entry: " + issue, file=sys.stderr)
        return 1
    folder = destination()
    folder.mkdir(parents=True, exist_ok=True)
    final = folder / "entry.txt"
    handle, spare = tempfile.mkstemp(prefix=".excuse-", dir=str(folder))
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write((EXCUSE + "\n").encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(spare, 0o644)
        os.replace(spare, final)
    except BaseException:
        try:
            os.unlink(spare)
        except OSError:
            pass
        raise
    return 0


if __name__ == "__main__":
    sys.exit(deliver())
