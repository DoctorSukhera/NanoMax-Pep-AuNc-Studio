# NanoMax Pep-AuNC Studio

**AI-Guided Inverse Design of Peptide-Programmed Gold Nanoclusters**

NanoMax Pep-AuNC Studio is a Streamlit research interface built around PepAuDB.  
The current release is an **evidence-guided research prototype**, not a validated experimental predictor.

## Current capabilities

- Evidence database explorer
- Peptide analogue search
- Evidence-guided synthesis planner
- Target design workspace
- Formation-control explorer
- PTT vs PDT mechanism separation
- Model-readiness / GO-WAIT-STOP dashboard
- Explicit peer-reviewed vs patent-primary provenance

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud

1. Create a GitHub repository, for example `nanomax-pep-aunc-studio`.
2. Upload the full contents of this folder.
3. Create a new Streamlit app.
4. Select `app.py` as the main file.
5. Deploy.

## Data

The app expects:

`data/NanoMax_PepAuDB_v0.4.xlsx`

The database contains explicit training-eligibility, evidence-level and QC fields.  
Do not remove these fields when extending the dataset.

## Scientific policy

No numerical prediction accuracy should be displayed until the relevant model target passes:

- target-specific data gate;
- source/paper grouped validation;
- homologous peptide/ligand-family leakage control;
- baseline comparison;
- y-scrambling/permutation testing;
- peer-reviewed-only sensitivity analysis;
- untouched external validation;
- uncertainty and out-of-domain analysis.

## Recommended next development phases

1. Expand direct primary peptide-AuNC experiment rows.
2. Acquire more explicit failed-synthesis controls.
3. Expand direct peptide-AuNC PTT/PCE/ΔT evidence.
4. Benchmark real-data models in the Colab validation notebook.
5. Freeze validated model artifacts.
6. Connect only those frozen artifacts to the Studio.

---

**Status:** v0.1 Research Prototype  
**Database:** PepAuDB v0.4
