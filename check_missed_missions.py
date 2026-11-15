# -*- coding: utf-8 -*-
"""Recompute the share of requests that did not end in a completed mission, 2020 to 2024.

Input: data/norway_missed_missions_2020_2024.csv (aggregate counts supplied directly by one operator).
share = (declined + aborted) / (declined + aborted + completed)
"""
import csv
import sys

errors = 0
with open("data/norway_missed_missions_2020_2024.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter=";"):
        d, a, c = int(r["declined"]), int(r["aborted"]), int(r["completed_hems"])
        total = d + a + c
        share = round(100 * (d + a) / total, 1)
        ok = total == int(r["requests_total"]) and f"{share}%" == r["share_not_completed"]
        errors += not ok
        print(r["year"], "requests", total, "not completed", d + a, f"share {share}%", "OK" if ok else "MISMATCH")
sys.exit(1 if errors else 0)
