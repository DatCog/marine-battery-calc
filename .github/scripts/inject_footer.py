#!/usr/bin/env python3
"""Inject YOSUR MARINE company info + backlink into index.html (idempotent)."""
import pathlib
import sys

TARGET = pathlib.Path("index.html")
MARKER = "yosurmarine.com"

BLOCK = (
    '<section id="yosur-marine" style="max-width:64rem;margin:2.5rem auto 0;padding:0 1rem;">'
    '<div style="border:1px solid rgba(0,0,0,.06);background:#fff;border-radius:20px;padding:1.5rem;text-align:center;">'
    '<p style="margin:0 0 .5rem;font-size:.95rem;font-weight:600;color:#1d1d1f;">YOSUR MARINE</p>'
    '<p style="margin:0 0 1rem;font-size:.8rem;line-height:1.6;color:#86868b;">'
    'Supplier of GMDSS safety batteries (EPIRB, SART, VDR), industrial Li-SOCl2 cells '
    'and PLC backup batteries for vessels worldwide.</p>'
    '<p style="margin:0 0 .5rem;font-size:.8rem;">'
    '<a href="https://yosurmarine.com" style="color:#0071e3;font-weight:600;text-decoration:none;">'
    'Marine industrial batteries &amp; GMDSS safety cells &rarr; yosurmarine.com</a></p>'
    '<p style="margin:0;font-size:.8rem;color:#86868b;">Phone / WhatsApp: '
    '<a href="https://wa.me/8615309563264" style="color:#0071e3;text-decoration:none;">'
    '+86 153 0956 3264</a></p>'
    '<p style="margin:1rem 0 0;font-size:.7rem;color:#a1a1a6;">'
    '&copy; 2026 YOSUR MARINE. All rights reserved.</p>'
    '</div></section>'
)

META_FIXES = [
    (
        '<meta name="Calculate battery run time and discharge rates for marine and industrial applications instantly.">',
        '<meta name="description" content="Calculate battery run time and discharge rates for marine and industrial applications instantly.">',
    ),
]


def main() -> int:
    if not TARGET.exists():
        print("index.html not found")
        return 1

    html = TARGET.read_text(encoding="utf-8")
    changed = False

    for bad, good in META_FIXES:
        if bad in html:
            html = html.replace(bad, good)
            changed = True
            print("fixed malformed meta tag")

    if MARKER in html:
        print("backlink already present, skipping injection")
    else:
        lowered = html.lower()
        insert_at = None
        for tag in ("</body>", "</html>"):
            if tag in lowered:
                insert_at = lowered.rindex(tag)
                break
        if insert_at is None:
            html = html.rstrip() + "\n" + BLOCK + "\n"
        else:
            html = html[:insert_at] + BLOCK + "\n" + html[insert_at:]
        changed = True
        print("injected YOSUR MARINE block")

    if changed:
        TARGET.write_text(html, encoding="utf-8")
        print("index.html updated")
    else:
        print("nothing to do")
    return 0


if __name__ == "__main__":
    sys.exit(main())
