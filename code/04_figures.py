"""Step 4: figures for the page (img/), the blog (release/blog/b_*.png), the paper (release/paper/f_*.png) and the header."""
import numpy as np, pandas as pd
from PIL import Image
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch
from figstyle import *

R = jload(f"{DATA}/results.json")
S = jload(f"{DATA}/site.json")
d = pd.read_csv(f"{DATA}/taxa_named.csv", keep_default_na=False, na_values=[""], dtype={"gbif": str, "place_iso2": str})
EP = pd.read_csv(f"{DATA}/epithet_places.csv", keep_default_na=False, na_values=[""], dtype={"iso2": str})
BLOG, PAPERD = f"{ROOT}/release/blog", f"{ROOT}/release/paper"
for x in (BLOG, PAPERD):
    os.makedirs(x, exist_ok=True)
HALO = [pe.withStroke(linewidth=3.2, foreground=PAPER)]
GREEN, RED2, SAND, GREY = "#4F7A3A", "#B0301F", "#C9A86A", "#B8AE9C"
CRS = "+proj=robin +lon_0=0"
EXT = (-180, 180, -58, 84)


def out(fig, name, page=True, blog=True, paper=True, dpi=200):
    fig.savefig(f"{WORK}/{name}.png", dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
    im = Image.open(f"{WORK}/{name}.png").convert("RGB")
    if page:
        w = min(1600, im.size[0]); im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS).save(f"{IMG}/{name}.jpg", quality=84, optimize=True)
    if blog:
        w = min(1800, im.size[0]); im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS).save(f"{BLOG}/b_{name}.png", optimize=True)
    if paper:
        w = min(2000, im.size[0]); im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS).save(f"{PAPERD}/f_{name}.png", optimize=True)
    os.remove(f"{WORK}/{name}.png")


def world(ax):
    ext, f = ink_base(ax, CRS, EXT, ripple_m=(60e3, 150e3, 280e3), coast_lw=0.5, simplify=8000, min_area=3e8)
    ax.set_xlim(f(-180, 0)[0], f(180, 0)[0]); ax.set_ylim(f(0, -58)[1], f(0, 84)[1])
    return f


def nearest(r):
    b = [float(v) for v in r.box.split()]
    return min(max(r.place_lon, b[2]), b[3]), min(max(r.place_lat, b[0]), b[1])


# ---------- 1. the world of namesakes
a = d[d.verdict.isin(["yes", "no", "few"])]
fig = plt.figure(figsize=(14, 7.6)); parchment(fig)
ax = fig.add_axes([0.0, 0.03, 1, 0.84]); f = world(ax)
for _, r in a[a.verdict == "no"].iterrows():
    if r.box:
        lo, la = nearest(r)
        if abs(lo - r.place_lon) + abs(la - r.place_lat) > 0.05:
            xs, ys = f(np.linspace(r.place_lon, lo, 30), np.linspace(r.place_lat, la, 30))
            ax.plot(xs, ys, color=RED2, lw=0.7, alpha=0.6, ls=(0, (3, 2)), zorder=5)
for v, c, s, z in (("few", SAND, 7, 6), ("yes", GREEN, 9, 6.5), ("no", RED2, 26, 7)):
    x = a[a.verdict == v]; X, Y = f(x.place_lon.values, x.place_lat.values)
    ax.scatter(X, Y, s=s, c=c, edgecolors=INKC, linewidths=0.35, zorder=z)
fig.text(0.03, 0.95, "Named for a place: do they live there?", fontproperties=FELL, fontsize=24, color=INKC)
fig.text(0.03, 0.905, f"The namesake places of {len(a):,} species and subspecies with GBIF records, coloured by whether GBIF records them in that country",
         fontproperties=FELL, fontsize=13, color=MUT)
lx = fig.add_axes([0.03, 0.08, 0.24, 0.2]); lx.axis("off"); lx.set_xlim(0, 1); lx.set_ylim(0, 1)
for i, (c, s, l) in enumerate(((GREEN, 40, "recorded in the namesake's country"), (RED2, 80, "5 or more records, none there"), (SAND, 30, "fewer than 5 records, none there"))):
    lx.scatter([0.05], [0.85 - i * 0.22], s=s, c=c, edgecolors=INKC, linewidths=0.5)
    lx.text(0.12, 0.85 - i * 0.22, l, fontproperties=FELL, fontsize=12, va="center", color=INKC)
