import streamlit as st
import pandas as pd
from utils import incarca_date, curata_date, TINTA

st.set_page_config(page_title="Dashboard Financiar - Risc de Credit", page_icon="💳", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=IBM+Plex+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');
:root {
    --bg: #0f1117; --surface: #1a1d27; --border: #2a2e3c; --accent: #4f9dff;
    --accent2: #7ee787; --text: #e8e8e8; --muted: #8b92a5; --display: 'Syne', sans-serif;
    --mono: 'IBM Plex Mono', monospace; --body: 'DM Sans', sans-serif;
}
html, body, [class*="css"] { background-color: var(--bg) !important; color: var(--text) !important; font-family: var(--body) !important; }
h1, h2, h3, h4 { font-family: var(--display) !important; color: var(--text) !important; letter-spacing: -0.5px; }
[data-testid="stSidebar"] { background-color: #14161e !important; border-right: 1px solid var(--border); }
[data-testid="stSidebar"] * { color: var(--text) !important; }
.hero { border-top: 4px solid var(--accent); background: var(--surface); padding: 44px 48px; border-radius: 6px; margin-bottom: 36px; }
.hero-label { font-family: var(--mono); font-size: 12px; color: var(--accent); letter-spacing: 3px; text-transform: uppercase; margin-bottom: 12px; }
.hero-title { font-family: var(--display); font-size: 54px; font-weight: 800; line-height: 1.05; margin: 0 0 16px 0; }
.hero-sub { font-size: 16px; color: #aab; max-width: 680px; line-height: 1.6; }
.sec-header { font-family: var(--mono); font-size: 11px; letter-spacing: 3px; text-transform: uppercase; color: var(--accent); margin: 40px 0 18px 0; padding-bottom: 10px; border-bottom: 1px solid var(--border); }
.page-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.page-card { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 20px 24px; transition: border-color 0.2s; }
.page-card:hover { border-color: var(--accent); }
.page-num { font-family: var(--mono); font-size: 11px; color: var(--accent); letter-spacing: 2px; margin-bottom: 6px; }
.page-name { font-family: var(--display); font-size: 17px; font-weight: 700; margin-bottom: 8px; }
.page-desc { font-size: 13.5px; color: #99a; line-height: 1.55; }
.ok-banner { background: #0f2a1e; border: 1px solid #1e5c3a; border-left: 4px solid var(--accent2); border-radius: 6px; padding: 18px 24px; color: #a8eecb; font-size: 15px; line-height: 1.6; }
.ok-banner strong { color: var(--accent2); }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 💳 Dashboard Financiar")
st.sidebar.markdown("**Analiza riscului de credit**")
st.sidebar.markdown("Emitent de carduri de credit, Taiwan, 2005")
st.sidebar.markdown("---")

st.markdown("""
<div class="hero">
    <div class="hero-label">Pachete Software / Python &amp; Streamlit</div>
    <div class="hero-title">Analiza Riscului<br>de Credit</div>
    <div class="hero-sub">
        Dashboard interactiv pentru analiza portofoliului de carduri de credit al unui emitent
        din Taiwan (30.000 de clienti). Explorare de date, vizualizari dinamice, segmentarea
        clientilor si modele predictive pentru probabilitatea de neplata.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="sec-header">Structura aplicatiei</div>', unsafe_allow_html=True)
st.markdown("""
<div class="page-grid">
    <div class="page-card"><div class="page-num">PAGINA 01</div><div class="page-name">Date &amp; Statistici</div><div class="page-desc">Importul fisierului CSV in pandas, tratarea valorilor lipsa, statistici descriptive si structura datelor.</div></div>
    <div class="page-card"><div class="page-num">PAGINA 02</div><div class="page-name">Filtrare &amp; Explorare</div><div class="page-desc">Filtrarea interactiva cu widget-uri, accesarea datelor cu loc si iloc, gruparea si agregarea in pandas.</div></div>
    <div class="page-card"><div class="page-num">PAGINA 03</div><div class="page-name">Vizualizari</div><div class="page-desc">Grafice dinamice cu matplotlib, seaborn si plotly: distributii, rate de default si serii de timp.</div></div>
    <div class="page-card"><div class="page-num">PAGINA 04</div><div class="page-name">Pregatirea Datelor</div><div class="page-desc">Codificarea variabilelor categoriale si scalarea variabilelor numerice pentru modelare.</div></div>
    <div class="page-card"><div class="page-num">PAGINA 05</div><div class="page-name">Clasificare &amp; Segmentare</div><div class="page-desc">Regresie logistica (scikit-learn) pentru predictia neplatei si clusterizare K-Means a clientilor.</div></div>
    <div class="page-card"><div class="page-num">PAGINA 06</div><div class="page-name">Regresie Multipla</div><div class="page-desc">Model de regresie multipla (statsmodels) pentru explicarea sumei facturate, cu interpretarea coeficientilor.</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="sec-header">Incarca setul de date</div>', unsafe_allow_html=True)
st.markdown("""
Incarca fisierul **credit_card_default.csv** o singura data, aici. Datele sunt salvate in
`st.session_state` si raman disponibile in toate paginile aplicatiei. Daca nu incarci nimic,
aplicatia foloseste automat fisierul inclus in folderul `date/`.
""")

with st.expander("De ce session_state?"):
    st.code("""
st.session_state["date_curate"] = curata_date(pd.read_csv(fisier))

if "date_curate" not in st.session_state:
    st.warning("Te rog incarca datele din pagina Home.")
    st.stop()
date = st.session_state["date_curate"]
""", language="python")

fisier = st.file_uploader("Alege fisierul CSV", type=["csv"], label_visibility="collapsed")
if fisier is not None:
    date_brute = pd.read_csv(fisier)
    st.session_state["date_brute"] = date_brute
    st.session_state["date_curate"] = curata_date(date_brute)
    st.rerun()

if "date_curate" not in st.session_state:
    st.session_state["date_brute"] = incarca_date()
    st.session_state["date_curate"] = curata_date(st.session_state["date_brute"])

date = st.session_state["date_curate"]
rata_default = date[TINTA].mean() * 100

st.markdown(f"""
<div class="ok-banner">
    <strong>Date incarcate.</strong> Setul contine <strong>{len(date):,} clienti</strong>,
    cu o rata generala de neplata de <strong>{rata_default:.2f}%</strong>. Poti naviga liber
    intre toate paginile din meniul lateral.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Clienti", f"{len(date):,}")
col2.metric("Rata default", f"{rata_default:.2f}%")
col3.metric("Limita medie", f"{date['LIMIT_BAL'].mean():,.0f} NT$")
col4.metric("Varsta medie", f"{date['AGE'].mean():.0f} ani")
col5.metric("Variabile", f"{st.session_state['date_brute'].shape[1]}")

st.markdown("<br>", unsafe_allow_html=True)
st.dataframe(date.head(8), use_container_width=True)

st.markdown("---")
st.markdown('<p style="text-align:center; color:#445; font-size:13px; font-family:\'IBM Plex Mono\', monospace;">Dashboard Financiar &middot; Pachete Software &middot; Python &amp; Streamlit</p>', unsafe_allow_html=True)
