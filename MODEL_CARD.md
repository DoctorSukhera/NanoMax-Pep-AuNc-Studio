# NanoMax Pep-AuNC Studio — Model Card

## Release
v0.1 Research Prototype

## Intended use
Evidence navigation, literature analogue comparison, synthesis-planning support, and model-readiness assessment for peptide-programmed gold nanocluster research.

## Not yet intended for
- claiming exact Au nuclearity for a novel peptide;
- predicting experimental formation success with validated accuracy;
- predicting PTT conversion efficiency or temperature rise;
- replacing wet-lab validation;
- clinical decision making.

## Why the predictive engine is locked
PepAuDB v0.4 contains valuable direct experimental evidence, but current target-specific sample diversity is still below the project’s operational gates for defensible external predictive claims.

## Validation requirements before unlocking
1. Sufficient independent peptide-AuNC records per target.
2. Paper/source grouped cross-validation.
3. Homologous peptide and multi-ligand leakage control.
4. Simple baseline comparisons.
5. Y-scrambling/permutation checks.
6. Peer-reviewed-only sensitivity analysis.
7. Untouched independent external papers/labs.
8. Uncertainty and out-of-domain reporting.

## Evidence hierarchy
- Peer-reviewed primary experimental evidence
- Patent-primary experimental evidence
- Review-derived leads
- Cross-regime mechanistic evidence
- Benchmark-only material systems

These categories must remain explicit in both training and reporting.
