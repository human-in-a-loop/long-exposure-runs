(* created: 2026-05-15T00:05:00Z
   cycle: 2
   run_id: run-2026-05-14T232311Z
   agent: worker
   milestone: M2

   Exact finite largest-part recurrence diagnostics for gap-two partitions.
   Optional env vars:
     KMAX=40
     NMAX=30
     OUTDIR=data/finite_experiments
*)

ClearAll["Global`*"];

env[name_, default_] := Module[{v = Environment[name]},
  If[StringQ[v] && StringLength[v] > 0, v, default]
];

KMax = ToExpression[env["KMAX", "40"]];
NMax = ToExpression[env["NMAX", "30"]];
OutDir = env["OUTDIR", "data/finite_experiments"];
If[! DirectoryQ[OutDir], CreateDirectory[OutDir, CreateIntermediateDirectories -> True]];

trunc[expr_] := Normal[Series[expr, {q, 0, KMax}]] // Expand;
coeff[poly_, k_Integer] := Coefficient[poly, q, k];
coeffs[poly_] := Table[coeff[poly, k], {k, 0, KMax}];
maxAbsCoeff[poly_] := Max[Abs[coeffs[poly]]];
firstNonzero[poly_] := Module[{ks = Select[Range[0, KMax], coeff[poly, #] != 0 &]},
  If[Length[ks] == 0, "none_through_KMax", First[ks]]
];

gapG[a_Integer, nmax_Integer] := Module[{g = Association[]},
  Do[g[n] = 1, {n, -2, a - 1}];
  Do[g[n] = trunc[g[n - 1] + q^n g[n - 2]], {n, a, nmax}];
  g
];

residueProductBound[residues_List, n_Integer] := Module[{parts},
  parts = Select[Range[n], MemberQ[residues, Mod[#, 5]] &];
  trunc[Times @@ ((1/(1 - q^#)) & /@ parts)]
];

g1 = gapG[1, NMax];
g2 = gapG[2, NMax];

rows = Prepend[
  Join[
    Table[
      With[{diff = trunc[g1[n] - residueProductBound[{1, 4}, n]]},
        {"smallest_ge_1_vs_P14_parts_le_N", n, Mod[n, 5], firstNonzero[diff], maxAbsCoeff[diff]}
      ],
      {n, 0, NMax}
    ],
    Table[
      With[{diff = trunc[g2[n] - residueProductBound[{2, 3}, n]]},
        {"smallest_ge_2_vs_P23_parts_le_N", n, Mod[n, 5], firstNonzero[diff], maxAbsCoeff[diff]}
      ],
      {n, 0, NMax}
    ]
  ],
  {"comparison", "N", "N_mod_5", "first_nonzero_k", "max_abs_coeff"}
];

Export[FileNameJoin[{OutDir, "finite_gap_subsequence.csv"}], rows, "CSV"];

Print["KMax=", KMax];
Print["NMax=", NMax];
Print["Final G_N^(1) minus bounded P14 first nonzero: ", rows[[NMax + 2, 4]]];
Print["Final G_N^(2) minus bounded P23 first nonzero: ", rows[[-1, 4]]];
Print["Wrote outputs in ", OutDir];
