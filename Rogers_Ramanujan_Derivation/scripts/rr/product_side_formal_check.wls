(* created: 2026-05-15T03:20:00Z
   cycle: 9
   run_id: run-2026-05-14T232311Z
   agent: worker
   milestone: M3

   Product-side formalization sanity checks for the Rogers-Ramanujan proof.
   This script verifies finite truncation residuals only; the proof is in
   docs/proof/product_side.md. Optional env vars:
     KMAX=40
     OUTDIR=data/finite_experiments
*)

ClearAll["Global`*"];

env[name_, default_] := Module[{v = Environment[name]},
  If[StringQ[v] && StringLength[v] > 0, v, default]
];

workspace = DirectoryName[DirectoryName[DirectoryName[$InputFileName]]];
KMax = ToExpression[env["KMAX", "40"]];
OutDir = env["OUTDIR", "data/finite_experiments"];
If[! AbsoluteFileNameQ[OutDir], OutDir = FileNameJoin[{workspace, OutDir}]];
If[! DirectoryQ[OutDir], CreateDirectory[OutDir, CreateIntermediateDirectories -> True]];

trunc[expr_] := Normal[Series[expr, {q, 0, KMax}]] // Expand;
coeff[poly_, k_Integer] := Coefficient[poly, q, k];
coeffs[poly_] := Table[coeff[poly, k], {k, 0, KMax}];
maxAbsCoeff[poly_] := Max[Abs[coeffs[poly]]];
firstNonzero[poly_] := Module[{ks = Select[Range[0, KMax], coeff[poly, #] != 0 &]},
  If[Length[ks] == 0, "none_through_KMax", First[ks]]
];

qPochFinite[n_Integer] := Product[1 - q^j, {j, 1, n}];
prodClass[r_Integer, step_Integer] := Product[1 - q^(r + step m), {m, 0, Floor[(KMax - r)/step]}];
prodClasses[rs_List, step_Integer] := Times @@ (prodClass[#, step] & /@ rs);

seriesS[alpha_Integer] := Sum[
  q^(n^2 + alpha n)/qPochFinite[n],
  {n, 0, KMax}
];

bilateralB[0] := Sum[(-1)^j q^(j (5 j - 1)/2), {j, -KMax, KMax}];
bilateralB[1] := Sum[(-1)^j q^(j (5 j - 3)/2), {j, -KMax, KMax}];

euler = prodClasses[{1, 2, 3, 4, 5}, 5];
jacobiProduct[0] := prodClasses[{2, 3, 5}, 5];
jacobiProduct[1] := prodClasses[{1, 4, 5}, 5];
targetProduct[0] := trunc[1/prodClasses[{1, 4}, 5]];
targetProduct[1] := trunc[1/prodClasses[{2, 3}, 5]];

residualRows = {{
  "check",
  "alpha_case",
  "first_nonzero_k",
  "max_abs_coefficient"
}};

addResidual[check_, alpha_, expr_] := Module[{poly = trunc[expr]},
  residualRows = Append[residualRows, {
    check,
    alpha,
    firstNonzero[poly],
    maxAbsCoeff[poly]
  }]
];

Do[
  addResidual[
    "euler_times_series_minus_bilateral",
    alpha,
    trunc[euler seriesS[alpha]] - trunc[bilateralB[alpha]]
  ];
  addResidual[
    "bilateral_minus_jacobi_product",
    alpha,
    trunc[bilateralB[alpha]] - trunc[jacobiProduct[alpha]]
  ];
  addResidual[
    "series_minus_reciprocal_residue_product",
    alpha,
    trunc[seriesS[alpha]] - targetProduct[alpha]
  ],
  {alpha, 0, 1}
];

Export[FileNameJoin[{OutDir, "product_side_residuals.csv"}], residualRows, "CSV"];

Print["KMax=", KMax];
Print["Transformed identity max residual: ",
  Max[#[[4]] & /@ Select[Rest[residualRows], #[[1]] == "euler_times_series_minus_bilateral" &]]
];
Print["Jacobi product max residual: ",
  Max[#[[4]] & /@ Select[Rest[residualRows], #[[1]] == "bilateral_minus_jacobi_product" &]]
];
Print["Final product identity max residual: ",
  Max[#[[4]] & /@ Select[Rest[residualRows], #[[1]] == "series_minus_reciprocal_residue_product" &]]
];
Print["Wrote outputs in ", OutDir];
