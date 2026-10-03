"""Verification-friendly multi-objective cantilever beam design."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize


@dataclass(frozen=True)
class BeamConfig:
    length: float = 10.0
    n_segments: int = 8
    width: float = 0.05
    density: float = 7800.0
    gravity: float = 9.81
    youngs_modulus: float = 210e9
    tip_load: float = 1000.0
    allowable_stress: float = 250e6
    min_height: float = 0.02
    max_height: float = 0.50

    @property
    def dx(self) -> float:
        return self.length / self.n_segments

    @property
    def x_mid(self) -> np.ndarray:
        return (np.arange(self.n_segments, dtype=float) + 0.5) * self.dx


def _validated_heights(heights: np.ndarray, config: BeamConfig) -> np.ndarray:
    values = np.asarray(heights, dtype=float)
    if values.shape != (config.n_segments,):
        raise ValueError(
            f"Expected {config.n_segments} segment heights, got shape {values.shape}."
        )
    if not np.all(np.isfinite(values)):
        raise ValueError("Segment heights must be finite.")
    if np.any(values <= 0.0):
        raise ValueError("Segment heights must be positive.")
    return values


def beam_metrics(
    heights: np.ndarray, config: BeamConfig | None = None
) -> tuple[float, float, float]:
    """Return weight [N], tip deflection [mm], and maximum stress [Pa]."""
    cfg = config or BeamConfig()
    h = _validated_heights(heights, cfg)

    area = cfg.width * h
    inertia = cfg.width * h**3 / 12.0
    lever_arm = cfg.length - cfg.x_mid
    bending_moment = cfg.tip_load * lever_arm

    weight = cfg.density * cfg.gravity * float(np.sum(area * cfg.dx))
    max_stress = float(np.max(bending_moment * (h / 2.0) / inertia))
    deflection_m = float(
        np.sum(
            cfg.tip_load
            * lever_arm**2
            / (cfg.youngs_modulus * inertia)
            * cfg.dx
        )
    )
    return weight, 1_000.0 * deflection_m, max_stress


class BeamTradeoffProblem(ElementwiseProblem):
    """Minimize beam weight and tip deflection under a stress limit."""

    def __init__(self, config: BeamConfig | None = None):
        self.config = config or BeamConfig()
        super().__init__(
            n_var=self.config.n_segments,
            n_obj=2,
            n_ieq_constr=1,
            xl=np.full(self.config.n_segments, self.config.min_height),
            xu=np.full(self.config.n_segments, self.config.max_height),
        )

    def _evaluate(self, x, out, *args, **kwargs) -> None:
        weight, deflection_mm, max_stress = beam_metrics(x, self.config)
        out["F"] = np.array([weight, deflection_mm], dtype=float)
        # pymoo inequality convention: G <= 0 is feasible.
        out["G"] = np.array(
            [max_stress / self.config.allowable_stress - 1.0],
            dtype=float,
        )


def solve_pareto(
    *,
    config: BeamConfig | None = None,
    pop_size: int = 96,
    generations: int = 120,
    seed: int = 2026,
):
    """Run deterministic-seed NSGA-II and return pymoo's result object."""
    if pop_size < 4:
        raise ValueError("pop_size must be at least 4.")
    if generations < 1:
        raise ValueError("generations must be positive.")

    problem = BeamTradeoffProblem(config)
    algorithm = NSGA2(pop_size=pop_size, eliminate_duplicates=True)
    result = minimize(
        problem,
        algorithm,
        ("n_gen", generations),
        seed=seed,
        verbose=False,
    )
    if result.X is None or result.F is None:
        raise RuntimeError("NSGA-II returned no feasible Pareto solutions.")
    return result


def knee_point_index(objectives: np.ndarray) -> int:
    """Pick the non-dominated point nearest the normalized ideal point."""
    values = np.atleast_2d(np.asarray(objectives, dtype=float))
    if values.shape[1] != 2 or values.shape[0] == 0:
        raise ValueError("Expected a non-empty (n, 2) objective matrix.")

    lower = values.min(axis=0)
    span = np.maximum(values.max(axis=0) - lower, 1e-12)
    normalized = (values - lower) / span
    return int(np.argmin(np.linalg.norm(normalized, axis=1)))
