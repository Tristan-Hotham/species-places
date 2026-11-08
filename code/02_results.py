"""Step 2: every number quoted anywhere, into data/results.json, plus data/site.json for the map."""
import csv, collections
import numpy as np
import pandas as pd
from common import *

B = jload(f"{WORK}/build.json")
GN = dict(B["groups"])
d = pd.read_csv(f"{DATA}/taxa_named.csv", keep_default_na=False, na_values=[""], dtype={"gbif": str, "place_iso2": str, "place_here": str})
for c in ("note", "place_iso2", "place_here", "top_countries", "group", "box", "place_type", "class", "family", "key_via", "gbif"):
    d[c] = d[c].fillna("")
e = pd.read_csv(f"{DATA}/epithet_taxa_sample.csv", keep_default_na=False, na_values=[""], dtype={"gbif": str, "iso2": str})
e["iso2"] = e["iso2"].fillna(""); e["top_countries"] = e["top_countries"].fillna("")
EP = pd.read_csv(f"{DATA}/epithet_places.csv", keep_default_na=False, na_values=[""], dtype={"iso2": str})
R = {"min_n": MIN_N}

# ---------------- part 1
R["named"] = {"wikidata_items": len(d), "duplicates": int((d.verdict == "duplicate").sum()), "notplace": int((d.verdict == "notplace").sum()),
              "excluded": int((d.verdict == "excluded").sum()), "synonym_absent": int((d.verdict == "synonym").sum())}
d0 = d
d = d[~d.verdict.isin(["duplicate", "notplace"])].copy()
R["named"].update({"taxa": len(d), "species": int((d["rank"] == "species").sum()), "subspecies": int((d["rank"] == "subspecies").sum()),
              "with_key": int((d.gbif != "").sum()), "key_by_match": int((d.key_via == "gbif name match").sum()),
              "with_records": int((d.n > 0).sum()), "no_country": int((d.verdict == "nocountry").sum()), "few": int((d.verdict == "few").sum())})
a = d[d.verdict.isin(["yes", "no"])].copy()
life = a[a.group != "microbes"]
R["named"]["assessed"] = len(a)
R["named"]["assessed_life"] = len(life)
R["named"]["microbes_assessed"] = int((a.group == "microbes").sum())
R["named"]["yes_pc"] = 100 * (life.verdict == "yes").mean()
R["named"]["no"] = int((life.verdict == "no").sum())
R["named"]["majority_pc"] = 100 * (life.share_in >= 50).mean()
R["named"]["all_pc"] = 100 * (life.share_in >= 99.95).mean()
R["named"]["microbe_yes_pc"] = 100 * (a[a.group == "microbes"].verdict == "yes").mean()
R["named"]["median_n"] = float(life.n.median())
big = life[life.n >= 100]
R["named"]["n100"] = len(big); R["named"]["n100_yes_pc"] = 100 * (big.verdict == "yes").mean(); R["named"]["n100_majority_pc"] = 100 * (big.share_in >= 50).mean()
R["named"]["no_box0"] = int((life[life.verdict == "no"].box_km == 0).sum())
R["named"]["no_median_box_km"] = float(life[life.verdict == "no"].box_km.median())
R["named"]["no_box1000"] = int((life[life.verdict == "no"].box_km >= 1000).sum())
grp = {}
for g, x in a.groupby("group"):
    grp[g] = {"name": GN[g], "n": len(x), "yes_pc": 100 * (x.verdict == "yes").mean(), "majority_pc": 100 * (x.share_in >= 50).mean(),
              "no": int((x.verdict == "no").sum())}
R["groups"] = grp
# by kind of namesake place
def kind(t):
    t = t.lower()
    if re.search(r"sovereign state|country|republic|kingdom", t): return "country"
    if re.search(r"island|archipelago|atoll", t): return "island"
    if re.search(r"mountain|massif|peak|volcano|hill", t): return "mountain"
    if re.search(r"river|lake|stream|reservoir|bay|sea|strait", t): return "water"
    if re.search(r"city|town|village|settlement|municipal|county|prefecture|province|state|region|district", t): return "region or settlement"
    return "other"
life = life.assign(kind=life.place_type.map(kind))
R["kinds"] = {k: {"n": len(x), "yes_pc": 100 * (x.verdict == "yes").mean(), "majority_pc": 100 * (x.share_in >= 50).mean()} for k, x in life.groupby("kind")}