lx.plot([0.0, 0.1], [0.19, 0.19], color=RED2, lw=1.2, ls=(0, (3, 2))); lx.text(0.12, 0.19, "to the nearest edge of its records' box", fontproperties=FELL, fontsize=12, va="center", color=INKC)
fig.text(0.97, 0.015, "Taxa: Wikidata (CC0). Records: GBIF.org. Map: Natural Earth.", fontproperties=FELL, fontsize=10, color=MUT, ha="right")
out(fig, "world")

# ---------- 2. groups
G = sorted(R["groups"].values(), key=lambda g: g["yes_pc"])
fig = plt.figure(figsize=(12, 7)); parchment(fig)
ax = fig.add_axes([0.30, 0.1, 0.62, 0.70])
y = np.arange(len(G))
ax.barh(y, [g["yes_pc"] for g in G], color=GREEN, edgecolor=INKC, lw=0.5, height=0.7, label="recorded in the namesake's country")
ax.barh(y, [g["majority_pc"] for g in G], color="#B9CC97", edgecolor=INKC, lw=0.5, height=0.36, label="most records there")
ax.set_yticks(y); ax.set_yticklabels([f"{g['name']} ({g['n']})" for g in G], fontproperties=FELL, fontsize=12.5)
for i, g in enumerate(G):
    ax.text(g["yes_pc"] + 1, i, f"{g['yes_pc']:.0f}%", va="center", fontproperties=FELL, fontsize=11.5, color=INKC)
ax.set_xlim(0, 108); ax.set_xticks(range(0, 101, 20)); ax.set_xticklabels([f"{v}%" for v in range(0, 101, 20)], fontproperties=FELL, fontsize=11)
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
ax.legend(loc="upper left", bbox_to_anchor=(0.0, 1.07), ncol=2, prop=FELL, frameon=False)
fig.text(0.04, 0.94, "Fungi and microbes stray furthest", fontproperties=FELL, fontsize=22, color=INKC)
fig.text(0.04, 0.895, "Share of assessed taxa recorded in the country of the place they are named after, by group (number assessed)", fontproperties=FELL, fontsize=12.5, color=MUT)
out(fig, "groups")

# ---------- 3. the misnamed: arrows from namesake to the main country of records
CENT = jload(f"{WORK}/build.json")["cent"]
PLN = {"Guyanas": "the Guianas", "Newtown Linford": "Leicestershire"}
OVR = {"SC": (55.7, -4.4), "ID": (110.3, -7.3), "IT": (14.3, 37.5), "CA": (-55.5, 47.2)}   # draw to Seychelles, Java, Sicily and Newfoundland, not the country centroid
fig = plt.figure(figsize=(14, 7.6)); parchment(fig)
ax = fig.add_axes([0.0, 0.03, 1, 0.84]); f = world(ax)
LAB = {"Lodoicea maldivica": ("coco de mer", (80, -40), "center"), "Pitta guajana": ("Javan banded pitta", (-28, -34), "center"),
       "Ranodon sibiricus": ("Central Asian salamander", (178, 29), "right"), "Dracunculus medinensis": ("Guinea worm", (-21, 17), "right"),
       "Elephas melitensis": ("Maltese dwarf elephant", (-13, 31), "right"), "Bradgatia linfordensis": ("a Charnwood fossil", (-30, 42), "center"),
       "Aspergillus egyptiacus": ("a soil fungus", (30, -47), "center")}
for nm in LAB:
    ft = R["feat"][nm]
    r = d[d.name == nm].iloc[0]
    k = ft["top"][0][0]; tx, ty = OVR.get(k, CENT[k])
    X0_, Y0_ = f(r.place_lon, r.place_lat); X1_, Y1_ = f(tx, ty)
    ax.add_patch(FancyArrowPatch((X0_, Y0_), (X1_, Y1_), arrowstyle="-|>", mutation_scale=14, color=RED2, lw=1.6,
                                 connectionstyle="arc3,rad=0.2", zorder=8, shrinkA=4, shrinkB=4))
    ax.scatter([X0_], [Y0_], s=40, c=PAPER, edgecolors=RED2, linewidths=1.6, zorder=9)
    ax.scatter([X1_], [Y1_], s=40, c=GREEN, edgecolors=INKC, linewidths=0.8, zorder=9)
    com, (lx_, ly_), ha_ = LAB[nm]
    lxm, lym = f(lx_, ly_)
    lxm, lym = float(lxm), float(lym)
    ax.annotate(f"{nm}\n{com}: {PLN.get(r.place, r.place)} to {ft['top'][0][2]}", (X0_, Y0_), xytext=(lxm, lym), fontproperties=FELLIT, fontsize=10.5, color=INKC,
                ha=ha_, va="center", zorder=10, path_effects=HALO, arrowprops=dict(arrowstyle="-", color=MUT, lw=0.5, shrinkA=2, shrinkB=4))
