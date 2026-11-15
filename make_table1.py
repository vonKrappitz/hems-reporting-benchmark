# -*- coding: utf-8 -*-
"""Build Table 1 and the fillability states from the data file, and check the arithmetic.

Input:   data/table1_cells.csv (separator ';'), 95 cells = 19 metrics x 5 operators
Outputs: output/table1.md, output/fillability_states.json

Every derived cell is recomputed from the values it rests on and compared with the
value in the data file. The script stops with an error if any check fails.
"""
import csv
import json
import sys
from collections import defaultdict

DATA = "data/table1_cells.csv"
OPERATORS = ["Rega", "OAMTC", "ADAC", "DRF", "Norway"]
HEADERS = ["Rega", "ÖAMTC", "ADAC", "DRF", "Air Ambulance Services of Norway"]

METRICS = [
    ("A", "Annual missions (operator-reported total)"),
    ("A", "Annual missions (harmonised clinical total)"),
    ("A", "Permanent bases"),
    ("A", "24/7 bases"),
    ("A", "% of bases 24/7"),
    ("A", "Helicopters in fleet"),
    ("A", "Missions per base / year"),
    ("A", "Missions per helicopter / year"),
    ("B", "Primary missions"),
    ("B", "Secondary missions"),
    ("B", "Secondary mission share %"),
    ("B", "Night missions %"),
    ("B", "Stations with winch"),
    ("B", "Stations with NVIS/NVG"),
    ("B", "IFR stations"),
    ("B", "PinS approaches"),
    ("B", "Stations with blood/plasma"),
    ("B", "Annual flight hours"),
    ("DEN", "Missed-mission denominator"),
]

# The dagger does not mark harmonisation, which is carried by the cell state.
# It marks a metric whose value misleads when read directly, until the
# definitional rule given in the table notes is applied.
DAGGER = {"Annual missions (operator-reported total)", "24/7 bases",
          "% of bases 24/7", "Primary missions", "Secondary missions",
          "Night missions %", "Stations with winch", "IFR stations",
          "Annual flight hours"}

# Inputs of the derived cells that are not cells of the table themselves.
FLEET_FOR_DENSITY = {"Rega": 20, "OAMTC": 32, "ADAC": 55, "DRF": 50, "Norway": 14}
NIGHT_MISSIONS = {"Rega": 2848, "OAMTC": 1286, "ADAC": 3159, "DRF": 4058}

STATES = ("reported", "derived", "harmonised", "missing")


def load():
    cells = {}
    with open(DATA, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            cells[(r["tier"], r["metric"], r["operator"])] = r
    return cells


def num(s):
    s = s.replace("~", "").replace("%", "").replace(" ", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def check_arithmetic(cells):
    """Recompute every derived cell and compare it with the data file."""
    errors, ok = [], 0

    def v(metric, op):
        return cells[[k for k in cells if k[1] == metric and k[2] == op][0]]["value"]

    # density and share indicators use the harmonised clinical total
    missions = {op: num(v("Annual missions (harmonised clinical total)", op))
                for op in OPERATORS}

    def check(name, expected_str, computed, digits):
        nonlocal ok
        e = num(expected_str)
        if e is None:
            return
        if abs(round(computed, digits) - e) <= 0.5 * 10 ** (-digits) + 1e-9:
            ok += 1
        else:
            errors.append(f"{name}: data file {expected_str} vs computed "
                          f"{round(computed, digits)}")

    for op in OPERATORS:
        bases = num(v("Permanent bases", op))
        b247 = num(v("24/7 bases", op))
        if b247 is not None and bases:
            check(f"% of bases 24/7 {op}", v("% of bases 24/7", op), 100 * b247 / bases, 1)
        check(f"missions per base {op}", v("Missions per base / year", op),
              missions[op] / bases, 0)
        check(f"missions per helicopter {op}", v("Missions per helicopter / year", op),
              missions[op] / FLEET_FOR_DENSITY[op], 0)
        sec = num(v("Secondary missions", op))
        if sec is not None:
            check(f"secondary share {op}", v("Secondary mission share %", op),
                  100 * sec / missions[op], 1)
        if op in NIGHT_MISSIONS:
            check(f"night share {op}", v("Night missions %", op),
                  100 * NIGHT_MISSIONS[op] / missions[op], 1)
    return errors, ok


def table(cells):
    lines = ["| Tier | Metric | " + " | ".join(HEADERS) + " |",
             "|---|---|---|---|---|---|---|"]
    for tier, m in METRICS:
        name = m + " †" if m in DAGGER else m
        t = "-" if tier == "DEN" else tier
        row = [cells[(tier, m, op)]["value"] for op in OPERATORS]
        lines.append(f"| {t} | {name} | " + " | ".join(row) + " |")
    return "\n".join(lines)


def states(cells):
    """Fillability states per tier for Figure 1 (matrix) and Figure 2 (bars)."""
    rows, counts = [], defaultdict(lambda: defaultdict(int))
    for tier, m in METRICS:
        row = []
        for op in OPERATORS:
            st = cells[(tier, m, op)]["state"]
            assert st in STATES, st
            row.append(st)
            counts[tier][st] += 1
        rows.append({"tier": tier, "metric": m, "dagger": m in DAGGER, "states": row})
    return {"matrix": rows, "counts": {t: dict(c) for t, c in counts.items()},
            "operators": HEADERS}


def main():
    cells = load()
    if len(cells) != 95:
        print(f"ERROR: expected 95 cells, found {len(cells)}")
        sys.exit(1)
    errors, ok = check_arithmetic(cells)
    with open("output/table1.md", "w", encoding="utf-8") as f:
        f.write(table(cells) + "\n")
    with open("output/fillability_states.json", "w", encoding="utf-8") as f:
        json.dump(states(cells), f, ensure_ascii=False, indent=1)
    print(f"Cells: {len(cells)}. Arithmetic checks passed: {ok}. Errors: {len(errors)}.")
    for e in errors:
        print("  ERROR:", e)
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
