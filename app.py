
from pathlib import Path
from difflib import SequenceMatcher
import re

import numpy as np
import pandas as pd
import streamlit as st

APP_NAME = "NanoMax Pep-AuNC Studio"
APP_VERSION = "v0.1 · Research Prototype"
DB_VERSION = "PepAuDB v0.4"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "NanoMax_PepAuDB_v0.4.xlsx"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- visual system ----------
st.markdown(
    """
    <style>
    :root {
      --ink:#10243e;
      --muted:#5f6f82;
      --line:#dfe6ee;
      --soft:#f5f8fb;
      --blue:#1f4e79;
      --blue2:#2f75b5;
      --gold:#b88a22;
      --ok:#2f6b4f;
      --warn:#9a6c10;
      --bad:#9c2f2f;
    }

    html, body, [class*="css"]  {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 1440px;
    }
    .nm-hero {
        border: 1px solid var(--line);
        background: linear-gradient(135deg, #ffffff 0%, #f4f8fc 65%, #eef4f8 100%);
        border-radius: 22px;
        padding: 26px 30px;
        margin-bottom: 18px;
        box-shadow: 0 8px 28px rgba(16,36,62,.06);
    }
    .nm-kicker {
        color: var(--blue2);
        font-size: .78rem;
        font-weight: 800;
        letter-spacing: .14em;
        text-transform: uppercase;
    }
    .nm-title {
        color: var(--ink);
        font-size: 2.35rem;
        line-height: 1.06;
        font-weight: 800;
        margin: 6px 0 7px 0;
    }
    .nm-subtitle {
        color: var(--muted);
        font-size: 1.02rem;
        max-width: 950px;
        line-height: 1.55;
    }
    .nm-badges { margin-top: 15px; }
    .nm-badge {
        display: inline-block;
        margin: 0 7px 6px 0;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid #d4dee9;
        background: #fff;
        color: #33485f;
        font-size: .77rem;
        font-weight: 700;
    }
    .nm-section {
        color: var(--ink);
        font-size: 1.34rem;
        font-weight: 800;
        margin: 18px 0 8px;
    }
    .nm-card {
        border: 1px solid var(--line);
        background: #fff;
        border-radius: 16px;
        padding: 17px 18px;
        min-height: 100%;
    }
    .nm-card h4 { margin: 0 0 6px 0; color: var(--ink); }
    .nm-card p { color: var(--muted); margin: 0; line-height: 1.48; }
    .nm-note {
        border-left: 4px solid var(--blue2);
        background: #f5f8fb;
        border-radius: 8px;
        padding: 11px 13px;
        color: #31465d;
        margin: 8px 0 14px;
    }
    .nm-warning {
        border-left: 4px solid #c29021;
        background: #fff9ec;
        border-radius: 8px;
        padding: 11px 13px;
        color: #664b16;
        margin: 8px 0 14px;
    }
    .nm-locked {
        border: 1px dashed #c6d0db;
        background: #f8fafc;
        border-radius: 14px;
        padding: 16px;
        color: #58697a;
    }
    .nm-footer {
        border-top: 1px solid var(--line);
        margin-top: 30px;
        padding-top: 12px;
        color: #788797;
        font-size: .78rem;
    }
    div[data-testid="stMetric"] {
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 12px 14px;
        background: white;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 7px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding-left: 16px;
        padding-right: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- helpers ----------
@st.cache_data(show_spinner=False)
def load_excel():
    if not DB_PATH.exists():
        return {}
    xls = pd.ExcelFile(DB_PATH)
    out = {}
    for sheet in xls.sheet_names:
        try:
            # Most PepAuDB sheets use title row 1, blank row 2, headers row 3.
            df = pd.read_excel(DB_PATH, sheet_name=sheet, header=2)
            df = df.dropna(how="all")
            out[sheet] = df
        except Exception:
            pass
    return out

DATA = load_excel()

def get_sheet(name):
    return DATA.get(name, pd.DataFrame()).copy()

MASTER = get_sheet("PepAuDB_v0.4")
GATES = get_sheet("Model_Gates_v0.4")
FORMATION = get_sheet("Formation_Controls_v0.4")
THERAPY = get_sheet("Therapy_Context_v0.4")
SEQUENCES = get_sheet("Sequence_Library_v0.4")
SOURCES = get_sheet("Source_Expansion_v0.4")

if not MASTER.empty and "Record_ID" in MASTER.columns:
    MASTER = MASTER[MASTER["Record_ID"].notna()].copy()

AA20 = set("ACDEFGHIKLMNPQRSTVWY")
GSH_ALIASES = {"GSH","Γ-ECG","γ-ECG","ΓECG","γECG"}

def clean_single_sequence(seq):
    if seq is None or (isinstance(seq, float) and np.isnan(seq)):
        return None
    text = str(seq).strip()
    if text in GSH_ALIASES or text.upper() == "GSH":
        return "ECG"
    if any(x in text.upper() for x in ["CONFLICT","PENDING","MULTIPLE","FAMILY"]):
        return None
    text = text.upper().replace("-NH2","").replace("NH2-","")
    text = re.sub(r"[^A-Z]", "", text)
    if not text or any(a not in AA20 for a in text):
        return None
    return text

def parse_ligands(seq):
    if seq is None or (isinstance(seq, float) and np.isnan(seq)):
        return []
    parts = re.split(r"\s*\+\s*", str(seq))
    return [x for x in (clean_single_sequence(p) for p in parts) if x]

def sequence_identity(a, b):
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()

def ligand_set_similarity(query, raw):
    q = clean_single_sequence(query)
    comps = parse_ligands(raw)
    if not q or not comps:
        return 0.0
    return max(sequence_identity(q, c) for c in comps)

def fmt_num(x, suffix=""):
    if pd.isna(x):
        return "—"
    try:
        f = float(x)
        return f"{f:g}{suffix}"
    except Exception:
        return str(x)

def evidence_badge(level):
    t = str(level)
    if "PEER_REVIEWED" in t:
        return "Peer-reviewed"
    if "PATENT" in t:
        return "Patent primary"
    if "REVIEW" in t:
        return "Review-derived"
    return t if t and t != "nan" else "Unspecified"

def hero():
    st.markdown(
        f"""
        <div class="nm-hero">
          <div class="nm-kicker">NanoMax · Peptide × AI × Gold Nanoclusters</div>
          <div class="nm-title">{APP_NAME}</div>
          <div class="nm-subtitle">
            Evidence-guided inverse design workspace for peptide-programmed gold nanoclusters:
            sequence → synthesis → structure → function.
          </div>
          <div class="nm-badges">
            <span class="nm-badge">{APP_VERSION}</span>
            <span class="nm-badge">{DB_VERSION}</span>
            <span class="nm-badge">Evidence-traceable</span>
            <span class="nm-badge">No validated prediction claims</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def footer():
    st.markdown(
        """
        <div class="nm-footer">
        NanoMax Pep-AuNC Studio is a research prototype. Current outputs are evidence-navigation and
        design-support results, not experimentally validated predictions or clinical recommendations.
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_status_pill(status):
    status = str(status)
    if "GO" in status:
        return f"🟢 {status}"
    if "WAIT" in status or "EARLY" in status:
        return f"🟠 {status}"
    return f"🔴 {status}"

def top_analogs(query, n=8, allowed=None):
    if MASTER.empty or "Sequence" not in MASTER.columns:
        return pd.DataFrame()
    m = MASTER.copy()
    if allowed is not None and "Material_Regime" in m.columns:
        m = m[m["Material_Regime"].isin(allowed)]
    m["Similarity"] = m["Sequence"].apply(lambda x: ligand_set_similarity(query, x))
    m = m[m["Similarity"] > 0].sort_values("Similarity", ascending=False).head(n)
    return m

# ---------- sidebar ----------
with st.sidebar:
    st.markdown("### NanoMax Pep-AuNC Studio")
    st.caption("Research interface · evidence first")
    page = st.radio(
        "Workspace",
        [
            "Home",
            "Target Design",
            "Candidate Explorer",
            "Synthesis Planner",
            "Evidence Database",
            "Model Readiness",
            "About",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    if not MASTER.empty:
        st.metric("Database records", len(MASTER))
    if not MASTER.empty and "Source_ID" in MASTER.columns:
        st.metric("Evidence sources", MASTER["Source_ID"].nunique())
    st.caption("Model release state: research prototype")

# ---------- pages ----------
if page == "Home":
    hero()

    c1, c2, c3, c4 = st.columns(4)
    total = len(MASTER) if not MASTER.empty else 0
    sources = MASTER["Source_ID"].nunique() if not MASTER.empty and "Source_ID" in MASTER else 0
    neg = 0
    if not MASTER.empty and "Formation_Label" in MASTER.columns:
        neg = int((pd.to_numeric(MASTER["Formation_Label"], errors="coerce") == 0).sum())
    core = 0
    if not MASTER.empty and "Training_Eligibility" in MASTER.columns:
        core = int((MASTER["Training_Eligibility"].astype(str) == "TRAIN_CORE").sum())

    c1.metric("Master records", total)
    c2.metric("Independent sources", sources)
    c3.metric("Explicit formation negatives", neg)
    c4.metric("TRAIN_CORE records", core)

    st.markdown('<div class="nm-section">What this studio does now</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        st.markdown(
            '<div class="nm-card"><h4>Evidence navigation</h4><p>Trace peptide sequences, synthesis variables, structural outputs, optical properties, therapy mechanism and provenance back to literature records.</p></div>',
            unsafe_allow_html=True,
        )
    with b:
        st.markdown(
            '<div class="nm-card"><h4>Design support</h4><p>Compare a proposed peptide against literature analogues and surface the most relevant evidence without inventing unsupported numerical predictions.</p></div>',
            unsafe_allow_html=True,
        )
    with c:
        st.markdown(
            '<div class="nm-card"><h4>Model readiness</h4><p>Expose GO / WAIT / STOP gates, negative-control coverage and the exact blockers preventing premature accuracy claims.</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="nm-section">Research pathway</div>', unsafe_allow_html=True)
    st.markdown(
        """
        **1. Define target** → **2. Inspect peptide analogues** → **3. Review synthesis evidence** →
        **4. Check material/therapy regime** → **5. Evaluate model readiness** →
        **6. Generate candidates only after a validated model release**
        """
    )

    st.markdown(
        '<div class="nm-warning"><b>Prediction engine intentionally locked.</b> '
        'The current database does not yet satisfy the scientific gates required for validated peptide→AuNC nuclearity, formation, PTT or optical prediction.</div>',
        unsafe_allow_html=True,
    )

elif page == "Target Design":
    hero()
    st.markdown('<div class="nm-section">Target Design Workspace</div>', unsafe_allow_html=True)
    st.caption("Define what you want the AuNC system to do. The studio converts it into evidence requirements, not a fabricated prediction.")

    left, right = st.columns([1, 1.2])
    with left:
        mode = st.selectbox(
            "Design mode",
            ["Atomic-precision AuNC", "NIR-emissive AuNC", "PTT-only", "Theranostic", "PDT auxiliary"],
        )
        target_size = st.number_input("Desired core size (nm)", min_value=0.5, max_value=10.0, value=2.0, step=0.1)
        target_em = st.number_input("Desired emission peak (nm)", min_value=350, max_value=1400, value=650, step=10)
        require_targeting = st.toggle("Require biofunctional / targeting peptide domain", value=False)
        prioritize_stability = st.toggle("Prioritize colloidal/serum stability", value=True)

    with right:
        st.markdown("#### Design interpretation")
        priorities = []
        if mode == "Atomic-precision AuNC":
            priorities += [
                "Prefer literature with explicit Au nuclearity (Auₙ), ligand count and mass-spectrometric/structural evidence.",
                "Treat sequence order and Cys/His/Tyr/Trp/Met positions as primary features.",
                "Avoid mixing larger AuNP/bipyramid records into the atomic target model.",
            ]
        elif mode == "NIR-emissive AuNC":
            priorities += [
                "Prioritize direct peptide-AuNC records with excitation/emission and PLQY measured in the primary source.",
                "Use synthesis pH, temperature, time and Au:peptide ratio as co-equal design variables.",
            ]
        elif mode == "PTT-only":
            priorities += [
                "Optimize NIR absorption/laser overlap, photothermal conversion efficiency, ΔT/heating rate and cycling stability.",
                "Do not maximize PLQY by default because radiative and nonradiative pathways can compete.",
                "Exclude PDT-only ROS systems from the PTT target.",
            ]
        elif mode == "Theranostic":
            priorities += [
                "Use a Pareto objective rather than a single weighted score.",
                "Balance imaging emission/PLQY against photothermal heat generation and stability.",
            ]
        else:
            priorities += [
                "Keep PDT as a distinct task from PTT.",
                "Require ROS/photosensitization endpoints rather than using laser wavelength as a mechanism proxy.",
            ]
        if require_targeting:
            priorities.append("Separate AuNC-forming domain from targeting/biofunctional domain where the evidence supports modular design.")
        if prioritize_stability:
            priorities.append("Require hydrodynamic size/zeta/stability evidence before prioritizing a candidate.")

        for i, p in enumerate(priorities, 1):
            st.markdown(f"**{i}.** {p}")

        st.markdown(
            '<div class="nm-note"><b>Current system state:</b> This page defines the design objective. '
            'Candidate generation remains locked until the corresponding model gate passes.</div>',
            unsafe_allow_html=True,
        )

elif page == "Candidate Explorer":
    hero()
    st.markdown('<div class="nm-section">Candidate Explorer</div>', unsafe_allow_html=True)
    st.caption("Enter a peptide sequence to locate the closest experimental evidence in PepAuDB.")

    query = st.text_input("Peptide sequence", value="CCYGGPKKKRKPG", placeholder="Example: CCYLQLQAEER")
    regime = st.selectbox(
        "Evidence regime",
        ["Core AuNC only", "All gold regimes"],
    )
    allowed = None
    if regime == "Core AuNC only":
        allowed = {"atomically_precise_AuNC", "ultrasmall_AuNC_unknown_nuclearity"}

    if st.button("Find literature analogues", type="primary", use_container_width=False):
        qclean = clean_single_sequence(query)
        if not qclean:
            st.error("Enter a standard amino-acid sequence using one-letter codes.")
        else:
            analogs = top_analogs(qclean, n=10, allowed=allowed)
            if analogs.empty:
                st.info("No usable sequence analogue was found in the current database.")
            else:
                st.success(f"Found {len(analogs)} evidence analogues.")
                show_cols = [
                    c for c in [
                        "Record_ID","Source_ID","Sequence","Similarity","Material_Regime",
                        "Au_Nuclearity","Core_Size_nm","Emission_Peak_nm","PLQY_pct",
                        "Training_Eligibility","Evidence_Level","DOI_URL"
                    ] if c in analogs.columns
                ]
                view = analogs[show_cols].copy()
                if "Similarity" in view:
                    view["Similarity"] = (view["Similarity"] * 100).round(1)
                    view = view.rename(columns={"Similarity":"Sequence similarity (%)"})
                st.dataframe(view, use_container_width=True, hide_index=True)

                best = analogs.iloc[0]
                st.markdown("#### Closest evidence record")
                x1, x2, x3, x4 = st.columns(4)
                x1.metric("Similarity", f"{best['Similarity']*100:.1f}%")
                x2.metric("Core size", fmt_num(best.get("Core_Size_nm"), " nm"))
                x3.metric("Emission", fmt_num(best.get("Emission_Peak_nm"), " nm"))
                x4.metric("Nuclearity", fmt_num(best.get("Au_Nuclearity")))

                st.markdown(
                    f'<div class="nm-note"><b>Evidence type:</b> {evidence_badge(best.get("Evidence_Level"))}. '
                    'Similarity is a literature-navigation metric, not a predicted probability of experimental success.</div>',
                    unsafe_allow_html=True,
                )

elif page == "Synthesis Planner":
    hero()
    st.markdown('<div class="nm-section">Evidence-Guided Synthesis Planner</div>', unsafe_allow_html=True)
    st.caption("Shows synthesis conditions reported for the nearest peptide/AuNC analogues. It does not invent an exact recipe.")

    query = st.text_input("Proposed peptide sequence", value="CCYLQLQAEER")
    n = st.slider("Number of evidence analogues", 1, 8, 5)

    if st.button("Build evidence plan", type="primary"):
        analogs = top_analogs(
            query,
            n=n,
            allowed={"atomically_precise_AuNC","ultrasmall_AuNC_unknown_nuclearity"},
        )
        if analogs.empty:
            st.warning("No suitable direct AuNC analogue is available.")
        else:
            cols = [
                c for c in [
                    "Record_ID","Sequence","Similarity","Au_Precursor","Peptide_or_Ligand_Condition",
                    "Reducing_Agent","pH","Temperature_C","Time_h","Mixing_or_Process",
                    "Core_Size_nm","Au_Nuclearity","Emission_Peak_nm","PLQY_pct",
                    "Evidence_Level","DOI_URL"
                ] if c in analogs.columns
            ]
            plan = analogs[cols].copy()
            if "Similarity" in plan:
                plan["Similarity"] = (plan["Similarity"] * 100).round(1)
                plan.rename(columns={"Similarity":"Sequence similarity (%)"}, inplace=True)
            st.dataframe(plan, use_container_width=True, hide_index=True)

            st.markdown("#### Recommended experimental planning approach")
            st.markdown(
                """
                1. **Start from the nearest peer-reviewed analogue**, not from a single model-generated exact recipe.
                2. Define a small **design-of-experiments (DOE)** around reported pH, temperature, time and ligand:Au ratio.
                3. Keep the peptide sequence fixed while perturbing one or two synthesis variables initially.
                4. Record both successful and failed conditions; failed syntheses are essential training data.
                5. Characterize **core size/nuclearity**, hydrodynamic size, optical response and thermal/PDT endpoints separately.
                """
            )
            st.markdown(
                '<div class="nm-warning"><b>Do not treat blank fields as zero.</b> '
                'A blank means the current source extraction did not support a precise numeric value.</div>',
                unsafe_allow_html=True,
            )

elif page == "Evidence Database":
    hero()
    st.markdown('<div class="nm-section">PepAuDB Evidence Explorer</div>', unsafe_allow_html=True)

    if MASTER.empty:
        st.error("PepAuDB v0.4 could not be loaded.")
    else:
        c1, c2, c3 = st.columns(3)
        regimes = sorted([x for x in MASTER.get("Material_Regime", pd.Series(dtype=str)).dropna().astype(str).unique()])
        levels = sorted([x for x in MASTER.get("Evidence_Level", pd.Series(dtype=str)).dropna().astype(str).unique()])
        elig = sorted([x for x in MASTER.get("Training_Eligibility", pd.Series(dtype=str)).dropna().astype(str).unique()])

        with c1:
            selected_regimes = st.multiselect("Material regime", regimes)
        with c2:
            selected_levels = st.multiselect("Evidence level", levels)
        with c3:
            selected_elig = st.multiselect("Training eligibility", elig)

        view = MASTER.copy()
        if selected_regimes:
            view = view[view["Material_Regime"].isin(selected_regimes)]
        if selected_levels:
            view = view[view["Evidence_Level"].isin(selected_levels)]
        if selected_elig:
            view = view[view["Training_Eligibility"].isin(selected_elig)]

        st.caption(f"{len(view)} records shown")
        core_cols = [
            c for c in [
                "Record_ID","Source_ID","Sequence","Material_Regime","Au_Nuclearity","Core_Size_nm",
                "pH","Temperature_C","Time_h","Emission_Peak_nm","PLQY_pct","Formation_Label",
                "Training_Eligibility","Evidence_Level","DOI_URL"
            ] if c in view.columns
        ]
        st.dataframe(view[core_cols], use_container_width=True, hide_index=True)

        with st.expander("Formation controls"):
            if FORMATION.empty:
                st.write("No formation-control sheet available.")
            else:
                st.dataframe(FORMATION, use_container_width=True, hide_index=True)

        with st.expander("Therapy context: PTT vs PDT"):
            if THERAPY.empty:
                st.write("No therapy-context sheet available.")
            else:
                st.dataframe(THERAPY, use_container_width=True, hide_index=True)

elif page == "Model Readiness":
    hero()
    st.markdown('<div class="nm-section">Model Readiness & Validation Gates</div>', unsafe_allow_html=True)

    if GATES.empty:
        st.warning("Model_Gates_v0.4 sheet not found.")
    else:
        for _, row in GATES.iterrows():
            if pd.isna(row.get("Gate")):
                continue
            with st.expander(f"{row.get('Gate')} · {row.get('Module')} — {render_status_pill(row.get('Status'))}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Current evidence**")
                    st.write(row.get("Current_Evidence","—"))
                    st.markdown("**What improved in v0.4**")
                    st.write(row.get("What_Improved_v0.4","—"))
                with c2:
                    st.markdown("**Required operational gate**")
                    st.write(row.get("Required_Operational_Gate","—"))
                    st.markdown("**Remaining blocker**")
                    st.write(row.get("Remaining_Blocker","—"))
                st.markdown("**Validation rule**")
                st.write(row.get("Validation_Rule","—"))
                st.markdown("**Patent policy**")
                st.write(row.get("Patent_Policy","—"))

    st.markdown(
        '<div class="nm-locked"><b>Validated prediction engine: LOCKED</b><br>'
        'Unlock condition: target-specific data gate + grouped nested cross-validation + baseline comparison + '
        'y-scrambling + peer-reviewed-only sensitivity analysis + untouched external validation.</div>',
        unsafe_allow_html=True,
    )

elif page == "About":
    hero()
    st.markdown('<div class="nm-section">About the Platform</div>', unsafe_allow_html=True)
    st.markdown(
        """
        **NanoMax Pep-AuNC Studio** is designed as an evidence-guided inverse-design environment for
        peptide-programmed gold nanoclusters.

        The intended long-term modeling chain is:

        **Peptide sequence + synthesis environment → formation/structure → optical/thermal properties → biological function**

        The project currently emphasizes scientific traceability over premature prediction. Every record carries
        material-regime, training-eligibility and evidence-level information so that atomically precise AuNCs,
        larger gold structures, patents, reviews and therapy benchmarks are not silently mixed.
        """
    )

    st.markdown("#### Planned validated model stack")
    st.markdown(
        """
        - Mechanistic peptide descriptors + position-sensitive residue features
        - SPARROW/ALBATROSS auxiliary conformational features
        - Frozen protein-language-model embeddings where sample size justifies them
        - Small-data regressors/classifiers: ElasticNet, Random Forest, CatBoost/boosting, Gaussian Process
        - Paper-wise and ligand-family leakage controls
        - Uncertainty, conformal/ensemble intervals and out-of-domain detection
        - Pareto optimization for theranostic design
        """
    )

    st.markdown("#### Current scientific boundary")
    st.info(
        "The current version is an evidence-navigation and design-support prototype. "
        "It does not claim experimental accuracy for new peptide sequences."
    )

footer()
