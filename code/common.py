"""Shared paths, constants and helpers for the species-places study ("Named for a place, living somewhere else").

Raw inputs (read in place, never modified):
  NAMED  /home/claude/newdata/raw_new8/species_named_places.tsv
         Wikidata (CC0) query result: taxa with P138 "named after" a place that has coordinates; columns ?t (taxon item),
         ?name, ?rank, ?gbif (P846 GBIF taxon key), ?n (namesake item), ?nl (label), ?ncoord (WKT point), ?nc and ?ncl
         (country of the namesake), ?ntypel (its type), ?parentname, ?kingdomname (empty), ?sl (sitelinks). One row per
         combination of types and countries.
  RAW/gbif_ranges_full.json   GBIF API, fetched for this study: {"R": {key: {n, c: {ISO2: count}, b: [minLat, maxLat,
         minLng, maxLng, total], tax: {...}}}, "M": {name: species/match result}} for the taxon keys in NAMED and exact
         name matches for taxa without a key. n and c: /v1/occurrence/search with hasCoordinate=true,
         hasGeospatialIssue=false, occurrenceStatus=PRESENT; b: /v2/map/occurrence/density/capabilities; tax: /v1/species.
  data/epithet_stems.tsv     203 Latin place adjectives (anglica, scotica, japonica...) with the place and an ISO2 code.
  RAW/epithet_taxa.tsv       all 62,188 Wikidata species and subspecies whose last word is one of those stems (CC0).
  RAW/epithet_gbif_countries.json   GBIF country facets for a sample: every British-stem taxon with a GBIF key, and up
         to 40 at random per other stem.
  GEO    /home/claude/newdata/raw/geo/ne_10m_admin_0_countries.geojson, ne_50m_land.geojson (Natural Earth, public domain)
GBIF occurrence data are published under CC0, CC BY or CC BY-NC by their datasets; this study redistributes only
counts aggregated by country and bounding boxes, which GBIF's terms allow with citation.
"""
import json, gzip, os, re, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMED = os.environ.get("SP_NAMED", "/home/claude/newdata/raw_new8/species_named_places.tsv")
RAW = os.path.join(ROOT, "data", "raw")
GEO = os.environ.get("SP_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("SP_FONTS", "/home/claude/ref/fonts")
INK = os.environ.get("SP_INK", "/home/claude/studies/ink-map")
INKFONTS = os.path.join(INK, "fonts", "ttf")
DATA = os.path.join(ROOT, "data")
IMG = os.path.join(ROOT, "img")
WORK = os.environ.get("SP_WORK", "/home/claude/work/new8/species-places/work")
for d in (DATA, IMG, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "species-places"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
BYLINE = "Dr Tristan Hotham · Independent researcher · 2026"
MIN_N = 5        # a taxon is assessed when GBIF holds at least this many usable occurrence records for it


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    """Remove em and en dashes and double hyphens from text (house style)."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def nonan(v):
    if isinstance(v, float) and v != v:
        return None
    if isinstance(v, list):
        return [nonan(x) for x in v]
    if isinstance(v, dict):
        return {k: nonan(x) for k, x in v.items()}
    return v


def jsave(obj, path, indent=None):
    obj = nonan(obj)
    if os.path.abspath(path).startswith(DATA):
        obj = dash(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, allow_nan=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "hm": return hm(v)
    raise ValueError(f)


def hm(minutes):
    """minutes as 'H h MM min' style words: '6 h 49 min', '0 min'"""
    m = int(round(float(minutes)))
    h, mm = divmod(m, 60)
    return f"{h} h {mm:02d} min" if h else f"{mm} min"


def gc_km(lat1, lon1, lat2, lon2):
    import numpy as np
    p1, p2, l1, l2 = map(np.radians, (lat1, lat2, lon1, lon2))
    return 6371.0 * 2 * np.arcsin(np.sqrt(np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin((l2 - l1) / 2) ** 2))
