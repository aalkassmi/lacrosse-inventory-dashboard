# La Crosse Inventory Performance

Static page showing every Premier Truck Group of La Crosse unit (new and used) with listing views, Google Ads share, leads, calls, price, days on lot and listing status. Same layout as the Chattanooga page.

- `index.html`: the page (no build step).
- `data/inventory.json`: the data. A refresh only replaces this file.
- `scripts/build_inventory.py`: builds the data by slicing La Crosse (dealer 967) out of the Wieland Regional dashboard's data file, so the two pages always match.

Sources: Mixpanel project 3822144 (dealer ID 967) for activity; Motive for live inventory and price.

Hosted on Cloudflare Workers, auto-deploying from `main`.

## Weekly refresh

A scheduled task runs every Monday after the Wieland Regional refresh. It reads `data/inventory.json` from `aalkassmi/wieland-inventory-dashboard`, runs `python3 scripts/build_inventory.py --src <that file>`, and pushes only `data/inventory.json`. If Wieland hasn't refreshed yet (same window as last week), or a sanity check fails, nothing is pushed and the site keeps last week's data.
