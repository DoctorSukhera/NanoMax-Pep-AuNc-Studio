# NanoMax Pep-AuNC Studio

**AI-Guided Design of Peptide-Programmed Gold Nanoclusters**

NanoMax Pep-AuNC Studio is an evidence-first research platform for peptide-programmed gold nanoclusters (AuNCs). The first public-facing release deliberately separates **what the literature supports** from **what the predictive models are not yet ready to claim**.

## Current release

- **Studio:** v0.1 Research Prototype
- **Database:** PepAuDB v0.6
- **Benchmark:** Real-Data Benchmark v0.4
- **Synthetic labels in current benchmark:** No
- **Production predictive model:** No
- **Experimental validation of novel candidates:** Not yet

## What the app includes

- **Design Studio** — candidate sequence descriptors and nearest literature analogues.
- **Target Builder** — ranks evidence records against desired nuclearity, size, emission and QY targets.
- **Evidence Explorer** — curated quantitative peptide-AuNC records with paper/lab provenance.
- **Atomic Precision** — nuclearity audit with explicit structural evidence.
- **Formation Controls** — matched success/failure controls and relative PL evidence.
- **Model & Validation** — paper-grouped and lab-aware out-of-fold benchmark results.
- **Model Card** — current scientific claims, limitations and deployment gates.

## Why the app does not show a "high accuracy" badge

The current real-data benchmark shows that model performance depends strongly on the target. Core size has the first encouraging cross-paper signal, while emission, PLQY and atomic nuclearity are not yet sufficiently generalizable. The Studio therefore exposes the evidence and validation state instead of converting weak retrospective performance into a misleading confidence score.

## Repository structure

```text
NanoMax_Pep-AuNC_Studio_v0.1/
├── app.py
├── model_card.json
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
├── data/
│   ├── NanoMax_PepAuDB_v0.6.xlsx
│   ├── training_view.csv
│   ├── atomic_nuclearity.csv
│   ├── formation_controls.csv
│   ├── relative_pl.csv
│   ├── literature_additions.csv
│   └── benchmark.csv
└── docs/
    ├── VALIDATION.md
    └── DATA_POLICY.md
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository, recommended name: `nanomax-pep-aunc-studio`.
2. Upload the contents of this folder to the repository root.
3. In Streamlit Community Cloud choose **Create app**.
4. Select the repository and set the main file path to `app.py`.
5. Deploy.

No secrets are required for v0.1.

## Scientific positioning

The application should be described as:

> **NanoMax Pep-AuNC Studio — AI-Guided Design of Peptide-Programmed Gold Nanoclusters**

The current version is best characterized as an **evidence and candidate-assessment platform**, not yet as a validated atomic-nuclearity or PTT prediction engine.

## Data policy

PepAuDB uses source-specific evidence classes and retains important domain separations. Peptide-templated AuNCs, peptide-functionalized preformed AuNCs, larger Au nanoparticles, doped clusters and literature-only benchmarks are not silently treated as equivalent training examples.

See `docs/DATA_POLICY.md` and `docs/VALIDATION.md`.
