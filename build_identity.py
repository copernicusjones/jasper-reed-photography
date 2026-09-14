#!/usr/bin/env python3
"""Give the Jasper Reed hub a complete, consistent identity layer.

Adds, idempotently:
  - a shared site nav (injected right after <body>)
  - a shared site footer (injected before </body>)
  - shared nav/footer CSS (injected before </head>)

Safe to re-run: markers prevent duplicate injection.

Usage: python build_identity.py [--dry-run]
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

NAV_MARK = "<!-- jr-nav -->"
FOOT_MARK = "<!-- jr-footer -->"
CSS_MARK = "<!-- jr-nav-css -->"

NAV_CSS = """<style>
/* jr-nav-css */
.jr-nav{background:#0e1116;color:#fff}
.jr-nav .jr-inner{max-width:56rem;margin:0 auto;padding:.85rem 1.25rem;display:flex;flex-wrap:wrap;align-items:center;gap:.35rem 1.15rem}
.jr-nav a{color:#c8d4e0;text-decoration:none;font-size:.9rem;font-weight:500}
.jr-nav a:hover{color:#fff}
.jr-nav .jr-brand{color:#fff;font-weight:700;font-size:.95rem;letter-spacing:.2px;margin-right:auto}
.jr-nav .jr-brand span{color:#7f9fd4;font-weight:500}
.jr-foot{border-top:1px solid #e3e7ec;background:#fafafa;color:#666;font-size:.86rem;margin-top:3rem}
.jr-foot .jr-inner{max-width:56rem;margin:0 auto;padding:1.75rem 1.25rem;display:flex;flex-wrap:wrap;gap:.6rem 1.5rem;align-items:flex-start;justify-content:space-between}
.jr-foot a{color:#2563eb;text-decoration:none}
.jr-foot .jr-col{min-width:200px}
.jr-foot strong{color:#111;display:block;margin-bottom:.3rem;font-size:.88rem}
</style>"""

NAV_TPL = """<nav class="jr-nav"><div class="jr-inner">
  <a class="jr-brand" href="{home}">Jasper Reed <span>Photography &amp; Automation</span></a>
  <a href="{p}about.html">About</a>
  <a href="{p}services.html">Services</a>
  <a href="{p}contact.html">Contact</a>
  <a href="{home}">Free Resources</a>
</div></nav>"""

FOOT_TPL = """<footer class="jr-foot"><div class="jr-inner">
  <div class="jr-col">
    <strong>Jasper Reed Photography &amp; Automation</strong>
    Remote / Worldwide — async work, no calls.<br>
    <a href="mailto:jasper-reed@agentmail.to">jasper-reed@agentmail.to</a>
  </div>
  <div class="jr-col">
    <strong>Services</strong>
    <a href="{p}services.html">Services &amp; Pricing</a><br>
    <a href="{p}about.html">About</a><br>
    <a href="{p}contact.html">Contact</a>
  </div>
  <div class="jr-col">
    <strong>Free Resources</strong>
    <a href="{p}client-questionnaire.html">Client Questionnaire</a><br>
    <a href="{p}shoot-day-checklist.html">Shoot-Day Checklist</a><br>
    <a href="{p}pricing-guide.html">Pricing Guide</a><br>
    <a href="{home}">All resources →</a>
  </div>
</div>
<div class="jr-inner" style="padding-top:0;color:#888">
  <span>© 2026 Jasper Reed Photography &amp; Automation. Free to use and adapt.</span>
</div></footer>"""


def collect_pages():
    """Return (path, is_root) for every HTML page under ROOT."""
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


def inject(html: str, is_root: bool) -> str:
    p_links = "pages/" if is_root else ""
    home = "./" if is_root else "../index.html"
    nav = NAV_TPL.format(p=p_links, home=home)
    foot = FOOT_TPL.format(p=p_links, home=home)

    if CSS_MARK not in html:
        html = html.replace("</head>", NAV_CSS + "\n</head>", 1)
    if NAV_MARK not in html:
        body_open = re.search(r"<body[^>]*>", html)
        if body_open:
            ins = body_open.end()
            html = html[:ins] + "\n" + NAV_MARK + "\n" + nav + html[ins:]
    if FOOT_MARK not in html:
        html = html.replace("</body>", FOOT_MARK + "\n" + foot + "\n</body>", 1)
    return html


def main():
    dry = "--dry-run" in sys.argv
    total = 0
    for path, is_root in collect_pages():
        with open(path, encoding="utf-8") as f:
            orig = f.read()
        new = inject(orig, is_root)
        rel = os.path.relpath(path, ROOT)
        if new == orig:
            print(f"  unchanged  {rel}")
            continue
        if not dry:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(new)
        print(f"  {'would update' if dry else 'updated'}   {rel}  (+{len(new)-len(orig)} chars)")
        total += 1
    print(f"--- {total} page(s) {'would be ' if dry else ''}updated ---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