fig.text(0.03, 0.95, "From the name to the range", fontproperties=FELL, fontsize=24, color=INKC)
fig.text(0.03, 0.905, "Arrows run from the place in a species' name (open circle) to the country with most of its GBIF records (green)", fontproperties=FELL, fontsize=13, color=MUT)
fig.text(0.97, 0.015, "Taxa: Wikidata (CC0). Records: GBIF.org. Map: Natural Earth.", fontproperties=FELL, fontsize=10, color=MUT, ha="right")
out(fig, "misnamed")

# ---------- 4. the share at home
a = d[d.verdict.isin(["yes", "no"]) & (d.group != "microbes")]
fig = plt.figure(figsize=(12, 6.4)); parchment(fig)
ax = fig.add_axes([0.08, 0.12, 0.88, 0.7])
sh = a.share_in.clip(0, 100)
zero = int((sh == 0).sum())
bins = np.arange(0, 101, 5); bins[-1] = 100.01
h, _ = np.histogram(sh[sh > 0], bins=bins)
ax.bar([-4], [zero], width=4.6, color=RED2, edgecolor=INKC, lw=0.5)
ax.bar(bins[:-1] + 2.5, h, width=4.6, color=[GREEN if i == len(h) - 1 else "#8DAA5B" for i in range(len(h))], edgecolor=INKC, lw=0.5)
ax.set_xticks([-4] + list(range(0, 101, 10))); ax.set_xticklabels(["none"] + [f"{v}%" for v in range(0, 101, 10)], fontproperties=FELL, fontsize=11)
ax.text(-4, zero * 1.04 + 8, f"{zero}\nnone there", ha="center", va="bottom", fontproperties=FELL, fontsize=11.5, color=INKC)
ax.set_xlabel("Share of a taxon's GBIF records that are in its namesake's country", fontproperties=FELL, fontsize=12)
ax.set_ylabel("Taxa", fontproperties=FELL, fontsize=12)
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
ax.text(97.5, h[-1] * 1.02, f"{R['named']['all_pc']:.0f}%\nall at home", ha="center", va="bottom", fontproperties=FELL, fontsize=11.5, color=INKC)
fig.text(0.04, 0.93, "Most live only where they are named", fontproperties=FELL, fontsize=22, color=INKC)
fig.text(0.04, 0.88, f"Plants, animals and fungi with at least {MIN_N} GBIF records or any record at home ({len(a):,} taxa)", fontproperties=FELL, fontsize=12.5, color=MUT)
out(fig, "share")

# ---------- 5. Latin epithets
ECOL = lambda s: GREY if s != s else RED2 if s < 70 else "#D98A3A" if s < 80 else "#E7C25A" if s < 90 else "#8DAA5B" if s < 99.95 else GREEN
fig = plt.figure(figsize=(14, 7.6)); parchment(fig)
ax = fig.add_axes([0.0, 0.03, 1, 0.84]); f = world(ax)
E = EP.sort_values("taxa_wikidata", ascending=False)
X, Y = f(E.lon.values, E.lat.values)
ax.scatter(X, Y, s=8 + 2.2 * np.sqrt(E.taxa_wikidata.values) * 4, c=[ECOL(s) for s in E.share_yes], edgecolors=INKC,
           linewidths=np.where(E.british == 1, 1.8, 0.6), alpha=0.9, zorder=7)
for _, r in E[E.taxa_wikidata >= 1500].iterrows():
    x, y = f(r.lon, r.lat)
    ax.text(x, y, r.place.split(" (")[0], fontproperties=FELLIT, fontsize=9.5, ha="center", va="center", color=INKC, zorder=9, path_effects=HALO)
lx = fig.add_axes([0.03, 0.08, 0.2, 0.25]); lx.axis("off"); lx.set_xlim(0, 1); lx.set_ylim(0, 1)
for i, (c, l) in enumerate(((GREEN, "all recorded there"), ("#8DAA5B", "90 to 99%"), ("#E7C25A", "80 to 89%"), ("#D98A3A", "70 to 79%"), (RED2, "under 70%"))):
    lx.scatter([0.05], [0.9 - i * 0.15], s=60, c=c, edgecolors=INKC, linewidths=0.5); lx.text(0.13, 0.9 - i * 0.15, l, fontproperties=FELL, fontsize=12, va="center")
