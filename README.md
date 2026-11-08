# Named for a place, living somewhere else?

Do species named after a place live there? 2,901 species and subspecies that Wikidata says are named after a place with coordinates, and 61,815 whose Latin epithet names a place (202 adjectives such as anglica, scotica, hibernica, japonica), tested against where GBIF records them.

Interactive page: https://maps.tristanhotham.com/species-places/
Paper: https://doi.org/10.5281/zenodo.24058123
Blog post: https://blog.tristanhotham.com/2026/10/31/species-places/
Code and data: https://github.com/Tristan-Hotham/species-places

## Headline results

- Of 1,210 plants, animals and fungi with enough GBIF records to test (at least 5 records, or any record at home), 97.6% are recorded in the country of their namesake, 87.6% have most records there and 70.0% have no records elsewhere. Among those with 100+ records, 71% have most records at home.
- 29 have at least 5 records and none in their namesake's country, e.g. Lodoicea maldivica (coco de mer; 292 of 301 records in the Seychelles), Pitta guajana / Hydrornis guajanus (Guianas; recorded in Indonesia), Ranodon sibiricus (Siberia; Kazakhstan and China). Most of the rest are gaps in GBIF (fossils, marine species, records just over a border).
- Hand check: of the 53 taxa first found absent from home, 24 (45%) were data errors (duplicates, synonym keys, regions pinned on one country, wrong links) and were removed or corrected; a random 30 of the taxa recorded at home held 3 wrong links, and a check of every assessed name whose epithet does not echo its namesake removed 49 more. In all 58 wrong links are excluded (`data/overrides.tsv`).
- By group: reptiles 98%, insects 100%, plants 98%, birds 98% (most records at home 69%), fungi 81%, microbes and viruses 66%.
- Latin epithets: about 91% of non-British epithet taxa (stratified sample, weighted) are recorded in the named place; British and Irish epithets, checked in full, 81% of 323 (hibernica 61%, Republic of Ireland only).

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js` | The interactive page (built by `code/03_build_site.py`): The Inked World base map with every namesake place, the GBIF box of any taxon, and the Latin epithet view. |
| `header.png` | Social card, 1200 x 630. |
| `data/taxa_named.csv` | One row per taxon named after a place (2,901): Wikidata QID, name, rank, GBIF key and how it was found, group and classification, namesake place(s), its countries, GBIF record count, records in the namesake's countries, top countries, record box, distance from namesake to box, verdict (yes, no, few, norecords, nokey, nocountry, synonym, excluded, duplicate, notplace) and a note. |
| `data/epithet_taxa_sample.csv` | The 7,756 epithet taxa checked: epithet, place, countries tested, GBIF counts, verdict (yes, no, few, norecords, nokey, nocountry, synonym, excluded, duplicate, notplace) and a note. |
| `data/epithet_places.csv` | Per place: adjectives, Wikidata taxa, sampled, assessed, share recorded there. |
| `data/overrides.tsv` | Hand corrections: test countries for continents and cross-border regions, and the taxa excluded as wrong "named after" links, each with a reason. |
| `data/review_absent.tsv` | The 53 taxa first found absent from home, each with its category (misnomer, not recorded, duplicate, synonym key, region corrected, wrong link) and what was done. |
| `data/epithet_stems.tsv` | The Latin place adjectives and their places (argentina is dropped in code as ambiguous). |
| `data/raw/` | Inputs fetched for the study: GBIF counts by country and boxes (`gbif_ranges_full.json`, `epithet_gbif_countries.json`), Wikidata epithet taxa, and the key lists. |
| `data/site.json` | Page data. |
| `data/results.json` | Every number quoted anywhere. |
| `code/` | Scripts, run in order, templates and `qa.js`. |
| `release/` | Paper (`paper/`), blog post and figures (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- Named taxa: Wikidata species and subspecies with P138 "named after" an item with coordinates; GBIF key from P846, else an exact GBIF name match (175 taxa). Items sharing a GBIF accepted taxon and a namesake are counted once (51 dropped); namesakes that are ships or institutions are left out (36).
- GBIF: per key, occurrence count with coordinates, no geospatial issue and status present; counts by country; density-map bounding box; backbone classification.
- Test countries: the namesake's Wikidata countries, the country or territory containing its coordinates (Natural Earth), and overseas territories GBIF codes separately. Continents and cross-border regions count as all their countries; subnational regions as their country (Siberia = Russia). Recorded there = any record in a test country; not there = at least 5 records and none; a synonym key with no records at home is not tested (7). Marine records count where GBIF assigns them to a country's waters; namesakes at sea or in Antarctica (9) are not tested.
- Epithets: 202 Latin place adjectives in 79 places (12 multi-country regions counted as any of their countries); all British and Irish taxa with a GBIF key, up to 40 random taxa with a key per other adjective; the non-British share is weighted by the inverse sampling fraction of each adjective.
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

Hotham, T. (2026) Named for a place, living somewhere else? Species named after places, tested against where GBIF records them. Zenodo. https://doi.org/10.5281/zenodo.24058123

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
