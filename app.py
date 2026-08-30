import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# ============================================================
# PAGE CONFIG (must be first Streamlit call)
# ============================================================
st.set_page_config(
    page_title="Audit Web Portal | Internal Audit Activities",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# BRAND COLORS (kept from the original app: orange + navy blue,
# same accent Yashoda's site uses for its nav underline)
# ============================================================
ORANGE = "#FF8C00"
NAVY = "#004AAD"
NAVY_DEEP = "#00337A"
PAPER = "#F5F7FA"
PANEL = "#FFFFFF"
BORDER = "#E5E9F0"
MUTED = "#64748B"
GREEN = "#15803D"

# ============================================================
# DATA LOADING
#   - looks for ONLINE2.xlsx bundled next to this script first
#     (fixes the old hardcoded H:\RAM\ONLINE2.xlsx path, which
#      only worked on one specific office PC)
#   - falls back to a sidebar uploader if the file isn't found,
#     so the portal never just shows a blank page
# ============================================================
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "ONLINE2.xlsx")
REQUIRED_COLS = ["AUDIT DIVISION", "DEPARTMENT", "AUDIT ACTIVITY", "LINKS"]


@st.cache_data
def load_data(source):
    df = pd.read_excel(source, sheet_name="HTC")
    df.columns = [str(c).strip().upper() for c in df.columns]
    for col in REQUIRED_COLS:
        if col not in df.columns:
            df[col] = pd.NA
    df["AUDIT DIVISION"] = df["AUDIT DIVISION"].astype(str).str.strip()
    df = df[df["AUDIT DIVISION"].notna() & (df["AUDIT DIVISION"] != "") & (df["AUDIT DIVISION"] != "nan")]
    return df


data_source = DEFAULT_PATH if os.path.exists(DEFAULT_PATH) else None

with st.sidebar:
    st.markdown("### ⚙️ Portal Data")
    uploaded = st.file_uploader("Replace menu data (.xlsx, sheet 'HTC')", type=["xlsx"])
    if uploaded is not None:
        data_source = uploaded
    elif data_source:
        st.caption("Using bundled ONLINE2.xlsx")
    else:
        st.warning("No data file found — upload ONLINE2.xlsx to populate the menu.")

if data_source is None:
    st.error("No audit menu data available. Please upload the ONLINE2.xlsx file from the sidebar.")
    st.stop()

df = load_data(data_source)

# rows with a Department filled in are real, clickable menu entries;
# rows that are just a division name (placeholder) get parked separately
active_rows = df[df["DEPARTMENT"].notna() & (df["DEPARTMENT"].astype(str).str.strip() != "") & (df["DEPARTMENT"].astype(str) != "nan")]
placeholder_divisions = sorted(set(df["AUDIT DIVISION"].unique()) - set(active_rows["AUDIT DIVISION"].unique()))

