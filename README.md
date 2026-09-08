# NanoMax Pep-AuNC Studio v0.2

**Target-first AI-guided design support for peptide-programmed gold nanoclusters in cancer photothermal therapy (PTT).**

## Scientific question

> Which peptide sequence, under which synthesis conditions, is most likely to produce a specific gold nanocluster architecture with the optical, photothermal, stability, targeting, and safety properties required for cancer PTT?

v0.2 reorganizes the Studio around that question. The application no longer starts with “enter a peptide and inspect it.” It starts with **the AuNC/cancer-PTT target** and moves through a closed-loop discovery workflow.

## Main user flow

1. **Define Target**  
   Cancer indication, receptor/target, atomic precision, nuclearity, core size, laser wavelength, optical goals, stability and safety requirements.

2. **Design Space**  
   Peptide length/Cys constraints, desired motif, cyclic/D-amino-acid allowance, and practical pH/temperature/time limits.

3. **Inverse Design**  
   Evidence-constrained ranking of peptide–synthesis systems against the target vector.

4. **Candidate Portfolio**  
   Multiple design anchors are compared rather than presenting one opaque “best peptide.”

5. **Design Explainer**  
   Sequence motifs, direct observations, provenance, unresolved objectives and scientific caveats are shown separately.

6. **Synthesis Planner**  
   A selected candidate is anchored to the primary-literature protocol and a bounded local DOE is generated only around known structured conditions.

7. **Validation & Model**  
   Paper-grouped, lab-aware and baseline comparisons remain visible. PTT benchmarks are shown as evidence, not as a trained PTT predictor.

8. **Experiment Feedback**  
   The user can download a prospective feedback template and upload wet-lab measurements for session-level review.

Supporting scientific material is grouped under **Evidence & Methods**:
- PepAuDB Explorer
- Atomic Precision
- Formation Science
- Model Card

## Critical scientific distinction

The interface explicitly distinguishes:

- **OBSERVED** — directly reported/source-supported evidence.
- **ESTIMATED** — a model-derived value, only allowed when a target passes its gate.
- **GATED** — insufficient evidence/validation for a predictive value.

At v0.2, the platform is primarily an **evidence-constrained inverse-design and experimental-planning system**. It is not yet a validated end-to-end sequence+synthesis→PTT/safety predictor.

## Current data state

- PepAuDB v0.6
- 66 curated records
- 23 quantitative training-view rows
- 10 nuclearity-labeled training records
- 14 independent lab groups
- 3 verified formation negatives
- Real-Data Benchmark v0.4
- No synthetic labels in the current scientific benchmark

## New v0.2 data layers

- `data/synthesis_records.csv` — structured synthesis context extracted from PepAuDB v0.6
- `data/ptt_benchmarks.csv` — PTT benchmark/reference layer
- `notebooks/NanoMax_PepAu_RealData_Benchmark_v0.4.ipynb`

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud

Use repository name:

```text
nanomax-pep-aunc-studio
```

Set the main file to:

```text
app.py
```

No secrets are required for v0.2.

## Next scientific milestone

The next model milestone is not visual. It is to acquire enough independent direct peptide-AuNC data to unlock:
- formation probability,
- atomic nuclearity,
- emission/PLQY,
- direct sequence+synthesis→PTT,
- stability,
- targeting,
- safety,

under external prospective validation.
