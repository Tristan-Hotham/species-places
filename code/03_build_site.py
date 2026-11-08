"""Step 3: index.html from code/page_template.html and data/results.json, with the facts written in words checked.
10.5281/zenodo.24058123, https://doi.org/10.5281/zenodo.24058123 and https://blog.tristanhotham.com/2026/10/31/species-places/ stay as placeholders for the publisher."""
import re, time
from common import *

R = jload(f"{DATA}/results.json")
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}
G = R["groups"]; F = R["feat"]
# facts stated in words
assert min(G[g]["yes_pc"] for g in ("reptiles", "insects", "arachnids")) > max(G["fungi"]["yes_pc"], G["microbes"]["yes_pc"])
assert G["birds"]["majority_pc"] < G["plants"]["majority_pc"]
assert R["named"]["n100_majority_pc"] < R["named"]["majority_pc"]
assert {t[0] for t in F["Dracunculus medinensis"]["top"]} == {"BJ", "US", "AU", "IN"}
assert R["ep"]["brit"]["Ireland"]["yes_pc"] == min(v["yes_pc"] for k, v in R["ep"]["brit"].items() if v["n"] >= 10)
assert "GB" not in R["ep"]["brit_feat"]["robertus"]["top"] and R["ep"]["brit_feat"]["robertus"]["top"].startswith("FI")
assert R["ep"]["brit_feat"]["urophyllum"]["top"].split(":")[0] == "PG"
assert R["ep"]["brit_feat"]["chrysoblephus"]["top"].startswith("ZA")
assert F["Pitta guajana"]["top"][0][0] == "ID" and F["Bradgatia linfordensis"]["top"][0][0] == "CA" and F["Aspergillus egyptiacus"]["top"][0][0] == "AU"
assert {t[0] for t in F["Verbascum adrianopolitanum"]["top"]} <= {"GR", "BG", "US"} and F["Elephas melitensis"]["top"][0][0] == "IT"
rows = "".join(f'<tr><td>{g["name"]}</td><td class="r">{g["n"]}</td><td class="r">{g["yes_pc"]:.0f}%</td><td class="r">{g["majority_pc"]:.0f}%</td><td class="r">{g["no"]}</td></tr>'
               for k, g in sorted(G.items(), key=lambda kv: -kv[1]["n"]))
t = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
fs = open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read()
t = t.replace("{{TABLE_GROUPS}}", rows).replace("{{FULLSCREEN}}", fs)
t = t.replace("{{BYLINE}}", BYLINE).replace("{{AI}}", AI).replace("{{VERSION}}", time.strftime("%Y%m%d"))
t = re.sub(r"\{\{([^}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(R, m.group(1)), m.group(3)), t)
assert set(re.findall(r"\{\{([^}]+)\}\}", t)) <= KEEP, set(re.findall(r"\{\{([^}]+)\}\}", t))
vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", t, flags=re.S)
for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
    assert bad not in vis, bad
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
js = open(os.path.join(ROOT, "js", "page.js"), encoding="utf-8").read()
assert "—" not in js and "–" not in js
print("index.html", len(t) // 1024, "KB")