# ============================================================
# GLOBAL CSS
# ============================================================
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background: {PAPER}; }}
    #MainMenu, footer, header {{ visibility: hidden; }}

    /* ---- top utility bar ---- */
    .util-bar {{
        display: flex; justify-content: space-between; align-items: center;
        background: {NAVY_DEEP}; color: #fff; padding: 6px 26px; font-size: 12.5px;
        margin: -1rem -1rem 0 -1rem; letter-spacing: .02em;
    }}
    .util-bar span {{ color: rgba(255,255,255,.85); }}
    .util-bar b {{ color: {ORANGE}; }}

    /* ---- header ---- */
    .header-wrap {{
        background: {PANEL}; padding: 18px 26px; margin: 0 -1rem 0 -1rem;
        border-bottom: 3px solid {ORANGE};
        display: flex; align-items: center; justify-content: space-between;
    }}
    .header-title {{ text-align: left; }}
    .header-title .line1 {{
        color: {ORANGE}; font-family: 'Poppins', sans-serif; font-weight: 800;
        font-size: 26px; letter-spacing: .01em; line-height: 1.2;
    }}
    .header-title .line2 {{
        color: {NAVY}; font-family: 'Poppins', sans-serif; font-weight: 700;
        font-size: 15px; letter-spacing: .06em; text-transform: uppercase; margin-top: 2px;
    }}
    .header-badge {{
        display: flex; align-items: center; gap: 10px; background: {PAPER};
        border: 1px solid {BORDER}; border-radius: 10px; padding: 8px 16px;
    }}

    /* ---- hero ---- */
    .hero {{
        background: linear-gradient(120deg, {NAVY_DEEP} 0%, {NAVY} 55%, {ORANGE} 150%);
        margin: 0 -1rem 0 -1rem; padding: 46px 26px 40px; color: #fff;
    }}
    .hero h1 {{ font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 32px; margin: 0 0 8px 0; }}
    .hero p {{ font-size: 15px; color: rgba(255,255,255,.85); max-width: 640px; margin: 0; }}
    .hero-stats {{ display: flex; gap: 34px; margin-top: 26px; flex-wrap: wrap; }}
    .hero-stat-num {{ font-family: 'Poppins', sans-serif; font-weight: 800; font-size: 28px; color: {ORANGE}; }}
    .hero-stat-label {{ font-size: 12px; color: rgba(255,255,255,.75); text-transform: uppercase; letter-spacing: .05em; }}

    /* ---- division cards ---- */
    .div-card {{
        background: {PANEL}; border: 1px solid {BORDER}; border-radius: 14px;
        padding: 18px 16px; text-align: center; box-shadow: 0 2px 6px rgba(0,20,60,.05);
        transition: transform .15s ease, box-shadow .15s ease; height: 100%;
    }}
    .div-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 18px rgba(0,20,60,.10); }}
    .div-card .div-name {{
        font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 15px; color: {NAVY}; margin-top: 6px;
    }}
    .div-card .div-count {{ font-size: 12px; color: {MUTED}; margin-top: 2px; }}
    .div-icon {{ font-size: 26px; }}

    /* ---- activity rows ---- */
    .activity-row {{
        display: flex; align-items: center; justify-content: space-between;
        background: {PANEL}; border: 1px solid {BORDER}; border-radius: 10px;
        padding: 12px 16px; margin-bottom: 8px;
    }}
    .activity-name {{ font-weight: 600; font-size: 14px; color: #1E293B; }}
    .activity-dept {{ font-size: 12px; color: {MUTED}; }}
    .badge-live {{
        background: #E7F6EC; color: {GREEN}; font-size: 11px; font-weight: 700;
        padding: 3px 10px; border-radius: 20px; letter-spacing: .03em;
    }}
    .badge-soon {{
        background: #FFF3E0; color: {ORANGE}; font-size: 11px; font-weight: 700;
        padding: 3px 10px; border-radius: 20px; letter-spacing: .03em;
    }}
    .dept-heading {{
        font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 14px;
        color: {NAVY}; margin: 18px 0 8px 0; padding-bottom: 4px; border-bottom: 2px solid {BORDER};
    }}

    /* ---- footer ---- */
    .footer {{
        background: {NAVY_DEEP}; color: rgba(255,255,255,.75); margin: 40px -1rem -1rem -1rem;
        padding: 24px 26px; font-size: 12.5px; text-align: center;
    }}
    .footer b {{ color: {ORANGE}; }}

    div.stButton > button {{
        border-radius: 8px; border: 1px solid {BORDER}; background: {PANEL};
        font-weight: 600; font-size: 13px;
    }}
    div.stButton > button:hover {{ border-color: {ORANGE}; color: {ORANGE}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# TOP UTILITY BAR
# ============================================================
now = datetime.now().strftime("%d %b %Y, %I:%M %p")
st.markdown(
    f"""
    <div class="util-bar">
        <span>🛡️ <b>Internal Audit Portal</b> &nbsp;|&nbsp; Verification &amp; Compliance Tools</span>
        <span>📅 {now} &nbsp;|&nbsp; Audit Helpdesk: <b>ext. 2200</b></span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HEADER
# ============================================================
st.markdown(
    f"""
    <div class="header-wrap">
        <div class="header-title">
            <div class="line1">WELCOME TO AUDIT DEPARTMENT</div>
            <div class="line2">Internal Audit Activities — Auto Verification Tool</div>
        </div>
        <div class="header-badge">
            <span style="font-size:22px;">🏥</span>
            <div>
                <div style="font-weight:700;color:{NAVY};font-size:13px;">Hospital Internal Audit</div>
                <div style="font-size:11px;color:{MUTED};">Digital Verification Suite</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HERO with live counts pulled from the actual data
# ============================================================
n_divisions = df["AUDIT DIVISION"].nunique()
n_departments = active_rows["DEPARTMENT"].nunique()
n_activities = active_rows["AUDIT ACTIVITY"].nunique()
n_live_tools = active_rows["LINKS"].notna().sum()

st.markdown(
    f"""
    <div class="hero">
        <h1>Find & Run Your Audit Verification Tool</h1>
        <p>Browse by Audit Division, drill into a Department, and launch the right verification
           activity — all from one place. Divisions without a live tool yet are marked
           <b>Coming Soon</b>.</p>
        <div class="hero-stats">
            <div><div class="hero-stat-num">{n_divisions}</div><div class="hero-stat-label">Audit Divisions</div></div>
            <div><div class="hero-stat-num">{n_departments}</div><div class="hero-stat-label">Departments</div></div>
            <div><div class="hero-stat-num">{n_activities}</div><div class="hero-stat-label">Audit Activities</div></div>
            <div><div class="hero-stat-num">{n_live_tools}</div><div class="hero-stat-label">Live Tools</div></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# ============================================================
# SEARCH BAR (Yashoda-style: search + two filter dropdowns)
# ============================================================
search_col, div_col, dept_col = st.columns([2, 1, 1])
with search_col:
    search_term = st.text_input("🔍 Search audit activity", placeholder="e.g. cash collection, pay sheet...")
with div_col:
    division_filter = st.selectbox("Audit Division", ["All Divisions"] + sorted(df["AUDIT DIVISION"].unique().tolist()))
with dept_col:
    dept_options = ["All Departments"] + sorted(active_rows["DEPARTMENT"].dropna().unique().tolist())
    department_filter = st.selectbox("Department", dept_options)

st.write("")

# ============================================================
# QUICK-ACCESS DIVISION CARDS
# ============================================================
if "selected_division" not in st.session_state:
    st.session_state.selected_division = None

st.markdown("#### 🗂️ Browse by Audit Division")
division_counts = active_rows.groupby("AUDIT DIVISION")["AUDIT ACTIVITY"].count().to_dict()
all_divisions = sorted(df["AUDIT DIVISION"].unique())
icons = ["🏢", "💰", "🧾", "🩺", "💊", "🏬", "📋", "⚕️", "📊"]

cols = st.columns(min(len(all_divisions), 7))
for i, division in enumerate(all_divisions):
    count = division_counts.get(division, 0)
    with cols[i % len(cols)]:
        st.markdown(
            f"""
            <div class="div-card">
                <div class="div-icon">{icons[i % len(icons)]}</div>
                <div class="div-name">{division}</div>
                <div class="div-count">{count} activit{'y' if count == 1 else 'ies'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("View", key=f"btn_{division}", use_container_width=True):
            st.session_state.selected_division = division

st.write("")
st.markdown("---")

# ============================================================
# FILTERED ACTIVITY LISTING
# ============================================================
filtered = active_rows.copy()

if st.session_state.selected_division:
    filtered = filtered[filtered["AUDIT DIVISION"] == st.session_state.selected_division]
    header_note = f"Showing: **{st.session_state.selected_division}**"
    if st.button("✖ Clear division filter"):
        st.session_state.selected_division = None
        st.rerun()
else:
    header_note = "Showing: **All Divisions**"

if division_filter != "All Divisions":
    filtered = filtered[filtered["AUDIT DIVISION"] == division_filter]
if department_filter != "All Departments":
    filtered = filtered[filtered["DEPARTMENT"] == department_filter]
if search_term:
    filtered = filtered[filtered["AUDIT ACTIVITY"].str.contains(search_term, case=False, na=False)]

st.markdown(f"#### 📌 Audit Activities &nbsp;·&nbsp; {header_note}")

if filtered.empty:
    st.info("No audit activities match this filter yet.")
else:
    for division in sorted(filtered["AUDIT DIVISION"].unique()):
        div_df = filtered[filtered["AUDIT DIVISION"] == division]
        st.markdown(f"**{division}**")
        for department in sorted(div_df["DEPARTMENT"].unique()):
            st.markdown(f'<div class="dept-heading">{department}</div>', unsafe_allow_html=True)
            dept_rows = div_df[div_df["DEPARTMENT"] == department]
            for _, row in dept_rows.iterrows():
                link = row["LINKS"]
                has_link = pd.notna(link) and str(link).strip() not in ("", "nan")
                c1, c2 = st.columns([4, 1])
                with c1:
                    badge = '<span class="badge-live">● LIVE</span>' if has_link else '<span class="badge-soon">COMING SOON</span>'
                    st.markdown(
                        f"""
                        <div class="activity-row">
                            <div>
                                <div class="activity-name">{row['AUDIT ACTIVITY']}</div>
                                <div class="activity-dept">{department}</div>
                            </div>
                            {badge}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c2:
                    if has_link:
                        st.link_button("Open Tool ↗", str(link).strip(), use_container_width=True)

# ============================================================
# PLACEHOLDER DIVISIONS (no departments yet)
# ============================================================
if placeholder_divisions:
    with st.expander(f"🕒 Divisions awaiting setup ({len(placeholder_divisions)})"):
        st.write(", ".join(placeholder_divisions))
        st.caption("These divisions exist in the menu data but have no departments or activities mapped yet.")

# ============================================================
# FOOTER
# ============================================================
st.markdown(
    f"""
    <div class="footer">
        <b>Internal Audit Portal</b> &nbsp;|&nbsp; Auto Verification Tool Suite<br>
        For access issues or to add a new audit activity, contact the Audit Helpdesk.<br>
        © {datetime.now().year} — All internal audit tools are for authorized hospital staff use only.
    </div>
    """,
    unsafe_allow_html=True,
)