lx.text(0.0, 0.08, "Size: species in Wikidata with the epithet.\nThick ring: British and Irish.", fontproperties=FELL, fontsize=11, color=MUT, va="center")
fig.text(0.03, 0.95, "japonica, sinensis, anglica: are they there?", fontproperties=FELL, fontsize=24, color=INKC)
fig.text(0.03, 0.905, f"{R['ep']['stems']} Latin place adjectives; share of sampled species with GBIF records that are recorded in the place's country or region",
         fontproperties=FELL, fontsize=13, color=MUT)
fig.text(0.97, 0.015, "Taxa: Wikidata (CC0). Records: GBIF.org. Map: Natural Earth.", fontproperties=FELL, fontsize=10, color=MUT, ha="right")
out(fig, "epithets")

# ---------- 6. British epithets
B = R["ep"]["brit"]
STEM = {"Britain": "britannica", "England": "anglica", "Scotland": "scotica", "Wales": "cambrica", "Ireland": "hibernica", "London": "londinensis", "Cornwall": "cornubiensis"}
order = sorted(B, key=lambda k: B[k]["yes_pc"])
fig = plt.figure(figsize=(12, 6.4)); parchment(fig)
ax = fig.add_axes([0.28, 0.12, 0.64, 0.72])
for i, k in enumerate(order):
    v = B[k]
    ax.barh(i, v["yes_pc"], color=GREEN if v["n"] >= 10 else "#B9CC97", edgecolor=INKC, lw=0.5, height=0.66)
    ax.text(v["yes_pc"] + 1, i, f"{v['yes_pc']:.0f}%  ({v['yes']} of {v['n']})", va="center", fontproperties=FELL, fontsize=11.5)
ax.set_yticks(range(len(order))); ax.set_yticklabels([f"{STEM[k]} ({k})" for k in order], fontproperties=FELLIT, fontsize=13)
ax.set_xlim(0, 118); ax.set_xticks(range(0, 101, 20)); ax.set_xticklabels([f"{v}%" for v in range(0, 101, 20)], fontproperties=FELL, fontsize=11)
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
ax.axvline(R["ep"]["nonbrit_weighted_yes_pc"], color=MUT, lw=1, ls=(0, (4, 3)))
ax.text(R["ep"]["nonbrit_weighted_yes_pc"], len(order) - 0.35, "other epithets", ha="center", fontproperties=FELL, fontsize=10.5, color=MUT)
fig.text(0.04, 0.93, "The British epithets", fontproperties=FELL, fontsize=22, color=INKC)
fig.text(0.04, 0.88, "Share of taxa with enough GBIF records that are recorded in the United Kingdom (hibernica: the Republic of Ireland). Pale: fewer than 10 taxa.",
         fontproperties=FELL, fontsize=12, color=MUT)
out(fig, "british")

# ---------- header 1200 x 630
fig = plt.figure(figsize=(12, 6.3), dpi=100); parchment(fig)
ax = fig.add_axes([0.43, 0.06, 0.56, 0.56]); f = world(ax); ax.set_facecolor("none")
a = d[d.verdict.isin(["yes", "no"])]
for v, c, s in (("yes", GREEN, 5), ("no", RED2, 22)):
    x = a[a.verdict == v]; X, Y = f(x.place_lon.values, x.place_lat.values); ax.scatter(X, Y, s=s, c=c, edgecolors=INKC, linewidths=0.3, zorder=7)
r = d[d.name == "Lodoicea maldivica"].iloc[0]
X0_, Y0_ = f(r.place_lon, r.place_lat); X1_, Y1_ = f(55.7, -4.4)
ax.add_patch(FancyArrowPatch((X0_, Y0_), (X1_, Y1_), arrowstyle="-|>", mutation_scale=16, color=RED2, lw=2, connectionstyle="arc3,rad=0.3", zorder=9))
fig.text(0.04, 0.84, "Named for a place,", fontproperties=FELL, fontsize=38, color=INKC)
fig.text(0.04, 0.70, "living somewhere else?", fontproperties=HAND, fontsize=42, color=RED)
fig.text(0.04, 0.55, f"{R['named']['taxa']:,} species named after a place.\n{R['named']['yes_pc']:.0f}% of the plants, animals and fungi\nGBIF can test are recorded there.\nThe coco de mer, named for the\nMaldives, grows in the Seychelles.",
         fontproperties=FELL, fontsize=17, color=INKC, linespacing=1.35, va="top")
fig.text(0.04, 0.06, "maps.tristanhotham.com/species-places", fontproperties=FELL, fontsize=13, color=MUT)
fig.savefig(f"{ROOT}/header.png", dpi=100, facecolor=fig.get_facecolor()); plt.close(fig)
assert Image.open(f"{ROOT}/header.png").size == (1200, 630)
print("figures done")
