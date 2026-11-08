"""Step 7: README.md, LICENSE and reddit/post.md from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
N, E, G, F = R["named"], R["ep"], R["groups"], R["feat"]
readme = f"""# Named for a place, living somewhere else?

Do species named after a place live there? {N['taxa']:,} species and subspecies that Wikidata says are named after a place with coordinates, and {E['taxa_wikidata']:,} whose Latin epithet names a place ({E['stems']} adjectives such as anglica, scotica, hibernica, japonica), tested against where GBIF records them.

Interactive page: https://maps.tristanhotham.com/species-places/
Paper: {{https://doi.org/10.5281/zenodo.24058123}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/species-places/}}
Code and data: https://github.com/Tristan-Hotham/species-places

## Headline results

- Of {N['assessed_life']:,} plants, animals and fungi with enough GBIF records to test (at least {R['min_n']} records, or any record at home), {N['yes_pc']:.1f}% are recorded in the country of their namesake, {N['majority_pc']:.1f}% have most records there and {N['all_pc']:.1f}% have no records elsewhere. Among those with 100+ records, {N['n100_majority_pc']:.0f}% have most records at home.
- {N['no']} have at least {R['min_n']} records and none in their namesake's country, e.g. Lodoicea maldivica (coco de mer; {F['Lodoicea maldivica']['top'][0][1]} of {F['Lodoicea maldivica']['n']} records in the Seychelles), Pitta guajana / Hydrornis guajanus (Guianas; recorded in Indonesia), Ranodon sibiricus (Siberia; Kazakhstan and China). Most of the rest are gaps in GBIF (fossils, marine species, records just over a border).
- Hand check: of the {R['review']['n']} taxa first found absent from home, {R['review']['errors']} ({R['review']['error_pc']:.0f}%) were data errors (duplicates, synonym keys, regions pinned on one country, wrong links) and were removed or corrected; a random {R['review']['spot_n']} of the taxa recorded at home held {R['review']['spot_wrong']} wrong links, and a check of every assessed name whose epithet does not echo its namesake removed {R['review']['yes_wrong_links']} more. In all {N['excluded']} wrong links are excluded (`data/overrides.tsv`).
- By group: reptiles {G['reptiles']['yes_pc']:.0f}%, insects {G['insects']['yes_pc']:.0f}%, plants {G['plants']['yes_pc']:.0f}%, birds {G['birds']['yes_pc']:.0f}% (most records at home {G['birds']['majority_pc']:.0f}%), fungi {G['fungi']['yes_pc']:.0f}%, microbes and viruses {G['microbes']['yes_pc']:.0f}%.
- Latin epithets: about {E['nonbrit_weighted_yes_pc']:.0f}% of non-British epithet taxa (stratified sample, weighted) are recorded in the named place; British and Irish epithets, checked in full, {E['brit_yes_pc']:.0f}% of {E['brit_assessed']} (hibernica {E['brit']['Ireland']['yes_pc']:.0f}%, Republic of Ireland only).

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js` | The interactive page (built by `code/03_build_site.py`): The Inked World base map with every namesake place, the GBIF box of any taxon, and the Latin epithet view. |
| `header.png` | Social card, 1200 x 630. |
| `data/taxa_named.csv` | One row per taxon named after a place ({N['taxa']:,}): Wikidata QID, name, rank, GBIF key and how it was found, group and classification, namesake place(s), its countries, GBIF record count, records in the namesake's countries, top countries, record box, distance from namesake to box, verdict (yes, no, few, norecords, nokey, nocountry, synonym, excluded, duplicate, notplace) and a note. |
| `data/epithet_taxa_sample.csv` | The {E['sampled']:,} epithet taxa checked: epithet, place, countries tested, GBIF counts, verdict (yes, no, few, norecords, nokey, nocountry, synonym, excluded, duplicate, notplace) and a note. |
| `data/epithet_places.csv` | Per place: adjectives, Wikidata taxa, sampled, assessed, share recorded there. |
| `data/overrides.tsv` | Hand corrections: test countries for continents and cross-border regions, and the taxa excluded as wrong "named after" links, each with a reason. |
| `data/review_absent.tsv` | The {R['review']['n']} taxa first found absent from home, each with its category (misnomer, not recorded, duplicate, synonym key, region corrected, wrong link) and what was done. |
| `data/epithet_stems.tsv` | The Latin place adjectives and their places (argentina is dropped in code as ambiguous). |
| `data/raw/` | Inputs fetched for the study: GBIF counts by country and boxes (`gbif_ranges_full.json`, `epithet_gbif_countries.json`), Wikidata epithet taxa, and the key lists. |
| `data/site.json` | Page data. |
| `data/results.json` | Every number quoted anywhere. |
| `code/` | Scripts, run in order, templates and `qa.js`. |
| `release/` | Paper (`paper/`), blog post and figures (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- Named taxa: Wikidata species and subspecies with P138 "named after" an item with coordinates; GBIF key from P846, else an exact GBIF name match ({N['key_by_match']} taxa). Items sharing a GBIF accepted taxon and a namesake are counted once ({N['duplicates']} dropped); namesakes that are ships or institutions are left out ({N['notplace']}).
- GBIF: per key, occurrence count with coordinates, no geospatial issue and status present; counts by country; density-map bounding box; backbone classification.
- Test countries: the namesake's Wikidata countries, the country or territory containing its coordinates (Natural Earth), and overseas territories GBIF codes separately. Continents and cross-border regions count as all their countries; subnational regions as their country (Siberia = Russia). Recorded there = any record in a test country; not there = at least {R['min_n']} records and none; a synonym key with no records at home is not tested ({N['synonym_absent']}). Marine records count where GBIF assigns them to a country's waters; namesakes at sea or in Antarctica ({N['no_country']}) are not tested.
- Epithets: {E['stems']} Latin place adjectives in {E['places']} places ({E['regions']} multi-country regions counted as any of their countries); all British and Irish taxa with a GBIF key, up to 40 random taxa with a key per other adjective; the non-British share is weighted by the inverse sampling fraction of each adjective.
- Caveats: GBIF coverage is uneven and type specimens make presence easy; country is coarse and boxes cruder; records under other ranks are missed; Wikidata links are incomplete and sometimes wrong (the hand checks cover every apparent miss and every non-echoing tested name, not untested taxa or microbes); the epithet test reads names, not intentions.

## How to rerun

Needs Python 3 with numpy, pandas, shapely, pyproj, matplotlib and Pillow, xelatex and pdftotext; node with Playwright for `code/qa.js`. `code/00_fetch_gbif.py` documents the GBIF calls (it needs api.gbif.org); its outputs are in `data/raw/`.

```
python3 code/01_build.py        # verdicts for named taxa and epithets
python3 code/02_results.py      # results.json and page data
python3 code/03_build_site.py   # index.html
python3 code/04_figures.py      # figures and header
python3 code/05_paper.py        # paper PDF (set DOI=10.5281/zenodo.N to fill the DOI)
python3 reddit/collage.py       # collage
python3 code/07_readme.py       # README, LICENSE, Reddit post
python3 code/06_release.py      # blog post, Zenodo files
```

## Sources and licences

- Wikidata (https://www.wikidata.org/), CC0: taxa, namesakes, coordinates, countries.
- GBIF.org (https://www.gbif.org/), occurrence, species and maps APIs, 2026. Records are published by their datasets under CC0, CC BY or CC BY-NC; only counts aggregated by country and bounding boxes are redistributed here. Please cite GBIF.org when reusing.
- Natural Earth (public domain): country outlines.
- Base map on the page: The Inked World (https://maps.tristanhotham.com/ink-map/), OpenStreetMap vector tiles by OpenFreeMap (ODbL), AWS Terrain Tiles. Fonts: MedievalSharp, IM Fell (SIL OFL).
- Derived data, text and figures: CC BY 4.0. Code: MIT.

## Citation

Hotham, T. (2026) Named for a place, living somewhere else? Species named after places, tested against where GBIF records them. Zenodo. {{https://doi.org/10.5281/zenodo.24058123}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
lic = """MIT License (code)

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Text, figures, the paper, the collage and the derived data in data/: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.

Wikidata content is CC0. The GBIF counts in data/ are aggregated from occurrence records published under CC0, CC BY or CC BY-NC by their datasets; cite GBIF.org when reusing them.
"""
post = f"""**Title:** [OC] Do species named after a place live there? {N['yes_pc']:.0f}% do. The coco de mer, named for the Maldives, grows only in the Seychelles

**Body:**

I took {N['taxa']:,} species and subspecies that Wikidata says are named after a place and checked where GBIF (the Global Biodiversity Information Facility) has records of them.

- Of {N['assessed_life']:,} plants, animals and fungi with enough records, {N['yes_pc']:.0f}% are recorded in the namesake's country and {N['majority_pc']:.0f}% mostly there.
- {N['no']} have 5+ records and none there (after a hand check that threw out {R['review']['errors']} data errors from the first {R['review']['n']}): the coco de mer (Maldives, really the Seychelles), the Javan banded pitta (named for the Guianas), the Central Asian salamander (named for Siberia).
- Fungi ({G['fungi']['yes_pc']:.0f}%) and microbes ({G['microbes']['yes_pc']:.0f}%) stray most.
- Latin British epithets (anglica, scotica, hibernica...): {E['brit_yes_pc']:.0f}% recorded in the UK, vs about {E['nonbrit_weighted_yes_pc']:.0f}% for other place epithets.
- Caveat: GBIF is uneven; one record (often the type specimen) counts as present.

Interactive map: https://maps.tristanhotham.com/species-places/

**Source comment:**

Data: Wikidata "named after" links (CC0); GBIF.org occurrence counts by country via the GBIF API; Natural Earth. Tools: Python (pandas, matplotlib), MapLibre. Code and data: https://github.com/Tristan-Hotham/species-places
"""
for txt in (readme, post):
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
        assert bad not in txt.replace("```", "").replace("|---|---|", ""), bad
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
print("README", len(readme.split()), "words")
