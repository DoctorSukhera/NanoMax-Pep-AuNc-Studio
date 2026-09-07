from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

APP_NAME = "NanoMax Pep-AuNC Studio"
APP_VERSION = "v0.1"
DATA_VERSION = "PepAuDB v0.6"
BENCHMARK_VERSION = "Real-Data Benchmark v0.4"

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
:root {
    --ink:#132238;
    --muted:#617083;
    --line:#DCE5EF;
    --panel:#F7F9FC;
    --blue:#0B5CAB;
    --blue2:#174A7E;
    --green:#13795B;
    --amber:#A76400;
    --red:#B42318;
}
.block-container {padding-top:1.6rem; padding-bottom:3rem; max-width:1450px;}
[data-testid="stSidebar"] {border-right:1px solid var(--line);}
[data-testid="stSidebar"] .block-container {padding-top:1.2rem;}
h1,h2,h3 {letter-spacing:-0.02em;}
h1 {font-weight:720;}
.smallcaps {
    font-size:.76rem; letter-spacing:.12em; text-transform:uppercase;
    color:#6A7788; font-weight:700;
}
.hero {
    border:1px solid var(--line); border-radius:18px;
    padding:28px 30px; background:linear-gradient(135deg,#FFFFFF 0%,#F3F7FC 100%);
    margin-bottom:18px;
}
.hero-title {font-size:2.25rem; line-height:1.05; font-weight:760; color:var(--ink);}
.hero-sub {font-size:1.02rem; color:#536276; margin-top:8px; max-width:900px;}
.brandline {font-size:.78rem; letter-spacing:.12em; color:var(--blue); font-weight:800;}
.badges {display:flex; flex-wrap:wrap; gap:8px; margin-top:16px;}
.badge {
    border:1px solid #CAD8E7; background:#fff; padding:5px 9px;
    border-radius:999px; font-size:.78rem; color:#42546A;
}
.metric-card {
    border:1px solid var(--line); background:#fff; border-radius:14px;
    padding:14px 16px; min-height:108px;
}
.metric-k {font-size:.74rem; text-transform:uppercase; letter-spacing:.08em; color:#718096; font-weight:700;}
.metric-v {font-size:1.55rem; font-weight:760; margin-top:5px; color:var(--ink);}
.metric-n {font-size:.78rem; color:#718096; margin-top:4px;}
.status {
    display:inline-block; border-radius:999px; padding:4px 9px;
    font-size:.76rem; font-weight:750; border:1px solid;
}
.status-go {background:#EAF8F2; color:#0B684D; border-color:#A9DCCB;}
.status-weak {background:#FFF7E8; color:#8C5500; border-color:#E8C47A;}
.status-stop {background:#FFF0EE; color:#A1261C; border-color:#E7B2AC;}
.note {
    border-left:4px solid var(--blue); padding:11px 14px;
    background:#F4F8FC; color:#405268; border-radius:0 10px 10px 0;
}
.science-box {
    border:1px solid var(--line); border-radius:14px; background:#fff;
    padding:16px 18px; height:100%;
}
hr {border:none; border-top:1px solid var(--line); margin:1.2rem 0;}
div[data-testid="stDataFrame"] {border:1px solid var(--line); border-radius:12px; overflow:hidden;}
[data-testid="stMetricValue"] {font-weight:760;}
.footer {
    margin-top:2.2rem; padding-top:1.1rem; border-top:1px solid var(--line);
    color:#7B8795; font-size:.78rem;
}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_csv(name: str) -> pd.DataFrame:
    p = DATA / name
    df = pd.read_csv(p)
    return df


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
model_card = load_model_card()

# Numeric coercion.
for df in [training, atomic, formation, relative_pl, literature, benchmark]:
    for c in df.columns:
        if c in {
            "Au_Nuclearity", "Core_Size_nm", "Hydrodynamic_Size_nm", "pH", "Temp_C", "Time_h",
            "Emission_nm", "PLQY_pct", "Ligand_Count", "Peptide_Ligand_Count",
            "MAE", "RMSE", "R2", "Spearman", "N", "Paper_Groups", "Lab_Groups",
            "Sequence_Clusters", "Fold_Change"
        }:
            df[c] = pd.to_numeric(df[c], errors="coerce")


AA = set("ACDEFGHIKLMNPQRSTVWY")
KD = {
    "A":1.8,"C":2.5,"D":-3.5,"E":-3.5,"F":2.8,"G":-0.4,"H":-3.2,"I":4.5,"K":-3.9,
    "L":3.8,"M":1.9,"N":-3.5,"P":-1.6,"Q":-3.5,"R":-4.5,"S":-0.8,"T":-0.7,
    "V":4.2,"W":-0.9,"Y":-1.3
}


def clean_sequence(seq: str) -> str:
    s = re.sub(r"[^A-Za-z]", "", (seq or "").upper())
    return "".join(a for a in s if a in AA)


def sequence_descriptors(seq: str) -> dict:
    s = clean_sequence(seq)
    L = len(s)
    if L == 0:
        return {}
    cpos = [i for i, a in enumerate(s) if a == "C"]
    c_spacing = float(np.mean(np.diff(cpos))) if len(cpos) >= 2 else np.nan
    charge = s.count("K") + s.count("R") + 0.1*s.count("H") - s.count("D") - s.count("E")
    arom = sum(s.count(a) for a in "FYW") / L
    hyd = float(np.mean([KD[a] for a in s]))
    return {
        "Sequence": s,
        "Length": L,
        "Cys": s.count("C"),
        "His": s.count("H"),
        "Tyr": s.count("Y"),
        "Trp": s.count("W"),
        "Met": s.count("M"),
        "Charge_proxy_pH7": charge,
        "Aromaticity": arom,
        "Mean_hydropathy": hyd,
        "CCY_motifs": s.count("CCY"),
        "Mean_Cys_spacing": c_spacing,
    }


def descriptor_vector(seq: str) -> np.ndarray:
    d = sequence_descriptors(seq)
    if not d:
        return np.full(11, np.nan)
    return np.array([
        d["Length"], d["Cys"], d["His"], d["Tyr"], d["Trp"], d["Met"],
        d["Charge_proxy_pH7"], d["Aromaticity"], d["Mean_hydropathy"],
        d["CCY_motifs"], d["Mean_Cys_spacing"]
    ], dtype=float)


@st.cache_data
def training_sequence_matrix():
    X = np.vstack([descriptor_vector(str(s)) for s in training["Sequence"].fillna("")])
    return X


def nearest_evidence(seq: str, n: int = 6) -> pd.DataFrame:
    q = descriptor_vector(seq)
    X = training_sequence_matrix().copy()
    # Robust dimension-wise scaling using literature distribution.
    med = np.nanmedian(X, axis=0)
    q75 = np.nanpercentile(X, 75, axis=0)
    q25 = np.nanpercentile(X, 25, axis=0)
    scale = q75 - q25
    scale[~np.isfinite(scale) | (scale == 0)] = 1.0

    # Replace missing literature/candidate features by the training median.
    X = np.where(np.isfinite(X), X, med)
    q = np.where(np.isfinite(q), q, med)
    dist = np.sqrt(np.mean(((X - q) / scale) ** 2, axis=1))

    out = training.copy()
    out["Descriptor_Distance"] = dist
    out = out.sort_values("Descriptor_Distance").head(n)
    cols = [
        "Record_ID","Source_ID","Sequence","Material_Regime","Au_Nuclearity",
        "Core_Size_nm","Emission_nm","PLQY_pct","Paper_Group","Lab_Group",
        "Descriptor_Distance","Critical_Validation_Note"
    ]
    return out[[c for c in cols if c in out.columns]]


def target_reference_ranking(
    target_nuclearity: float | None,
    target_size: float | None,
    target_emission: float | None,
    target_qy: float | None,
    n: int = 8,
) -> pd.DataFrame:
    df = training.copy()
    components = []
    weights = []
    for col, target, scale in [
        ("Au_Nuclearity", target_nuclearity, 8.0),
        ("Core_Size_nm", target_size, 0.8),
        ("Emission_nm", target_emission, 180.0),
        ("PLQY_pct", target_qy, 10.0),
    ]:
        if target is None:
            continue
        vals = pd.to_numeric(df[col], errors="coerce")
        available = vals.notna()
        component = (vals - float(target)).abs() / scale
        component = component.where(available, 2.5)  # missing target evidence is penalized, not imputed.
        components.append(component)
        weights.append(1.0)
    if not components:
        return df.head(0)

    score = sum(components) / sum(weights)
    df["Target_Distance"] = score
    cols = [
        "Record_ID","Source_ID","Sequence","Au_Nuclearity","Core_Size_nm",
        "Emission_nm","PLQY_pct","Paper_Group","Lab_Group","Target_Distance",
        "Critical_Validation_Note"
    ]
    return df.sort_values("Target_Distance").head(n)[[c for c in cols if c in df.columns]]


def status_badge(text: str, kind: str) -> str:
    return f'<span class="status status-{kind}">{text}</span>'


def hero():
    st.markdown(
        f"""
<div class="hero">
  <div class="brandline">NANOMAX · PEPTIDE × AI × ATOMIC GOLD</div>
  <div class="hero-title">{APP_NAME}</div>
  <div class="hero-sub">AI-guided design support for peptide-programmed gold nanoclusters, built around primary-literature evidence, leakage-aware validation and transparent model readiness.</div>
  <div class="badges">
    <span class="badge">{APP_VERSION} · Research Prototype</span>
    <span class="badge">{DATA_VERSION}</span>
    <span class="badge">{BENCHMARK_VERSION}</span>
    <span class="badge">No experimental validation claims</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def metric_card(label, value, note=""):
    st.markdown(
        f"""
<div class="metric-card">
  <div class="metric-k">{label}</div>
  <div class="metric-v">{value}</div>
  <div class="metric-n">{note}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def page_home():
    hero()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Curated evidence records", "66", "PepAuDB v0.6")
    with c2:
        metric_card("Atomic A1 records", "12", "Direct atomic peptide–AuNC evidence")
    with c3:
        metric_card("Nuclearity labels", "10", "Across 9 paper groups")
    with c4:
        metric_card("Independent lab groups", "14", "Lab-aware validation metadata")

    st.markdown("### Studio workflow")
    a,b,c,d,e = st.columns(5)
    for col, num, title, body in [
        (a,"01","Define","Set sequence, synthesis context and design targets."),
        (b,"02","Compare","Locate nearest primary-literature analogues."),
        (c,"03","Audit","Check atomic precision, formation and provenance."),
        (d,"04","Validate","Inspect paper-, lab- and sequence-grouped benchmarks."),
        (e,"05","Experiment","Use the evidence to prioritize prospective wet-lab tests."),
    ]:
        with col:
            st.markdown(
                f'<div class="science-box"><div class="smallcaps">{num}</div><h4>{title}</h4><div style="color:#607084">{body}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("### Model readiness")
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.markdown(status_badge("CORE SIZE · EXPLORATORY", "weak"), unsafe_allow_html=True)
        st.caption("First positive paper-grouped OOF R² (+0.231), N=13. Research-only.")
    with c2:
        st.markdown(status_badge("NUCLEARITY · NOT APPROVED", "stop"), unsafe_allow_html=True)
        st.caption("N=10; lab-aware performance is near, but does not beat, the median baseline.")
    with c3:
        st.markdown(status_badge("FORMATION · NOT APPROVED", "stop"), unsafe_allow_html=True)
        st.caption("Only three explicit negative controls, concentrated in two papers.")
    with c4:
        st.markdown(status_badge("EVIDENCE PLATFORM · GO", "go"), unsafe_allow_html=True)
        st.caption("Database, provenance, OOD-style proximity and validation evidence are deployable now.")

    st.markdown(
        '<div class="note"><b>Scientific boundary:</b> the Studio currently supports evidence-guided candidate assessment. It does not claim that a novel sequence will produce a specific Au nuclearity, emission wavelength or PTT response before experimental validation.</div>',
        unsafe_allow_html=True,
    )


def page_design_studio():
    st.markdown("## Design Studio")
    st.caption("Assess a candidate peptide against the current literature manifold and identify evidence-backed reference points.")

    left, right = st.columns([1.05, 1.4], gap="large")
    with left:
        seq = st.text_input("Candidate peptide sequence", value="CCYRGRKKRRQRRR", help="Standard one-letter amino-acid sequence.")
        mode = st.selectbox("Design intent", ["Atomic precision", "NIR optical", "Formation / synthesis", "Theranostic", "PTT-oriented"])
        st.markdown("**Optional synthesis context**")
        pH = st.number_input("pH", min_value=1.0, max_value=14.0, value=10.0, step=0.5)
        temp = st.number_input("Temperature (°C)", min_value=0.0, max_value=100.0, value=25.0, step=5.0)
        time_h = st.number_input("Reaction time (h)", min_value=0.0, max_value=72.0, value=12.0, step=0.5)

        d = sequence_descriptors(seq)
        if not d:
            st.error("Enter a valid amino-acid sequence.")
            return

        st.markdown("### Transparent descriptors")
        st.dataframe(
            pd.DataFrame({
                "Descriptor": list(d.keys())[1:],
                "Value": list(d.values())[1:]
            }),
            hide_index=True,
            use_container_width=True,
        )

    with right:
        st.markdown("### Nearest literature analogues")
        near = nearest_evidence(seq, 7)
        st.dataframe(
            near,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Descriptor_Distance": st.column_config.NumberColumn("Descriptor distance", format="%.2f"),
                "Core_Size_nm": st.column_config.NumberColumn("Core size (nm)", format="%.2f"),
                "PLQY_pct": st.column_config.NumberColumn("QY (%)", format="%.2f"),
            },
        )
        if len(near):
            d0 = float(near.iloc[0]["Descriptor_Distance"])
            if d0 < 0.55:
                prox = "Near the current literature descriptor manifold"
                kind = "go"
            elif d0 < 1.1:
                prox = "Moderate literature proximity"
                kind = "weak"
            else:
                prox = "Far from current literature evidence"
                kind = "stop"
            st.markdown(status_badge(prox.upper(), kind), unsafe_allow_html=True)
            st.caption("Descriptor distance is an evidence-proximity measure, not a probability of successful synthesis.")

        st.markdown("### Evidence-backed interpretation")
        cys = d["Cys"]
        pro = clean_sequence(seq).count("P")
        notes = []
        if cys == 0:
            notes.append("No Cys is present. The curated W24 Cys-ablation control formed aggregated Au nanoparticles rather than fluorescent AuNCs.")
        else:
            notes.append(f"The candidate contains {cys} Cys residue(s), providing a plausible Au-coordination/mineralization motif represented in the database.")
        if pro > 0:
            notes.append("Pro is present. In the W24 designer-peptide study, Pro-dependent 3D topology was experimentally important for AuNC formation.")
        if mode == "PTT-oriented":
            notes.append("PTT prediction is disabled: the current direct peptide-templated AuNC sequence+synthesis→PTT dataset is insufficient.")
        for n in notes:
            st.write("• " + n)


def page_target_builder():
    st.markdown("## Target Builder")
    st.caption("Rank existing evidence against a desired AuNC property profile. This is reference matching—not a prediction of a novel sequence.")

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        use_n = st.checkbox("Target nuclearity", True)
        n = st.number_input("Au atom count", 5, 100, 25) if use_n else None
    with c2:
        use_s = st.checkbox("Target core size", True)
        s = st.number_input("Core size (nm)", 0.5, 5.0, 1.5, step=0.1) if use_s else None
    with c3:
        use_e = st.checkbox("Target emission", True)
        e = st.number_input("Emission (nm)", 350, 1300, 750, step=10) if use_e else None
    with c4:
        use_q = st.checkbox("Target QY", False)
        q = st.number_input("PLQY (%)", 0.0, 50.0, 10.0, step=1.0) if use_q else None

    ranked = target_reference_ranking(n, s, e, q, 10)
    if ranked.empty:
        st.info("Select at least one target.")
        return

    st.markdown("### Closest evidence-backed reference points")
    st.dataframe(
        ranked,
        hide_index=True,
        use_container_width=True,
        column_config={"Target_Distance": st.column_config.NumberColumn("Target distance", format="%.2f")},
    )
    st.markdown(
        '<div class="note"><b>Use:</b> select reference records for experimental planning, then inspect their provenance and synthesis details in Evidence Explorer. Missing measurements are penalized rather than imputed as if known.</div>',
        unsafe_allow_html=True,
    )


def page_evidence():
    st.markdown("## Evidence Explorer")
    st.caption("Browse the quantitative training view and trace each result back to a paper/lab grouping.")

    c1,c2,c3 = st.columns(3)
    with c1:
        regime = st.multiselect("Material regime", sorted(training["Material_Regime"].dropna().unique()))
    with c2:
        eligibility = st.multiselect("Eligibility", sorted(training["Eligibility"].dropna().unique()))
    with c3:
        search = st.text_input("Sequence / record search", "")

    df = training.copy()
    if regime:
        df = df[df["Material_Regime"].isin(regime)]
    if eligibility:
        df = df[df["Eligibility"].isin(eligibility)]
    if search.strip():
        s = search.strip().upper()
        mask = (
            df["Sequence"].fillna("").str.upper().str.contains(s, regex=False)
            | df["Record_ID"].fillna("").str.upper().str.contains(s, regex=False)
            | df["Source_ID"].fillna("").str.upper().str.contains(s, regex=False)
        )
        df = df[mask]

    st.dataframe(df, hide_index=True, use_container_width=True, height=520)

    st.markdown("### Newly verified high-information sources")
    st.dataframe(literature, hide_index=True, use_container_width=True)


def page_atomic():
    st.markdown("## Atomic Precision")
    st.caption("Only records with explicit molecular/nuclearity evidence belong in this audit.")

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Atomic audit records", len(atomic))
    with c2: st.metric("Unique nuclearities", atomic["Au_Nuclearity"].nunique())
    with c3: st.metric("Independent papers", atomic["Paper_Group"].nunique())
    with c4: st.metric("Independent lab groups", atomic["Lab_Group"].nunique())

    fig = px.histogram(
        atomic, x="Au_Nuclearity", nbins=10,
        title="Atomic nuclearity distribution in the curated audit"
    )
    fig.update_layout(margin=dict(l=10,r=10,t=50,b=10), height=360)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(atomic, hide_index=True, use_container_width=True, height=480)

    st.markdown(
        '<div class="note"><b>Atomic-precision rule:</b> mass assignment, TGA, SAXS or equivalent structural evidence is preserved as source-specific evidence. Later DFT structures are not retrofitted onto older primary experiments unless the original experiment supports that assignment.</div>',
        unsafe_allow_html=True,
    )


def page_formation():
    st.markdown("## Formation Controls")
    st.caption("Success-biased literature is a major obstacle. This page keeps explicit positive and negative controls visible.")

    counts = formation["Training_Status"].value_counts().rename_axis("Status").reset_index(name="Count")
    fig = px.bar(counts, x="Status", y="Count", text="Count", title="Verified formation controls")
    fig.update_layout(margin=dict(l=10,r=10,t=50,b=10), height=330)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(formation, hide_index=True, use_container_width=True)

    st.markdown("### Relative photoluminescence evidence")
    st.caption("Pairwise evidence is retained as ranking data rather than converted into fabricated absolute QY labels.")
    st.dataframe(relative_pl, hide_index=True, use_container_width=True)


def page_validation():
    st.markdown("## Model & Validation")
    st.caption("Every target is compared against a simple baseline under grouped out-of-fold validation.")

    # Best learned versus dummy by target/validation.
    numeric = benchmark.copy()
    numeric = numeric[numeric["Validation"].isin(["paper_grouped","lab_grouped"])]
    numeric = numeric[numeric["MAE"].notna()]

    summaries = []
    for (target, validation), g in numeric.groupby(["Target","Validation"]):
        dummy = g[g["Model"] == "DummyMedian"]
        learned = g[g["Model"] != "DummyMedian"]
        if dummy.empty or learned.empty:
            continue
        d = dummy.sort_values("MAE").iloc[0]
        b = learned.sort_values("MAE").iloc[0]
        summaries.append({
            "Target": target,
            "Validation": validation,
            "Best learned model": b["Model"],
            "Best learned MAE": b["MAE"],
            "Dummy MAE": d["MAE"],
            "OOF R²": b["R2"],
            "Improvement vs dummy (%)": 100*(d["MAE"]-b["MAE"])/d["MAE"] if d["MAE"] else np.nan,
        })
    summary = pd.DataFrame(summaries)
    st.dataframe(summary, hide_index=True, use_container_width=True)

    # Dimensionless relative error improvement chart.
    if not summary.empty:
        fig = px.bar(
            summary,
            x="Target",
            y="Improvement vs dummy (%)",
            color="Validation",
            barmode="group",
            title="Learned-model MAE improvement versus dummy baseline",
        )
        fig.add_hline(y=0, line_dash="dash")
        fig.update_layout(height=390, margin=dict(l=10,r=10,t=50,b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Current decision gates")
    gate_table = pd.DataFrame([
        ["Core size", "Exploratory", "Paper/lab OOF R² +0.231; N=13", "No production badge"],
        ["Emission", "Stop", "Learned model worse than baseline", "Acquire controlled optical panels"],
        ["PLQY", "Stop", "Negative OOF R²", "Acquire independent QY panels"],
        ["Nuclearity", "Stop", "N=10; lab-aware model still not better than baseline", "Add independent atomic families"],
        ["Formation", "Stop", "Only 3 explicit negatives", "Mine independent failures"],
        ["PTT", "Stop", "Direct sequence+synthesis→PTT data insufficient", "Acquire peptide-templated PTT studies"],
    ], columns=["Target","Status","Evidence","Requirement"])
    st.dataframe(gate_table, hide_index=True, use_container_width=True)

    with st.expander("Full benchmark table"):
        st.dataframe(benchmark, hide_index=True, use_container_width=True)


def page_model_card():
    st.markdown("## Model Card & Scientific Boundary")
    st.json(model_card, expanded=False)

    st.markdown("### What the Studio can do now")
    st.write(
        "• Audit candidate peptide descriptors and literature proximity.\n"
        "• Rank evidence-backed reference points against a desired target profile.\n"
        "• Expose atomic-precision provenance and matched formation controls.\n"
        "• Compare learned models with a dummy baseline under paper-, lab- and sequence-aware validation.\n"
        "• Support experimental prioritization without presenting unvalidated predictions as facts."
    )
    st.markdown("### What it does not claim")
    st.write(
        "• It does not guarantee formation of an AuNC from a novel peptide.\n"
        "• It does not claim exact Au nuclearity for a novel sequence.\n"
        "• It does not provide an approved PTT prediction model.\n"
        "• It does not replace prospective synthesis, spectroscopy, mass spectrometry, TEM or biological validation."
    )


with st.sidebar:
    st.markdown(f"### {APP_NAME}")
    st.caption(f"{APP_VERSION} · {DATA_VERSION}")
    page = st.radio(
        "Workspace",
        [
            "Home",
            "Design Studio",
            "Target Builder",
            "Evidence Explorer",
            "Atomic Precision",
            "Formation Controls",
            "Model & Validation",
            "Model Card",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown('<div class="smallcaps">Scientific state</div>', unsafe_allow_html=True)
    st.markdown(status_badge("EVIDENCE PLATFORM · GO", "go"), unsafe_allow_html=True)
    st.markdown(status_badge("PREDICTIVE MODEL · GATED", "stop"), unsafe_allow_html=True)
    st.caption("Predictions remain research-only until external prospective validation.")

if page == "Home":
    page_home()
elif page == "Design Studio":
    page_design_studio()
elif page == "Target Builder":
    page_target_builder()
elif page == "Evidence Explorer":
    page_evidence()
elif page == "Atomic Precision":
    page_atomic()
elif page == "Formation Controls":
    page_formation()
elif page == "Model & Validation":
    page_validation()
elif page == "Model Card":
    page_model_card()

st.markdown(
    f'<div class="footer">{APP_NAME} · {APP_VERSION} · {DATA_VERSION} · Research prototype. Evidence-guided design support only; no clinical or experimental validation claims.</div>',
    unsafe_allow_html=True,
)
