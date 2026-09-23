"""Restrained, responsive visual system for the city policy simulator."""
import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root { --ink:#182636; --muted:#607080; --paper:#f5f6f8; --line:#dce2e9; --accent:#245b96; --green:#257451; }
        .stApp { background:var(--paper); color:var(--ink); }
        [data-testid="stHeader"] { background:rgba(245,246,248,.96); }
        [data-testid="stMainBlockContainer"], .main .block-container { max-width:1240px; padding:2.5rem 2.5rem 4rem; }
        h1,h2,h3 { color:var(--ink); letter-spacing:-.025em; }
        h2 { font-size:1.6rem !important; } h3 { font-size:1.3rem !important; }
        .app-masthead { display:flex; justify-content:space-between; align-items:center; gap:1rem; padding-bottom:1rem; border-bottom:1px solid var(--line); color:var(--muted); font-size:.75rem; letter-spacing:.03em; }
        .app-brand { display:flex; align-items:center; gap:.65rem; color:var(--ink); font-weight:700; }
        .app-mark { width:24px; height:24px; display:grid; place-items:center; background:var(--ink); color:white; font-size:.78rem; border-radius:4px; }
        .city-hero { display:flex; align-items:flex-end; justify-content:space-between; gap:2rem; padding:2rem 0 1.7rem; margin-bottom:.6rem; border-bottom:1px solid var(--line); }
        .hero-copy { max-width:690px; }
        .hero-kicker { color:var(--accent); font-size:.72rem; font-weight:650; letter-spacing:.08em; text-transform:uppercase; }
        .hero-title { margin:.5rem 0 .7rem !important; font-size:clamp(2rem,3.4vw,3rem) !important; line-height:1.1 !important; font-weight:700 !important; letter-spacing:-.045em; }
        .hero-subtitle { max-width:600px; margin:0; color:var(--muted); line-height:1.65; font-size:.96rem; }
        .hero-note { flex-shrink:0; padding-left:1.4rem; border-left:2px solid var(--accent); color:var(--muted); font-size:.78rem; line-height:1.8; }
        .hero-note strong { color:var(--ink); font-size:.82rem; font-weight:650; }
        .section-label { margin:1.2rem 0 .15rem; color:var(--accent); font-size:.7rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }
        .section-intro { margin:0 0 1rem; color:var(--muted); line-height:1.6; font-size:.87rem; max-width:900px; }
        .district-card { min-height:185px; padding:1rem; border:1px solid var(--line); border-radius:6px; background:#fff; }
        .district-card-head { display:flex; flex-wrap:wrap; align-items:baseline; justify-content:space-between; gap:.3rem; }
        .district-card-name { font-size:.95rem; font-weight:700; color:var(--ink); }
        .district-card-pop { font-size:.7rem; color:var(--muted); white-space:nowrap; font-variant-numeric:tabular-nums; }
        .district-card-profile { min-height:3.9em; margin:.65rem 0; color:var(--muted); font-size:.77rem; line-height:1.4; }
        .district-signals-label { margin:.7rem 0 .4rem; color:var(--muted); font-size:.6rem; text-transform:uppercase; letter-spacing:.06em; }
        .district-chips { display:flex; flex-wrap:wrap; gap:.3rem; }
        .district-chip { padding:.25rem .4rem; border-left:2px solid #b46b24; background:#faf0e6; color:#86511c; font-size:.66rem; line-height:1.35; }
        .district-calm { color:var(--green); font-size:.68rem; line-height:1.4; }
        .decision-meta { display:flex; flex-wrap:wrap; gap:.35rem .8rem; margin:.2rem 0; color:var(--muted); font-size:.74rem; line-height:1.6; }
        .meta-pill { color:var(--accent); font-weight:650; }
        .coverage-pill { display:flex; align-items:center; gap:.5rem; min-height:2.5rem; margin-top:1.7rem; padding:.55rem .8rem; border:1px solid var(--line); border-radius:6px; color:var(--muted); background:#f8fafc; font-size:.85rem; }
        .coverage-dot { width:6px; height:6px; border-radius:50%; background:var(--accent); }
        .budget-status-row,.budget-foot { display:flex; justify-content:space-between; align-items:center; gap:1rem; }
        .budget-status { color:var(--green); font-weight:650; font-size:.78rem; }
        .budget-status.is-over { color:#b42332; }
        .budget-explainer,.budget-foot { color:var(--muted); font-size:.72rem; }
        .budget-track { height:5px; overflow:hidden; margin:.6rem 0; background:#e3e8ef; border-radius:2px; }
        .budget-fill { display:block; height:100%; background:var(--accent); }
        .budget-fill.is-over { background:#b42332; }
        [data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--line); border-radius:8px; }
        [data-testid="stMetric"] { padding:.85rem 1rem; border:1px solid var(--line); border-radius:6px; background:#fff; }
        [data-testid="stMetricLabel"] { color:var(--muted); font-size:.77rem; }
        [data-testid="stMetricValue"] { color:var(--ink); font-variant-numeric:tabular-nums; font-size:1.9rem; font-weight:600; }
        [data-testid="stSelectbox"] label { color:var(--muted); font-size:.78rem; }
        [data-baseweb="select"] > div { border-radius:6px; background:#fff; border-color:var(--line); }
        .stButton button { min-height:2.7rem; border-radius:6px; font-weight:600; box-shadow:none; }
        .stButton button[kind="primary"] { background:var(--accent); border-color:var(--accent); color:#fff; }
        .stButton button[kind="primary"]:hover { background:#1c4879; border-color:#1c4879; }
        .stButton button:focus-visible { outline:3px solid #8fb4df; outline-offset:2px; }
        [data-testid="stAlert"] { border-radius:6px; font-size:.85rem; }
        [data-testid="stTable"] { max-width:100%; overflow-x:auto; }
        [data-testid="stTable"] table { min-width:900px; }
        .app-footer { border-top:1px solid var(--line); margin-top:2rem; padding-top:.9rem; color:var(--muted); font-size:.7rem; }
        @media(max-width:900px) {
          [data-testid="stMainBlockContainer"],.main .block-container { padding:2rem 1.25rem 3rem; }
          .city-hero { align-items:flex-start; flex-direction:column; gap:1.2rem; }
          .hero-note { border-left-width:1px; padding-left:.8rem; }
          .district-card { padding:.8rem; }
        }
        @media(max-width:640px) {
          .app-masthead { align-items:flex-start; flex-direction:column; gap:.4rem; }
          .district-card,.district-card-profile { min-height:0; }
          .budget-status-row { align-items:flex-start; flex-direction:column; gap:.3rem; }
          .coverage-pill { margin-top:0; }
        }
        </style>
        <header class="app-masthead">
          <div class="app-brand"><span class="app-mark" aria-hidden="true">А</span> АСТАНА / ГОРОДСКИЕ РЕШЕНИЯ</div>
          <span>HackAlem AI · Спец-трек Astana Innovations</span>
        </header>
        <section class="city-hero">
          <div class="hero-copy">
            <div class="hero-kicker">Симулятор управления городом</div>
            <h1 class="hero-title">Аким на 5 часов</h1>
            <p class="hero-subtitle">Распределите бюджет между городскими инициативами.
            Сравните изменения в районах и оцените последствия своих решений.</p>
          </div>
          <div class="hero-note"><strong>5 решений · 100 у.е.</strong><br>Горизонт оценки — 8 кварталов<br>Учебная модель на синтетических данных</div>
        </section>
        """,
        unsafe_allow_html=True,
    )
