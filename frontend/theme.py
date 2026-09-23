"""Visual theme and lightweight, reduced-motion-aware animation for the app."""

import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
          --ink: #18332b;
          --muted: #62776f;
          --paper: #f3f6f2;
          --card: #ffffff;
          --line: #dce7df;
          --green: #16745a;
          --mint: #bfe6d3;
          --amber: #e8ad4c;
          --red: #bb5149;
        }
        html { scroll-behavior: smooth; }
        .stApp {
          background:
            radial-gradient(ellipse at 92% 0%, rgba(191,230,211,.38), transparent 30%),
            var(--paper);
          color: var(--ink);
        }
        [data-testid="stHeader"] { background: transparent; }
        .main .block-container {
          max-width: 1320px;
          padding: 2.1rem 2rem 4rem;
        }
        h1, h2, h3, p, label { color: var(--ink); }
        h2 { letter-spacing: -.025em; }
        .city-hero {
          position: relative;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 2rem;
          overflow: hidden;
          padding: clamp(1.6rem, 4vw, 3.2rem);
          margin: 0 0 1.7rem;
          border: 1px solid rgba(220,231,223,.7);
          border-radius: 28px;
          background: linear-gradient(116deg, #fff 4%, #f8fbf8 58%, #e6f4ec 100%);
          box-shadow: 0 18px 52px rgba(27,61,48,.08);
          animation: rise-in .55s ease-out both;
        }
        .hero-copy { max-width: 760px; position: relative; z-index: 1; }
        .hero-kicker {
          display: inline-flex; align-items: center; gap: .5rem;
          padding: .42rem .75rem; border-radius: 999px;
          background: #e8f4ed; color: #267456;
          font: 700 .72rem/1.2 ui-sans-serif, system-ui, sans-serif;
          letter-spacing: .12em; text-transform: uppercase;
        }
        .hero-title {
          margin: 1rem 0 .55rem; color: var(--ink);
          font: 750 clamp(2.1rem, 4.2vw, 3.65rem)/1.05 ui-sans-serif, system-ui, sans-serif;
          letter-spacing: -.055em;
        }
        .hero-title span { color: var(--green); }
        .hero-subtitle {
          max-width: 650px; margin: 0; color: var(--muted);
          font: 400 clamp(.98rem, 1.4vw, 1.12rem)/1.65 ui-sans-serif, system-ui, sans-serif;
        }
        .hero-note {
          display: inline-flex; margin-top: 1.1rem; padding: .48rem .72rem;
          border: 1px solid #e5ebe6; border-radius: 11px;
          color: #51675e; background: rgba(255,255,255,.72);
          font: 600 .82rem/1.3 ui-sans-serif, system-ui, sans-serif;
        }
        .hero-art { flex: 0 0 min(31%, 340px); min-width: 210px; }
        .hero-art svg { width: 100%; height: auto; display: block; }
        .hero-tower { transform-origin: center bottom; animation: skyline-float 5.5s ease-in-out infinite; }
        .hero-glow { animation: glow-breathe 4.5s ease-in-out infinite; transform-origin: center; }
        .section-label {
          margin: .35rem 0 .25rem; color: #43816a;
          font: 750 .73rem/1.2 ui-sans-serif, system-ui, sans-serif;
          letter-spacing: .13em; text-transform: uppercase;
        }
        .section-intro { margin: 0 0 1.1rem; color: var(--muted); line-height: 1.5; }
        .district-card {
          min-height: 196px; padding: 1rem 1rem .9rem;
          border: 1px solid var(--line); border-radius: 18px;
          background: rgba(255,255,255,.94);
          box-shadow: 0 7px 22px rgba(27,61,48,.045);
          animation: rise-in .48s ease-out both;
          transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
        }
        .district-card:hover { transform: translateY(-3px); border-color: #b7d8c4; box-shadow: 0 12px 28px rgba(27,61,48,.09); }
        .district-card-head { display:flex; justify-content:space-between; gap:.5rem; align-items:baseline; }
        .district-card-name { color:var(--ink); font:750 1.02rem/1.2 ui-sans-serif,system-ui,sans-serif; }
        .district-card-pop { color:#43816a; font:700 .78rem/1.2 ui-sans-serif,system-ui,sans-serif; white-space:nowrap; }
        .district-card-profile { min-height:2.55em; margin:.55rem 0 .75rem; color:var(--muted); font:400 .8rem/1.45 ui-sans-serif,system-ui,sans-serif; }
        .district-signals-label { margin-bottom:.35rem; color:#85958d; font:700 .63rem/1.2 ui-sans-serif,system-ui,sans-serif; letter-spacing:.09em; text-transform:uppercase; }
        .district-chips { display:flex; flex-wrap:wrap; gap:.32rem; }
        .district-chip { padding:.27rem .42rem; border-radius:7px; background:#fbf1df; color:#8a6126; font:650 .67rem/1.2 ui-sans-serif,system-ui,sans-serif; }
        .district-calm { color:#498268; font:600 .72rem/1.3 ui-sans-serif,system-ui,sans-serif; }
        .selection-card { padding: 1.08rem 1.05rem .75rem; border:1px solid var(--line); border-radius:18px; background:#fff; box-shadow:0 7px 22px rgba(27,61,48,.04); animation:rise-in .38s ease-out both; }
        .selection-number { color:#77a38c; font:750 .72rem/1.2 ui-sans-serif,system-ui,sans-serif; letter-spacing:.12em; text-transform:uppercase; }
        .selection-title { margin:.25rem 0 .8rem; color:var(--ink); font:750 1rem/1.25 ui-sans-serif,system-ui,sans-serif; }
        .decision-meta { display:flex; flex-wrap:wrap; gap:.4rem .65rem; align-items:center; margin:.2rem 0 .7rem; color:#62776f; font:500 .78rem/1.5 ui-sans-serif,system-ui,sans-serif; }
        .meta-pill { display:inline-flex; padding:.25rem .5rem; border-radius:7px; background:#f1f6f2; color:#45685a; font-weight:650; }
        .coverage-pill { display:flex; min-height:2.55rem; align-items:center; gap:.45rem; padding:.5rem .65rem; border:1px solid #d8ebe0; border-radius:10px; background:#f3faf5; color:#267456; font:700 .81rem/1.25 ui-sans-serif,system-ui,sans-serif; }
        .coverage-dot { width:.48rem; height:.48rem; border-radius:50%; background:#45a777; box-shadow:0 0 0 4px #dff1e6; }
        .budget-status-row { display:flex; justify-content:space-between; align-items:center; gap:1rem; margin:.4rem 0 .45rem; }
        .budget-explainer { color:#7c8c84; font:500 .73rem/1.3 ui-sans-serif,system-ui,sans-serif; }
        .budget-status { padding:.43rem .65rem; border-radius:999px; background:#e8f4ed; color:#267456; font:700 .75rem/1.2 ui-sans-serif,system-ui,sans-serif; white-space:nowrap; }
        .budget-status.is-over { background:#fbeceb; color:var(--red); }
        .budget-track { height:9px; overflow:hidden; margin:.9rem 0 .45rem; border-radius:99px; background:#eaf0eb; }
        .budget-fill { display:block; height:100%; border-radius:inherit; background:linear-gradient(90deg,#6fc294,#16745a); background-size:180% 100%; animation:budget-flow 3s linear infinite; transition:width .35s ease; }
        .budget-fill.is-over { background:linear-gradient(90deg,#e1a478,#bb5149); }
        .budget-foot { display:flex; justify-content:space-between; gap:1rem; color:#7c8c84; font:500 .7rem/1.3 ui-sans-serif,system-ui,sans-serif; }
        .district-score-card { padding:.8rem 0; border-bottom:1px solid #e8eee9; }
        .district-score-head { display:flex; justify-content:space-between; gap:1rem; color:var(--ink); font:650 .84rem/1.3 ui-sans-serif,system-ui,sans-serif; }
        .district-score-head span:last-child { color:#537267; font-variant-numeric:tabular-nums; }
        .district-score-track { height:7px; margin-top:.48rem; border-radius:99px; background:#e8efea; overflow:hidden; }
        .district-score-fill { height:100%; border-radius:inherit; background:linear-gradient(90deg,#8dcda8,#318467); animation:score-grow .8s cubic-bezier(.2,.7,.2,1) both; transform-origin:left; }
        .district-score-card.is-weak .district-score-head span:first-child { color:#9a6b31; }
        .stButton button[kind="primary"] { min-height:3rem; border-radius:12px; background:#16745a; border:1px solid #16745a; font-weight:750; box-shadow:0 7px 16px rgba(22,116,90,.15); transition:transform .16s ease, box-shadow .16s ease, background .16s ease; }
        .stButton button[kind="primary"]:hover { background:#115f49; border-color:#115f49; transform:translateY(-1px); box-shadow:0 10px 20px rgba(22,116,90,.2); }
        .stButton button:disabled { opacity:.5; transform:none; }
        div[data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--line); border-radius:16px; background:rgba(255,255,255,.68); }
        div[data-testid="stMetric"] { padding:.8rem .9rem; border:1px solid var(--line); border-radius:14px; background:#fff; }
        div[data-testid="stMetricLabel"] { color:#70847a; }
        div[data-testid="stMetricValue"] { color:var(--ink); }
        div[data-testid="stSelectbox"] label { font-size:.81rem; font-weight:650; color:#4d675b; }
        div[data-testid="stTable"] { max-width:100%; overflow-x:auto; }
        div[data-testid="stTable"] table { min-width:900px; }
        details { border-radius:12px; }
        @keyframes rise-in { from {opacity:0;transform:translateY(9px)} to {opacity:1;transform:translateY(0)} }
        @keyframes skyline-float { 0%,100% {transform:translateY(0)} 50% {transform:translateY(-5px)} }
        @keyframes glow-breathe { 0%,100% {opacity:.65;transform:scale(.98)} 50% {opacity:1;transform:scale(1.04)} }
        @keyframes budget-flow { from {background-position:0 0} to {background-position:180% 0} }
        @keyframes score-grow { from {transform:scaleX(.02)} to {transform:scaleX(1)} }
        @media (max-width: 780px) {
          .main .block-container {padding:1rem 1rem 3rem;}
          .city-hero {border-radius:20px; padding:1.4rem;}
          .hero-art {min-width:125px; flex-basis:27%; opacity:.75;}
          .district-card {min-height:170px; padding:.8rem;}
          .budget-status-row {align-items:flex-start;}
          .budget-status {white-space:normal;}
          .budget-explainer {text-align:right;}
        }
        @media (max-width: 520px) { .hero-art {display:none;} .hero-title {font-size:2.15rem;} }
        @media (prefers-reduced-motion: reduce) {
          *, *::before, *::after {scroll-behavior:auto !important; animation-duration:.01ms !important; animation-iteration-count:1 !important; transition-duration:.01ms !important;}
        }
        </style>
        <section class="city-hero">
          <div class="hero-copy">
            <div class="hero-kicker">Astana · City Lab</div>
            <div class="hero-title">Аким на <span>5 часов</span></div>
            <p class="hero-subtitle">Проверьте, как пять городских решений меняют качество жизни районов — при одном общем бюджете и реальных ограничениях симуляции.</p>
            <div class="hero-note">5 инициатив · 100 виртуальных у.е. · 8 кварталов</div>
          </div>
          <div class="hero-art" aria-hidden="true">
            <svg viewBox="0 0 340 220" fill="none" xmlns="http://www.w3.org/2000/svg">
              <ellipse cx="184" cy="195" rx="147" ry="13" fill="#CDE7D7"/>
              <circle class="hero-glow" cx="247" cy="61" r="41" fill="#E5F4E9"/>
              <path d="M16 185h309" stroke="#A9CDB7" stroke-width="2" stroke-linecap="round"/>
              <g fill="#C5E3D1">
                <path d="M26 185v-51h25v51H26Zm4-42h5v7h-5v-7Zm11 0h5v7h-5v-7Zm-11 14h5v7h-5v-7Zm11 0h5v7h-5v-7Z"/>
                <path d="M55 185v-75h30v75H55Zm6-65h6v8h-6v-8Zm13 0h6v8h-6v-8Zm-13 18h6v8h-6v-8Zm13 0h6v8h-6v-8Z"/>
                <path d="M264 185v-64h23v64h-23Zm5-53h5v7h-5v-7Zm9 0h5v7h-5v-7Zm-9 14h5v7h-5v-7Zm9 0h5v7h-5v-7Z"/>
                <path d="M291 185v-48h26v48h-26Zm5-38h5v7h-5v-7Zm10 0h5v7h-5v-7Zm-10 13h5v7h-5v-7Zm10 0h5v7h-5v-7Z"/>
              </g>
              <g class="hero-tower">
                <path d="M125 185 151 67h22l27 118" fill="#6FAF88"/>
                <path d="M151 67h22l27 118h-75L151 67Z" stroke="#438E68" stroke-width="2"/>
                <path d="M154 86h17m-22 21h27m-31 22h36m-40 22h45m-50 22h55" stroke="#DDF1E4" stroke-width="3" stroke-linecap="round"/>
                <path d="M162 67V35" stroke="#438E68" stroke-width="3" stroke-linecap="round"/>
                <circle cx="162" cy="31" r="8" fill="#E8B65B" stroke="#FFF7E5" stroke-width="4"/>
                <path d="M137 185h50" stroke="#317857" stroke-width="3" stroke-linecap="round"/>
              </g>
              <path d="M101 185v-31h14v31m101 0v-42h16v42" stroke="#9BCBAD" stroke-width="7" stroke-linecap="round"/>
              <circle cx="73" cy="91" r="3" fill="#E7B45A"/><circle cx="222" cy="111" r="3" fill="#E7B45A"/><circle cx="108" cy="74" r="2.5" fill="#80BD96"/>
            </svg>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
