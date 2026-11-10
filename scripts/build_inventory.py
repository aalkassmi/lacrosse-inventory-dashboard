"""Build data/inventory.json for the La Crosse Inventory Performance dashboard.

Usage:  python3 scripts/build_inventory.py --src <path to wieland data/inventory.json> [--today YYYY-MM-DD]

La Crosse (dealer 967) is one of the five stores in the Wieland Regional dashboard
(repo aalkassmi/wieland-inventory-dashboard), whose Monday refresh already pulls Motive listings and
Mixpanel activity for it. This script slices that file to La Crosse so both pages always show the same
numbers. Exits non-zero and writes nothing if a check fails.
"""
import argparse, datetime as dt, json, os, sys

STORE, NAME, DEALER = "Premier Truck Group of La Crosse", "La Crosse", 967
OUT = "data/inventory.json"
KEYS = ["s", "c", "n", "v", "ad", "l", "k", "p", "d", "on", "t"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--today", default=dt.date.today().isoformat())
    a = ap.parse_args()
    src = json.load(open(a.src))
    prev = json.load(open(OUT)) if os.path.exists(OUT) else None
    today = dt.date.fromisoformat(a.today)

    units = [{k: u.get(k, False if k == "t" else None) for k in KEYS} for u in src["units"] if u.get("loc") == NAME]
    units.sort(key=lambda u: (-(u["l"] + u["k"]), -u["v"]))

    problems = []
    if src.get("dealer_ids", {}).get(NAME) != DEALER:
        problems.append("source file has no La Crosse (967) store")
    on = [u for u in units if u["on"]]
    if not any(u["c"] == "New" for u in on) and not any(u["c"] == "Used" for u in on):
        problems.append("no listed units")
    V = sum(u["v"] for u in units)
    if V == 0:
        problems.append("zero views")
    if prev:
        PV = sum(u["v"] for u in prev["units"])
        if PV and V < 0.25 * PV:
            problems.append(f"total views {V} is below 25% of last file ({PV})")
    if problems:
        print("NOT WRITTEN:\n  " + "\n  ".join(problems)); sys.exit(1)

    out = {"store": STORE, "dealer_id": DEALER, "window_label": src["window_label"],
           "age_as_of": src["age_as_of"], "updated": f"{today.strftime('%b')} {today.day}, {today.year}",
           "units": units}
    json.dump(out, open(OUT, "w"), indent=1)

    ag = [u["d"] for u in on if u["d"] is not None]
    print(f"window {out['window_label']} | units {len(units)} | listed new {sum(u['c']=='New' for u in on)} "
          f"used {sum(u['c']=='Used' for u in on)} | views {V}" + (f" (last file {PV})" if prev else "")
          + f" | leads {sum(u['l'] for u in units)} calls {sum(u['k'] for u in units)}"
          + f" | avg age {round(sum(ag)/len(ag)) if ag else '-'} | no price {sum(u['p']==0 for u in on)}"
          + f" | listed w/ 0 views {sum(u['v']==0 for u in on)}")
    top = sorted(on, key=lambda u: (-(u["l"] + u["k"]), -u["v"]))[:3]
    print("top listed: " + "; ".join(f"{u['s']} {u['n']} ({u['l']} leads, {u['k']} calls)" for u in top))
    old = [u for u in on if u["c"] == "New" and (u["d"] or 0) >= 365]
    print(f"new units 365+ days: {len(old)} " + ", ".join(f"{u['s']} {u['d']}d" for u in old))


if __name__ == "__main__":
    main()
