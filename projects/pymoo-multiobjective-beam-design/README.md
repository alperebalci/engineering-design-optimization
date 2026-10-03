# pymoo Multi-Objective Beam Design

A compact engineering-design benchmark that uses **pymoo 0.6.2** and NSGA-II to expose a real trade-off that the repository's single-objective SLSQP example cannot represent directly.

## Research question

How does a cantilever-beam design trade structural mass against stiffness when maximum bending stress remains a hard feasibility constraint?

The design vector contains piecewise-constant beam heights. The two minimized objectives are:

1. beam weight in newtons;
2. tip deflection in millimetres.

Feasibility requires maximum bending stress to remain below the allowable stress. The mechanics use the same Euler-Bernoulli / Castigliano assumptions as the repository's root beam example.

This is intentionally not another scalarized weighted-sum solve. NSGA-II returns a non-dominated set so the weight-versus-stiffness trade-off remains visible.

## Why pymoo belongs here

`pymoo` adds material capability rather than syntax:

- non-dominated sorting and Pareto-front search;
- constraint-aware multi-objective evolutionary optimization;
- reproducible seeded runs;
- a direct path to NSGA-III, MOEA/D, indicators, and many-objective extensions.

The root SciPy/SLSQP model remains the exact single-objective teaching example. This project complements it rather than replacing it.

## Install

```bash
python -m pip install -e '.[dev]'
```

## Run

```bash
pymoo-beam --population 96 --generations 120 --seed 2026
```

or

```bash
python -m pymoo_beam
```

The CLI prints the Pareto-front size, objective ranges, and a normalized knee-point design.

## Test

```bash
pytest
```

The tests verify the mechanical monotonicity expected from thicker sections, pymoo's `G <= 0` constraint convention, a seeded NSGA-II smoke run, and the knee-point selector.

## Claims boundary

This is an educational/research benchmark, not a certified structural design tool. Buckling, fatigue, dynamic loads, local stability, manufacturing rules, safety factors, and code compliance are outside scope.
