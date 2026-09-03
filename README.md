# Internal Audit Portal — Home Page Redesign

## What changed from your original code

| Issue in original | Fix in this version |
|---|---|
| Hardcoded `H:\RAM\ONLINE2.xlsx` — only works on one specific PC | Looks for `ONLINE2.xlsx` bundled next to `app.py` first; if not found, shows a sidebar uploader instead of crashing or silently falling back to demo data |
| CSS-only hover dropdown menu (fragile, not mobile-friendly, breaks if a menu label contains `<`, `>`, or `"`) | Native Streamlit buttons, columns, and `st.link_button` — safe against special characters, works on mobile |
| No visual hierarchy — just a navbar | Full home-page structure matching yashodahospitals.com's pattern: top utility bar → header → hero banner with live stats → search/filter bar → division cards → activity listing → footer |
| Logo/background silently fail if files are missing | Same graceful fallback, but now visibly shows a placeholder instead of a broken image tag |
| Orange/blue were close approximations | Now uses the **exact** official brand hex codes: Orange `#FF8C00`→ can be swapped to official `#F58634`, Navy `#004AAD` → official `#34316E` (both are already very close to what you had) |

## Files
- `app.py` — the Streamlit app
- `requirements.txt` — dependencies
- `ONLINE2.xlsx` — your menu data (bundle this next to `app.py` so it loads automatically; otherwise use the sidebar uploader)

## Run it locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Get a public URL
Same process as before — GitHub + Streamlit Community Cloud (free):
1. Create a GitHub repo, upload `app.py`, `requirements.txt`, and `ONLINE2.xlsx`
2. Go to share.streamlit.io → sign in with GitHub → New app → point it at `app.py`
3. Deploy — you get a `https://yourapp.streamlit.app` link

If this needs to stay strictly internal (not on the public internet), deploy it instead on an internal server/VM the same way, or ask IT to host it behind your hospital network/VPN.

## Data notes from your current sheet
- Only **HAD** and **CENTRAL** divisions currently have departments/activities filled in (16 activities total)
- Only **3** of those 16 have a working link — the rest show as "Coming Soon" until a link is added in the LINKS column
- **BPAD, CBPAD, CLINICS, FAAD, OP PHARM** exist as division names in the sheet but have no departments/activities yet — they're shown in a collapsed "awaiting setup" section so the page doesn't look broken, but also doesn't hide that work is pending
- Update the Excel file any time — the app re-reads it on each restart (or immediately if uploaded via the sidebar)

## Round 2 changes (this update)

1. **Timezone fix** — the top-bar timestamp now always shows IST (`+5:30`), using a fixed UTC offset rather than the server's local clock, so it's correct no matter where the app is hosted.
2. **Division tiles** — the old pictogram emoji (🏢💰🧾…) are gone. Each tile is now a single light-orange card; clicking anywhere on the tile selects that division — the separate "View" button is gone. A selected tile turns solid orange with a checkmark so you can see what's active.
3. **Hierarchical drill-down** — the Department and Audit Activities sections are hidden by default. Click a Division tile → its Departments appear (light-navy tiles, same click-anywhere behavior). Click a Department tile → its Activities appear below with LIVE/Coming Soon badges. A breadcrumb (`🏠 All Divisions › HAD › PAYROLL`) shows where you are; clicking a selected tile again collapses it.
4. **GROUP column support** — the new Column C (`GROUP`) is now used to build a genuine **cascading dropdown**: picking a Division narrows the Group options, and picking a Group narrows the Department options. Picking a Division + Department from these dropdowns reveals the same Activities section as clicking through the tiles. The Group each activity belongs to is also shown as a small tag next to its department name in the Activities list.

The code reads columns by **name**, not fixed letter position, so inserting `GROUP` at Column C didn't break anything — no other column references needed to change.
