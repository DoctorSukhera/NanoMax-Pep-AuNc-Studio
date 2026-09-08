# Scientific workflow — NanoMax Pep-AuNC Studio

## Inverse-design formulation

The intended forward model is:

`peptide sequence + synthesis conditions -> formation -> AuNC architecture -> optical/PTT/stability/targeting/safety`

The intended inverse-design problem is:

`desired cancer-PTT property vector -> ranked peptide + synthesis candidates`

The current v0.2 application implements an evidence-constrained version of the inverse problem. It searches the curated experimental evidence space and does not fabricate values for objectives that are not yet learnable.

## Why the workflow is target-first

A sequence-first UI answers:

> What do we know about this peptide?

The scientific project requires:

> What AuNC do we need, and which peptide + synthesis system should we test?

Therefore the primary path is:

**TARGET -> DESIGN SPACE -> INVERSE SEARCH -> PORTFOLIO -> EXPLANATION -> SYNTHESIS -> VALIDATION -> FEEDBACK**

## Multi-objective principle

PTT performance, fluorescence, atomic precision, targeting, stability and safety can conflict. Future versions should use Pareto optimization rather than an arbitrary single weighted score.

Until the full target stack is trainable, v0.2 uses an evidence-match ranking only for objectives supported by current structured data and visibly marks the others as GATED.

## Closed loop

Prospective wet-lab results should eventually populate a dedicated experimental table with:
- candidate ID,
- synthesis batch,
- replicate,
- precursor and peptide concentrations,
- pH, temperature, time,
- reduction strategy,
- purification,
- mass/TEM architecture,
- optical measurements,
- laser/PTT context,
- stability,
- targeting,
- safety,
- instrument metadata.

Those data then become the basis for active learning and later true inverse design.
