#!/usr/bin/env python3
"""
sync_from_dashboard.py  --  Pull the SDS app's product list from the Dashboard
------------------------------------------------------------------------------
The Cherokee Safety Program Dashboard is the single source of truth for SDS.
This script reads the Dashboard's SDS records and regenerates the app's
`sds-index.json` so the app shows the same products, the same 13 product
classes (categories), manufacturer, status, and GHS hazards.

WHAT IT DOES
  1. Reads every Dashboard SDS record  (_Dashboard/data/documents/*.json,
     type == "SDS" with a productClass).
  2. Figures out each product's PDF:
       - first, a known link from tools/pdf_aliases.json (the one-time
         clean-up we did for the original 53 products);
       - otherwise the record's own filePath (what the Dashboard "Add SDS"
         form saves) -- that PDF is copied into  sds/_added/  in the app;
       - otherwise the product is listed with "SDS not on file".
  3. Writes sds-index.json (what the web app reads).
  4. Prints what changed and lists any new PDF files to upload.

HOW TO RUN
    python tools/sync_from_dashboard.py
Then upload the changed files (sds-index.json + anything new in sds/_added/)
to GitHub -- or just ask Claude to "sync the SDS app" and it will push for you.

Edit DASH_ROOT below if the Dashboard ever moves.
"""

import json, glob, os, re, shutil, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
APP  = os.path.dirname(HERE)                              # the SDS-App folder
# Dashboard lives one level up from SDS-App, in the Cherokee Safety Program folder
PROGRAM = os.path.dirname(APP)
DASH_ROOT = os.path.join(PROGRAM, "_Dashboard", "data", "documents")
ALIASES   = os.path.join(HERE, "pdf_aliases.json")
INDEX_OUT = os.path.join(APP, "sds-index.json")
ADDED_DIR = os.path.join(APP, "sds", "_added")

CLASS_LABEL = {
    "gas":"Gas","wire":"Welding wire","electrode":"Stick electrode","aerosol":"Aerosol",
    "paint":"Paint / coating","solvent":"Solvent","cutting-fluid":"Cutting fluid",
    "maintenance":"Maintenance / lube","fuel":"Fuel","metal-prep":"Metal prep",
    "adhesive":"Adhesive / sealant","cleaner":"Cleaner","other":"Other",
}

def parse_ghs(s):
    out=[]
    for t in re.split(r"[,/]", str(s or "")):
        m=re.search(r"GHS\s*0?(\d)", t.upper())
        if m:
            c="GHS0"+m.group(1)
            if c not in out: out.append(c)
    return out

def win_to_local(p):
    """Convert a Windows path under the program folder to a path we can read here."""
    if not p: return ""
    tail = p.replace("\\","/").split("Cherokee Safety Program",1)[-1].lstrip("/")
    return os.path.join(PROGRAM, tail)

def load_records():
    recs=[]
    for f in glob.glob(os.path.join(DASH_ROOT,"*.json")):
        try: d=json.load(open(f,encoding="utf-8"))
        except Exception: continue
        if isinstance(d,dict) and d.get("type")=="SDS" and d.get("productClass"):
            recs.append(d)
    return recs

def main():
    aliases = json.load(open(ALIASES,encoding="utf-8")) if os.path.exists(ALIASES) else {}
    recs = load_records()
    os.makedirs(ADDED_DIR, exist_ok=True)
    new_files=[]
    items=[]
    for r in recs:
        rid=r["id"]
        rel=aliases.get(rid)          # known link from the one-time clean-up
        if rel is None:               # a product the Dashboard added later
            src=win_to_local(r.get("filePath",""))
            if r.get("filePath") and os.path.exists(src):
                base=os.path.basename(src)
                dest=os.path.join(ADDED_DIR, base)
                if not os.path.exists(dest):
                    try: shutil.copy2(src,dest); new_files.append("sds/_added/"+base)
                    except Exception: pass
                rel="sds/_added/"+base
            else:
                rel=""                # no PDF available yet
        cls=r.get("productClass","other")
        items.append({
            "id":rid,"product":r["title"],
            "category":CLASS_LABEL.get(cls,"Other"),"category_key":cls,
            "manufacturer":r.get("manufacturer") or "",
            "revision":(r.get("revision") or r.get("version") or "").strip(),
            "status":r.get("status") or "","signal":r.get("signalWord") or "",
            "ghs":parse_ghs(r.get("ghsPictograms")),"location":r.get("location") or "",
            "path":rel,"has_pdf":bool(rel),
        })
    items.sort(key=lambda x:(x["category"].lower(), x["product"].lower()))
    out={"generated":datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
         "count":len(items),
         "categories":sorted({i["category"] for i in items}),
         "items":items}
    json.dump(out, open(INDEX_OUT,"w",encoding="utf-8"), indent=2, ensure_ascii=False)

    print(f"Synced {len(items)} products in {len(out['categories'])} categories.")
    nopdf=[i['product'] for i in items if not i['has_pdf']]
    if nopdf: print(f"  {len(nopdf)} awaiting an SDS PDF: " + ", ".join(nopdf))
    if new_files:
        print("  NEW PDF files to upload:"); [print("   ",f) for f in new_files]
    else:
        print("  No new PDF files. Upload only sds-index.json.")

if __name__ == "__main__":
    main()
