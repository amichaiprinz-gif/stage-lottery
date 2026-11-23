#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fails on any number without a source. Every data/*.csv must have the columns source_url and source_date; a row that
holds a digit in any other column needs source_url starting with https:// and source_date as YYYY-MM-DD (a real date).
Exit 0 when all is well, 1 with one line per problem otherwise.

    python3 tools/check_sources.py [repo root]
"""
import csv, datetime, glob, os, re, sys

DIGIT = re.compile(r"\d")


def check_file(path):
    problems = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        if "source_url" not in cols or "source_date" not in cols:
            return ["%s: חסרות העמודות source_url ו source_date" % path]
        for i, row in enumerate(reader, start=2):
            values = [v for k, v in row.items() if k not in ("source_url", "source_date") and isinstance(v, str)]
            if not any(DIGIT.search(v) for v in values):
                continue
            url, date = (row.get("source_url") or "").strip(), (row.get("source_date") or "").strip()
            if not url.startswith("https://") or any(c.isspace() for c in url):
                problems.append("%s שורה %d: מספר בלי קישור למקור" % (path, i))
            try:
                datetime.date.fromisoformat(date)
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
                    raise ValueError
            except ValueError:
                problems.append("%s שורה %d: מספר בלי תאריך מקור (YYYY-MM-DD)" % (path, i))
    return problems


def main(root="."):
    problems = []
    for path in sorted(glob.glob(os.path.join(root, "data", "**", "*.csv"), recursive=True)):
        problems += check_file(path)
    for p in problems:
        print(p)
    print("תקין" if not problems else "%d בעיות" % len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
