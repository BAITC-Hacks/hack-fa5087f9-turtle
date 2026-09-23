"""Quiet typography and a single reading column for the city simulator."""
import streamlit as st
from pathlib import Path


def apply_theme() -> None:
    logo = Path(__file__).with_name("favicon.svg").read_text(encoding="utf-8")
    st.markdown(
        """
        <style>
        :root { --ink:#1d1d1f; --muted:#6e6e73; --paper:#fff; --line:#e5e5e7; --accent:#0071e3; --green:#24734a; }
        html,body,[data-testid="stApp"] { font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
        .stApp { background:var(--paper); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
        .stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,.stApp button,.stApp input { font-family:inherit; }
        [data-testid="stHeader"] { background:rgba(255,255,255,.96); }
        [data-testid="stMainBlockContainer"],.main .block-container { max-width:1100px; padding:5rem 2.5rem 4rem; }
        h1,h2,h3,p,label { color:var(--ink); }
        h1,h2,h3 { letter-spacing:-.035em; font-weight:600 !important; }
        h2 { font-size:2rem !important; line-height:1.2 !important; }
        h3 { font-size:1.65rem !important; line-height:1.3 !important; }
        p { line-height:1.65; }
        .app-masthead { display:flex; justify-content:space-between; align-items:center; gap:1rem; padding-bottom:1.1rem; border-bottom:1px solid var(--line); font-size:.75rem; color:var(--muted); }
        .app-brand { display:flex; align-items:center; gap:.65rem; color:var(--ink); font-size:1rem; font-weight:600; letter-spacing:-.025em; }
        .app-logo svg { width:32px; height:32px; display:block; }
        .city-hero { text-align:center; padding:3.6rem 0 3rem; margin-bottom:1rem; animation:content-arrive .45s ease-out both; }
        .hero-kicker { color:var(--muted); font-size:.86rem; font-weight:500; }
        .hero-title { margin:.65rem auto 1rem !important; padding:0 !important; font-size:clamp(2.7rem,5.5vw,4.5rem) !important; line-height:1.08 !important; letter-spacing:-.06em !important; font-weight:650 !important; }
        .hero-subtitle { max-width:620px; margin:0 auto !important; color:var(--muted); font-size:1.14rem; line-height:1.55; text-wrap:balance; }
        .hero-title span { color:var(--accent); }
        .hero-facts { display:flex; justify-content:center; flex-wrap:wrap; gap:0; margin:1.8rem auto 0; }
        .hero-fact { padding:0 1.65rem; color:var(--muted); font-size:.74rem; line-height:1.5; border-right:1px solid var(--line); }
        .hero-fact:last-child { border-right:0; }
        .hero-fact strong { display:block; color:var(--ink); font-size:1.55rem; font-weight:600; letter-spacing:-.035em; }
        .hero-fact:nth-child(2) strong { color:var(--accent); }
        .section-label { margin:2rem 0 .1rem; color:var(--muted); font-size:.74rem; font-weight:500; letter-spacing:.02em; }
        .section-intro { max-width:740px; margin:0 0 1.1rem; color:var(--muted); line-height:1.65; font-size:.93rem; }
        .district-card { min-height:230px; padding:1.1rem; border:0; border-radius:16px; background:#f5f5f7; }
        .district-card { transition:background-color .18s ease; }
        .district-card:hover { background:#eef5fc; }
        .district-card-head { display:flex; flex-direction:column; gap:.35rem; }
        .district-card-name { font-size:1.02rem; font-weight:600; letter-spacing:-.02em; }
        .district-card-pop { font-size:.72rem; color:var(--muted); font-variant-numeric:tabular-nums; }
        .district-card-profile { min-height:5.5em; margin:.7rem 0; color:#515154; font-size:.77rem; line-height:1.45; }
        .district-signals-label { margin:.7rem 0 .35rem; color:var(--muted); font-size:.64rem; }
        .district-chips { display:flex; flex-direction:column; gap:.3rem; }
        .district-chip { padding:0; color:#a3461b; font-size:.67rem; line-height:1.4; }
        .district-calm { color:var(--muted); font-size:.68rem; line-height:1.4; }
        .decision-meta { display:flex; justify-content:space-between; gap:1rem; margin:.4rem 0 .2rem; color:var(--muted); font-size:.75rem; line-height:1.6; }
        .meta-pill { color:#515154; font-weight:600; }
        .decision-effects { margin:0 !important; max-width:780px; color:var(--muted); font-size:.76rem; line-height:1.6; }
        .initiative-price { display:flex; flex-direction:column; align-items:flex-end; gap:.15rem; color:var(--muted); font-size:.7rem; padding-top:.1rem; }
        .initiative-price strong { color:var(--ink); font-size:1.65rem; line-height:1.25; font-weight:600; font-variant-numeric:tabular-nums; }
        .coverage-pill { display:flex; align-items:center; gap:.5rem; min-height:2.5rem; margin-top:1.7rem; padding:.5rem .7rem; color:var(--muted); font-size:.8rem; }
        .coverage-dot { width:5px; height:5px; border-radius:50%; background:var(--accent); }
        .budget-status-row,.budget-foot { display:flex; justify-content:space-between; align-items:center; gap:1rem; }
        .budget-status { color:var(--accent); font-weight:500; font-size:.8rem; }
        .validation-ready { margin:.2rem 0 !important; padding:.8rem 1rem; border-radius:10px; background:#f0f6ff; color:#175c9b; font-size:.88rem; }
        .budget-status.is-over { color:#b42332; }
        .budget-explainer,.budget-foot { color:var(--muted); font-size:.73rem; }
        .budget-track { height:4px; overflow:hidden; margin:.7rem 0; background:#eeeef0; border-radius:4px; }
        .budget-fill { display:block; height:100%; background:var(--accent); transition:width .3s ease; }
        .budget-fill.is-over { background:#b42332; }
        [data-testid="stMetric"] { padding:1rem; border:0; border-radius:14px; background:#f5f5f7; }
        [data-testid="stMetricLabel"] { color:var(--muted); font-size:.78rem; }
        [data-testid="stMetricValue"] { color:var(--ink); font-variant-numeric:tabular-nums; font-size:2rem; font-weight:500; letter-spacing:-.04em; }
        [data-testid="stSelectbox"] label { color:#515154; font-size:.8rem; }
        [data-baseweb="select"] > div { min-height:46px; border-radius:10px; background:#fff; border-color:#d2d2d7; }
        .stButton button { min-height:2.8rem; border-radius:24px; font-weight:500; box-shadow:none; transition:background-color .15s ease,transform .15s ease; }
        .stButton button:active { transform:scale(.99); }
        .stButton button[kind="primary"] { background:var(--accent); border-color:var(--accent); color:#fff; }
        .stButton button[kind="primary"] p { color:#fff !important; }
        .stButton button[kind="primary"]:hover { background:#0077ed; border-color:#0077ed; }
        .stButton button:focus-visible { outline:3px solid #81b7f0; outline-offset:3px; }
        [data-testid="stAlert"] { border-radius:12px; font-size:.88rem; }
        [data-testid="stTable"] { max-width:100%; overflow-x:auto; }
        [data-testid="stTable"] table { min-width:900px; }
        [class*="st-key-decision_card_"] { padding:1.1rem 1.25rem !important; border:1px solid var(--line) !important; border-radius:16px !important; background:#fff; }
        .st-key-ai_explanation { max-width:820px; margin:0 auto; padding:1.6rem 2rem !important; border:0 !important; border-radius:18px !important; background:#f5f5f7; }
        .st-key-ai_explanation p { max-width:72ch; font-size:1rem; line-height:1.75; }
        .st-key-ai_explanation h3 { margin-top:1rem; font-size:1.25rem !important; letter-spacing:-.02em; }
        .st-key-ai_explanation { animation:content-arrive .3s ease-out both; }
        @keyframes content-arrive { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }
        @media(prefers-reduced-motion:reduce) {
          .city-hero,.st-key-ai_explanation { animation:none; }
          .district-card,.budget-fill,.stButton button { transition:none; }
          .stButton button:active { transform:none; }
        }
        .app-footer { border-top:1px solid var(--line); margin-top:3rem; padding-top:1rem; color:var(--muted); font-size:.72rem; line-height:1.6; }
        @media(max-width:900px) {
          [data-testid="stMainBlockContainer"],.main .block-container { padding:4.5rem 1.2rem 3rem; }
          .city-hero { padding:2.5rem 0 2rem; }
          .district-card { padding:.9rem; }
          .hero-subtitle { font-size:1.05rem; }
        }
        @media(max-width:640px) {
          .app-masthead { align-items:flex-start; flex-direction:column; gap:.35rem; }
          .district-card,.district-card-profile { min-height:0; }
          .district-card-head { flex-direction:row; justify-content:space-between; }
          .hero-fact { padding:0 .9rem; }
          .hero-fact strong { font-size:1.3rem; }
          .budget-status-row,.decision-meta { align-items:flex-start; flex-direction:column; gap:.2rem; }
          .coverage-pill { margin-top:0; padding-left:0; }
          .initiative-price { flex-direction:row; align-items:baseline; gap:.4rem; }
          .st-key-ai_explanation { padding:1rem !important; }
        }
        </style>
        <header class="app-masthead">
          <span class="app-brand"><span class="app-logo">__LOGO__</span>Fifth Move</span>
          <span>HackAlem AI · Astana Innovations</span>
        </header>
        <section class="city-hero">
          <div class="hero-kicker">Симулятор городских решений</div>
          <h1 class="hero-title">Fifth <span>Move.</span></h1>
          <p class="hero-subtitle">Вы определяете приоритеты города.<br>
          Посмотрите, как ваши решения меняют жизнь районов.</p>
          <div class="hero-facts">
            <div class="hero-fact"><strong>5</strong>решений</div>
            <div class="hero-fact"><strong>100</strong>условных единиц</div>
            <div class="hero-fact"><strong>8</strong>кварталов</div>
          </div>
        </section>
        """.replace("__LOGO__", logo),
        unsafe_allow_html=True,
    )
