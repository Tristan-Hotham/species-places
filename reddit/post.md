**Title:** [OC] Do species named after a place live there? 98% do. The coco de mer, named for the Maldives, grows only in the Seychelles

**Body:**

I took 2,901 species and subspecies that Wikidata says are named after a place and checked where GBIF (the Global Biodiversity Information Facility) has records of them.

- Of 1,210 plants, animals and fungi with enough records, 98% are recorded in the namesake's country and 88% mostly there.
- 29 have 5+ records and none there (after a hand check that threw out 24 data errors from the first 53): the coco de mer (Maldives, really the Seychelles), the Javan banded pitta (named for the Guianas), the Central Asian salamander (named for Siberia).
- Fungi (81%) and microbes (66%) stray most.
- Latin British epithets (anglica, scotica, hibernica...): 81% recorded in the UK, vs about 91% for other place epithets.
- Caveat: GBIF is uneven; one record (often the type specimen) counts as present.

Interactive map: https://maps.tristanhotham.com/species-places/

**Source comment:**

Data: Wikidata "named after" links (CC0); GBIF.org occurrence counts by country via the GBIF API; Natural Earth. Tools: Python (pandas, matplotlib), MapLibre. Code and data: https://github.com/Tristan-Hotham/species-places
