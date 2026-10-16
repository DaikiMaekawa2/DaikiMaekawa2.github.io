#!/usr/bin/env python3
"""Generate _includes/reach-map.svg: a dot-matrix silhouette of Singapore,
grouped by its five URA regions, for the "Our Reach" section.

    python3 scripts/make_reach_map.py path/to/planning_area_boundary.geojson

Source: URA "Master Plan 2019 Planning Area Boundary (No Sea)" GeoJSON from
data.gov.sg (Singapore Open Data Licence; the attribution line sits under
the map). Download it from data.gov.sg; it is ~2MB, so it is not committed.

The output is deliberately REGION-LEVEL only: no venue positions are drawn
(see CLAUDE.md, Confidentiality). It is static, so it needs no JavaScript
and no third-party origin, and it only needs regenerating if the design
changes, never when the business grows.
"""

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent.parent
OUT = SITE_DIR / "_includes" / "reach-map.svg"

STEP = 0.0068          # grid spacing in degrees of longitude (~750 m)
SCALE = 1600           # px per degree of longitude
PAD = 14
REGION_KEYS = {
    "CENTRAL REGION": "central", "EAST REGION": "east", "WEST REGION": "west",
    "NORTH REGION": "north", "NORTH-EAST REGION": "north-east",
}
# Region labels are positioned on each region's dot centroid, nudged so
# they sit inside the land mass rather than straddling a coast.
LABEL_NUDGE = {"central": (0, 14), "east": (6, 0), "west": (-4, 0),
               "north": (0, -4), "north-east": (2, -6)}
# Leave out the offshore island planning areas: they read as noise at
# this scale and none of them host events.
SKIP_AREAS = {"WESTERN ISLANDS", "NORTH-EASTERN ISLANDS", "SOUTHERN ISLANDS"}


def rings(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    return [poly[0] for poly in geom["coordinates"]]


def inside(x, y, ring):
    hit = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][:2]
        xj, yj = ring[j][:2]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            hit = not hit
        j = i
    return hit


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    data = json.loads(Path(sys.argv[1]).read_text())
    areas = []
    for f in data["features"]:
        p = f["properties"]
        if p["PLN_AREA_N"] in SKIP_AREAS:
            continue
        rs = rings(f["geometry"])
        xs = [c[0] for r in rs for c in r]
        ys = [c[1] for r in rs for c in r]
        areas.append((REGION_KEYS[p["REGION_N"]], rs, (min(xs), min(ys), max(xs), max(ys))))

    lon0 = min(a[2][0] for a in areas); lon1 = max(a[2][2] for a in areas)
    lat0 = min(a[2][1] for a in areas); lat1 = max(a[2][3] for a in areas)
    kx = SCALE
    ky = SCALE / math.cos(math.radians((lat0 + lat1) / 2))  # keep shapes true
    step_lat = STEP * kx / ky                                 # square grid on screen

    dots = defaultdict(list)
    lat = lat1
    while lat >= lat0:
        lon = lon0
        while lon <= lon1:
            for region, rs, (a, b, c, d) in areas:
                if a <= lon <= c and b <= lat <= d and any(inside(lon, lat, r) for r in rs):
                    dots[region].append((round((lon - lon0) * kx + PAD, 1),
                                         round((lat1 - lat) * ky + PAD, 1)))
                    break
            lon += STEP
        lat -= step_lat

    w = round((lon1 - lon0) * kx + 2 * PAD)
    h = round((lat1 - lat0) * ky + 2 * PAD)
    out = [f'<svg class="reach-map" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
           'role="img" aria-labelledby="reach-map-title">',
           '<title id="reach-map-title">{{ t.reach.map_aria }}</title>']
    for region in REGION_KEYS.values():
        pts = dots[region]
        d = "".join(f"M{x} {y}h0" for x, y in pts)
        out.append(f'<path class="reach-dots reach-{region}" d="{d}"/>')
    for region in REGION_KEYS.values():
        pts = dots[region]
        cx = sum(p[0] for p in pts) / len(pts) + LABEL_NUDGE[region][0]
        cy = sum(p[1] for p in pts) / len(pts) + LABEL_NUDGE[region][1]
        key = region.replace("-", "_")
        out.append(f'<text class="reach-label" x="{cx:.0f}" y="{cy:.0f}">{{{{ t.reach.regions.{key} }}}}</text>')
    out.append("</svg>")
    OUT.write_text("\n".join(out) + "\n")
    total = sum(len(v) for v in dots.values())
    print(f"wrote {OUT.relative_to(SITE_DIR)}: {total} dots, {w}x{h}, "
          f"{OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
