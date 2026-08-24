import numpy as np
from scipy.optimize import minimize

# Cantilever beam design optimization
# Rectangular cross-section with constant width and segment-wise variable height.
# Euler-Bernoulli beam theory is used for bending stress and tip deflection.

# Geometry and discretization
LENGTH = 10.0           # m
N_SEGMENTS = 10
DX = LENGTH / N_SEGMENTS
WIDTH = 0.05            # m

# Material / loading
DENSITY = 7800.0        # kg/m^3
GRAVITY = 9.81          # m/s^2
YOUNGS_MODULUS = 210e9  # Pa
TIP_LOAD = 1000.0       # N

# Design constraints
ALLOWABLE_STRESS = 250e6       # Pa
ALLOWABLE_TIP_DEFLECTION = 0.01  # m
MIN_HEIGHT = 0.02              # m
MAX_HEIGHT = 0.50              # m

# Midpoint locations for piecewise-constant beam segments.
X_MID = (np.arange(N_SEGMENTS) + 0.5) * DX


def section_properties(heights):
    """Return area, second moment of area, and extreme-fiber distance."""
    heights = np.asarray(heights, dtype=float)
    area = WIDTH * heights
    inertia = WIDTH * heights**3 / 12.0
    c = heights / 2.0
    return area, inertia, c


def beam_weight(heights):
    """Total beam weight in newtons."""
    area, _, _ = section_properties(heights)
    volume = np.sum(area * DX)
    return DENSITY * GRAVITY * volume


def bending_moments():
    """Bending moment at each segment midpoint for a tip point load."""
    return TIP_LOAD * (LENGTH - X_MID)


def bending_stresses(heights):
    """Maximum absolute bending stress in each segment, in pascals."""
    _, inertia, c = section_properties(heights)
    return bending_moments() * c / inertia


def tip_deflection(heights):
    """
    Approximate the tip deflection with midpoint numerical integration.

    From Castigliano's theorem for a cantilever carrying a tip load P:
        delta = integral_0^L [P (L-x)^2 / (E I(x))] dx

    I(x) is piecewise constant over each design segment.
    """
    _, inertia, _ = section_properties(heights)
    lever_arm = LENGTH - X_MID
    integrand = TIP_LOAD * lever_arm**2 / (YOUNGS_MODULUS * inertia)
    return np.sum(integrand * DX)


def stress_constraint(heights):
    """SLSQP inequality convention: feasible values are >= 0."""
    return ALLOWABLE_STRESS - bending_stresses(heights)


def deflection_constraint(heights):
    """SLSQP inequality convention: feasible values are >= 0."""
    return ALLOWABLE_TIP_DEFLECTION - tip_deflection(heights)


def optimize_beam(initial_height=0.15):
    """Run constrained beam-weight minimization and return SciPy result."""
    x0 = np.full(N_SEGMENTS, initial_height, dtype=float)
    bounds = [(MIN_HEIGHT, MAX_HEIGHT)] * N_SEGMENTS
    constraints = [
        {"type": "ineq", "fun": stress_constraint},
        {"type": "ineq", "fun": deflection_constraint},
    ]

    return minimize(
        beam_weight,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 2000, "ftol": 1e-10, "disp": False},
    )


def main():
    result = optimize_beam()

    print("Optimization success:", result.success)
    print("Message:", result.message)

    if not result.success:
        raise RuntimeError("Optimization failed; inspect solver message above.")

    h_opt = result.x
    sigma = bending_stresses(h_opt)
    delta = tip_deflection(h_opt)

    print("\nOptimal segment heights [m]:")
    for i, h in enumerate(h_opt, start=1):
        print(f"  Segment {i:02d}: {h:.6f}")

    print(f"\nMinimum beam weight: {beam_weight(h_opt):.3f} N")
    print(f"Maximum bending stress: {np.max(sigma) / 1e6:.3f} MPa")
    print(f"Tip deflection: {delta * 1e3:.3f} mm")
    print(f"Stress utilization: {np.max(sigma) / ALLOWABLE_STRESS:.4f}")
    print(
        "Deflection utilization: "
        f"{delta / ALLOWABLE_TIP_DEFLECTION:.4f}"
    )


if __name__ == "__main__":
    main()
