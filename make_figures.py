# -*- coding: utf-8 -*-
"""Draw Figures 1 and 2 from output/fillability_states.json (written by make_table1.py).

Figure 1. Fillability matrix, one cell per metric and operator, value printed in the cell.
Figure 2. Stacked shares of the four fillability states per tier, counts printed in the bars.
Each figure is written as PNG (300 dpi), TIFF (1000 dpi, LZW) and SVG.
"""
import csv
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch

COLOUR = {"reported": "#2f7a36", "derived": "#7fb069",
          "harmonised": "#e8930c", "missing": "#b8b8b8"}
LABEL = {"reported": "reported", "derived": "derived",
         "harmonised": "harmonised (rule applied)", "missing": "missing"}

with open("output/fillability_states.json", encoding="utf-8") as f:
    S = json.load(f)
value = {}
with open("data/table1_cells.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter=";"):
        value[(r["metric"], r["operator"])] = r["value"]
OPS = ["Rega", "OAMTC", "ADAC", "DRF", "Norway"]
HEAD = ["Rega", "ÖAMTC", "ADAC", "DRF", "Air Ambulance\nServices of Norway"]

# ---------- Figure 1. Fillability matrix ----------
rows = S["matrix"]
n_r, n_c = len(rows), len(OPS)
fig, ax = plt.subplots(figsize=(9.5, 8.2))
for i, w in enumerate(rows):
    y = n_r - 1 - i
    for j, st in enumerate(w["states"]):
        ax.add_patch(Rectangle((j, y), 1, 1, facecolor=COLOUR[st],
                               edgecolor="white", linewidth=1.4))
        v = value[(w["metric"], OPS[j])]
        ax.text(j + 0.5, y + 0.5, v, ha="center", va="center",
                fontsize=7.2, color="white" if st != "missing" else "#444")
ticks = [("† " if w["dagger"] else "") + w["metric"] for w in rows]
ax.set_yticks([n_r - 1 - i + 0.5 for i in range(n_r)])
ax.set_yticklabels(ticks, fontsize=8)
ax.set_xticks([j + 0.5 for j in range(n_c)])
ax.set_xticklabels(HEAD, fontsize=9)
ax.xaxis.tick_top()
# tier separators are placed from the tier field of the data, not hard-coded
nA = sum(1 for w in rows if w["tier"] == "A")
nB = sum(1 for w in rows if w["tier"] == "B")
for gr in (nA, nA + nB):
    ax.axhline(n_r - gr, color="black", linewidth=1.1)
ax.set_xlim(0, n_c); ax.set_ylim(0, n_r)
ax.tick_params(length=0)
for sp in ax.spines.values():
    sp.set_visible(False)
ax.text(n_c + 0.15, n_r - nA / 2, "Tier A", rotation=270, va="center", ha="left",
        transform=ax.transData, fontsize=9, fontweight="bold")
ax.text(n_c + 0.15, n_r - nA - nB / 2, "Tier B", rotation=270, va="center", ha="left",
        transform=ax.transData, fontsize=9, fontweight="bold")
ax.text(0.5, -0.085, "† value cannot be read across operators without the rule stated in the table notes",
        transform=ax.transAxes, ha="center", va="top", fontsize=8.5, color="#444")
ax.legend(handles=[Patch(facecolor=COLOUR[k], label=LABEL[k]) for k in COLOUR],
          loc="upper center", bbox_to_anchor=(0.5, -0.005), ncol=3, frameon=False,
          fontsize=8)
plt.tight_layout()
plt.savefig("output/figure1_fillability_matrix.png", dpi=300, bbox_inches="tight")
plt.savefig("output/figure1_fillability_matrix.tif", dpi=1000, bbox_inches="tight", pil_kwargs={"compression": "tiff_lzw"})
plt.savefig("output/figure1_fillability_matrix.svg", bbox_inches="tight")
plt.close()

# ---------- Figure 2. Stacked bars ----------
tiers = ["A", "B", "DEN"]
tier_names = ["Tier A", "Tier B", "Missed-mission\ndenominator"]
fig, ax = plt.subplots(figsize=(6.4, 4.4))
for x, t in enumerate(tiers):
    total = sum(S["counts"][t].values())
    bottom = 0.0
    for st in ["reported", "derived", "harmonised", "missing"]:
        n = S["counts"][t].get(st, 0)
        if n == 0:
            continue
        share = 100.0 * n / total
        ax.bar(x, share, bottom=bottom, color=COLOUR[st], width=0.62,
               edgecolor="white")
        ax.text(x, bottom + share / 2, str(n), ha="center", va="center",
                fontsize=10, color="white" if st != "missing" else "#333",
                fontweight="bold")
        bottom += share
ax.set_xticks(range(len(tiers)))
ax.set_xticklabels(tier_names, fontsize=9)
ax.set_ylabel("Share of cells (%)", fontsize=9)
ax.set_ylim(0, 100)
ax.legend(handles=[Patch(facecolor=COLOUR[k], label=LABEL[k]) for k in COLOUR],
          loc="upper center", bbox_to_anchor=(0.5, -0.10), ncol=3, frameon=False,
          fontsize=8)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
plt.tight_layout()
plt.savefig("output/figure2_states_by_tier.png", dpi=300, bbox_inches="tight")
plt.savefig("output/figure2_states_by_tier.tif", dpi=1000, bbox_inches="tight", pil_kwargs={"compression": "tiff_lzw"})
plt.savefig("output/figure2_states_by_tier.svg", bbox_inches="tight")
plt.close()
print("Figures written to output/.")
