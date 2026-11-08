"""Step 1: one row per taxon named after a place, with its GBIF record and the test: does it live there?
Outputs: data/taxa_named.csv, data/epithet_taxa_sample.csv, data/epithet_places.csv, WORK/build.json."""
import csv, collections
import numpy as np
from common import *

# ---------------- countries: Wikidata labels and Natural Earth names to ISO2
NE = jload(f"{GEO}/ne_10m_admin_0_countries.geojson")["features"]
ISO = {}
ISONAME = {}
CENT = {}
from shapely.geometry import shape
for f in NE:
    p = f["properties"]; a2 = p["ISO_A2_EH"] if p["ISO_A2_EH"] not in ("-99", None) else p["ISO_A2"]
    if a2 in ("-99", None): continue
    for k in ("NAME", "NAME_LONG", "ADMIN", "FORMAL_EN", "NAME_SORT", "GEOUNIT", "SUBUNIT", "BRK_NAME"):
        if p.get(k): ISO.setdefault(p[k].lower(), a2)
    ISONAME.setdefault(a2, p["NAME"])
    g = shape(f["geometry"]); pt = g.representative_point()
    if a2 not in CENT or g.area > CENT[a2][2]:
        CENT[a2] = (pt.x, pt.y, g.area)
ISO.update({"people's republic of china": "CN", "united states": "US", "kingdom of the netherlands": "NL", "russia": "RU",
            "south korea": "KR", "north korea": "KP", "czech republic": "CZ", "czechia": "CZ", "ivory coast": "CI",
            "democratic republic of the congo": "CD", "republic of the congo": "CG", "taiwan": "TW", "vietnam": "VN",
            "laos": "LA", "the gambia": "GM", "the bahamas": "BS", "east timor": "TL", "timor-leste": "TL",
            "eswatini": "SZ", "cape verde": "CV", "federated states of micronesia": "FM", "kingdom of denmark": "DK",
            "state of palestine": "PS", "sahrawi arab democratic republic": "EH", "north macedonia": "MK",
            "kingdom of the netherlands": "NL", "georgia": "GE", "turkey": "TR", "brunei": "BN", "syria": "SY",
            "iran": "IR", "bolivia": "BO", "venezuela": "VE", "tanzania": "TZ", "moldova": "MD", "são tomé and príncipe": "ST",
            "hong kong": "HK", "macau": "MO", "new caledonia": "NC", "french polynesia": "PF", "réunion": "RE",
            "greenland": "GL", "puerto rico": "PR", "falkland islands": "FK", "faroe islands": "FO"})
ISO.update({"siam": "TH", "tokugawa shogunate": "JP", "empire of japan": "JP", "french indochina": "VN", "union of south africa": "ZA",
            "united kingdom of great britain and ireland": "GB", "joseon": "KR", "korean empire": "KR"})
ISONAME.update({"GF": "French Guiana", "GP": "Guadeloupe", "MQ": "Martinique", "RE": "Réunion", "YT": "Mayotte", "US": "United States", "CN": "China", "GB": "United Kingdom", "KR": "South Korea", "RU": "Russia",
                "CD": "DR Congo", "CG": "Congo", "TW": "Taiwan", "CZ": "Czechia", "KP": "North Korea"})


from shapely.strtree import STRtree
from shapely.geometry import Point
NEG = [shape(f["geometry"]) for f in NE]
NEA2 = [(f["properties"]["ISO_A2_EH"] if f["properties"]["ISO_A2_EH"] not in ("-99", None) else f["properties"]["ISO_A2"]) for f in NE]
NETREE = STRtree(NEG)


def where(lon, lat):
    """ISO2 of the country (or territory, as GBIF codes it) that a point lies in today, or None at sea"""
    pt = Point(lon, lat)
    for j in NETREE.query(pt):
        if NEG[j].contains(pt) and NEA2[j] not in ("-99", None):
            return NEA2[j]
    return None


