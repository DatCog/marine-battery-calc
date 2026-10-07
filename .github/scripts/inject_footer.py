#!/usr/bin/env python3
"""Inject YOSUR MARINE company info + backlinks into index.html.

Three independent, idempotent operations. Each carries its own guard so that
re-running never duplicates anything and one operation failing does not block
the other two:

  1. footer block       -> inserted before </body>
                           guard: id="yosur-marine"
  2. related-tools card -> inserted INSIDE the existing
                           "Related Battery Engineering Calculators" grid
                           (no-op on pages that have no such section)
                           guard: data-yosur-related
  3. meta repair        -> <meta name="<a description sentence>"> is a real
                           defect (the page ends up with no description at
                           all); rewritten to name="description" content="..."

Run from the repository root: python3 .github/scripts/inject_footer.py
"""

import pathlib
import sys

TARGET = pathlib.Path("index.html")

FOOTER_GUARD = 'id="yosur-marine"'
RELATED_GUARD = "data-yosur-related"
RELATED_HEADING = "Related Battery Engineering Calculators"
GRID_OLD = '<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-medium">'
GRID_NEW = (
    '<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 '
    'gap-4 text-xs font-medium">'
)

FOOTER_BLOCK = (
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

RELATED_CARD = (
    '<a data-yosur-related target="_blank" rel="noopener" href="https://yosurmarine.com" '
    'class="p-4 rounded-2xl bg-[#fff7ed] hover:bg-[#ffedd5] text-[#1d1d1f] '
    'transition-all duration-200 flex items-center justify-between group">'
    '<span>\u2693 YOSUR MARINE \u2014 GMDSS &amp; Marine Industrial Batteries</span>'
    '<span class="text-[#0071e3] group-hover:translate-x-1 transition-transform">\u2192</span>'
    '</a>'
)

META_FIXES = [
    (
        '<meta name="Calculate battery run time and discharge rates for marine '
        'and industrial applications instantly.">',
        '<meta name="description" content="Calculate battery run time and discharge '
        'rates for marine and industrial applications instantly.">',
    ),
]


def fix_meta(html):
    """Repair <meta name="<description>"> into a real description meta tag."""
    changed = False
    for bad, good in META_FIXES:
        if bad in html:
            html = html.replace(bad, good)
            changed = True
    return html, changed


def inject_footer(html):
    """Append the YOSUR MARINE footer block just before </body>."""
    if FOOTER_GUARD in html:
        return html, False

    lowered = html.lower()
    insert_at = None
    for tag in ("</body>", "</html>"):
        if tag in lowered:
            insert_at = lowered.rindex(tag)
            break

    if insert_at is None:
        return html.rstrip() + "\n" + FOOTER_BLOCK + "\n", True
    return html[:insert_at] + FOOTER_BLOCK + "\n" + html[insert_at:], True


def inject_related(html):
    """Add a contextual YOSUR MARINE card inside the related-tools grid.

    The card goes after the LAST <a> of that section so it lands inside the
    grid container rather than beside it. Pages without the section are left
    untouched.
    """
    if RELATED_GUARD in html:
        return html, False

    start = html.find(RELATED_HEADING)
    if start < 0:
        return html, False

    end = html.find("</section>", start)
    if end < 0:
        return html, False

    seg = html[start:end]

    # Widen the 3-column grid so the 4th card has a slot on desktop.
    seg = seg.replace(GRID_OLD, GRID_NEW, 1)

    anchor = seg.rfind("</a>")
    if anchor < 0:
        return html, False

    cut = anchor + len("</a>")
    seg = seg[:cut] + "\n        " + RELATED_CARD + seg[cut:]

    return html[:start] + seg + html[end:], True


def main():
    if not TARGET.exists():
        print("index.html not found")
        return 1

    html = TARGET.read_text(encoding="utf-8")
    changed = False

    for name, fn in (
        ("meta", fix_meta),
        ("footer", inject_footer),
        ("related", inject_related),
    ):
        html, did = fn(html)
        print("%-8s %s" % (name, "applied" if did else "no change"))
        changed = changed or did

    if changed:
        TARGET.write_text(html, encoding="utf-8")
        print("index.html updated")
    else:
        print("nothing to do")
    return 0


if __name__ == "__main__":
    sys.exit(main())
