# species-places: working notes

Built 2026 from the coordinator's GBIF fetch (data/raw/). Steps: code/01_build.py .. 07_readme.py, reddit/collage.py, code/qa.js.
- Verdicts: recorded there = any GBIF record in the namesake's Wikidata country, the Natural Earth country containing its point,
  or GBIF-coded overseas territories of those; not there = >= 5 records, none there. Microbes reported apart.
- Epithets: argentina dropped (also "silvery"); 12 multi-country regions; hibernica = IE only; non-British share weighted.
- Verified online: coco de mer naming (capasia.eu), Ranodon type locality (AMNH ASW), Dracunculus etymology (EID 2016),
  Beck et al. 2014 (Ecol. Inform. 19:10-15), Meyer et al. 2016 (Ecol. Lett. 19, doi 10.1111/ele.12624), Chrysoblephus anglicus = Englishman.
- QA: 11 screenshots at 1280 and 390, no console errors (aborted tile requests during flyTo only).
- Review (2026): hand-checked all 53 first-pass "absent" taxa (data/review_absent.tsv): 24 data errors (5 duplicates, 7 synonym keys,
  3 regions pinned on one country, 9 wrong links); 29 kept (3 misnomers, 26 recording gaps). Spot check of 30 random "at home": 3 wrong
  links; full check of non-echoing epithets removed 49 wrong links. Overrides in data/overrides.tsv. Duplicates merged by GBIF
  acceptedKey + namesake (51); ships/institutions dropped (36); synonym keys cannot show absence. Epithet weighting now per adjective.
  Meyer 2016 = Ecol. Lett. 19(8) 992-1006; coco de mer source = Crouzet 2024 (Capasia). New headline: 2,901 taxa, 1,210 tested,
  98% / 88% / 70%, 29 absent; British epithets 81% vs about 91%.
