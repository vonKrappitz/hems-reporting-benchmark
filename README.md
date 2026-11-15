# HEMS reporting benchmark: data and code

This repository reproduces Table 1, Table 2, Figure 1 and Figure 2 of a benchmark of the
public operational reporting of five European helicopter emergency medical services,
2020 to 2024. The accompanying manuscript is under review, and its full reference will be
added here on publication.

Every value in the tables and every cell of the figures is produced by the scripts here
from the data files here. Nothing is typed into a figure by hand.

## How to run

    pip install -r requirements.txt
    python make_table1.py             # Table 1, fillability states, 19 arithmetic checks
    python check_missed_missions.py   # share of requests without a completed mission, 2020 to 2024
    python make_figures.py            # Figure 1 and Figure 2 as PNG, TIFF and SVG
    python check_label_collisions.py  # confirms that no labels overlap

Run the commands from the repository root. Results are written to `output/`.

## Contents

| Path | What it holds |
|---|---|
| `data/table1_cells.csv` | The 95 cells of Table 1, that is 19 metrics for 5 operators, each with its fillability state and its source |
| `data/table2_direct_disclosure.csv` | The 13 fields of Table 2, which fill only under direct disclosure |
| `data/norway_missed_missions_2020_2024.csv` | Declined, aborted and completed requests per year for the one service that disclosed them |
| `make_table1.py` | Builds Table 1 and the state matrix, and recomputes every derived cell |
| `make_figures.py` | Draws both figures from the state matrix |
| `check_missed_missions.py` | Recomputes the yearly share of requests that did not end in a completed mission |
| `check_label_collisions.py` | Checks both figures for overlapping text |
| `output/` | The generated table, state matrix and figures |

## Data dictionary, `data/table1_cells.csv`

| Column | Meaning |
|---|---|
| `tier` | `A` mandatory core, `B` conditional tier, `DEN` missed-mission denominator |
| `metric` | Name of the indicator as printed in Table 1 |
| `operator` | `Rega`, `OAMTC`, `ADAC`, `DRF` or `Norway` |
| `value` | Value as printed in Table 1. A tilde marks an approximation, `n.d.` marks no data |
| `state` | `reported`, `derived`, `harmonised` or `missing` |
| `source` | Public document the value was read from, or the note that it is computed or not publicly reported |
| `location` | Page of the source, or the calculation behind a derived value |

The four states follow the Methods of the manuscript. A value is `reported` when the operator
publishes it directly, `derived` when it is computed from published values, `harmonised` when
it becomes comparable only after a stated rule, and `missing` when public reporting does not
contain it.

## Sources

Table 1 rests on public annual and activity reports only, read in the same way for all five
operators. Table 2 and the yearly series of declined and aborted requests are aggregate counts
supplied directly by one operator. The repository contains no patient-level data.

## Reproducibility

The figures in `output/` were generated with the library versions pinned in `requirements.txt`.
With those versions the TIFF files reproduce bit for bit.

    sha256, first 16 characters
    e0b3cb6809b99745  output/figure1_fillability_matrix.tif
    d61b16891b6f1076  output/figure2_states_by_tier.tif

Other Matplotlib versions draw the same figures from the same data, with a crop that may
differ by a few pixels.
