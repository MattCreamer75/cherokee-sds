#!/usr/bin/env python3
"""
build_index.py  --  Cherokee SDS App index builder
---------------------------------------------------
Scans the /sds folder, finds every Safety Data Sheet PDF, and writes
sds-index.json next to index.html. The web app reads that JSON to power search.

You normally never run this by hand: the GitHub Action runs it automatically
every time you add or remove a PDF. But you CAN run it locally:

    python tools/build_index.py

Records per SDS: product, manufacturer, category, revision (best-effort),
path, and has_text (False = scanned image, searchable by name only).
It is safe to re-run anytime. It never changes your PDFs.
"""

import os
import re
import json
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SDS_DIR = os.path.join(ROOT, "sds")
OUTPUT = os.path.join(ROOT, "sds-index.json")

# PDFs whose path contains any of these (case-insensitive) are NOT SDS -> skipped.
EXCLUDE_FOLDERS = ["training verification", "print and sign", "signed -"]

try:
    import pdfplumber
    HAVE_PDF = True
except Exception:
    HAVE_PDF = False

DATE_LABELS = [r"Revision date", r"Date of (?:issue|revision)",
               r"Issue date", r"Version date", r"Revision"]

DATE_TOKEN = (r"(\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}"
              r"|\d{4}[/.\-]\d{1,2}[/.\-]\d{1,2}"
              r"|[A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4}"
              r"|\d{1,2}[-\s][A-Z][a-z]+[-\s]\d{4})")


def clean_product_name(filename):
    name = os.path.splitext(filename)[0].strip()
    name = re.sub(r"\s*\(\d+\)\s*$", "", name)   # drop trailing "(34)"
    return name.strip()


def manufacturer_from_name(filename):
    matches = re.findall(r"\(([^)]+)\)", filename)
    if matches:
        cand = matches[-1].strip()
        if not cand.isdigit():
            return cand
    return None


def extract_from_pdf(path):
    if not HAVE_PDF:
        return (None, None, None)
    try:
        with pdfplumber.open(path) as pdf:
            text = "\n".join((p.extract_text() or "") for p in pdf.pages[:2])
    except Exception:
        return (None, None, False)
    if not text.strip():
        return (None, None, False)   # scanned image

    rev = None
    for label in DATE_LABELS:
        m = re.search(label + r"[:\s]{0,4}" + DATE_TOKEN, text, re.IGNORECASE)
        if m:
            rev = m.group(1).strip()
            break

    manu = None
    for pat in [r"Company name[:\s]+([A-Z][A-Za-z0-9&,\.\- ]{2,50})",
                r"Manufacturer[:\s]+([A-Z][A-Za-z0-9&,\.\- ]{2,50})"]:
        m = re.search(pat, text)
        if m:
            manu = m.group(1).strip().rstrip(",.")
            break
    return (manu, rev, True)


def is_excluded(rel_path):
    low = rel_path.lower()
    return any(bad in low for bad in EXCLUDE_FOLDERS)


def main():
    records = []
    if not os.path.isdir(SDS_DIR):
        print("!! No 'sds' folder found at", SDS_DIR)
        return

    for dirpath, _dirs, files in os.walk(SDS_DIR):
        for f in files:
            if not f.lower().endswith(".pdf"):
                continue
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
            if is_excluded(rel):
                continue
            inside = os.path.relpath(full, SDS_DIR).replace(os.sep, "/").split("/")
            category = inside[0] if len(inside) > 1 else "Uncategorized"
            manu_name = manufacturer_from_name(f)
            manu_pdf, rev, has_text = extract_from_pdf(full)
            records.append({
                "product": clean_product_name(f),
                "manufacturer": manu_name or manu_pdf or "",
                "category": category,
                "revision": rev or "",
                "path": rel,
                "has_text": bool(has_text),
            })

    records.sort(key=lambda r: (r["category"].lower(), r["product"].lower()))
    out = {"generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
           "count": len(records), "items": records}
    with open(OUTPUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    cats = sorted({r["category"] for r in records})
    print("Indexed %d SDS across %d categories: %s" % (len(records), len(cats), ", ".join(cats)))
    print("Wrote", OUTPUT)


if __name__ == "__main__":
    main()
