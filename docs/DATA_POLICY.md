# PepAuDB data policy

PepAuDB is the evidence layer of NanoMax Pep-AuNC Studio.

## Core rules

- Prefer primary experimental papers.
- Preserve the exact peptide sequence and chemical modifications.
- Keep peptide-templated AuNCs separate from post-functionalized AuNCs.
- Keep larger AuNP/bipyramid/superstructure studies separate from ultrasmall/atomic AuNC targets.
- Do not convert relative fluorescence into invented absolute PLQY.
- Do not infer failed synthesis from missing data.
- Do not assign an atomic formula from later theory if the original experiment did not establish it.
- Preserve paper and lab grouping for leakage-aware validation.
- Treat PTT laser wavelength, power density, concentration and heating endpoint as required context.

## Evidence classes

- `A1` — direct peptide atomic AuNC
- `A2` — direct peptide AuNC, nuclearity unresolved
- `B1` — peptide-AuNP mechanistic evidence
- `C1/C2` — PTT or biomedical benchmark
- `D1` — method/reference evidence

The data release in this repository remains a research dataset and should be versioned whenever records or QC decisions change.
