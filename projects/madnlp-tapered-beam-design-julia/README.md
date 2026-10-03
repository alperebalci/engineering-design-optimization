# MadNLP Tapered Cantilever Beam Design

A Julia/JuMP engineering-design project using **MadNLP** to solve a smooth nonlinear constrained optimization problem.

## Design problem

A cantilever beam has fixed width and segment-wise variable height `h_i`. The objective minimizes mass while enforcing:

- bending-stress limits in every segment;
- a tip-deflection limit;
- lower and upper manufacturing bounds on every segment height.

For a rectangular section:

```text
I_i = b h_i^3 / 12
sigma_i = 6 M_i / (b h_i^2)
```

Tip deflection is approximated from Castigliano's theorem using midpoint quadrature.

## Run

```bash
julia --project=. -e 'using Pkg; Pkg.add(["JuMP","MadNLP"])'
julia --project=. beam_design.jl
```

The script prints the local NLP status, minimum mass, maximum stress, tip deflection, and optimized segment heights.

## Why MadNLP

MadNLP is designed for large-scale nonlinear programming and exposes structure-aware KKT linear algebra. This example complements the SciPy/SLSQP implementation already present at the repository root with a dedicated mathematical-programming solver workflow.

## Engineering scope

This is an educational optimization model, not a certified structural-design calculation. It omits buckling, fatigue, shear deformation, local instability, code checks, and finite-element validation.
