"""Step 0 (needs api.gbif.org, which the build container cannot reach): fetch, for every GBIF taxon key the study needs,
the occurrence count with coordinates, the country facet, the density-map bounds and the higher taxonomy.

Usage:  python3 code/00_fetch_gbif.py data/raw/gbif_keys_needed.txt gbif_ranges_full.json
        (add --match data/raw/names_without_key.txt to also resolve names that have no GBIF key in Wikidata)
Output: {key: {"n": int, "c": [{"name": ISO2, "count": int}, ...], "b": [minLat, maxLat, minLng, maxLng, total],
               "tax": {"kingdom", "phylum", "class", "order", "family", "rank", "status", "acceptedKey", "canonicalName"}}}
Same shape as raw_new8/gbif_ranges.json, plus "tax". Resumable: keys already in the output file are skipped.
Polite: one request at a time, 0.25 s apart, retries with backoff on errors and HTTP 429/5xx.
"""
import json, os, sys, time, urllib.request, urllib.parse

API = "https://api.gbif.org"


def get(url, tries=6):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "species-places study (maps.tristanhotham.com)"}), timeout=60) as r:
                return json.load(r)
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(2 ** i)
        finally:
            time.sleep(0.25)


def one(key):
    sp = get(f"{API}/v1/species/{key}")
    q = urllib.parse.urlencode({"taxonKey": key, "hasCoordinate": "true", "hasGeospatialIssue": "false", "occurrenceStatus": "PRESENT",
                                "limit": 0, "facet": "country", "facetLimit": 300})
    oc = get(f"{API}/v1/occurrence/search?{q}")
    facets = (oc.get("facets") or [{}])[0].get("counts", []) if oc.get("facets") else []
    cap = get(f"{API}/v2/map/occurrence/density/capabilities.json?taxonKey={key}")
    b = [cap.get("minLat"), cap.get("maxLat"), cap.get("minLng"), cap.get("maxLng"), cap.get("total")]
    return {"n": oc.get("count", 0), "c": [{"name": f["name"], "count": f["count"]} for f in facets], "b": b,
            "tax": {k: sp.get(k) for k in ("kingdom", "phylum", "class", "order", "family", "rank", "taxonomicStatus", "acceptedKey", "canonicalName")}}


def main():
    keys = [l.split("\t")[0].strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip() and not l.startswith("#")]
    out_path = sys.argv[2]
    out = json.load(open(out_path)) if os.path.exists(out_path) else {}
    if "--match" in sys.argv:
        names = [l.strip() for l in open(sys.argv[sys.argv.index("--match") + 1], encoding="utf-8") if l.strip()]
        m = out.setdefault("_matched", {})
        for nm in names:
            if nm in m: continue
            r = get(f"{API}/v1/species/match?" + urllib.parse.urlencode({"name": nm, "strict": "true"}))
            m[nm] = {"usageKey": r.get("usageKey"), "matchType": r.get("matchType"), "confidence": r.get("confidence")}
            if r.get("matchType") == "EXACT" and r.get("usageKey"):
                keys.append(str(r["usageKey"]))
    for i, k in enumerate(keys):
        if k in out and "err" not in out[k]:
            continue
        try:
            out[k] = one(k)
        except Exception as e:
            out[k] = {"err": repr(e)}
        if i % 50 == 0:
            json.dump(out, open(out_path, "w")); print(i, len(keys), flush=True)
    json.dump(out, open(out_path, "w"))
    print("done", sum(1 for k, v in out.items() if k != "_matched" and "err" not in v), "ok,", sum(1 for v in out.values() if "err" in v), "errors")


if __name__ == "__main__":
    main()
