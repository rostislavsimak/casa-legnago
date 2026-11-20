"""Controlla data.json prima della pubblicazione. Uso: python3 check_data.py"""
import json, sys, re
from datetime import datetime

REQ = ["id", "title", "zone", "price", "sqm", "bedrooms", "bathrooms", "garage",
       "storage", "energy", "driveMin", "firstSeen", "note", "sources"]
errors = []
try:
    d = json.load(open("data.json", encoding="utf-8"))
except Exception as e:
    print("ERRORE: data.json non e' JSON valido:", e); sys.exit(1)

try:
    datetime.fromisoformat(d["updated"])
except Exception:
    errors.append("'updated' mancante o non in formato ISO")

ls = d.get("listings")
if not isinstance(ls, list) or not ls:
    errors.append("'listings' vuoto o mancante")
    ls = []
ids = set()
for i, l in enumerate(ls):
    tag = l.get("id", f"#{i}")
    for k in REQ:
        if k not in l:
            errors.append(f"{tag}: manca il campo {k}")
    if tag in ids:
        errors.append(f"{tag}: id duplicato")
    ids.add(tag)
    for k in ("price", "sqm", "bedrooms", "bathrooms", "driveMin"):
        v = l.get(k)
        if v is not None and not isinstance(v, (int, float)):
            errors.append(f"{tag}: {k} deve essere un numero o null")
    for k in ("garage", "storage"):
        if l.get(k) not in (True, False, None):
            errors.append(f"{tag}: {k} deve essere true/false/null")
    srcs = l.get("sources") or []
    if not srcs:
        errors.append(f"{tag}: nessun link")
    for s in srcs:
        if not re.match(r"^https://", str(s.get("url", ""))):
            errors.append(f"{tag}: link non https: {s.get('url')}")
    if l.get("status") == "removed":
        errors.append(f"{tag}: annuncio rimosso, non va pubblicato")

if errors:
    print("ERRORI:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: {len(ls)} annunci, aggiornato {d['updated']}")
