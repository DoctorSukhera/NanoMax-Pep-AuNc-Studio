# Validation policy

NanoMax Pep-AuNC Studio uses a deliberately conservative validation framework.

## Required validation views

1. **Paper-grouped out-of-fold validation**  
   Records from the same paper remain in the same fold.

2. **Lab-aware grouped validation**  
   Closely related papers from the same laboratory/platform are grouped together when known. This is important for the Au16(RGDC)14 / Au22(KCK)16 photochemical family.

3. **Sequence-cluster leakage control**  
   Near-duplicate peptide families should not be allowed to inflate apparent generalization.

4. **Dummy baseline**  
   A learned model must beat a simple median baseline before it is treated as useful.

5. **External prospective validation**  
   Production claims require independent future data not used for training or model selection.

## Current target state

| Target | Current state |
|---|---|
| Core size | Exploratory; first positive OOF R² |
| Emission | Not approved |
| PLQY | Not approved |
| Atomic nuclearity | Not approved |
| Formation classifier | Not approved |
| PTT | Not approved |

A better-looking algorithm is not a substitute for independent evidence.
