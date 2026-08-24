import numpy as np

from beam_optimization import (
    ALLOWABLE_STRESS,
    ALLOWABLE_TIP_DEFLECTION,
    N_SEGMENTS,
    bending_stresses,
    optimize_beam,
    tip_deflection,
)


def test_default_optimization_is_feasible():
    result = optimize_beam()
    assert result.success
    assert len(result.x) == N_SEGMENTS
    assert np.max(bending_stresses(result.x)) <= ALLOWABLE_STRESS * (1.0 + 1e-7)
    assert tip_deflection(result.x) <= ALLOWABLE_TIP_DEFLECTION * (1.0 + 1e-7)


def test_optimum_tapers_toward_free_end():
    result = optimize_beam()
    assert result.success
    # For this load case and model, the optimum should be non-increasing
    # from the fixed end toward the free end.
    assert np.all(np.diff(result.x) <= 1e-6)
