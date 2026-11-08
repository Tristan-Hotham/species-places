"""Step 5: the paper. Fills code/paper_template.tex from data/results.json, adds tables, compiles with xelatex.
Output: release/paper/Hotham_Species_Places.pdf and .tex beside the f_*.png figures. The DOI stays a placeholder."""
import subprocess
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Species_Places"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")

G = R["groups"]
assert all(G[g]["yes_pc"] >= 95 for g in ("reptiles", "insects", "arachnids", "plants", "amphibians"))   # "almost always"


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pc": return f"{round(float(v))}\\%"
    if f == "f1": return f"{float(v):.1f}"
    return tex(str(v))


rows = "".join(f"{g['name']} & {g['n']} & {g['yes_pc']:.0f}\\% & {g['majority_pc']:.0f}\\% & {g['no']}\\\\\n" for k, g in sorted(G.items(), key=lambda kv: -kv[1]["n"]))
TG = ("\\begin{table}[tbp]\\centering\\small\\caption{Assessed taxa by group: number, share recorded in the namesake's country, share with most records there, "
      "and number not recorded there.}\\label{tab:groups}\\begin{tabular}{lrrrr}\\toprule Group & Assessed & Recorded there & Mostly there & Not there\\\\\\midrule\n"
      + rows + "\\bottomrule\\end{tabular}\\end{table}")
iso = jload(f"{WORK}/build.json")["isoname"]
rows = ""
for p in R["no_top"][:18]:
    top = ", ".join(f"{iso.get(x.split(':')[0], x.split(':')[0])} {x.split(':')[1]}" for x in p["top"].split()[:2])
    rows += f"\\textit{{{tex(p['name'])}}} & {tex(p['place'])} & {p['n']:,} & {tex(top)}\\\\\n"
TN = ("\\begin{table}[tbp]\\centering\\small\\caption{Plants, animals and fungi with most GBIF records and none in their namesake's country.}\\label{tab:no}"
      "\\begin{tabular}{llrl}\\toprule Taxon & Named after & Records & Most records\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("{{AI}}", AI).replace("{{TABLE_GROUPS}}", TG).replace("{{TABLE_NO}}", TN)
t = re.sub(r"\{\{(?!TABLE_|DOI)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
DOI = os.environ.get("DOI")          # the publisher sets DOI=10.5281/zenodo.N and reruns this step
t = t.replace("https://doi.org/10.5281/zenodo.24058123", f"\\url{{https://doi.org/{DOI}}}" if DOI else "https://doi.org/\\{\\{DOI\\}\\}")   # as in the sibling studies
assert "{{" not in t and "--" not in t and "—" not in t and "–" not in t
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–") + txt.count("--"))
