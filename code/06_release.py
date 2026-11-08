"""Step 6: blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.24058123, https://doi.org/10.5281/zenodo.24058123 and https://blog.tristanhotham.com/2026/10/31/species-places/ stay as placeholders for the publisher."""
import json as _json, shutil, zipfile, importlib.util
from PIL import Image
from common import *

spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "03_build_site.py"))
spec.loader.exec_module(importlib.util.module_from_spec(spec))          # shared fact checks (and rebuilds index.html)
R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_Species_Places"
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = re.sub(r"\{\{(?!IMG)([^}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(R, m.group(1)), m.group(3)), post)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u_), post, re.M) for u_ in used) and "wp:image" not in post
for img in used:
    assert Image.open(f"{REL}/blog/{img}").size[0] == 1800, img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
assert set(re.findall(r"\{\{([^|}]+)\}\}", post)) <= KEEP, set(re.findall(r"\{\{([^|}]+)\}\}", post))
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS", "civil serv"):
    assert bad not in vis, bad
assert AI in post
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
N = R["named"]
meta = {"title": "Named for a place, living somewhere else?",
        "slug": "species-places",
        "excerpt": f"Thousands of species are named after a place. I matched {N['taxa']:,} of them to GBIF records: {N['yes_pc']:.0f}% of those I could test are recorded in that country. The coco de mer, named for the Maldives, grows in the Seychelles.",
        "seo_description": f"Do species named after a place live there? {N['yes_pc']:.0f}% are recorded in that country; the coco de mer is named for the Maldives but grows in the Seychelles.",
        "tags": ["maps", "data visualisation", "biodiversity", "taxonomy", "scientific names", "GBIF", "Wikidata", "natural history"],
        "header_alt": f"Title card on parchment reading 'Named for a place, living somewhere else?' beside a world map of green and red dots at the places species are named after, with a red arrow from the Maldives to the Seychelles."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/species-places_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for dd in ("code", "js", "data", "data/raw"):
        for fn in sorted(os.listdir(os.path.join(ROOT, dd))):
            p = os.path.join(ROOT, dd, fn)
            if fn.endswith(".pyc") or fn == "__pycache__" or not os.path.isfile(p):
                continue
            z.write(p, f"species-places/{dd}/{fn}")
    for fn in ("README.md", "LICENSE", "index.html"):
        z.write(os.path.join(ROOT, fn), f"species-places/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), "species-places/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = re.sub(r"\\textit\{([^}]*)\}", r"\1", ab).replace("\\%", "%").replace("\\&", "&").replace("``", "\"").replace("''", "\"")
assert "\\" not in ab and "$" not in ab, ab
zmeta = {"title": "Named for a Place, Living Somewhere Else? Species Named After Places, Tested Against Where GBIF Records Them",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive page: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/species-places/}}.</p><p>Sources: Wikidata (CC0); GBIF.org occurrence, species and maps APIs (counts aggregated by country; records published under CC0, CC BY or CC BY-NC); Natural Earth (public domain). Derived data CC BY 4.0, code MIT.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["biological nomenclature", "toponyms", "specific epithets", "GBIF", "Wikidata", "species distributions", "misnomers", "biodiversity data"],
         "license": "cc-by-4.0", "language": "eng",
         "notes": "Text, figures and derived data CC BY 4.0; code MIT. Wikidata content CC0; GBIF counts aggregated with citation to GBIF.org.",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://www.gbif.org/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.wikidata.org/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "10.1016/j.ecoinf.2013.11.002", "relation": "references", "resource_type": "publication-article"},
                                 {"identifier": "10.1111/ele.12624", "relation": "references", "resource_type": "publication-article"}],
         "files": sorted(os.listdir(Z))}
sj = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS", "civil serv"):
    assert bad not in sj, bad
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
