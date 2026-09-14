#!/usr/bin/env python3
"""Wire favicon into every page, and surface About/Contact on the homepage.

Idempotent: uses explicit markers.

Usage: python wire_favicon.py [--dry-run]
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

FAV_MARK = "<!-- jr-favicon -->"
FAV_ROOT = ('<link rel="icon" href="favicon.svg" type="image/svg+xml">')
FAV_NEST = ('<link rel="icon" href="../favicon.svg" type="image/svg+xml">')

# Homepage: a card linking to About (Contact is already in nav).
ABOUT_CARD = """    <div class="card">
      <h3><a href="pages/about.html">About Jasper Reed</a></h3>
      <p>How this business works: async delivery, written scope and fixed price before payment, an evidence report with every job, and no calls.</p>
      <span class="tag">about</span><span class="tag">how it works</span>
    </div>
"""


def collect_pages():
    pages = []
    idx = os.path.join(ROOT, "index.html")
    if os.path.exists(idx):
        pages.append((idx, True))
    pd = os.path.join(ROOT, "pages")
    if os.path.isdir(pd):
        for f in sorted(os.listdir(pd)):
            if f.endswith(".html"):
                pages.append((os.path.join(pd, f), False))
    return pages


def main():
    dry = "--dry-run" in sys.argv
    changed = 0
    for path, is_root in collect_pages():
        with open(path, encoding="utf-8") as f:
            orig = f.read()
        new = orig
        tag = FAV_ROOT if is_root else FAV_NEST
        if FAV_MARK not in new:
            new = new.replace("</head>", FAV_MARK + "\n" + tag + "\n</head>", 1)
        # Homepage only: insert About card at the top of the resource grid.
        if is_root and "pages/about.html" not in new:
            m = re.search(r'(<div class="grid">\s*\n)', new)
            if m:
                new = new[: m.end()] + ABOUT_CARD + new[m.end():]
        rel = os.path.relpath(path, ROOT)
        if new == orig:
            print(f"  unchanged  {rel}")
            continue
        if not dry:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(new)
        print(f"  {'would update' if dry else 'updated'}   {rel}  (+{len(new)-len(orig)} chars)")
        changed += 1
    print(f"--- {changed} page(s) {'would be ' if dry else ''}updated ---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
