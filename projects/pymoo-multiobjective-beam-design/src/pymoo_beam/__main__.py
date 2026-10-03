"""CLI for the pymoo multi-objective beam benchmark."""

from __future__ import annotations

import argparse
import json

import numpy as np

from .model import BeamConfig, beam_metrics, knee_point_index, solve_pareto


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--population", type=int, default=96)
    parser.add_argument("--generations", type=int, default=120)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    config = BeamConfig()
    result = solve_pareto(
        config=config,
        pop_size=args.population,
        generations=args.generations,
        seed=args.seed,
    )
    objectives = np.atleast_2d(result.F)
    designs = np.atleast_2d(result.X)
    idx = knee_point_index(objectives)
    weight, deflection_mm, max_stress = beam_metrics(designs[idx], config)

    payload = {
        "pareto_points": int(objectives.shape[0]),
        "selected_point": {
            "weight_N": weight,
            "tip_deflection_mm": deflection_mm,
            "max_stress_MPa": max_stress / 1e6,
            "stress_utilization": max_stress / config.allowable_stress,
            "segment_heights_m": designs[idx].tolist(),
        },
        "objective_ranges": {
            "weight_N": [
                float(objectives[:, 0].min()),
                float(objectives[:, 0].max()),
            ],
            "tip_deflection_mm": [
                float(objectives[:, 1].min()),
                float(objectives[:, 1].max()),
            ],
        },
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
