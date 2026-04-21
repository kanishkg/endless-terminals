I'm a compliance officer auditing our company's resource allocation systems. We have a legacy linear programming solver that was used to determine optimal staffing for our call center, but the original documentation is gone and I need to verify the solution meets all our regulatory constraints.

The solver output file is at /home/user/audit/solver_output.dat and contains the raw solution values. The constraint definitions are in /home/user/audit/constraints.csv. I need you to verify whether this solution is actually feasible and optimal, then produce an audit report.

The constraints.csv file has the format:
```
constraint_name,type,coefficients,rhs
```
Where `type` is either "LE" (less than or equal), "GE" (greater than or equal), or "EQ" (equal). The `coefficients` field contains pipe-separated coefficients for variables x1 through x6 (representing staff counts for 6 different shift types). The `rhs` is the right-hand side value.

The solver_output.dat file contains lines in format `xN = value` for each variable.

The objective function we were maximizing is: `3.5*x1 + 4.2*x2 + 2.8*x3 + 5.1*x4 + 3.9*x5 + 4.7*x6` (representing total productivity units).

Your tasks:
1. Parse both files and check if the current solution satisfies ALL constraints (within a tolerance of 0.0001 for floating point comparisons).
2. Use an LP solver (scipy, pulp, or any available tool) to find the actual optimal solution.
3. Compare the stored solution against the true optimum.
4. Generate an audit report at /home/user/audit/compliance_report.json

The compliance_report.json must have exactly this structure:
```json
{
  "audit_timestamp": "<ISO 8601 timestamp>",
  "stored_solution": {
    "x1": <float>,
    "x2": <float>,
    "x3": <float>,
    "x4": <float>,
    "x5": <float>,
    "x6": <float>,
    "objective_value": <float>
  },
  "feasibility_check": {
    "is_feasible": <boolean>,
    "violated_constraints": [<list of constraint names that are violated, empty if feasible>]
  },
  "optimal_solution": {
    "x1": <float>,
    "x2": <float>,
    "x3": <float>,
    "x4": <float>,
    "x5": <float>,
    "x6": <float>,
    "objective_value": <float>
  },
  "optimality_gap": <float representing percentage difference between stored and optimal objective>,
  "compliance_status": "<COMPLIANT if feasible and gap <= 1.0%, NON_COMPLIANT otherwise>"
}
```

All float values in the JSON should be rounded to exactly 4 decimal places. The optimality_gap should be calculated as `100 * abs(stored_obj - optimal_obj) / optimal_obj`.

This audit is time-sensitive so please proceed directly with the analysis.