# GBIF codes overseas territories apart from their country; Natural Earth and Wikidata often fold them in
DEPEND = {"FR": "GF GP MQ RE YT NC PF PM WF BL MF TF", "GB": "SH GI FK IO KY BM VG AI MS TC PN GS JE GG IM",
          "DK": "GL FO", "NL": "AW CW SX BQ", "US": "PR GU VI AS MP UM", "CN": "HK MO", "NO": "SJ BV",
          "AU": "CX CC NF HM", "NZ": "CK NU TK", "FI": "AX", "PT": "", "ES": ""}


# ---------------- hand-checked overrides (data/overrides.tsv): region namesakes given too few countries, wrong links
CONT = collections.defaultdict(set)
for f in NE:
    p = f["properties"]; a2 = p["ISO_A2_EH"] if p["ISO_A2_EH"] not in ("-99", None) else p["ISO_A2"]
    if a2 not in ("-99", None): CONT[p["CONTINENT"]].add(a2)
OV = list(csv.DictReader(open(f"{DATA}/overrides.tsv", encoding="utf-8"), delimiter="\t"))
PLACE_OV = {o["qid"]: (CONT[o["iso2"][1:]] if o["iso2"].startswith("@") else set(o["iso2"].split())) for o in OV if o["kind"] == "place"}
TAX_OV = {o["qid"]: o["reason"] for o in OV if o["kind"] == "taxon" and o["action"] == "exclude"}
# namesakes that are ships or institutions rather than places: not tested
NOTPLACE = re.compile(r"\b(ship|vessel|shipwreck|gunboat|watercraft|research institute|university|college|museum|library|"
                      r"educational institution|organization|public institution|school)\b", re.I)
NOTPLACE_KEEP = re.compile(r"\b(town|city|village|cave|island|archaeological site|municipality|settlement)\b", re.I)
SYN = {"SYNONYM", "HOMOTYPIC_SYNONYM", "HETEROTYPIC_SYNONYM", "PROPARTE_SYNONYM"}


def notplace(types):
    ts = [t for t in types if t]
    return bool(ts) and any(NOTPLACE.search(t) for t in ts) and not any(NOTPLACE_KEEP.search(t) for t in ts)


def lit(v):
    v = v.strip()
    m = re.match(r'^"(.*)"(@[\w-]+)?$', v)
    return m.group(1) if m else v


def qid(v):
    return v.strip().strip("<>").rsplit("/", 1)[-1]


# ---------------- groups from the GBIF backbone
FISH = {"Actinopterygii", "Elasmobranchii", "Sarcopterygii", "Petromyzonti", "Myxini", "Holocephali", "Cladistia", "Teleostei"}
REPT = {"Squamata", "Testudines", "Crocodylia", "Reptilia", "Rhynchocephalia"}
GROUPS = [("plants", "Plants"), ("fungi", "Fungi and lichens"), ("insects", "Insects"), ("arachnids", "Spiders, mites and scorpions"),
          ("inverts", "Other invertebrates"), ("fish", "Fish"), ("amphibians", "Amphibians"), ("reptiles", "Reptiles"),
          ("birds", "Birds"), ("mammals", "Mammals"), ("microbes", "Microbes, viruses and other")]


def group(t):
    k, ph, cl = t.get("kingdom"), t.get("phylum"), t.get("class")
    if k == "Plantae": return "plants"
    if k == "Fungi": return "fungi"
    if k in ("Animalia", "Metazoa"):
        if cl == "Insecta": return "insects"
        if cl == "Arachnida": return "arachnids"
        if cl in FISH: return "fish"
        if cl == "Amphibia": return "amphibians"
        if cl in REPT: return "reptiles"
        if cl == "Aves": return "birds"
        if cl == "Mammalia": return "mammals"
        if ph == "Chordata": return "fish" if cl is None else "inverts"
        return "inverts"
    return "microbes"


def box_km(lon, lat, b):
    """great-circle km from a point to the nearest point of a lat/lon box [minLat, maxLat, minLng, maxLng]"""
    la = min(max(lat, b[0]), b[1]); lo = min(max(lon, b[2]), b[3])
    return float(gc_km(lat, lon, la, lo)), (lo, la)


