from __future__ import annotations

import json
import math
import re
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

APP_NAME = "NanoMax Pep-AuNC Studio"
APP_VERSION = "v0.2"
DATA_VERSION = "PepAuDB v0.6"
BENCHMARK_VERSION = "Real-Data Benchmark v0.4"

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"

NAV = [
    "Home",
    "1 · Define Target",
    "2 · Design Space",
    "3 · Inverse Design",
    "4 · Candidate Portfolio",
    "5 · Design Explainer",
    "6 · Synthesis Planner",
    "7 · Validation & Model",
    "8 · Experiment Feedback",
    "Evidence & Methods",
]

st.set_page_config(
    page_title=APP_NAME,
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------
st.markdown(
    """
<style>
:root {
  --ink:#132238;
  --muted:#64748B;
  --line:#DCE5EF;
  --panel:#F7F9FC;
  --blue:#0B5CAB;
  --blue2:#174A7E;
  --green:#13795B;
  --amber:#A76400;
  --red:#B42318;
}
.block-container {padding-top:1.35rem; padding-bottom:3rem; max-width:1450px;}
[data-testid="stSidebar"] {border-right:1px solid var(--line);}
[data-testid="stSidebar"] .block-container {padding-top:1.0rem;}
h1,h2,h3,h4 {letter-spacing:-0.025em;}
h1 {font-weight:760;}
.smallcaps {
  font-size:.74rem; letter-spacing:.12em; text-transform:uppercase;
  color:#718096; font-weight:800;
}
.hero {
  border:1px solid var(--line); border-radius:19px;
  padding:28px 31px; background:linear-gradient(135deg,#FFFFFF 0%,#F3F7FC 100%);
  margin-bottom:18px;
}
.hero-title {font-size:2.35rem; line-height:1.04; font-weight:780; color:var(--ink);}
.hero-sub {font-size:1.02rem; color:#536276; margin-top:9px; max-width:1020px;}
.brandline {font-size:.77rem; letter-spacing:.13em; color:var(--blue); font-weight:850;}
.question {
  font-size:1.18rem; line-height:1.55; font-weight:620; color:#22324A;
  max-width:1100px; margin-top:15px;
}
.badges {display:flex; flex-wrap:wrap; gap:8px; margin-top:16px;}
.badge {
  border:1px solid #CAD8E7; background:#fff; padding:5px 9px;
  border-radius:999px; font-size:.76rem; color:#42546A;
}
.status {
  display:inline-block; border-radius:999px; padding:4px 9px;
  font-size:.73rem; font-weight:780; border:1px solid;
}
.status-go {background:#EAF8F2; color:#0B684D; border-color:#A9DCCB;}
.status-weak {background:#FFF7E8; color:#8C5500; border-color:#E8C47A;}
.status-stop {background:#FFF0EE; color:#A1261C; border-color:#E7B2AC;}
.status-observed {background:#EAF3FF; color:#174A7E; border-color:#B9D3F3;}
.status-estimated {background:#F4EDFF; color:#6941C6; border-color:#D4C4F7;}
.status-gated {background:#FFF0EE; color:#A1261C; border-color:#E7B2AC;}
.metric-card, .science-box, .candidate-card, .step-card {
  border:1px solid var(--line); background:#fff; border-radius:14px;
  padding:15px 17px;
}
.metric-card {min-height:108px;}
.metric-k {font-size:.73rem; text-transform:uppercase; letter-spacing:.08em; color:#718096; font-weight:750;}
.metric-v {font-size:1.52rem; font-weight:770; margin-top:5px; color:var(--ink);}
.metric-n {font-size:.77rem; color:#718096; margin-top:4px;}
.step-card {min-height:150px;}
.step-num {font-size:.73rem; color:#6C7A8E; font-weight:800; letter-spacing:.09em;}
.step-title {font-size:1.05rem; font-weight:760; margin-top:6px; color:#1F2A3A;}
.step-body {font-size:.82rem; color:#64748B; margin-top:6px; line-height:1.5;}
.note {
  border-left:4px solid var(--blue); padding:11px 14px;
  background:#F4F8FC; color:#405268; border-radius:0 10px 10px 0;
}
.warn {
  border-left:4px solid #C47A00; padding:11px 14px;
  background:#FFF8EA; color:#604517; border-radius:0 10px 10px 0;
}
.seq {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size:1.18rem; letter-spacing:.04em; padding:12px 14px;
  border:1px solid var(--line); border-radius:10px; background:#F8FAFC;
  overflow-wrap:anywhere;
}
.kv-grid {
  display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px 18px;
}
.kv {border-bottom:1px solid #EDF2F7; padding:7px 0;}
.kv-k {font-size:.72rem; color:#7A8797; text-transform:uppercase; letter-spacing:.06em;}
.kv-v {font-size:.92rem; color:#25364C; font-weight:650; margin-top:2px;}
.flow {
  display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:9px; align-items:stretch;
}
.flowbox {border:1px solid var(--line); border-radius:12px; padding:12px; background:#fff;}
.flowhead {font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; color:#718096; font-weight:800;}
.flowtext {font-size:.84rem; color:#33465E; margin-top:5px; line-height:1.45;}
hr {border:none; border-top:1px solid var(--line); margin:1.25rem 0;}
div[data-testid="stDataFrame"] {border:1px solid var(--line); border-radius:12px; overflow:hidden;}
.footer {
  margin-top:2.2rem; padding-top:1.1rem; border-top:1px solid var(--line);
  color:#7B8795; font-size:.76rem;
}
@media (max-width: 900px) {
  .flow {grid-template-columns:1fr;}
  .kv-grid {grid-template-columns:1fr;}
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------
@st.cache_data
def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name)

@st.cache_data
def load_model_card() -> dict:
    with open(BASE / "model_card.json", "r", encoding="utf-8") as f:
        return json.load(f)

training = load_csv("training_view.csv")
atomic = load_csv("atomic_nuclearity.csv")
formation = load_csv("formation_controls.csv")
relative_pl = load_csv("relative_pl.csv")
literature = load_csv("literature_additions.csv")
benchmark = load_csv("benchmark.csv")
synthesis = load_csv("synthesis_records.csv")
ptt_benchmarks = load_csv("ptt_benchmarks.csv")
model_card = load_model_card()

NUMERIC = {
    "Au_Nuclearity","Core_Size_nm","Hydrodynamic_Size_nm","pH","Temp_C","Temperature_C",
    "Time_h","Emission_nm","Emission_Peak_nm","PLQY_pct","Ligand_Count","Peptide_Ligand_Count",
    "MAE","RMSE","R2","Spearman","N","Paper_Groups","Lab_Groups","Sequence_Clusters",
    "Fold_Change","Laser_nm","Laser_Power_W_cm2","PTT_Temperature_C","PTT_Time_min"
}
for df in [training, atomic, formation, relative_pl, literature, benchmark, synthesis, ptt_benchmarks]:
    for c in df.columns:
        if c in NUMERIC:
            df[c] = pd.to_numeric(df[c], errors="coerce")

# ---------------------------------------------------------------------
# State + helpers
# ---------------------------------------------------------------------
if "nav" not in st.session_state:
    st.session_state.nav = "Home"
if "queued_nav" in st.session_state:
    st.session_state.nav = st.session_state.pop("queued_nav")

def go(page: str):
    st.session_state.queued_nav = page
    st.rerun()

def init_default(key, value):
    if key not in st.session_state:
        st.session_state[key] = value

# Target defaults
for k, v in {
    "target_cancer":"Triple-negative breast cancer",
    "target_receptor":"αvβ3 integrin",
    "target_atomic":True,
    "target_use_nuclearity":True,
    "target_nuclearity":25,
    "target_nuclearity_tolerance":3,
    "target_core_goal":1.5,
    "target_core_max":2.0,
    "target_laser":808,
    "target_theranostic":True,
    "target_emission":750,
    "target_min_qy":5.0,
    "target_ptt_priority":5,
    "target_stability":"High",
    "target_safety":"Low dark cytotoxicity / high viability",
}.items():
    init_default(k, v)

# Design-space defaults
for k, v in {
    "ds_len_min":3, "ds_len_max":30, "ds_cys_min":1, "ds_cys_max":5,
    "ds_motif":"RGD", "ds_motif_strict":False, "ds_allow_cyclic":True, "ds_allow_d":False,
    "ds_ph_min":8.0, "ds_ph_max":12.5, "ds_temp_min":20.0, "ds_temp_max":70.0,
    "ds_time_min":0.25, "ds_time_max":24.0,
}.items():
    init_default(k, v)

AA = set("ACDEFGHIKLMNPQRSTVWY")
KD = {
    "A":1.8,"C":2.5,"D":-3.5,"E":-3.5,"F":2.8,"G":-0.4,"H":-3.2,"I":4.5,
    "K":-3.9,"L":3.8,"M":1.9,"N":-3.5,"P":-1.6,"Q":-3.5,"R":-4.5,"S":-0.8,
    "T":-0.7,"V":4.2,"W":-0.9,"Y":-1.3
}

def clean_sequence(seq: str) -> str:
    s = re.sub(r"[^A-Za-z]", "", str(seq or "").upper())
    return "".join(a for a in s if a in AA)

def sequence_descriptors(seq: str) -> dict:
    s = clean_sequence(seq)
    if not s:
        return {}
    L = len(s)
    cpos = [i+1 for i,a in enumerate(s) if a=="C"]
    ypos = [i+1 for i,a in enumerate(s) if a=="Y"]
    charge = s.count("K")+s.count("R")+0.1*s.count("H")-s.count("D")-s.count("E")
    arom = sum(s.count(a) for a in "FYW")/L
    hyd = float(np.mean([KD[a] for a in s]))
    spacing = float(np.mean(np.diff(cpos))) if len(cpos)>=2 else np.nan
    return {
        "Sequence":s,"Length":L,"Cys":s.count("C"),"His":s.count("H"),"Tyr":s.count("Y"),
        "Trp":s.count("W"),"Met":s.count("M"),"Charge proxy (pH 7)":round(charge,2),
        "Aromaticity":round(arom,4),"Mean hydropathy":round(hyd,3),
        "CCY motif": "Yes" if "CCY" in s else "No",
        "RGD motif": "Yes" if "RGD" in s else "No",
        "Cys positions":", ".join(map(str,cpos)) if cpos else "None",
        "Tyr positions":", ".join(map(str,ypos)) if ypos else "None",
        "Mean Cys spacing":round(spacing,2) if np.isfinite(spacing) else None,
    }

def nice(value, digits=2, suffix=""):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "—"
    if isinstance(value, (int, np.integer)):
        return f"{value}{suffix}"
    if isinstance(value, (float, np.floating)):
        return f"{value:.{digits}f}{suffix}"
    return str(value)

def humanize(name: str) -> str:
    mapping = {
        "Au_Nuclearity":"Au nuclearity",
        "Core_Size_nm":"Core size (nm)",
        "Hydrodynamic_Size_nm":"Hydrodynamic size (nm)",
        "Emission_nm":"Emission (nm)",
        "Emission_Peak_nm":"Emission (nm)",
        "PLQY_pct":"Quantum yield (%)",
        "Paper_Group":"Paper group",
        "Lab_Group":"Lab group",
        "Material_Regime":"Material regime",
        "Training_Eligibility":"Training eligibility",
        "Eligibility":"Training eligibility",
        "Record_ID":"Record",
        "Source_ID":"Source",
        "Target_Distance":"Evidence match distance",
    }
    return mapping.get(name, name.replace("_"," "))

def status(text: str, kind: str):
    st.markdown(f'<span class="status status-{kind}">{text}</span>', unsafe_allow_html=True)

def metric_card(label, value, note=""):
    st.markdown(
        f'<div class="metric-card"><div class="metric-k">{label}</div>'
        f'<div class="metric-v">{value}</div><div class="metric-n">{note}</div></div>',
        unsafe_allow_html=True,
    )

def stepper(active: int):
    labels = ["Target","Design space","Inverse design","Portfolio","Explain","Synthesis","Validate","Feedback"]
    html = '<div style="display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:6px;margin:8px 0 20px;">'
    for i, lab in enumerate(labels, start=1):
        bg = "#0B5CAB" if i == active else ("#EAF3FF" if i < active else "#F4F6F8")
        color = "#FFFFFF" if i == active else ("#174A7E" if i < active else "#7A8797")
        html += (
            f'<div style="border-radius:9px;padding:7px 5px;text-align:center;background:{bg};color:{color};'
            f'font-size:.72rem;font-weight:760;">{i} · {lab}</div>'
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def target_dict():
    return {
        "cancer":st.session_state.target_cancer,
        "receptor":st.session_state.target_receptor,
        "atomic":st.session_state.target_atomic,
        "use_nuclearity":st.session_state.target_use_nuclearity,
        "nuclearity":st.session_state.target_nuclearity,
        "nuclearity_tolerance":st.session_state.target_nuclearity_tolerance,
        "core_goal":st.session_state.target_core_goal,
        "core_max":st.session_state.target_core_max,
        "laser":st.session_state.target_laser,
        "theranostic":st.session_state.target_theranostic,
        "emission":st.session_state.target_emission,
        "min_qy":st.session_state.target_min_qy,
        "ptt_priority":st.session_state.target_ptt_priority,
        "stability":st.session_state.target_stability,
        "safety":st.session_state.target_safety,
    }

def constraints_dict():
    return {
        "len_min":st.session_state.ds_len_min, "len_max":st.session_state.ds_len_max,
        "cys_min":st.session_state.ds_cys_min, "cys_max":st.session_state.ds_cys_max,
        "motif":clean_sequence(st.session_state.ds_motif),
        "motif_strict":st.session_state.ds_motif_strict,
        "allow_cyclic":st.session_state.ds_allow_cyclic, "allow_d":st.session_state.ds_allow_d,
        "ph_min":st.session_state.ds_ph_min, "ph_max":st.session_state.ds_ph_max,
        "temp_min":st.session_state.ds_temp_min, "temp_max":st.session_state.ds_temp_max,
        "time_min":st.session_state.ds_time_min, "time_max":st.session_state.ds_time_max,
    }

def value_or_nan(row, col):
    try:
        return float(row[col]) if pd.notna(row[col]) else np.nan
    except Exception:
        return np.nan

def candidate_portfolio() -> pd.DataFrame:
    t = target_dict()
    c = constraints_dict()
    rows = []

    for _, r in training.iterrows():
        seq = clean_sequence(r.get("Sequence",""))
        if not seq:
            continue
        d = sequence_descriptors(seq)
        if d["Length"] < c["len_min"] or d["Length"] > c["len_max"]:
            continue
        if d["Cys"] < c["cys_min"] or d["Cys"] > c["cys_max"]:
            continue
        motif_match = bool(c["motif"] and c["motif"] in seq)
        if c["motif_strict"] and c["motif"] and not motif_match:
            continue

        penalties, observed = [], 0
        # Atomic architecture
        is_atomic = str(r.get("Material_Regime","")) == "atomically_precise_AuNC"
        if t["atomic"]:
            penalties.append(0.0 if is_atomic else 1.6)

        au_n = value_or_nan(r, "Au_Nuclearity")
        if t["use_nuclearity"]:
            if np.isfinite(au_n):
                observed += 1
                penalties.append(abs(au_n - t["nuclearity"]) / max(float(t["nuclearity_tolerance"]), 1.0))
            else:
                penalties.append(1.25)

        size = value_or_nan(r, "Core_Size_nm")
        if np.isfinite(size):
            observed += 1
            p = abs(size - t["core_goal"]) / 0.7
            if size > t["core_max"]:
                p += (size - t["core_max"]) / 0.5
            penalties.append(p)
        else:
            penalties.append(1.0)

        em = value_or_nan(r, "Emission_nm")
        if t["theranostic"]:
            if np.isfinite(em):
                observed += 1
                penalties.append(abs(em - t["emission"]) / 180.0)
            else:
                penalties.append(1.0)

        qy = value_or_nan(r, "PLQY_pct")
        if t["theranostic"]:
            if np.isfinite(qy):
                observed += 1
                penalties.append(max(0.0, t["min_qy"] - qy) / 8.0)
            else:
                penalties.append(0.9)

        if c["motif"]:
            penalties.append(0.0 if motif_match else 0.65)

        # Synthesis-window feasibility only where known.
        ph = value_or_nan(r, "pH")
        temp = value_or_nan(r, "Temp_C")
        tm = value_or_nan(r, "Time_h")
        for val, lo, hi in [
            (ph,c["ph_min"],c["ph_max"]),
            (temp,c["temp_min"],c["temp_max"]),
            (tm,c["time_min"],c["time_max"]),
        ]:
            if np.isfinite(val):
                penalties.append(0.0 if lo <= val <= hi else 0.75)
            else:
                penalties.append(0.18)

        mean_penalty = float(np.mean(penalties)) if penalties else 2.0
        coverage = observed / (4 if t["theranostic"] else 2)
        match_index = 100.0 * math.exp(-0.62*mean_penalty) * (0.72 + 0.28*min(1.0, coverage))

        rows.append({
            "Candidate_ID":r.get("Record_ID"),
            "Source_ID":r.get("Source_ID"),
            "Sequence":seq,
            "Evidence_Match_Index":round(match_index,1),
            "Atomic_Regime":"Yes" if is_atomic else "No",
            "Observed_Au_Nuclearity":au_n,
            "Observed_Core_Size_nm":size,
            "Observed_Emission_nm":em,
            "Observed_PLQY_pct":qy,
            "Observed_pH":ph,
            "Observed_Temp_C":temp,
            "Observed_Time_h":tm,
            "Targeting_Motif_Match":"Yes" if motif_match else ("Not requested" if not c["motif"] else "No"),
            "Paper_Group":r.get("Paper_Group"),
            "Lab_Group":r.get("Lab_Group"),
            "Material_Regime":r.get("Material_Regime"),
            "Critical_Validation_Note":r.get("Critical_Validation_Note"),
            "Evidence_Coverage":round(coverage,2),
        })

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["Evidence_Match_Index","Evidence_Coverage"], ascending=[False,False]).reset_index(drop=True)

def get_portfolio() -> pd.DataFrame:
    # Always recompute from current target/design state to avoid stale decisions.
    pf = candidate_portfolio()
    st.session_state.portfolio = pf
    return pf

def get_selected_record() -> str | None:
    rid = st.session_state.get("selected_record")
    if rid:
        return rid
    pf = get_portfolio()
    if not pf.empty:
        rid = str(pf.iloc[0]["Candidate_ID"])
        st.session_state.selected_record = rid
        return rid
    return None

def training_row(record_id: str) -> pd.Series | None:
    m = training[training["Record_ID"].astype(str) == str(record_id)]
    return None if m.empty else m.iloc[0]

def synthesis_row(record_id: str) -> pd.Series | None:
    m = synthesis[synthesis["Record_ID"].astype(str) == str(record_id)]
    return None if m.empty else m.iloc[0]

def queue_button(label: str, destination: str, key: str, type="primary"):
    if st.button(label, key=key, type=type, use_container_width=True):
        go(destination)

def format_regime(x):
    mapping = {
        "atomically_precise_AuNC":"Atomically precise AuNC",
        "ultrasmall_AuNC_unknown_nuclearity":"Ultrasmall AuNC · nuclearity unresolved",
    }
    return mapping.get(str(x), str(x).replace("_"," "))

def property_line(label, value, state="observed"):
    badge = {
        "observed":'<span class="status status-observed">OBSERVED</span>',
        "estimated":'<span class="status status-estimated">ESTIMATED</span>',
        "gated":'<span class="status status-gated">GATED</span>',
    }[state]
    st.markdown(
        f'<div style="display:flex;justify-content:space-between;gap:12px;align-items:center;'
        f'padding:8px 0;border-bottom:1px solid #EDF2F7;"><div><b>{label}</b><div style="color:#64748B;font-size:.82rem;">{value}</div></div>{badge}</div>',
        unsafe_allow_html=True
    )

# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"### {APP_NAME}")
    st.caption(f"{APP_VERSION} · {DATA_VERSION}")
    page = st.radio("Workflow", NAV, key="nav", label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div class="smallcaps">Scientific state</div>', unsafe_allow_html=True)
    status("EVIDENCE PLATFORM · GO","go")
    st.write("")
    status("PREDICTIVE MODEL · GATED","stop")
    st.caption("v0.2 is target-first and evidence-guided. Full multi-property prediction awaits stronger prospective data.")

# ---------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------
def page_home():
    st.markdown(
        f"""
<div class="hero">
  <div class="brandline">NANOMAX · PEPTIDE × AI × ATOMIC GOLD</div>
  <div class="hero-title">{APP_NAME}</div>
  <div class="hero-sub">Target-first inverse-design workflow for peptide-programmed gold nanoclusters in cancer photothermal therapy.</div>
  <div class="question">Which peptide sequence, under which synthesis conditions, is most likely to produce a specific gold nanocluster architecture with the optical, photothermal, stability, targeting, and safety properties required for cancer PTT?</div>
  <div class="badges">
    <span class="badge">{APP_VERSION} · Research Prototype</span>
    <span class="badge">{DATA_VERSION}</span>
    <span class="badge">{BENCHMARK_VERSION}</span>
    <span class="badge">Evidence-first · no unvalidated confidence claims</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    c1,c2,c3,c4 = st.columns(4)
    with c1: metric_card("Curated evidence","66","Source-separated records")
    with c2: metric_card("Atomic audit","10","Nuclearity-labeled training records")
    with c3: metric_card("Independent labs","14","Lab-aware validation metadata")
    with c4: metric_card("PTT predictor","GATED","Direct peptide-AuNC PTT data still sparse")

    st.markdown("### Target-first discovery loop")
    steps = [
        ("01","Define target","Specify architecture, laser/PTT, optical, targeting, stability and safety goals."),
        ("02","Design space","Bound peptide chemistry and experimentally feasible synthesis conditions."),
        ("03","Inverse design","Rank peptide + synthesis evidence against the target vector."),
        ("04","Portfolio","Compare multiple candidate solutions instead of a single opaque winner."),
        ("05","Explain","Trace sequence motifs, evidence provenance, uncertainty and missing objectives."),
        ("06","Plan synthesis","Turn a selected evidence anchor into a bounded DOE around known conditions."),
        ("07","Validate","Inspect paper-, lab- and sequence-aware model performance and property gates."),
        ("08","Feedback","Return wet-lab measurements to the closed-loop discovery workflow."),
    ]
    for row_start in (0,4):
        cols = st.columns(4)
        for col, (num,title,body) in zip(cols, steps[row_start:row_start+4]):
            with col:
                st.markdown(
                    f'<div class="step-card"><div class="step-num">{num}</div>'
                    f'<div class="step-title">{title}</div><div class="step-body">{body}</div></div>',
                    unsafe_allow_html=True,
                )
    st.write("")
    c1,c2 = st.columns([1,2])
    with c1:
        queue_button("Start with the target →","1 · Define Target","home_start")
    with c2:
        st.markdown(
            '<div class="note"><b>v0.2 design principle:</b> the user starts from the AuNC/cancer-PTT specification. '
            'The current engine ranks evidence-backed peptide–synthesis systems and clearly marks PTT, stability and safety as gated where direct labels are insufficient.</div>',
            unsafe_allow_html=True,
        )

def page_target():
    stepper(1)
    st.markdown("## 1 · Define Target")
    st.caption("Describe the AuNC you want to build and the cancer-PTT function it must perform.")

    a,b = st.columns([1.05,1], gap="large")
    with a:
        st.markdown("### Disease & targeting")
        st.selectbox(
            "Cancer indication",
            ["Triple-negative breast cancer","Breast cancer","Prostate cancer","Melanoma","Lung cancer","Other"],
            key="target_cancer",
        )
        st.selectbox(
            "Target receptor / biological target",
            ["αvβ3 integrin","HER2","EGFR","None / unspecified","Other"],
            key="target_receptor",
        )
        st.markdown("### Architecture")
        st.checkbox("Atomic precision required", key="target_atomic")
        st.checkbox("Specify target nuclearity", key="target_use_nuclearity")
        if st.session_state.target_use_nuclearity:
            x,y = st.columns(2)
            with x: st.number_input("Target Au atom count", 5, 100, key="target_nuclearity")
            with y: st.number_input("Acceptable ± Au atoms", 1, 20, key="target_nuclearity_tolerance")
        x,y = st.columns(2)
        with x: st.number_input("Preferred core size (nm)", 0.5, 5.0, step=0.1, key="target_core_goal")
        with y: st.number_input("Maximum core size (nm)", 0.5, 10.0, step=0.1, key="target_core_max")

    with b:
        st.markdown("### PTT & optical function")
        st.selectbox("Laser wavelength for PTT (nm)", [808,980,1064], key="target_laser")
        st.slider("PTT priority", 1, 5, key="target_ptt_priority",
                  help="PTT is collected as a target but not yet used as a learned prediction because direct peptide-AuNC PTT labels are sparse.")
        st.checkbox("Theranostic fluorescence is also required", key="target_theranostic")
        if st.session_state.target_theranostic:
            x,y = st.columns(2)
            with x: st.number_input("Preferred emission (nm)", 350, 1300, step=10, key="target_emission")
            with y: st.number_input("Minimum desired QY (%)", 0.0, 50.0, step=1.0, key="target_min_qy")
        st.markdown("### Stability & safety")
        st.selectbox("Desired serum stability", ["Moderate","High","Very high"], key="target_stability")
        st.selectbox(
            "Safety objective",
            ["Low dark cytotoxicity / high viability","Low hemolysis","Renal-clearance compatible","Balanced safety profile"],
            key="target_safety",
        )

    st.markdown("### Target specification vector")
    t = target_dict()
    cols = st.columns(5)
    vals = [
        ("Cancer",t["cancer"]),
        ("Target",t["receptor"]),
        ("Architecture",f"Au{t['nuclearity']} ± {t['nuclearity_tolerance']}" if t["use_nuclearity"] else "Flexible"),
        ("Core",f"{t['core_goal']:.1f} nm · max {t['core_max']:.1f}"),
        ("PTT",f"{t['laser']} nm · priority {t['ptt_priority']}/5"),
    ]
    for col,(k,v) in zip(cols,vals):
        with col: metric_card(k,v)
    st.markdown(
        '<div class="warn"><b>Coverage warning:</b> PTT, stability and safety are valid design objectives, but the present dataset does not yet support learned models for all three. They remain visible as explicit scientific gaps rather than being silently folded into a fabricated score.</div>',
        unsafe_allow_html=True,
    )
    c1,c2 = st.columns([3,1])
    with c2: queue_button("Continue to design space →","2 · Design Space","target_next")

def page_design_space():
    stepper(2)
    st.markdown("## 2 · Design Space")
    st.caption("Constrain what the inverse-design engine is allowed to consider—both peptide chemistry and practical synthesis conditions.")

    if st.session_state.target_receptor == "αvβ3 integrin" and "ds_motif_user_changed" not in st.session_state:
        st.session_state.ds_motif = "RGD"

    a,b = st.columns(2, gap="large")
    with a:
        st.markdown("### Peptide constraints")
        x,y = st.columns(2)
        with x: st.number_input("Minimum peptide length", 2, 100, key="ds_len_min")
        with y: st.number_input("Maximum peptide length", 2, 100, key="ds_len_max")
        x,y = st.columns(2)
        with x: st.number_input("Minimum Cys count", 0, 20, key="ds_cys_min")
        with y: st.number_input("Maximum Cys count", 0, 20, key="ds_cys_max")
        motif = st.text_input("Desired targeting / functional motif", key="ds_motif")
        if motif != "RGD":
            st.session_state.ds_motif_user_changed = True
        st.checkbox("Require motif as a strict filter", key="ds_motif_strict")
        x,y = st.columns(2)
        with x: st.checkbox("Allow cyclic peptides", key="ds_allow_cyclic")
        with y: st.checkbox("Allow D-amino-acid designs", key="ds_allow_d")

    with b:
        st.markdown("### Synthesis window")
        x,y = st.columns(2)
        with x: st.number_input("Minimum pH", 1.0, 14.0, step=0.5, key="ds_ph_min")
        with y: st.number_input("Maximum pH", 1.0, 14.0, step=0.5, key="ds_ph_max")
        x,y = st.columns(2)
        with x: st.number_input("Minimum temperature (°C)", 0.0, 100.0, step=5.0, key="ds_temp_min")
        with y: st.number_input("Maximum temperature (°C)", 0.0, 100.0, step=5.0, key="ds_temp_max")
        x,y = st.columns(2)
        with x: st.number_input("Minimum reaction time (h)", 0.0, 72.0, step=0.25, key="ds_time_min")
        with y: st.number_input("Maximum reaction time (h)", 0.0, 72.0, step=0.5, key="ds_time_max")
        st.multiselect(
            "Allowed reduction / formation strategies",
            ["Peptide-mediated","NaBH₄-assisted","Photochemical","TCEP + NaBH₄","Thermal/alkaline","Any evidence-backed strategy"],
            default=["Any evidence-backed strategy"],
            key="ds_reduction_modes",
        )

    st.markdown("### Active search envelope")
    c = constraints_dict()
    c1,c2,c3,c4 = st.columns(4)
    with c1: metric_card("Length",f"{c['len_min']}–{c['len_max']} aa")
    with c2: metric_card("Cys",f"{c['cys_min']}–{c['cys_max']}")
    with c3: metric_card("pH",f"{c['ph_min']:.1f}–{c['ph_max']:.1f}")
    with c4: metric_card("Temperature",f"{c['temp_min']:.0f}–{c['temp_max']:.0f} °C")
    st.markdown(
        '<div class="note"><b>Important:</b> a synthesis condition that is missing in a paper is treated as unknown, not assumed to lie inside your permitted window.</div>',
        unsafe_allow_html=True,
    )
    c1,c2 = st.columns([3,1])
    with c2: queue_button("Run inverse design →","3 · Inverse Design","design_next")

def page_inverse():
    stepper(3)
    st.markdown("## 3 · Inverse Design")
    st.caption("Search the current evidence space for peptide–synthesis systems closest to the target vector.")

    st.markdown("### Objective coverage")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: metric_card("Architecture","AVAILABLE","10 nuclearity labels")
    with c2: metric_card("Optical","PARTIAL","16 emission · 15 QY")
    with c3: metric_card("PTT","GATED","No direct trainable panel")
    with c4: metric_card("Stability","GATED","Not systematically labeled")
    with c5: metric_card("Targeting","MOTIF-LEVEL","Evidence + motif match")
    with c6: metric_card("Safety","GATED","Insufficient structured labels")

    st.markdown(
        '<div class="warn"><b>Evidence-constrained inverse design:</b> v0.2 ranks real experimental systems against the desired target and synthesis envelope. '
        'It does not yet generate a validated novel peptide or predict PTT/safety outcomes that the dataset cannot support.</div>',
        unsafe_allow_html=True,
    )

    pf = get_portfolio()
    if pf.empty:
        st.error("No evidence records satisfy the current hard peptide constraints. Relax the strict motif or sequence limits in Design Space.")
        return

    st.markdown("### Top evidence-ranked design anchors")
    top = pf.head(5).copy()
    display = top[[
        "Candidate_ID","Sequence","Evidence_Match_Index","Atomic_Regime",
        "Observed_Au_Nuclearity","Observed_Core_Size_nm","Observed_Emission_nm",
        "Observed_PLQY_pct","Targeting_Motif_Match"
    ]].rename(columns={
        "Candidate_ID":"Record",
        "Evidence_Match_Index":"Evidence match index",
        "Atomic_Regime":"Atomic regime",
        "Observed_Au_Nuclearity":"Observed Au nuclearity",
        "Observed_Core_Size_nm":"Observed core size (nm)",
        "Observed_Emission_nm":"Observed emission (nm)",
        "Observed_PLQY_pct":"Observed QY (%)",
        "Targeting_Motif_Match":"Motif match",
    })
    st.dataframe(display, hide_index=True, use_container_width=True)
    st.caption("Evidence match index is a target-distance/ranking measure within PepAuDB—not a probability of successful synthesis.")

    c1,c2 = st.columns([3,1])
    with c2: queue_button("Open candidate portfolio →","4 · Candidate Portfolio","inverse_next")

def candidate_card(row, key_prefix):
    rid = str(row["Candidate_ID"])
    seq = str(row["Sequence"])
    with st.container(border=True):
        x,y = st.columns([3,1])
        with x:
            st.markdown(f"#### {rid} · `{seq}`")
            st.caption(f"{format_regime(row['Material_Regime'])} · Source {row['Source_ID']} · Lab {row['Lab_Group']}")
        with y:
            st.metric("Evidence match", f"{row['Evidence_Match_Index']:.1f}/100")
        m1,m2,m3,m4 = st.columns(4)
        with m1: st.metric("Au nuclearity", nice(row["Observed_Au_Nuclearity"],0))
        with m2: st.metric("Core size", nice(row["Observed_Core_Size_nm"],2," nm"))
        with m3: st.metric("Emission", nice(row["Observed_Emission_nm"],0," nm"))
        with m4: st.metric("QY", nice(row["Observed_PLQY_pct"],2,"%"))
        status("OBSERVED LITERATURE ANCHOR","observed")
        st.write("")
        status("PTT / STABILITY / SAFETY · GATED","gated")
        if st.button("Inspect candidate", key=f"{key_prefix}_{rid}", use_container_width=True):
            st.session_state.selected_record = rid
            go("5 · Design Explainer")

def page_portfolio():
    stepper(4)
    st.markdown("## 4 · Candidate Portfolio")
    st.caption("Compare multiple design anchors. No single opaque 'best peptide' is presented as experimentally proven.")

    pf = get_portfolio()
    if pf.empty:
        st.error("No candidates are available under the current constraints.")
        return

    st.markdown(
        '<div class="note"><b>Portfolio logic:</b> architecture, available optical measurements, motif match and known synthesis-window compatibility contribute to ranking. '
        'PTT, systematic stability and safety are intentionally not converted into fake numerical scores.</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    top = pf.head(6)
    for i in range(0, len(top), 2):
        cols = st.columns(2, gap="large")
        for col, (_,row) in zip(cols, top.iloc[i:i+2].iterrows()):
            with col:
                candidate_card(row, "inspect")

def page_explainer():
    stepper(5)
    rid = get_selected_record()
    if not rid:
        st.error("Select a candidate from the portfolio first.")
        return
    tr = training_row(rid)
    sr = synthesis_row(rid)
    if tr is None:
        st.error("Selected record is not in the training view.")
        return

    seq = clean_sequence(tr["Sequence"])
    d = sequence_descriptors(seq)

    st.markdown(f"## 5 · Design Explainer — {rid}")
    st.caption("Separate direct observation from inference, expose sequence motifs, provenance and unresolved objectives.")
    st.markdown(f'<div class="seq">{seq}</div>', unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1: metric_card("Cys",d.get("Cys","—"),d.get("Cys positions",""))
    with c2: metric_card("Tyr",d.get("Tyr","—"),d.get("Tyr positions",""))
    with c3: metric_card("Charge proxy",d.get("Charge proxy (pH 7)","—"),"simple pH-7 sequence proxy")
    with c4: metric_card("Functional motifs",f"CCY: {d.get('CCY motif')} · RGD: {d.get('RGD motif')}")

    st.markdown("### Evidence chain")
    atomic_text = f"Observed Au{int(tr['Au_Nuclearity'])}" if pd.notna(tr.get("Au_Nuclearity")) else "Nuclearity unresolved"
    optical_text = (
        f"{nice(tr.get('Emission_nm'),0,' nm')} emission; QY {nice(tr.get('PLQY_pct'),2,'%')}"
        if pd.notna(tr.get("Emission_nm")) or pd.notna(tr.get("PLQY_pct"))
        else "Optical endpoint incomplete"
    )
    synth_text = "Primary synthesis context available" if sr is not None else "Synthesis context incomplete"
    flow = [
        ("Sequence",f"{d.get('Cys')} Cys · {d.get('Tyr')} Tyr · motif-aware"),
        ("Coordination / formation",synth_text),
        ("Architecture",atomic_text + f" · core {nice(tr.get('Core_Size_nm'),2,' nm')}"),
        ("Optical",optical_text),
        ("Cancer-PTT translation","PTT / stability / safety remain gated unless directly observed"),
    ]
    html = '<div class="flow">'
    for h,t in flow:
        html += f'<div class="flowbox"><div class="flowhead">{h}</div><div class="flowtext">{t}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("### Property evidence state")
    a,b = st.columns(2, gap="large")
    with a:
        property_line("Au nuclearity",nice(tr.get("Au_Nuclearity"),0),"observed" if pd.notna(tr.get("Au_Nuclearity")) else "gated")
        property_line("Core size",nice(tr.get("Core_Size_nm"),2," nm"),"observed" if pd.notna(tr.get("Core_Size_nm")) else "gated")
        property_line("Emission",nice(tr.get("Emission_nm"),0," nm"),"observed" if pd.notna(tr.get("Emission_nm")) else "gated")
        property_line("Quantum yield",nice(tr.get("PLQY_pct"),2,"%"),"observed" if pd.notna(tr.get("PLQY_pct")) else "gated")
    with b:
        property_line("Photothermal performance","Not modeled for this candidate","gated")
        property_line("Serum / colloidal stability","Not systematically labeled","gated")
        property_line("Targeting",f"Motif check: {st.session_state.ds_motif or 'none specified'}","observed" if st.session_state.ds_motif and st.session_state.ds_motif in seq else "gated")
        property_line("Safety","No validated sequence→safety model","gated")

    st.markdown("### Scientific caveat")
    st.info(str(tr.get("Critical_Validation_Note","No additional caveat recorded.")))
    c1,c2 = st.columns([3,1])
    with c2: queue_button("Plan synthesis →","6 · Synthesis Planner","explain_next")

def build_doe(anchor, c):
    ph = pd.to_numeric(pd.Series([anchor.get("pH")]), errors="coerce").iloc[0]
    temp = pd.to_numeric(pd.Series([anchor.get("Temperature_C")]), errors="coerce").iloc[0]
    tm = pd.to_numeric(pd.Series([anchor.get("Time_h")]), errors="coerce").iloc[0]
    rows = []
    def clipped(v, lo, hi):
        return min(max(v,lo),hi)
    rows.append(["E0 · Literature anchor",ph,temp,tm,"Reproduce the source condition first"])
    if np.isfinite(ph):
        rows.append(["E1 · pH−",clipped(ph-0.5,c["ph_min"],c["ph_max"]),temp,tm,"Local pH sensitivity"])
        rows.append(["E2 · pH+",clipped(ph+0.5,c["ph_min"],c["ph_max"]),temp,tm,"Local pH sensitivity"])
    if np.isfinite(temp):
        rows.append(["E3 · Temperature",ph,clipped(temp+10,c["temp_min"],c["temp_max"]),tm,"Temperature sensitivity"])
    if np.isfinite(tm):
        rows.append(["E4 · Time",ph,temp,clipped(tm*1.25,c["time_min"],c["time_max"]),"Kinetic sensitivity"])
    return pd.DataFrame(rows[:5], columns=["Experiment","pH","Temperature_C","Time_h","Purpose"])

def page_synthesis():
    stepper(6)
    rid = get_selected_record()
    if not rid:
        st.error("Select a candidate first.")
        return
    sr = synthesis_row(rid)
    tr = training_row(rid)
    st.markdown(f"## 6 · Synthesis Planner — {rid}")
    st.caption("Anchor planning to the primary literature and explore a bounded local DOE. No false-precision recipe is invented.")

    if sr is None:
        st.warning("No structured synthesis record is available for this candidate.")
        return

    st.markdown("### Literature synthesis anchor")
    a,b = st.columns([1.15,1], gap="large")
    with a:
        fields = [
            ("Peptide / ligand",sr.get("Peptide_or_Ligand")),
            ("Sequence",sr.get("Sequence")),
            ("Au precursor",sr.get("Au_Precursor")),
            ("Ligand / precursor condition",sr.get("Peptide_or_Ligand_Condition")),
            ("Reducing strategy",sr.get("Reducing_Agent")),
        ]
        html = '<div class="science-box"><div class="kv-grid">'
        for k,v in fields:
            html += f'<div class="kv"><div class="kv-k">{k}</div><div class="kv-v">{nice(v)}</div></div>'
        html += '</div></div>'
        st.markdown(html, unsafe_allow_html=True)
    with b:
        c1,c2,c3 = st.columns(3)
        with c1: st.metric("pH",nice(sr.get("pH"),1))
        with c2: st.metric("Temperature",nice(sr.get("Temperature_C"),1," °C"))
        with c3: st.metric("Time",nice(sr.get("Time_h"),2," h"))
        st.markdown("**Process**")
        st.write(nice(sr.get("Mixing_or_Process")))
        doi = str(sr.get("DOI_URL",""))
        if doi and doi != "nan":
            st.link_button("Open primary source",doi,use_container_width=True)

    st.markdown("### Proposed local DOE")
    doe = build_doe(sr, constraints_dict())
    if len(doe) <= 1:
        st.warning("Too few structured condition values are available to generate a responsible local DOE.")
    else:
        st.dataframe(
            doe.rename(columns={"Temperature_C":"Temperature (°C)","Time_h":"Time (h)"}),
            hide_index=True, use_container_width=True
        )
        st.markdown(
            '<div class="warn"><b>DOE status:</b> this matrix is a bounded sensitivity plan around a literature anchor, not a validated optimum. '
            'Reagent ratios, addition order and purification must remain tied to the cited source unless experimentally redesigned.</div>',
            unsafe_allow_html=True,
        )
    c1,c2 = st.columns([3,1])
    with c2: queue_button("Review validation →","7 · Validation & Model","synth_next")

def benchmark_summary():
    numeric = benchmark.copy()
    numeric = numeric[numeric["Validation"].isin(["paper_grouped","lab_grouped"])]
    numeric = numeric[numeric["MAE"].notna()]
    rows = []
    for (target,validation),g in numeric.groupby(["Target","Validation"]):
        dummy = g[g["Model"]=="DummyMedian"]
        learned = g[g["Model"]!="DummyMedian"]
        if dummy.empty or learned.empty:
            continue
        d = dummy.sort_values("MAE").iloc[0]
        b = learned.sort_values("MAE").iloc[0]
        rows.append({
            "Target":humanize(target),
            "Validation":validation.replace("_"," "),
            "Best learned model":b["Model"],
            "Learned MAE":b["MAE"],
            "Baseline MAE":d["MAE"],
            "OOF R²":b["R2"],
            "Improvement vs baseline (%)":100*(d["MAE"]-b["MAE"])/d["MAE"] if d["MAE"] else np.nan
        })
    return pd.DataFrame(rows)

def page_validation():
    stepper(7)
    st.markdown("## 7 · Validation & Model")
    st.caption("A target is not released simply because an algorithm produces a number. It must beat baseline under grouped validation.")

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        metric_card("Core size","EXPLORATORY","RF MAE 0.298 nm · OOF R² +0.231")
    with c2:
        metric_card("Nuclearity","NOT APPROVED","Lab-aware MAE 3.745 vs baseline 3.700")
    with c3:
        metric_card("Emission","NOT APPROVED","Learned model worse than baseline")
    with c4:
        metric_card("PTT","GATED","Insufficient direct peptide-AuNC labels")

    summary = benchmark_summary()
    st.markdown("### Grouped benchmark summary")
    st.dataframe(summary, hide_index=True, use_container_width=True)

    if not summary.empty:
        fig = px.bar(
            summary,
            x="Target",
            y="Improvement vs baseline (%)",
            color="Validation",
            barmode="group",
            title="MAE improvement versus simple baseline",
        )
        fig.add_hline(y=0, line_dash="dash")
        fig.update_layout(height=380, margin=dict(l=10,r=10,t=55,b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Photothermal evidence layer")
    st.caption("These are benchmark/reference records, not a learned sequence→PTT model.")
    ptt_show = ptt_benchmarks.rename(columns={c:humanize(c) for c in ptt_benchmarks.columns})
    st.dataframe(ptt_show, hide_index=True, use_container_width=True)

    st.markdown(
        '<div class="note"><b>Validation rule:</b> production release requires paper-grouped, lab-aware and sequence-aware robustness plus an untouched external/prospective test set.</div>',
        unsafe_allow_html=True,
    )
    c1,c2 = st.columns([3,1])
    with c2: queue_button("Prepare experiment feedback →","8 · Experiment Feedback","val_next")

def page_feedback():
    stepper(8)
    rid = get_selected_record()
    tr = training_row(rid) if rid else None
    st.markdown("## 8 · Experiment Feedback")
    st.caption("Close the loop by returning prospective wet-lab measurements to the Studio. v0.2 keeps uploaded feedback session-only.")

    if tr is None:
        st.info("Select a candidate first. A generic feedback template is still available.")

    template = pd.DataFrame([{
        "Candidate_ID":rid or "",
        "Sequence":clean_sequence(tr["Sequence"]) if tr is not None else "",
        "Literature_Reference_Au_Nuclearity":tr.get("Au_Nuclearity") if tr is not None else "",
        "Literature_Reference_Core_Size_nm":tr.get("Core_Size_nm") if tr is not None else "",
        "Observed_Au_Nuclearity":"",
        "Observed_Core_Size_nm":"",
        "Observed_Emission_nm":"",
        "Observed_PLQY_pct":"",
        "Laser_nm":st.session_state.target_laser,
        "Power_W_cm2":"",
        "PCE_pct":"",
        "DeltaT_C":"",
        "Serum_Stability_h":"",
        "Dark_Viability_pct":"",
        "Targeting_Readout":"",
        "Notes":"",
    }])
    st.download_button(
        "Download experiment feedback template",
        template.to_csv(index=False).encode("utf-8"),
        file_name=f"{APP_NAME.replace(' ','_')}_{rid or 'candidate'}_feedback.csv",
        mime="text/csv",
        use_container_width=True,
    )
    upload = st.file_uploader("Upload completed feedback CSV", type=["csv"])
    if upload is not None:
        try:
            obs = pd.read_csv(upload)
            st.session_state.feedback_df = obs
            st.success("Feedback loaded for this session.")
            st.dataframe(obs, hide_index=True, use_container_width=True)
            required = ["Observed_Au_Nuclearity","Observed_Core_Size_nm","Observed_Emission_nm","Observed_PLQY_pct"]
            present = [c for c in required if c in obs.columns]
            if present:
                st.markdown("### Prospective measurements detected")
                c1,c2,c3,c4 = st.columns(4)
                vals = []
                for col in required:
                    if col in obs.columns:
                        vals.append(pd.to_numeric(obs[col],errors="coerce").dropna())
                    else:
                        vals.append(pd.Series(dtype=float))
                labels = ["Au nuclearity","Core size","Emission","QY"]
                suffixes = [""," nm"," nm","%"]
                for col,label,ser,suf in zip([c1,c2,c3,c4],labels,vals,suffixes):
                    with col:
                        metric_card(label,nice(ser.iloc[0] if len(ser) else None,2,suf))
            st.markdown(
                '<div class="warn"><b>Persistence:</b> v0.2 does not automatically write uploaded results back to PepAuDB. '
                'After QC, prospective results should enter a separate experimental table with source, batch, replicate and instrument metadata.</div>',
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.error(f"Could not parse the feedback file: {e}")

def evidence_cards(df: pd.DataFrame, n=8):
    for i in range(0, min(len(df),n), 2):
        cols = st.columns(2)
        for col,(_,r) in zip(cols,df.iloc[i:i+2].iterrows()):
            with col:
                with st.container(border=True):
                    st.markdown(f"#### {r.get('Record_ID')} · `{clean_sequence(r.get('Sequence',''))}`")
                    st.caption(f"Source {r.get('Source_ID')} · {format_regime(r.get('Material_Regime'))}")
                    m1,m2,m3,m4 = st.columns(4)
                    with m1: st.metric("Au",nice(r.get("Au_Nuclearity"),0))
                    with m2: st.metric("Core",nice(r.get("Core_Size_nm"),2," nm"))
                    with m3: st.metric("Emission",nice(r.get("Emission_nm"),0," nm"))
                    with m4: st.metric("QY",nice(r.get("PLQY_pct"),2,"%"))

def page_evidence_methods():
    st.markdown("## Evidence & Methods")
    st.caption("Supporting scientific layers remain accessible without interrupting the target-first discovery workflow.")
    t1,t2,t3,t4 = st.tabs(["PepAuDB Explorer","Atomic Precision","Formation Science","Model Card"])

    with t1:
        a,b,c = st.columns(3)
        with a:
            regimes = st.multiselect("Material regime",sorted(training["Material_Regime"].dropna().unique()),key="ev_regime")
        with b:
            elig = st.multiselect("Training use",sorted(training["Eligibility"].dropna().unique()),key="ev_elig")
        with c:
            search = st.text_input("Sequence / record",key="ev_search")
        df = training.copy()
        if regimes: df = df[df["Material_Regime"].isin(regimes)]
        if elig: df = df[df["Eligibility"].isin(elig)]
        if search:
            q = search.upper()
            df = df[
                df["Sequence"].fillna("").str.upper().str.contains(q,regex=False)
                | df["Record_ID"].fillna("").str.upper().str.contains(q,regex=False)
            ]
        evidence_cards(df,8)
        with st.expander("Advanced raw database view"):
            pretty = df.rename(columns={c:humanize(c) for c in df.columns})
            st.dataframe(pretty,hide_index=True,use_container_width=True,height=480)

    with t2:
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Atomic records",len(atomic))
        with c2: st.metric("Unique nuclearities",atomic["Au_Nuclearity"].nunique())
        with c3: st.metric("Independent papers",atomic["Paper_Group"].nunique())
        with c4: st.metric("Independent labs",atomic["Lab_Group"].nunique())
        counts = atomic["Au_Nuclearity"].value_counts().sort_index().reset_index()
        counts.columns = ["Au nuclearity","Count"]
        fig = px.bar(counts,x="Au nuclearity",y="Count",text="Count",title="Exact nuclearity counts")
        fig.update_layout(height=350,margin=dict(l=10,r=10,t=55,b=10))
        st.plotly_chart(fig,use_container_width=True)
        show = atomic.rename(columns={c:humanize(c) for c in atomic.columns})
        st.dataframe(show,hide_index=True,use_container_width=True)

    with t3:
        counts = formation["Training_Status"].value_counts()
        c1,c2 = st.columns(2)
        with c1: metric_card("Verified AuNC-forming controls",int(counts.get("FORMATION_POSITIVE",0)))
        with c2: metric_card("Verified failure controls",int(counts.get("FORMATION_NEGATIVE",0)))
        st.markdown("### Matched formation evidence")
        show_cols = ["Sequence","Outcome","Fluorescence","Material_Observed","Matched_Counterpart","Conditions_Matched","Scientific_Note"]
        st.dataframe(formation[[c for c in show_cols if c in formation.columns]],hide_index=True,use_container_width=True)
        st.markdown("### Relative photoluminescence evidence")
        st.caption("Ranking evidence is retained as ranking evidence—not converted to invented absolute QY.")
        st.dataframe(relative_pl,hide_index=True,use_container_width=True)

    with t4:
        st.markdown("### Model identity")
        x1,x2,x3,x4 = st.columns(4)
        with x1: metric_card("Studio",APP_VERSION)
        with x2: metric_card("Database",DATA_VERSION)
        with x3: metric_card("Benchmark",BENCHMARK_VERSION)
        with x4: metric_card("Production ready","NO")
        st.markdown("### Approved now")
        st.write(
            "• Target specification and constrained evidence search\n"
            "• Candidate descriptor analysis and evidence ranking\n"
            "• Atomic-precision provenance audit\n"
            "• Literature-anchored synthesis planning\n"
            "• Paper-, lab- and sequence-aware validation"
        )
        st.markdown("### Gated")
        st.write(
            "• Validated novel-sequence nuclearity prediction\n"
            "• Formation probability for arbitrary novel peptides\n"
            "• Generalizable emission / PLQY prediction\n"
            "• Sequence+synthesis→PTT prediction\n"
            "• Validated stability, targeting and safety prediction"
        )
        with st.expander("Technical model card JSON"):
            st.json(model_card,expanded=False)

# Dispatch
if page == "Home":
    page_home()
elif page == "1 · Define Target":
    page_target()
elif page == "2 · Design Space":
    page_design_space()
elif page == "3 · Inverse Design":
    page_inverse()
elif page == "4 · Candidate Portfolio":
    page_portfolio()
elif page == "5 · Design Explainer":
    page_explainer()
elif page == "6 · Synthesis Planner":
    page_synthesis()
elif page == "7 · Validation & Model":
    page_validation()
elif page == "8 · Experiment Feedback":
    page_feedback()
elif page == "Evidence & Methods":
    page_evidence_methods()

st.markdown(
    f'<div class="footer">{APP_NAME} · {APP_VERSION} · {DATA_VERSION} · Target-first research prototype. '
    'Observed evidence, exploratory estimates and gated objectives are explicitly separated.</div>',
    unsafe_allow_html=True,
)
