"""Reddit collage (r/dataisbeautiful style): from name to range for the famous misnomers, the share recorded at home by group,
and the British epithets. Light parchment; labels on the sea with a halo; full legend; source footer.
Output: reddit/species_places_collage.png (2700 x 3150 px). Run after code/04_figures.py."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))
import numpy as np, pandas as pd
from PIL import Image
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch
from figstyle import *

R = jload(f"{DATA}/results.json")
d = pd.read_csv(f"{DATA}/taxa_named.csv", keep_default_na=False, na_values=[""], dtype={"gbif": str})
CENT = jload(f"{WORK}/build.json")["cent"]
OUT = os.path.join(ROOT, "reddit", "species_places_collage.png")
HALO = [pe.withStroke(linewidth=3.4, foreground=PAPER)]
GREEN, RED2, SAND = "#4F7A3A", "#B0301F", "#C9A86A"
fig = plt.figure(figsize=(9, 10.5), dpi=300); parchment(fig, seed=7)
fig.text(0.04, 0.965, "Named for a place, living somewhere else?", fontproperties=HAND, fontsize=27, color=RED, va="center")
fig.text(0.04, 0.932, f"{R['named']['taxa']:,} species and subspecies are named after a place in Wikidata. Where does GBIF record them?",
         fontproperties=FELL, fontsize=11.5, color=INKC, va="center")
fig.text(0.04, 0.912, f"Of the {R['named']['assessed_life']:,} plants, animals and fungi with enough records, {R['named']['yes_pc']:.0f}% are recorded in their namesake's country. A few are not:",
         fontproperties=FELL, fontsize=10.5, color=MUT, va="center")

# ---- map
ax = fig.add_axes([0.0, 0.5, 1.0, 0.39])
ext, f = ink_base(ax, "+proj=robin +lon_0=0", (-180, 180, -58, 84), ripple_m=(60e3, 150e3, 280e3), coast_lw=0.4, simplify=8000, min_area=3e8)
ax.set_xlim(f(-180, 0)[0], f(180, 0)[0]); ax.set_ylim(f(0, -58)[1], f(0, 84)[1]); ax.set_facecolor("none")
a = d[d.verdict.isin(["yes", "no"])]
for v, c, s in (("yes", GREEN, 2.2), ("no", RED2, 7)):
    x = a[a.verdict == v]; X, Y = f(x.place_lon.values, x.place_lat.values); ax.scatter(X, Y, s=s, c=c, edgecolors="none", alpha=0.55, zorder=5)
PLN = {"Guyanas": "the Guianas"}
OVR = {"SC": (55.7, -4.4), "ID": (110.3, -7.3), "IT": (14.3, 37.5), "AU": (134.0, -25.0)}
LAB = {"Lodoicea maldivica": ("coco de mer", (80, -30)), "Pitta guajana": ("Javan banded pitta", (-24, -34)),
       "Ranodon sibiricus": ("salamander", (178, 18)), "Dracunculus medinensis": ("Guinea worm", (-46, 21)),
       "Elephas melitensis": ("dwarf elephant", (-43, 37)), "Aspergillus egyptiacus": ("a soil fungus", (28, -45))}
for nm, (com, (lx_, ly_)) in LAB.items():
    ft = R["feat"][nm]; r = d[d.name == nm].iloc[0]
    k = ft["top"][0][0]; tx, ty = OVR.get(k, CENT[k])
    X0_, Y0_ = f(r.place_lon, r.place_lat); X1_, Y1_ = f(tx, ty)
    ax.add_patch(FancyArrowPatch((X0_, Y0_), (X1_, Y1_), arrowstyle="-|>", mutation_scale=10, color=RED2, lw=1.3, connectionstyle="arc3,rad=0.2", zorder=8, shrinkA=3, shrinkB=3))
    ax.scatter([X0_], [Y0_], s=22, c=PAPER, edgecolors=RED2, linewidths=1.2, zorder=9)
    ax.scatter([X1_], [Y1_], s=22, c=GREEN, edgecolors=INKC, linewidths=0.6, zorder=9)
    lxm, lym = (float(v) for v in f(lx_, ly_))
    ax.annotate(f"{nm}\n{com}: {PLN.get(r.place, r.place)} to {ft['top'][0][2]}", (X0_, Y0_), xytext=(lxm, lym), fontproperties=FELLIT, fontsize=6.9,
                color=INKC, ha="right" if lx_ > 170 else "center", va="center", zorder=10, path_effects=HALO, arrowprops=dict(arrowstyle="-", color=MUT, lw=0.4, shrinkA=2, shrinkB=3))
# legend for the map, on paper below it
lx = fig.add_axes([0.04, 0.462, 0.92, 0.03]); lx.axis("off"); lx.set_xlim(0, 1); lx.set_ylim(0, 1)
items = [("dot", GREEN, "namesake of a taxon recorded in that country"), ("dot", RED2, "namesake of a taxon with 5+ records, none there"),
         ("ring", RED2, "named for"), ("dotk", GREEN, "where most records are")]
xs = [0.0, 0.33, 0.68, 0.81]
for (k, c, l), x in zip(items, xs):
    if k == "ring": lx.scatter([x + 0.01], [0.5], s=26, c=PAPER, edgecolors=c, linewidths=1.2)
    else: lx.scatter([x + 0.01], [0.5], s=20, c=c, edgecolors=INKC if k == "dotk" else "none", linewidths=0.6)
    lx.text(x + 0.025, 0.5, l, fontproperties=FELL, fontsize=8.6, va="center", color=INKC)

# ---- groups
G = sorted(R["groups"].values(), key=lambda g: g["yes_pc"])
ax = fig.add_axes([0.25, 0.09, 0.27, 0.32])
y = np.arange(len(G))
ax.barh(y, [g["yes_pc"] for g in G], color=GREEN, edgecolor=INKC, lw=0.4, height=0.72)
ax.barh(y, [g["majority_pc"] for g in G], color="#B9CC97", edgecolor=INKC, lw=0.4, height=0.36)
ax.set_yticks(y); ax.set_yticklabels([g["name"] for g in G], fontproperties=FELL, fontsize=8.2)
for i, g in enumerate(G): ax.text(g["yes_pc"] + 1.5, i, f"{g['yes_pc']:.0f}%", va="center", fontproperties=FELL, fontsize=7.6)
ax.set_xlim(0, 112); ax.set_xticks([0, 50, 100]); ax.set_xticklabels(["0%", "50%", "100%"], fontproperties=FELL, fontsize=7.5)
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
fig.text(0.04, 0.435, "By group: recorded in the namesake's country", fontproperties=FELLSC, fontsize=10, color=RED)
fig.text(0.04, 0.418, "dark bar: any record there; pale bar: most records there", fontproperties=FELL, fontsize=8.4, color=MUT)

# ---- British epithets
B = R["ep"]["brit"]
STEM = {"Britain": "britannica", "England": "anglica", "Scotland": "scotica", "Wales": "cambrica", "Ireland": "hibernica", "London": "londinensis", "Cornwall": "cornubiensis"}
order = [k for k in sorted(B, key=lambda k: B[k]["yes_pc"]) if B[k]["n"] >= 10]
ax = fig.add_axes([0.73, 0.21, 0.22, 0.20])
for i, k in enumerate(order):
    ax.barh(i, B[k]["yes_pc"], color=GREEN, edgecolor=INKC, lw=0.4, height=0.66)
    ax.text(B[k]["yes_pc"] + 2, i, f"{B[k]['yes_pc']:.0f}%", va="center", fontproperties=FELL, fontsize=8)
ax.set_yticks(range(len(order))); ax.set_yticklabels([STEM[k] for k in order], fontproperties=FELLIT, fontsize=9.5)
ax.set_xlim(0, 118); ax.set_xticks([0, 50, 100]); ax.set_xticklabels(["0%", "50%", "100%"], fontproperties=FELL, fontsize=7.5)
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
fig.text(0.57, 0.435, "Latin British epithets: recorded in the UK?", fontproperties=FELLSC, fontsize=10, color=RED)
fig.text(0.57, 0.418, "hibernica: Republic of Ireland. Other epithets (sample): about " + f"{R['ep']['nonbrit_weighted_yes_pc']:.0f}%", fontproperties=FELL, fontsize=8.4, color=MUT)
fig.text(0.57, 0.17, f"Robertus scoticus, a 'Scottish' spider: {R['ep']['brit_feat']['robertus']['n']:,} GBIF\nrecords, from Finland, Norway and Sweden, none in Britain.\n"
         "Chrysoblephus anglicus is a South African sea bream.", fontproperties=FELLIT, fontsize=8.2, color=INKC, va="top", linespacing=1.35)

fig.text(0.04, 0.035, "Data: Wikidata 'named after' links and taxa (CC0); GBIF.org occurrence counts by country (records with coordinates, no geospatial issue). "
         "Presence means at least one record\nin the country; GBIF is uneven and a type specimen can be the only record. Dr Tristan Hotham, Independent researcher, 2026.",
         fontproperties=FELL, fontsize=7.6, color=MUT, va="center", linespacing=1.4)
fig.text(0.96, 0.075, "maps.tristanhotham.com/species-places", fontproperties=FELL, fontsize=9.5, color=RED, ha="right", va="center")
fig.savefig(OUT, dpi=300, facecolor=fig.get_facecolor()); plt.close(fig)
im = Image.open(OUT); print(OUT, im.size); assert im.size[0] >= 2400