G = jload(f"{RAW}/gbif_ranges_full.json")
GR, GM = G["R"], G["M"]

# ---------------- part 1: taxa named after a place in Wikidata
rows = list(csv.reader(open(NAMED, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))[1:]
T = collections.OrderedDict()
for r in rows:
    rank = lit(r[2]).lower()
    if rank not in ("species", "subspecies"): continue
    t = T.setdefault(qid(r[0]), {"qid": qid(r[0]), "name": lit(r[1]), "rank": rank, "gbif": lit(r[3]), "parent": lit(r[10]),
                                 "sl": int(lit(r[12]) or 0), "places": collections.OrderedDict()})
    m = re.match(r"POINT\(([-\d.eE]+) ([-\d.eE]+)\)", lit(r[6]))
    if not m: continue
    pq = qid(r[4])
    pl = t["places"].setdefault(pq, {"pq": pq, "pname": lit(r[5]), "lon": float(m.group(1)), "lat": float(m.group(2)), "countries": set(), "types": set()})
    if r[8]:
        c = lit(r[8]); a2 = ISO.get(c.lower())
        if a2: pl["countries"].add(a2)
        else: pl.setdefault("unk", set()).add(c)
    if r[9]: pl["types"].add(lit(r[9]))
unknown = collections.Counter(c for t in T.values() for p in t["places"].values() for c in p.get("unk", ()))
print("unmatched country labels", unknown.most_common(20))

out = []
for t in T.values():
    if not t["places"]: continue
    key = t["gbif"]; via = "wikidata"
    if not key:
        m = GM.get(t["name"])
        if m and m.get("matchType") == "EXACT" and m.get("usageKey"):
            key, via = str(m["usageKey"]), "gbif name match"
    g = GR.get(key) if key else None
    n = g["n"] if g else None
    c = g["c"] if g else {}
    tax = g["tax"] if g else {}
    pls = list(t["places"].values())
    for p in pls:
        w = where(p["lon"], p["lat"])
        p["here"] = w
        if p["pq"] in PLACE_OV: p["countries"] = set(PLACE_OV[p["pq"]])
        if w: p["countries"].add(w)          # e.g. Cayenne is in France for Wikidata and in French Guiana (GF) for GBIF
    cs = set().union(*[p["countries"] for p in pls])
    cs |= {x for a in list(cs) for x in DEPEND.get(a, "").split()}
    rec = {"qid": t["qid"], "name": t["name"], "rank": t["rank"], "gbif": key or "", "key_via": via if key else "",
           "group": group(tax) if g else "", "kingdom": tax.get("kingdom") or "", "class": tax.get("class") or "",
           "order": tax.get("order") or "", "family": tax.get("family") or "", "status": tax.get("taxonomicStatus") or "",
           "place_qid": "; ".join(p["pq"] for p in pls), "place": "; ".join(p["pname"] for p in pls),
           "place_type": "; ".join(sorted(set().union(*[p["types"] for p in pls])))[:200],
           "place_lon": pls[0]["lon"], "place_lat": pls[0]["lat"], "place_iso2": " ".join(sorted(cs)),
           "n": n if n is not None else "", "n_countries": len(c) if g else "",
           "in_country_n": sum(c.get(a, 0) for a in cs) if g else "",
           "top_countries": " ".join(f"{k}:{v}" for k, v in sorted(c.items(), key=lambda kv: -kv[1])[:6]) if g else "",
           "box": " ".join(str(v) for v in g["b"][:4]) if g and n else ""}
    rec["place_here"] = " ".join(sorted({p["here"] for p in pls if p["here"]}))
    if g and n:
        d = min(box_km(p["lon"], p["lat"], g["b"])[0] for p in pls)
        rec["box_km"] = round(d, 1)
    else:
        rec["box_km"] = ""
    rec["accepted_key"] = str(tax.get("acceptedKey") or key or "")
    rec["note"] = ""
    # the verdict
    if t["qid"] in TAX_OV: v = "excluded"; rec["note"] = TAX_OV[t["qid"]]
    elif all(notplace(p["types"]) for p in pls): v = "notplace"; rec["note"] = "namesake is a ship or an institution, not a place"
    elif not g: v = "nokey"
    elif not n: v = "norecords"
    elif not cs: v = "nocountry"
    elif rec["in_country_n"] > 0: v = "yes"
    elif n < MIN_N: v = "few"
    elif rec["status"] in SYN:
        # records under a synonym's key are only those filed under that name: they can show presence, not absence
        v = "synonym"; rec["note"] = "synonym key with no records at home; most records sit under the accepted name"
    else: v = "no"
    rec["verdict"] = v
    rec["share_in"] = round(100 * rec["in_country_n"] / n, 1) if g and n and cs else ""
    out.append(rec)
# ---------------- duplicates: Wikidata items for the same GBIF accepted taxon and the same namesake (recombinations,
# old genera). Keep the item on the accepted key if there is one (its records include the synonym's), else the most records.
dupg = collections.defaultdict(list)
for r in out:
    if r["accepted_key"] and r["verdict"] not in ("excluded", "notplace"):
        dupg[(r["accepted_key"], r["place_qid"])].append(r)
ndup = 0
for (ak, _), rs in dupg.items():
    if len(rs) < 2: continue
    keep = max(rs, key=lambda r: (r["gbif"] == ak, r["n"] if r["n"] != "" else -1))
    for r in rs:
        if r is not keep:
            r["verdict"] = "duplicate"; r["note"] = f"same GBIF accepted taxon and namesake as {keep['name']} ({keep['qid']})"; ndup += 1
print("duplicates removed", ndup)
keys = list(out[0].keys())
with open(f"{DATA}/taxa_named.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, keys); w.writeheader(); w.writerows(out)
print("taxa", len(out), collections.Counter(r["verdict"] for r in out))

# ---------------- part 2: epithet layer
ST = list(csv.DictReader(open(f"{DATA}/epithet_stems.tsv", encoding="utf-8"), delimiter="\t"))
# stems naming regions that span several countries: test against all of them
REGION = {"Caucasus": "GE AM AZ RU TR IR", "Himalaya": "NP IN BT CN PK", "Patagonia": "AR CL",
          "Arabia": "SA YE OM AE QA KW BH", "Mauretania (North Africa)": "MA DZ", "Borneo": "MY ID BN",
          "Guinea": "GN GW SL LR CI GH TG BJ NG CM GQ GA", "Congo": "CD CG AO", "Korea": "KR KP",
          "Tibet": "CN IN NP BT", "Siberia": "RU", "India": "IN PK BD LK NP BT", "China": "CN TW HK MO"}
# stems dropped as ambiguous: argentina is also Latin for silvery
DROP = {"argentina"}
BRIT = {"England", "Scotland", "Wales", "Britain", "London", "Cornwall", "Ireland"}
# where to draw each place on the map (lon, lat): subnational places by hand, countries from Natural Earth
PLACEXY = {"England": (-1.5, 52.6), "Scotland": (-4.2, 56.8), "Wales": (-3.7, 52.3), "Britain": (-2.3, 54.3), "London": (-0.12, 51.5),
           "Cornwall": (-4.9, 50.4), "Ireland": (-8.0, 53.3), "Crete": (24.9, 35.2), "Sicily": (14.1, 37.5), "Sardinia": (9.0, 40.1),
           "Corsica": (9.1, 42.1), "Balearic Islands": (2.9, 39.6), "Canary Islands": (-15.6, 28.3), "Madeira": (-16.95, 32.75),
           "Azores": (-27.5, 38.6), "Arabia": (46.0, 22.0), "Java": (110.0, -7.3), "Sumatra": (101.5, 0.0), "Borneo": (114.0, 1.0),
           "Cape (South Africa)": (19.5, -33.6), "Natal (South Africa)": (30.6, -29.2), "Mauretania (North Africa)": (-2.0, 33.5),
           "Virginia": (-78.6, 37.5), "Carolina": (-80.0, 34.8), "Florida": (-81.6, 28.3), "California": (-119.5, 37.2),
           "Texas": (-99.3, 31.3), "Patagonia": (-69.0, -45.0), "Tasmania": (146.6, -42.0), "Hawaii": (-155.5, 19.6),
           "Caucasus": (44.0, 42.7), "Siberia": (100.0, 62.0), "Tibet": (88.0, 31.5), "Himalaya": (84.0, 28.6),
           "Guinea": (-2.0, 7.5), "Congo": (21.0, -2.5), "Persia (Iran)": (54.0, 32.5), "Abyssinia (Ethiopia)": (39.5, 9.0)}
stem = {s["stem"]: s for s in ST}
EG = jload(f"{RAW}/epithet_gbif_countries.json")
ET = [l.rstrip("\n").split("\t") for l in open(f"{RAW}/epithet_taxa.tsv", encoding="utf-8")][1:]
pop = collections.Counter(); popkey = collections.Counter(); seenkey = set()
erows = []
for q, nm, key, rk in ET:
    ep = nm.split()[-1]
    s = stem.get(ep)
    if not s or ep in DROP: continue
    place = s["place"]
    pop[place] += 1
    if key: popkey[place] += 1
    g = EG.get(key) if key else None
    if g is None: continue
    if key in seenkey: continue          # two Wikidata items (e.g. arabica / arabicum spellings) on one GBIF key: count once
    seenkey.add(key)
    isos = (REGION.get(place) or s["iso2"]).split()
    n = g["n"]; cin = sum(g["c"].get(a, 0) for a in isos)
    erows.append({"qid": q, "name": nm, "rank": rk, "gbif": key, "epithet": ep, "place": place, "iso2": " ".join(isos),
                  "british": int(place in BRIT), "n": n, "in_n": cin,
                  "top_countries": " ".join(f"{k}:{v}" for k, v in sorted(g["c"].items(), key=lambda kv: -kv[1])[:6]),
                  "verdict": "norecords" if not n else "yes" if cin > 0 else "few" if n < MIN_N else "no"})
with open(f"{DATA}/epithet_taxa_sample.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, list(erows[0].keys())); w.writeheader(); w.writerows(erows)
# per place
P = []
for place in sorted(pop):
    rs = [r for r in erows if r["place"] == place]
    ass = [r for r in rs if r["verdict"] in ("yes", "no")]
    isos = (REGION.get(place) or next(s["iso2"] for s in ST if s["place"] == place)).split()
    xy = PLACEXY.get(place) or CENT.get(isos[0], (0, 0))[:2]
    P.append({"place": place, "iso2": " ".join(isos), "region": int(place in REGION and len(isos) > 1), "british": int(place in BRIT),
              "stems": " ".join(s["stem"] for s in ST if s["place"] == place and s["stem"] not in DROP), "taxa_wikidata": pop[place], "taxa_with_key": popkey[place],
              "sampled": len(rs), "with_records": sum(1 for r in rs if r["n"]), "assessed": len(ass), "yes": sum(1 for r in ass if r["verdict"] == "yes"),
              "share_yes": round(100 * sum(1 for r in ass if r["verdict"] == "yes") / len(ass), 1) if ass else "",
              "lon": round(xy[0], 3), "lat": round(xy[1], 3)})
with open(f"{DATA}/epithet_places.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, list(P[0].keys())); w.writeheader(); w.writerows(P)
jsave({"isoname": ISONAME, "cent": {k: [round(v[0], 2), round(v[1], 2)] for k, v in CENT.items()}, "groups": GROUPS,
       "region": REGION, "brit": sorted(BRIT)}, f"{WORK}/build.json")
print("epithet sample", len(erows), collections.Counter(r["verdict"] for r in erows), "places", len(P))
