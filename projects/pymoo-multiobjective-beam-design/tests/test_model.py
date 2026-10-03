import numpy as np

from pymoo_beam import (
    BeamConfig,
    BeamTradeoffProblem,
    beam_metrics,
    knee_point_index,
    solve_pareto,
)


def test_metrics_show_expected_weight_stiffness_tradeoff():
    cfg = BeamConfig(n_segments=4)
    thin = np.full(cfg.n_segments, 0.08)
    thick = np.full(cfg.n_segments, 0.16)

    thin_weight, thin_deflection, thin_stress = beam_metrics(thin, cfg)
    thick_weight, thick_deflection, thick_stress = beam_metrics(thick, cfg)

    assert thick_weight > thin_weight
    assert thick_deflection < thin_deflection
    assert thick_stress < thin_stress


def test_problem_uses_pymoo_constraint_sign_convention():
    cfg = BeamConfig(n_segments=4)
    problem = BeamTradeoffProblem(cfg)

    feasible = np.full(cfg.n_segments, cfg.max_height)
    infeasible = np.full(cfg.n_segments, cfg.min_height)

    feasible_out = {}
    infeasible_out = {}
    problem._evaluate(feasible, feasible_out)
    problem._evaluate(infeasible, infeasible_out)

    assert feasible_out["G"][0] <= 0.0
    assert infeasible_out["G"][0] > 0.0


def test_small_nsga2_run_returns_feasible_finite_front():
    cfg = BeamConfig(n_segments=4)
    result = solve_pareto(config=cfg, pop_size=32, generations=24, seed=7)

    objectives = np.atleast_2d(result.F)
    designs = np.atleast_2d(result.X)
    assert objectives.shape[0] >= 1
    assert np.all(np.isfinite(objectives))

    for design in designs:
        _, _, stress = beam_metrics(design, cfg)
        assert stress <= cfg.allowable_stress * (1.0 + 1e-6)


def test_knee_point_index_is_valid():
    objectives = np.array([[1.0, 9.0], [3.0, 4.0], [8.0, 1.0]])
    idx = knee_point_index(objectives)
    assert 0 <= idx < len(objectives)
