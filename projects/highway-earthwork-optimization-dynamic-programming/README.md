# Highway Earthwork Optimization — Dynamic Programming

This repository solves a 1-D highway earthwork balancing problem using dynamic programming (DP).

The road is divided into nine consecutive sections. Some sections require excavation (cut), while others require filling. Excavated soil can be transported between sections. The objective is to minimize excavation, filling, and hauling costs.

## Data

Volumes are given in units of `10^3 m^3`.

| Section | Type | Volume |
|---|---:|---:|
| 1 | Fill | 10 |
| 2 | Excavation | 28 |
| 3 | Excavation | 32 |
| 4 | Fill | 14 |
| 5 | Fill | 16 |
| 6 | Fill | 10 |
| 7 | Excavation | 13 |
| 8 | Fill | 12 |
| 9 | Fill | 11 |

Total excavation = 73 x 10^3 m^3 and total fill = 73 x 10^3 m^3, so the project is exactly balanced and requires no external borrow or waste site.

## Costs

- Excavation: `8 TL/m^3`
- Filling: `12 TL/m^3`
- Hauling: `2 TL/m^3` per section crossed

Because the total cut and fill volumes are fixed, excavation and filling costs are constant. The optimization therefore reduces to minimizing hauling cost.

## DP formulation

Let `v_i` be the signed earthwork volume at section `i`:

- `v_i > 0`: excavation surplus
- `v_i < 0`: fill requirement

Let `b_i` be the cumulative soil balance after section `i`:

`b_i = b_(i-1) + v_i`, with `b_0 = 0`.

The magnitude `|b_i|` is the amount of soil that must cross the boundary between sections `i` and `i+1`. Therefore the hauling cost across that boundary is:

`2 * |b_i|` thousand TL.

The DP stage cost is the hauling cost induced by the state after each section. Since the cumulative transition is deterministic, the optimal value is obtained by summing the minimum required boundary flows.

For this instance, the boundary balances are:

`[-10, 18, 50, 36, 20, 10, 23, 11, 0]`

Hence the minimum hauling cost is:

`2 * (10 + 18 + 50 + 36 + 20 + 10 + 23 + 11) = 356` thousand TL.

## One optimal transport plan

An optimal source-to-destination plan is:

| From | To | Volume (`10^3 m^3`) |
|---:|---:|---:|
| 2 | 1 | 10 |
| 2 | 4 | 14 |
| 2 | 5 | 4 |
| 3 | 5 | 12 |
| 3 | 6 | 10 |
| 3 | 8 | 10 |
| 7 | 8 | 2 |
| 7 | 9 | 11 |

This plan satisfies all excavation and fill requirements and attains the minimum hauling cost of `356,000 TL`.

## Minimum total cost

Excavation cost:

`73,000 * 8 = 584,000 TL`

Fill cost:

`73,000 * 12 = 876,000 TL`

Hauling cost:

`356,000 TL`

Therefore:

`Minimum total cost = 584,000 + 876,000 + 356,000 = 1,816,000 TL`

## Run

```bash
python earthwork_dp.py
```

No third-party packages are required.

## Why the earlier LP formulation was wrong

A naive transportation model that defines `x[i,j]` for every pair of sections can accidentally allow physically meaningless self-transfers such as `x[2,2]`. If the supply and demand constraints are also attached incorrectly, the solver can satisfy excavation and fill requirements independently rather than actually transporting cut material to fill sections.

This implementation avoids that modeling error by using the cumulative earthwork balance along the road, which is the natural DP state for a linear highway profile.

## License

This project is source-available for personal, educational, academic, and non-commercial research use only. Commercial use is prohibited. See [`LICENSE`](LICENSE).
