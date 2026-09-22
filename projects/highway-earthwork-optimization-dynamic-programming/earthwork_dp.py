from __future__ import annotations

from dataclasses import dataclass
from math import inf


# Volumes are expressed in units of 10^3 m^3.
# Positive values are excavation (cut), negative values are fill requirements.
NET_VOLUME = {
    1: -10,
    2: 28,
    3: 32,
    4: -14,
    5: -16,
    6: -10,
    7: 13,
    8: -12,
    9: -11,
}

EXCAVATION_COST = 8   # TL / m^3
FILL_COST = 12        # TL / m^3
HAUL_COST = 2         # TL / m^3 / section
THOUSAND_M3 = 1000


@dataclass(frozen=True)
class Step:
    section: int
    balance_before: int
    balance_after: int
    local_volume: int
    transport_cost: int


def solve_dp(net_volume: dict[int, int] = NET_VOLUME):
    """Solve the 1-D earthwork balancing problem by dynamic programming.

    State b after section i is the cumulative surplus (>0) or deficit (<0)
    of soil that must cross the boundary between sections i and i+1.

    Moving |b| thousand m^3 across one section boundary costs
    HAUL_COST * |b| in thousand TL.
    """
    sections = sorted(net_volume)

    # The balance transition is deterministic: b_i = b_{i-1} + net_i.
    # We still formulate it as a DP so the state/cost interpretation is explicit.
    dp: dict[int, tuple[int, list[Step]]] = {0: (0, [])}

    for section in sections:
        next_dp: dict[int, tuple[int, list[Step]]] = {}
        v = net_volume[section]

        for balance_before, (cost_so_far, path) in dp.items():
            balance_after = balance_before + v

            # No hauling charge after the final section because nothing crosses
            # beyond the project boundary.
            boundary_cost = 0 if section == sections[-1] else HAUL_COST * abs(balance_after)
            new_cost = cost_so_far + boundary_cost

            old = next_dp.get(balance_after, (inf, []))
            if new_cost < old[0]:
                next_dp[balance_after] = (
                    new_cost,
                    path + [
                        Step(
                            section=section,
                            balance_before=balance_before,
                            balance_after=balance_after,
                            local_volume=v,
                            transport_cost=boundary_cost,
                        )
                    ],
                )

        dp = next_dp

    if 0 not in dp:
        raise ValueError("Total excavation and fill are not balanced; external borrow/waste is required.")

    haul_cost_thousand_tl, path = dp[0]

    total_cut = sum(v for v in net_volume.values() if v > 0)
    total_fill = -sum(v for v in net_volume.values() if v < 0)

    earthwork_cost_thousand_tl = (
        total_cut * EXCAVATION_COST + total_fill * FILL_COST
    )
    total_cost_thousand_tl = earthwork_cost_thousand_tl + haul_cost_thousand_tl

    return {
        "total_cut_1000m3": total_cut,
        "total_fill_1000m3": total_fill,
        "earthwork_cost_thousand_tl": earthwork_cost_thousand_tl,
        "haul_cost_thousand_tl": haul_cost_thousand_tl,
        "total_cost_thousand_tl": total_cost_thousand_tl,
        "total_cost_tl": total_cost_thousand_tl * THOUSAND_M3,
        "steps": path,
    }


def reconstruct_transport_plan(net_volume: dict[int, int] = NET_VOLUME):
    """Construct one optimal source-to-destination transport plan.

    For a line network with cost proportional to distance, matching supply and
    demand greedily from left to right yields an optimal earthwork haul plan.
    Returned volumes are in units of 10^3 m^3.
    """
    supplies = [[i, v] for i, v in sorted(net_volume.items()) if v > 0]
    demands = [[j, -v] for j, v in sorted(net_volume.items()) if v < 0]

    plan: list[tuple[int, int, int]] = []
    si = di = 0

    while si < len(supplies) and di < len(demands):
        source, supply = supplies[si]
        dest, demand = demands[di]
        qty = min(supply, demand)
        plan.append((source, dest, qty))

        supplies[si][1] -= qty
        demands[di][1] -= qty

        if supplies[si][1] == 0:
            si += 1
        if demands[di][1] == 0:
            di += 1

    if si != len(supplies) or di != len(demands):
        raise ValueError("Unbalanced excavation/fill volumes.")

    return plan


def main():
    result = solve_dp()
    plan = reconstruct_transport_plan()

    print("Optimal transport plan (10^3 m^3):")
    for source, dest, qty in plan:
        print(f"  Section {source} -> Section {dest}: {qty}")

    print("\nCosts:")
    print(f"  Excavation + fill: {result['earthwork_cost_thousand_tl']} thousand TL")
    print(f"  Hauling:           {result['haul_cost_thousand_tl']} thousand TL")
    print(f"  Minimum total:     {result['total_cost_thousand_tl']} thousand TL")
    print(f"                     {result['total_cost_tl']:,} TL")


if __name__ == "__main__":
    main()
