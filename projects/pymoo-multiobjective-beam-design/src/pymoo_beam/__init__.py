"""Multi-objective beam design benchmark built on pymoo."""

from .model import (
    BeamConfig,
    BeamTradeoffProblem,
    beam_metrics,
    knee_point_index,
    solve_pareto,
)

__all__ = [
    "BeamConfig",
    "BeamTradeoffProblem",
    "beam_metrics",
    "knee_point_index",
    "solve_pareto",
]
