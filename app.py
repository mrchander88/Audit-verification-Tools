import streamlit as st
import pandas as pd
import os
from datetime import datetime, timezone, timedelta

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
# BRAND COLORS
# ============================================================
ORANGE = "#FF8C00"
ORANGE_LIGHT = "#FFE8D1"      # light-orange tile background (Audit Division tiles)
ORANGE_LIGHT_HOVER = "#FFDAB3"
ORANGE_LIGHT_BORDER = "#F5C089"
NAVY = "#004AAD"
NAVY_DEEP = "#00337A"
NAVY_LIGHT = "#E4ECFB"        # light-navy tile background (Department tiles)
NAVY_LIGHT_HOVER = "#D3E0F8"
NAVY_LIGHT_BORDER = "#AFC6EF"
PAPER = "#F5F7FA"
PANEL = "#FFFFFF"
BORDER = "#E5E9F0"
MUTED = "#64748B"
GREEN = "#15803D"

IST = timezone(timedelta(hours=5, minutes=30))  # fixed offset — no DST, no tzdata dependency

# ============================================================
# DATA LOADING
# ============================================================
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "ONLINE2.xlsx")
REQUIRED_COLS = ["AUDIT DIVISION", "GROUP", "DEPARTMENT", "AUDIT ACTIVITY", "LINKS"]


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

