#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checks that index.html shows the "unofficial" line (rule 3 in CLAUDE.md) as visible text, after the main heading.
Text inside comments, <script>, <style>, <template>, or an element marked hidden does not count.

    python3 tests/test_unofficial_line.py [path to html]
"""
import sys
from html.parser import HTMLParser

LINE = "כלי לא רשמי. אינו קשור למשרד הבריאות ואינו מחליף את המידע הרשמי."
SKIP = {"script", "style", "template", "noscript"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Visible(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []  # one bool per open element: is it hidden
        self.text = []
        self.h1_at = None

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        a = dict(attrs)
        style = (a.get("style") or "").replace(" ", "").lower()
        hidden = (tag in SKIP or "hidden" in a or a.get("aria-hidden") == "true"
                  or "display:none" in style or "visibility:hidden" in style)
        self.stack.append(hidden)
        if tag == "h1" and self.h1_at is None and not any(self.stack):
            self.h1_at = len("".join(self.text))

    def handle_endtag(self, tag):
        if tag in VOID or not self.stack:
            return
        self.stack.pop()

    def handle_data(self, data):
        if not any(self.stack):
            self.text.append(data)


def main(path="index.html"):
    with open(path, encoding="utf-8") as f:
        p = Visible()
        p.feed(f.read())
    text = " ".join("".join(p.text).split())
    at = text.find(LINE)
    if at < 0:
        print("נכשל: השורה \"לא רשמי\" לא מופיעה כטקסט גלוי ב %s" % path)
        return 1
    if p.h1_at is None:
        print("נכשל: אין כותרת ראשית (h1) ב %s" % path)
        return 1
    h1_text = " ".join("".join(p.text)[:p.h1_at].split())
    if at < len(h1_text):
        print("נכשל: השורה \"לא רשמי\" מופיעה לפני הכותרת הראשית ב %s" % path)
        return 1
    print("עבר: השורה \"לא רשמי\" גלויה ב %s" % path)
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(*sys.argv[1:2]))