# the misnamed: featured examples, chosen by hand from the "no" list and checked (notes in words on the page)
FEAT = ["Lodoicea maldivica", "Pitta guajana", "Ranodon sibiricus", "Dracunculus medinensis", "Elephas melitensis",
        "Verbascum adrianopolitanum", "Bradgatia linfordensis", "Suillellus caucasicus", "Aspergillus egyptiacus"]
feat = {}
for nm in FEAT:
    r = d[d.name == nm]
    assert len(r) == 1, nm
    r = r.iloc[0]
    assert r.verdict == "no", (nm, r.verdict)
    tc = [x.split(":") for x in r.top_countries.split()]
    feat[nm] = {"qid": r.qid, "name": nm, "place": r.place, "iso2": r.place_iso2, "n": int(r.n), "group": r.group,
                "top": [[k, int(v), B["isoname"].get(k, k)] for k, v in tc], "box_km": float(r.box_km)}
R["feat"] = feat
nolist = life[life.verdict == "no"].sort_values("n", ascending=False)
R["no_top"] = [{"name": r["name"], "place": r.place, "n": int(r.n), "top": r.top_countries, "group": r.group} for _, r in nolist.head(25).iterrows()]

# ---------------- part 2: epithets
ea = e[e.verdict.isin(["yes", "no"])]
R["ep"] = {"stems": int(sum(len(s.split()) for s in EP.stems)), "places": len(EP), "taxa_wikidata": int(EP.taxa_wikidata.sum()),
           "taxa_with_key": int(EP.taxa_with_key.sum()), "sampled": len(e), "with_records": int((e.n > 0).sum()), "assessed": len(ea),
           "regions": int(EP.region.sum())}
br = ea[ea.british == 1]; nb = ea[ea.british == 0]
R["ep"]["brit_sampled"] = int((e.british == 1).sum()); R["ep"]["brit_assessed"] = len(br)
R["ep"]["brit_yes_pc"] = 100 * (br.verdict == "yes").mean(); R["ep"]["brit_no"] = int((br.verdict == "no").sum())
R["ep"]["nonbrit_raw_yes_pc"] = 100 * (nb.verdict == "yes").mean()
# weighted estimate for the non-British stems. The sample was drawn per adjective (up to 40 taxa with a GBIF key each),
# so each sampled taxon stands for (taxa with a key for its adjective) / (taxa sampled for it): an inverse-probability weight.
ETW = [l.rstrip("\n").split("\t") for l in open(f"{RAW}/epithet_taxa.tsv", encoding="utf-8")][1:]
stemkey = collections.Counter(nm.split()[-1] for q, nm, key, rk in ETW if key)
stemsamp = e.groupby("epithet").size()
num = den = 0
for ep, x in nb.groupby("epithet"):
    wt = stemkey[ep] / stemsamp[ep]
    num += wt * (x.verdict == "yes").sum(); den += wt * len(x)
R["ep"]["nonbrit_weighted_yes_pc"] = 100 * num / den
R["ep"]["max_per_stem"] = int(stemsamp[e[e.british == 0].epithet.unique()].max())
brit = {}
for pl, x in br.groupby("place"):
    brit[pl] = {"n": len(x), "yes": int((x.verdict == "yes").sum()), "yes_pc": 100 * (x.verdict == "yes").mean(),
                "taxa_wikidata": int(EP.set_index("place").loc[pl, "taxa_wikidata"])}
R["ep"]["brit"] = brit
R["ep"]["brit_no_top"] = [{"name": r["name"], "n": int(r.n), "top": r.top_countries, "place": r.place} for _, r in br[br.verdict == "no"].sort_values("n", ascending=False).head(12).iterrows()]
pl = EP[(EP.assessed >= 15) & (EP.british == 0)].sort_values("share_yes")
R["ep"]["places_low"] = [{"place": r.place, "share": float(r.share_yes), "assessed": int(r.assessed), "region": int(r.region)} for _, r in pl.head(8).iterrows()]
R["ep"]["places_high"] = [{"place": r.place, "share": float(r.share_yes), "assessed": int(r.assessed)} for _, r in pl.tail(8).iloc[::-1].iterrows()]
R["ep"]["places_15"] = len(pl)
R["ep"]["places_15_all"] = int((pl.share_yes >= 99.95).sum())
for nm in ("Potentilla anglica subsp. anglica", "Robertus scoticus", "Chrysoblephus anglicus", "Urophyllum britannicum"):
    r = e[e.name == nm]; assert len(r) == 1 and r.iloc[0].verdict == "no", nm
    R["ep"].setdefault("brit_feat", {})[nm.split()[0].lower()] = {"name": nm, "n": int(r.iloc[0].n), "top": r.iloc[0].top_countries}

