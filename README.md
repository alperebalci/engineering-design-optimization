# Cantilever Beam Design Optimization

This repository demonstrates constrained structural optimization of a cantilever beam using Python and SciPy.

The beam has a rectangular cross-section with constant width and segment-wise variable height. The optimization minimizes total beam weight while enforcing bending-stress and tip-deflection limits.

## Mechanical model

The implementation uses Euler-Bernoulli beam theory for a cantilever carrying a point load at its free end.

For each segment:

- Cross-sectional area: `A = b h`
- Second moment of area: `I = b h^3 / 12`
- Bending stress: `sigma = M c / I`
- Bending moment under a tip load: `M(x) = P (L - x)`

The tip deflection is evaluated numerically from Castigliano's theorem:

`delta = integral_0^L P (L-x)^2 / (E I(x)) dx`

The integral is approximated with midpoint integration over the design segments.

## Optimization problem

Design variables are the segment heights `h_i`.

Objective:

- Minimize beam weight.

Constraints:

- Bending stress in every segment must remain below the allowable stress.
- Tip deflection must remain below the prescribed displacement limit.
- Every segment height must remain within manufacturing/design bounds.

The nonlinear constrained optimization problem is solved with SciPy's SLSQP algorithm.

## Default example

The included example uses:

- Beam length: 10 m
- Number of design segments: 10
- Cross-section width: 0.05 m
- Steel density: 7800 kg/m^3
- Young's modulus: 210 GPa
- Tip load: 1000 N
- Allowable bending stress: 250 MPa
- Maximum tip deflection: 10 mm
- Height bounds: 0.02 m to 0.50 m

For the default case, the displacement constraint governs the optimum. A representative run produces a maximum bending stress of about 6.67 MPa and a tip deflection of approximately 10 mm.

## Installation

```bash
python -m venv .venv
```

Activate the environment, then install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python beam_optimization.py
```

## Notes and limitations

This project is an educational engineering optimization example rather than a certified structural-design tool. Euler-Bernoulli assumptions apply: small deflections, linear-elastic material behavior, and negligible shear deformation. The load case is a single static point load at the free end. Real engineering design may additionally require buckling, fatigue, dynamic loading, shear stress, local stability, manufacturing constraints, safety factors, code compliance, and finite-element validation.

## License

This repository is released under a custom non-commercial license. Commercial use is prohibited without prior written permission. See `LICENSE` for the complete terms.
