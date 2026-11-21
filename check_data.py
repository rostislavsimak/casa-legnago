"""Controlla data.json prima della pubblicazione. Uso: python3 check_data.py"""
import json, sys, re
from datetime import datetime

REQ = ["id", "title", "zone", "price", "sqm", "bedrooms", "bathrooms", "garage",
       "storage", "energy", "driveMin", "firstSeen", "note", "sources"]
UK_REQ = ["title", "zone", "type", "note"]
errors, warnings = [], []
try:
    d = json.load(open("data.json", encoding="utf-8"))
except Exception as e:
    print("ERRORE: data.json non e' JSON valido:", e); sys.exit(1)

def iso(v):
    try:
        datetime.fromisoformat(str(v)); return True
    except Exception:
        return False

if not iso(d.get("updated")):
    errors.append("'updated' mancante o non in formato ISO")

ls = d.get("listings")
if not isinstance(ls, list) or not ls:
    errors.append("'listings' vuoto o mancante"); ls = []
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
    uk = l.get("uk")
    if not isinstance(uk, dict):
        errors.append(f"{tag}: manca la traduzione ucraina 'uk'")
    else:
        for k in UK_REQ:
            if not uk.get(k):
                errors.append(f"{tag}: manca uk.{k}")
        if l.get("questions") and len(uk.get("questions") or []) != len(l["questions"]):
            errors.append(f"{tag}: uk.questions deve avere lo stesso numero di domande dell'italiano")
    if l.get("published") is not None and not iso(l.get("published")):
        errors.append(f"{tag}: published deve essere una data ISO o null")
    if "questions" in l and not isinstance(l["questions"], list):
        errors.append(f"{tag}: questions deve essere una lista")
    ph = l.get("priceHistory", [])
    if not isinstance(ph, list) or any(not isinstance(p, dict) or not isinstance(p.get("price"), (int, float)) or not iso(p.get("date")) for p in ph):
        errors.append(f"{tag}: priceHistory non valido (lista di {{date, price}})")

aps = d.get("appointments", [])
if not isinstance(aps, list):
    errors.append("'appointments' deve essere una lista"); aps = []
for j, a in enumerate(aps):
    tag = a.get("id", f"appuntamento #{j}")
    if not iso(a.get("when")) or "+" not in str(a.get("when")):
        errors.append(f"{tag}: 'when' deve essere data e ora ISO con fuso (es. 2026-11-25T17:00:00+01:00)")
    if not a.get("title"):
        errors.append(f"{tag}: manca title")
    if a.get("outcome") not in (None, "liked", "discarded"):
        errors.append(f"{tag}: outcome deve essere null, liked o discarded")
    if not isinstance(a.get("uk"), dict) or not a["uk"].get("title"):
        errors.append(f"{tag}: manca uk.title")
    if a.get("listingId") not in ids and a.get("outcome") is None:
        warnings.append(f"{tag}: la casa {a.get('listingId')} non e' tra gli annunci attivi")

for w in warnings:
    print("AVVISO:", w)
if errors:
    print("ERRORI:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: {len(ls)} annunci, {len(aps)} appuntamenti, aggiornato {d['updated']}")
