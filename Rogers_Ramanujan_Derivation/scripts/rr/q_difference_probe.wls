(* created: 2026-05-14T23:55:00Z
   cycle: 2
   run_id: run-2026-05-14T232311Z
   agent: worker
   milestone: M2

   Exact q-difference ladder probes for the Rogers-Ramanujan derivation.
   Optional env vars:
     KMAX=40
     RMAX=12
     TAILR=45
     OUTDIR=data/finite_experiments
*)

ClearAll["Global`*"];

env[name_, default_] := Module[{v = Environment[name]},
  If[StringQ[v] && StringLength[v] > 0, v, default]
];

KMax = ToExpression[env["KMAX", "40"]];
RMax = ToExpression[env["RMAX", "12"]];
TailR = ToExpression[env["TAILR", ToString[KMax + 5]]];
InternalKMax = ToExpression[env["INTERNAL_KMAX", ToString[KMax + (RMax + 2) (RMax + 3)/2]]];
OutDir = env["OUTDIR", "data/finite_experiments"];
If[! DirectoryQ[OutDir], CreateDirectory[OutDir, CreateIntermediateDirectories -> True]];

qpoch[n_Integer] := Product[1 - q^j, {j, 1, n}];
trunc[expr_] := Normal[Series[expr, {q, 0, KMax}]] // Expand;
truncTo[expr_, k_Integer] := Normal[Series[expr, {q, 0, k}]] // Expand;
coeff[poly_, k_Integer] := Coefficient[poly, q, k];
coeffs[poly_] := Table[coeff[poly, k], {k, 0, KMax}];

aSeries[r_Integer] := trunc[
  Sum[q^(n^2 + r n)/qpoch[n], {n, 0, Floor[(-r + Sqrt[r^2 + 4 KMax])/2]}]
];

residueProduct[residues_List, k_Integer] := Module[{parts},
  parts = Select[Range[k], MemberQ[residues, Mod[#, 5]] &];
  truncTo[Times @@ ((1/(1 - q^#)) & /@ parts), k]
];

firstNonzero[poly_] := Module[{ks = Select[Range[0, KMax], coeff[poly, #] != 0 &]},
  If[Length[ks] == 0, "none_through_KMax", First[ks]]
];

maxAbsCoeff[poly_] := Max[Abs[coeffs[poly]]];

(* Proved series-side ladder residuals. *)
a = Association[Table[r -> aSeries[r], {r, 0, Max[RMax + 2, 2]}]];
ladderRows = Flatten[
  Table[
    With[{res = trunc[a[r] - a[r + 1] - q^(r + 1) a[r + 2]]},
      Table[{"series_ladder", r, k, coeff[res, k]}, {k, 0, KMax}]
    ],
    {r, 0, RMax}
  ],
  1
];

(* Backsolve the unique tail-normalized ladder: C_r=C_{r+1}+q^(r+1) C_{r+2}. *)
c = Association[];
c[TailR] = 1;
c[TailR + 1] = 1;
Do[
  c[r] = trunc[c[r + 1] + q^(r + 1) c[r + 2]],
  {r, TailR - 1, 0, -1}
];

p14Full = residueProduct[{1, 4}, InternalKMax];
p23Full = residueProduct[{2, 3}, InternalKMax];
p14 = trunc[p14Full];
p23 = trunc[p23Full];

(* Forward states forced by P14/P23. Divisibility by q^(r+1) is diagnostic only. *)
b = Association[0 -> p14, 1 -> p23];
bFull = Association[0 -> p14Full, 1 -> p23Full];
Do[
  bFull[r + 2] = truncTo[(bFull[r] - bFull[r + 1])/q^(r + 1), InternalKMax - (r + 1)];
  b[r + 2] = trunc[bFull[r + 2]],
  {r, 0, RMax}
];

backsolveRows = Join[
  {{"comparison", "r", "first_nonzero_k", "max_abs_coeff"}},
  Table[
    With[{diff = trunc[c[r] - a[r]]},
      {"backsolve_minus_series", r, firstNonzero[diff], maxAbsCoeff[diff]}
    ],
    {r, 0, Min[RMax, TailR - 1]}
  ],
  {
    {"backsolve_C0_minus_P14", 0, firstNonzero[trunc[c[0] - p14]], maxAbsCoeff[trunc[c[0] - p14]]},
    {"backsolve_C1_minus_P23", 1, firstNonzero[trunc[c[1] - p23]], maxAbsCoeff[trunc[c[1] - p23]]}
  },
  Table[
    With[{diff = trunc[b[r] - c[r]]},
      {"forward_from_products_minus_backsolve", r, firstNonzero[diff], maxAbsCoeff[diff]}
    ],
    {r, 0, RMax + 2}
  ],
  Table[
    With[{tailDiff = trunc[b[r] - 1]},
      {"forward_from_products_tail_minus_1", r, firstNonzero[tailDiff], maxAbsCoeff[tailDiff]}
    ],
    {r, Max[0, RMax - 2], RMax + 2}
  ]
];

residualRows = Prepend[ladderRows, {"check", "r", "k", "residual"}];

Export[FileNameJoin[{OutDir, "q_difference_residuals.csv"}], residualRows, "CSV"];
Export[FileNameJoin[{OutDir, "q_difference_backsolve.csv"}], backsolveRows, "CSV"];

Print["KMax=", KMax];
Print["RMax=", RMax];
Print["TailR=", TailR];
Print["InternalKMax=", InternalKMax];
Print["Series ladder max residual: ", Max[Abs[Last /@ Rest[residualRows]]]];
Print["Backsolve C0 minus P14 first nonzero: ", firstNonzero[trunc[c[0] - p14]]];
Print["Backsolve C1 minus P23 first nonzero: ", firstNonzero[trunc[c[1] - p23]]];
Print["Forward product state B", RMax + 2, " minus 1 first nonzero: ", firstNonzero[trunc[b[RMax + 2] - 1]]];
Print["Wrote outputs in ", OutDir];
