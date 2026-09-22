from earthwork_dp import reconstruct_transport_plan, solve_dp


def test_optimal_costs():
    result = solve_dp()
    assert result["total_cut_1000m3"] == 73
    assert result["total_fill_1000m3"] == 73
    assert result["earthwork_cost_thousand_tl"] == 1460
    assert result["haul_cost_thousand_tl"] == 356
    assert result["total_cost_thousand_tl"] == 1816
    assert result["total_cost_tl"] == 1_816_000


def test_transport_plan_balances_sections():
    plan = reconstruct_transport_plan()

    sent = {}
    received = {}
    for source, destination, amount in plan:
        sent[source] = sent.get(source, 0) + amount
        received[destination] = received.get(destination, 0) + amount

    assert sent == {2: 28, 3: 32, 7: 13}
    assert received == {1: 10, 4: 14, 5: 16, 6: 10, 8: 12, 9: 11}


def test_transport_plan_has_minimum_haul_cost():
    plan = reconstruct_transport_plan()
    haul_cost = sum(2 * abs(source - destination) * amount for source, destination, amount in plan)
    assert haul_cost == 356