# ---------------- checks behind words
assert R["named"]["yes_pc"] > 90 and R["named"]["majority_pc"] > 75
assert feat["Lodoicea maldivica"]["top"][0][0] == "SC" and feat["Lodoicea maldivica"]["top"][0][1] > 0.9 * feat["Lodoicea maldivica"]["n"]
assert {t[0] for t in feat["Pitta guajana"]["top"][:2]} == {"ID", "MY"}
assert {t[0] for t in feat["Ranodon sibiricus"]["top"]} <= {"KZ", "CN"}
assert feat["Elephas melitensis"]["top"] == [["IT", feat["Elephas melitensis"]["n"], "Italy"]]
assert {t[0] for t in feat["Verbascum adrianopolitanum"]["top"][:2]} == {"GR", "BG"}
assert feat["Bradgatia linfordensis"]["top"][0][0] == "CA" and feat["Aspergillus egyptiacus"]["top"][0][0] == "AU"
assert feat["Suillellus caucasicus"]["top"][0][0] == "FR"
# the hand review of the 53 cases first reported as absent (data/review_absent.tsv)
RV = pd.read_csv(f"{DATA}/review_absent.tsv", sep="\t", keep_default_na=False)
R["review"] = {"n": len(RV), "by": {k: int(v) for k, v in RV.category.value_counts().items()},
               "errors": int((~RV.category.isin(["misnomer", "not recorded"])).sum())}
R["review"]["kept"] = int(RV.category.isin(["misnomer", "not recorded"]).sum())
R["review"]["misnomer"] = int((RV.category == "misnomer").sum())
R["review"]["error_pc"] = 100 * R["review"]["errors"] / R["review"]["n"]
R["review"]["yes_wrong_links"] = int(sum(1 for r in d0.itertuples() if r.verdict == "excluded" and "hand check of names" in r.note))
R["review"]["spot_n"] = 30; R["review"]["spot_wrong"] = 3
assert R["review"]["kept"] == R["named"]["no"], (R["review"]["kept"], R["named"]["no"])
assert R["ep"]["brit_yes_pc"] < R["ep"]["nonbrit_raw_yes_pc"]
jsave(R, f"{DATA}/results.json", indent=1)

# ---------------- page data
iso = B["isoname"]
pts = []
for _, r in d[d.verdict != "nokey"].iterrows() if False else d.iterrows():
    v = r.verdict
    pts.append([r.qid, r["name"], round(float(r.place_lon), 3), round(float(r.place_lat), 3), r.place, r.place_qid.split("; ")[0], r.place_iso2,
                v, r.group, int(r.n) if r.n == r.n else -1, r.top_countries, [float(x) for x in r.box.split()] if r.box else None,
                float(r.share_in) if r.share_in == r.share_in else None, r.gbif, r["class"], r.family, r.note])
eps = [[r.place, r.lon, r.lat, r.iso2, int(r.british), int(r.region), r.stems, int(r.taxa_wikidata), int(r.sampled), int(r.assessed), int(r["yes"]),
        float(r.share_yes) if r.share_yes == r.share_yes else None] for _, r in EP.iterrows()]
ex = {}
for _, r in e[e.verdict.isin(["yes", "no"])].iterrows():
    ex.setdefault(r.place, []).append([r["name"], r.gbif, int(r.n), int(r.in_n), r.top_countries])
for k in ex:
    ex[k].sort(key=lambda t: (t[3] > 0, -t[2]))
    ex[k] = ex[k][:30]
jsave({"fields": ["qid", "name", "lon", "lat", "place", "pq", "iso", "v", "g", "n", "top", "box", "share", "gbif", "class", "family", "note"],
       "pts": pts, "groups": B["groups"], "iso": iso, "ep_fields": ["place", "lon", "lat", "iso", "brit", "region", "stems", "wd", "sampled", "assessed", "yes", "share"],
       "ep": eps, "ex": ex}, f"{DATA}/site.json")
print(json.dumps({k: R[k] for k in ("named", "ep")}, indent=1, ensure_ascii=False)[:5000])
print(json.dumps(R["groups"], indent=0)[:1500]); print(R["kinds"])
print(os.path.getsize(f"{DATA}/site.json") // 1024, "KB site.json")
