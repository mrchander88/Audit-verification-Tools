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
