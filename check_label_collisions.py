# -*- coding: utf-8 -*-
"""Programmatic check that no two text labels overlap on either figure.

Re-runs make_figures.py while capturing the figures before they are closed, reads the
bounding boxes of all text artists after rendering, and counts pairs whose overlap
exceeds a small tolerance. Exits with an error if any collision is found.
"""
import itertools
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AREA_TOLERANCE = 2.0  # px^2, allows anti-aliasing contact


def collisions(fig):
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    texts = []
    for ax in fig.get_axes():
        arts = list(ax.texts) + ax.get_xticklabels() + ax.get_yticklabels()
        leg = ax.get_legend()
        if leg is not None:
            arts += leg.get_texts()
        for t in arts:
            if not t.get_text().strip():
                continue
            texts.append((t.get_text(), t.get_window_extent(renderer=rend)))
    pairs = []
    for (t1, b1), (t2, b2) in itertools.combinations(texts, 2):
        w = min(b1.x1, b2.x1) - max(b1.x0, b2.x0)
        h = min(b1.y1, b2.y1) - max(b1.y0, b2.y0)
        if w > 0 and h > 0 and w * h > AREA_TOLERANCE:
            pairs.append((t1, t2, round(w * h, 1)))
    return pairs


def main():
    captured = []
    orig_close = plt.close

    def capture(f=None):
        if f is not None and hasattr(f, "canvas"):
            captured.append(f)
        elif plt.get_fignums():
            captured.append(plt.gcf())
        orig_close(f)

    plt.close = capture
    with open("make_figures.py", encoding="utf-8") as f:
        exec(compile(f.read(), "make_figures.py", "exec"), {"__name__": "collisions"})
    plt.close = orig_close

    total = 0
    for i, fig in enumerate(captured, 1):
        pairs = collisions(fig)
        print(f"Figure {i}: collisions {len(pairs)}")
        for t1, t2, area in pairs:
            print(f"  COLLISION [{area} px2]: '{t1[:30]}' x '{t2[:30]}'")
        total += len(pairs)
    if total:
        print(f"RESULT: {total} collisions.")
        sys.exit(1)
    print("RESULT: no collisions.")


if __name__ == "__main__":
    main()
