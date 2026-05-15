(* created: 2026-05-14T23:31:00Z
   cycle: 1
   run_id: run-2026-05-14T232311Z
   agent: worker
   milestone: M1

   Exact finite experiments for the Rogers-Ramanujan foundation.
   Optional env vars:
     KMAX=40
     OUTDIR=data/finite_experiments
*)

ClearAll["Global`*"];

env[name_, default_] := Module[{v = Environment[name]},
  If[StringQ[v] && StringLength[v] > 0, v, default]
];

KMax = ToExpression[env["KMAX", "40"]];
OutDir = env["OUTDIR", "data/finite_experiments"];
If[! DirectoryQ[OutDir], CreateDirectory[OutDir, CreateIntermediateDirectories -> True]];

qpoch[n_Integer] := Product[1 - q^j, {j, 1, n}];
trunc[expr_] := Normal[Series[expr, {q, 0, KMax}]] // Expand;
coeffs[poly_] := Table[Coefficient[poly, q, k], {k, 0, KMax}];

series1[] := trunc[Sum[q^(n^2)/qpoch[n], {n, 0, Floor[Sqrt[KMax]]}]];
series2[] := trunc[Sum[q^(n^2 + n)/qpoch[n], {n, 0, Floor[(-1 + Sqrt[1 + 4 KMax])/2]}]];
seriesShifted[] := trunc[Sum[q^(n^2 + 2 n)/qpoch[n], {n, 0, Floor[-1 + Sqrt[1 + KMax]]}]];

residueProduct[residues_List] := Module[{parts},
  parts = Select[Range[KMax], MemberQ[residues, Mod[#, 5]] &];
  trunc[Times @@ ((1/(1 - q^#)) & /@ parts)]
];

s1 = series1[];
s2 = series2[];
sShift = seriesShifted[];
p14 = residueProduct[{1, 4}];
p23 = residueProduct[{2, 3}];
p13 = residueProduct[{1, 3}];
p24 = residueProduct[{2, 4}];

coeffRows = Prepend[
  Table[
    {
      k,
      Coefficient[s1, q, k],
      Coefficient[p14, q, k],
      Coefficient[s2, q, k],
      Coefficient[p23, q, k],
      Coefficient[p13, q, k],
      Coefficient[p24, q, k],
      Coefficient[sShift, q, k]
    },
    {k, 0, KMax}
  ],
  {"k", "S1_gap_smallest_ge_1", "P14_residues_1_4", "S2_gap_smallest_ge_2", "P23_residues_2_3", "P13_negative_control", "P24_negative_control", "S_shift_n2_plus_2n_negative_control"}
];

diffRows = Prepend[
  Join[
    Table[{"RR1_true_S1_minus_P14", k, Coefficient[s1 - p14, q, k]}, {k, 0, KMax}],
    Table[{"RR2_true_S2_minus_P23", k, Coefficient[s2 - p23, q, k]}, {k, 0, KMax}],
    Table[{"NC_residues_13_S1_minus_P13", k, Coefficient[s1 - p13, q, k]}, {k, 0, KMax}],
    Table[{"NC_residues_24_S2_minus_P24", k, Coefficient[s2 - p24, q, k]}, {k, 0, KMax}],
    Table[{"NC_shifted_exponent_Sshift_minus_P14", k, Coefficient[sShift - p14, q, k]}, {k, 0, KMax}]
  ],
  {"comparison", "k", "difference"}
];

Export[FileNameJoin[{OutDir, "rr_coefficients.csv"}], coeffRows, "CSV"];
Export[FileNameJoin[{OutDir, "rr_differences.csv"}], diffRows, "CSV"];

firstNonzero[poly_] := Module[{ks = Select[Range[0, KMax], Coefficient[poly, q, #] != 0 &]},
  If[Length[ks] == 0, "none_through_KMax", First[ks]]
];

residueWeight[r_Integer, residues_List] := Total[Select[Divisors[r], MemberQ[residues, Mod[#, 5]] &]];
verifyProductRecurrence[coeff_List, residues_List] := Table[
  n coeff[[n + 1]] - Sum[residueWeight[r, residues] coeff[[n - r + 1]], {r, 1, n}],
  {n, 1, KMax}
];

recRows = Prepend[
  Join[
    {{"product_P14_log_derivative_recurrence", "max_abs_residual", Max[Abs[verifyProductRecurrence[coeffs[p14], {1, 4}]]]}},
    {{"product_P23_log_derivative_recurrence", "max_abs_residual", Max[Abs[verifyProductRecurrence[coeffs[p23], {2, 3}]]]}},
    {{"first_nonzero_RR1_true_difference", "k", firstNonzero[s1 - p14]}},
    {{"first_nonzero_RR2_true_difference", "k", firstNonzero[s2 - p23]}},
    {{"first_nonzero_NC_residues_13", "k", firstNonzero[s1 - p13]}},
    {{"first_nonzero_NC_residues_24", "k", firstNonzero[s2 - p24]}},
    {{"first_nonzero_NC_shifted_exponent", "k", firstNonzero[sShift - p14]}}
  ],
  {"candidate_or_check", "measure", "value"}
];

Export[FileNameJoin[{OutDir, "rr_recurrence_candidates.csv"}], recRows, "CSV"];

Print["KMax=", KMax];
Print["RR1 first nonzero diff: ", firstNonzero[s1 - p14]];
Print["RR2 first nonzero diff: ", firstNonzero[s2 - p23]];
Print["NC {1,3} first nonzero diff: ", firstNonzero[s1 - p13]];
Print["NC {2,4} first nonzero diff: ", firstNonzero[s2 - p24]];
Print["NC shifted exponent first nonzero diff: ", firstNonzero[sShift - p14]];
Print["Wrote outputs in ", OutDir];
