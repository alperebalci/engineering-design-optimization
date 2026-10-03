using JuMP
using MadNLP
import MathOptInterface as MOI

length_beam = 10.0
segments = 12
width = 0.05
density = 7800.0
youngs_modulus = 210e9
tip_load = 1000.0
allowable_stress = 250e6
max_tip_deflection = 0.010
h_min = 0.02
h_max = 0.50

dx = length_beam / segments
x_mid = [(i - 0.5) * dx for i in 1:segments]
moment = [tip_load * (length_beam - x) for x in x_mid]

model = Model(MadNLP.Optimizer)

@variable(model, h_min <= h[1:segments] <= h_max, start = 0.10)

@objective(model, Min, density * width * dx * sum(h[i] for i in 1:segments))

@NLconstraint(
    model,
    [i = 1:segments],
    6.0 * moment[i] / (width * h[i]^2) <= allowable_stress,
)

@NLconstraint(
    model,
    sum(
        tip_load * (length_beam - x_mid[i])^2 * dx /
        (youngs_modulus * (width * h[i]^3 / 12.0))
        for i in 1:segments
    ) <= max_tip_deflection,
)

optimize!(model)

status = termination_status(model)
status in (MOI.LOCALLY_SOLVED, MOI.OPTIMAL, MOI.ALMOST_LOCALLY_SOLVED) ||
    error("MadNLP did not return a solved status: $status")

h_star = value.(h)
stress = [6.0 * moment[i] / (width * h_star[i]^2) for i in 1:segments]
deflection = sum(
    tip_load * (length_beam - x_mid[i])^2 * dx /
    (youngs_modulus * (width * h_star[i]^3 / 12.0))
    for i in 1:segments
)

println("status             = ", status)
println("minimum mass       = ", round(objective_value(model), digits = 6), " kg")
println("maximum stress     = ", round(maximum(stress) / 1e6, digits = 6), " MPa")
println("tip deflection     = ", round(deflection * 1000, digits = 6), " mm")
println("segment heights    = ", round.(h_star, digits = 6))