# Safety net — guaranteed to run every time regardless of caching behavior.
# If a stale cached result, or a bundled Excel file that predates the GROUP
# column, ever gets through, this still prevents a KeyError anywhere below.
for col in REQUIRED_COLS:
    if col not in df.columns:
        df[col] = pd.NA

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

    /* ---- breadcrumb ---- */
    .crumb {{
        font-size: 13.5px; color: {MUTED}; margin: 4px 0 14px 0;
    }}
    .crumb b {{ color: {NAVY}; }}

    /* ---- section title ---- */
    .section-title {{
        font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 16px;
        color: {NAVY}; margin: 22px 0 12px 0;
    }}

    /* ---- Audit Division tiles: light orange, whole tile clickable ---- */
    div[class*="st-key-tile_div_"] button {{
        background: {ORANGE_LIGHT} !important;
        border: 1px solid {ORANGE_LIGHT_BORDER} !important;
        border-radius: 14px !important;
        padding: 22px 14px !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 700 !important;
        font-size: 14.5px !important;
        color: {NAVY} !important;
        height: 100% !important;
        white-space: normal !important;
        box-shadow: 0 2px 6px rgba(0,20,60,.05) !important;
        transition: transform .15s ease, box-shadow .15s ease, background .15s ease !important;
    }}
    div[class*="st-key-tile_div_"] button:hover {{
        background: {ORANGE_LIGHT_HOVER} !important;
        border-color: {ORANGE} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 18px rgba(255,140,0,.20) !important;
    }}
    div[class*="st-key-tile_div_selected_"] button {{
        background: {ORANGE} !important;
        border-color: {ORANGE} !important;
        color: #fff !important;
    }}

    /* ---- Department tiles: light navy, whole tile clickable ---- */
    div[class*="st-key-tile_dept_"] button {{
        background: {NAVY_LIGHT} !important;
        border: 1px solid {NAVY_LIGHT_BORDER} !important;
        border-radius: 14px !important;
        padding: 18px 14px !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 700 !important;
        font-size: 13.5px !important;
        color: {NAVY} !important;
        height: 100% !important;
        white-space: normal !important;
        transition: transform .15s ease, box-shadow .15s ease, background .15s ease !important;
    }}
    div[class*="st-key-tile_dept_"] button:hover {{
        background: {NAVY_LIGHT_HOVER} !important;
        border-color: {NAVY} !important;
        transform: translateY(-2px) !important;
    }}
    div[class*="st-key-tile_dept_selected_"] button {{
        background: {NAVY} !important;
        border-color: {NAVY} !important;
        color: #fff !important;
    }}

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

    /* ---- footer ---- */
    .footer {{
        background: {NAVY_DEEP}; color: rgba(255,255,255,.75); margin: 40px -1rem -1rem -1rem;
        padding: 24px 26px; font-size: 12.5px; text-align: center;
    }}
    .footer b {{ color: {ORANGE}; }}

    /* default button style for everything else (back links, Open Tool, etc.) */
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
# TOP UTILITY BAR — timestamp in IST
# ============================================================
now_ist = datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")
st.markdown(
    f"""
    <div class="util-bar">
        <span>🛡️ <b>Internal Audit Portal</b> &nbsp;|&nbsp; Verification &amp; Compliance Tools</span>
        <span>📅 {now_ist} &nbsp;|&nbsp; Audit Helpdesk: <b>ext. 2200</b></span>
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
n_groups = active_rows["GROUP"].nunique()
n_departments = active_rows["DEPARTMENT"].nunique()
n_activities = active_rows["AUDIT ACTIVITY"].nunique()
n_live_tools = active_rows["LINKS"].notna().sum()

st.markdown(
    f"""
    <div class="hero">
        <h1>Find & Run Your Audit Verification Tool</h1>
        <p>Click an Audit Division below, then a Department, to reach the verification
           activity you need. Divisions without a live tool yet are marked
           <b>Coming Soon</b>.</p>
        <div class="hero-stats">
            <div><div class="hero-stat-num">{n_divisions}</div><div class="hero-stat-label">Audit Divisions</div></div>
            <div><div class="hero-stat-num">{n_groups}</div><div class="hero-stat-label">Groups</div></div>
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
# DEPENDENT (CASCADING) DROPDOWN FILTER
#   Division -> Group -> Department, each narrowed by the one before it.
#   Picking a Division + Department here reveals the Activities section,
#   same as clicking through the tiles below.
# ============================================================
if "selected_division" not in st.session_state:
    st.session_state.selected_division = None
if "selected_department" not in st.session_state:
    st.session_state.selected_department = None

filt_div_col, filt_group_col, filt_dept_col = st.columns(3)

with filt_div_col:
    division_options = ["All Divisions"] + sorted(df["AUDIT DIVISION"].dropna().unique().tolist())
    division_filter = st.selectbox("Audit Division", division_options, key="filter_division")

group_scope = active_rows if division_filter == "All Divisions" else active_rows[active_rows["AUDIT DIVISION"] == division_filter]
with filt_group_col:
    group_options = ["All Groups"] + sorted(group_scope["GROUP"].dropna().unique().tolist())
    group_filter = st.selectbox("Group", group_options, key="filter_group")

dept_scope = group_scope if group_filter == "All Groups" else group_scope[group_scope["GROUP"] == group_filter]
with filt_dept_col:
    dept_options = ["All Departments"] + sorted(dept_scope["DEPARTMENT"].dropna().unique().tolist())
    department_filter = st.selectbox("Department", dept_options, key="filter_department")

# a real Division + Department picked via the dropdowns drives the same
# session state the tiles use, so the Activities section appears either way
if division_filter != "All Divisions":
    st.session_state.selected_division = division_filter
    if department_filter != "All Departments":
        st.session_state.selected_department = department_filter

st.write("")

# ============================================================
# AUDIT DIVISION TILES — light-orange, whole tile is the click target
# ============================================================
st.markdown('<div class="section-title">🗂️ Browse by Audit Division</div>', unsafe_allow_html=True)

division_counts = active_rows.groupby("AUDIT DIVISION")["AUDIT ACTIVITY"].count().to_dict()
all_divisions = sorted(df["AUDIT DIVISION"].unique())

cols = st.columns(min(len(all_divisions), 7)) if all_divisions else []
for i, division in enumerate(all_divisions):
    count = division_counts.get(division, 0)
    is_selected = st.session_state.selected_division == division
    key_prefix = "tile_div_selected_" if is_selected else "tile_div_"
    with cols[i % len(cols)]:
        with st.container(key=f"{key_prefix}{division}"):
            label = f"{'✓ ' if is_selected else ''}{division}\n\n{count} activit{'y' if count == 1 else 'ies'}"
            if st.button(label, key=f"btn_div_{division}", use_container_width=True):
                if is_selected:
                    st.session_state.selected_division = None
                else:
                    st.session_state.selected_division = division
                st.session_state.selected_department = None
                st.rerun()

# ============================================================
# BREADCRUMB
# ============================================================
if st.session_state.selected_division:
    crumb = f'<span class="crumb">🏠 All Divisions &nbsp;›&nbsp; <b>{st.session_state.selected_division}</b>'
    if st.session_state.selected_department:
        crumb += f' &nbsp;›&nbsp; <b>{st.session_state.selected_department}</b>'
    crumb += "</span>"
    st.markdown(crumb, unsafe_allow_html=True)

# ============================================================
# DEPARTMENT TILES — only shown once a Division is selected
# ============================================================
if st.session_state.selected_division:
    dept_rows_for_div = active_rows[active_rows["AUDIT DIVISION"] == st.session_state.selected_division]

    if dept_rows_for_div.empty:
        st.info(f"No departments are mapped under **{st.session_state.selected_division}** yet.")
    else:
        st.markdown('<div class="section-title">📁 Select a Department</div>', unsafe_allow_html=True)
        dept_counts = dept_rows_for_div.groupby("DEPARTMENT")["AUDIT ACTIVITY"].count().to_dict()
        departments = sorted(dept_rows_for_div["DEPARTMENT"].unique())

        dcols = st.columns(min(len(departments), 4)) if departments else []
        for i, department in enumerate(departments):
            count = dept_counts.get(department, 0)
            is_selected = st.session_state.selected_department == department
            key_prefix = "tile_dept_selected_" if is_selected else "tile_dept_"
            with dcols[i % len(dcols)]:
                with st.container(key=f"{key_prefix}{department}"):
                    label = f"{'✓ ' if is_selected else ''}{department}\n\n{count} activit{'y' if count == 1 else 'ies'}"
                    if st.button(label, key=f"btn_dept_{department}", use_container_width=True):
                        if is_selected:
                            st.session_state.selected_department = None
                        else:
                            st.session_state.selected_department = department
                        st.rerun()

    # ============================================================
    # AUDIT ACTIVITIES — only shown once a Department is selected
    # ============================================================
    if st.session_state.selected_department:
        act_rows = active_rows[
            (active_rows["AUDIT DIVISION"] == st.session_state.selected_division)
            & (active_rows["DEPARTMENT"] == st.session_state.selected_department)
        ]
        st.markdown('<div class="section-title">📌 Audit Activities</div>', unsafe_allow_html=True)

        if act_rows.empty:
            st.info("No audit activities found for this department.")
        else:
            for _, row in act_rows.iterrows():
                link = row["LINKS"]
                has_link = pd.notna(link) and str(link).strip() not in ("", "nan")
                c1, c2 = st.columns([4, 1])
                with c1:
                    badge = '<span class="badge-live">● LIVE</span>' if has_link else '<span class="badge-soon">COMING SOON</span>'
                    group_tag = f' &nbsp;·&nbsp; {row["GROUP"]}' if pd.notna(row.get("GROUP")) else ""
                    st.markdown(
                        f"""
                        <div class="activity-row">
                            <div>
                                <div class="activity-name">{row['AUDIT ACTIVITY']}</div>
                                <div class="activity-dept">{row['DEPARTMENT']}{group_tag}</div>
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
        © {datetime.now(IST).year} — All internal audit tools are for authorized hospital staff use only.
    </div>
    """,
    unsafe_allow_html=True,
)
