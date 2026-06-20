(* created: 2026-05-15T00:25:00Z
   cycle: 3
   run_id: run-2026-05-14T232311Z
   agent: worker
   milestone: M2

   Product-transform finite experiments for the Rogers-Ramanujan derivation.
   Optional env vars:
     KMAX=50
     NMAX=24
     OUTDIR=data/finite_experiments
*)

ClearAll["Global`*"];

env[name_, default_] := Module[{v = Environment[name]},
  If[StringQ[v] && StringLength[v] > 0, v, default]
];

KMax = ToExpression[env["KMAX", "50"]];
NMax = ToExpression[env["NMAX", "24"]];
OutDir = env["OUTDIR", "data/finite_experiments"];
If[! DirectoryQ[OutDir], CreateDirectory[OutDir, CreateIntermediateDirectories -> True]];

qpoch[n_Integer] := Product[1 - q^j, {j, 1, n}];
trunc[expr_] := Normal[Series[expr, {q, 0, KMax}]] // Expand;
coeff[poly_, k_Integer] := Coefficient[poly, q, k];
coeffs[poly_] := Table[coeff[poly, k], {k, 0, KMax}];
maxAbsCoeff[poly_] := Max[Abs[coeffs[poly]]];
firstNonzero[poly_] := Module[{ks = Select[Range[0, KMax], coeff[poly, #] != 0 &]},
  If[Length[ks] == 0, "none_through_KMax", First[ks]]
];

qbin[n_Integer, k_Integer, base_] := If[k < 0 || k > n, 0, QBinomial[n, k, base]];

h[alpha_Integer, n_Integer] := trunc[
  Sum[q^(r^2 + alpha r) qpoch[n]/qpoch[r], {r, 0, n}]
];

bilateralExponent[alpha_Integer, j_Integer] := j (5 j - (2 alpha + 1))/2;

bilateralPlain[alpha_Integer] := Module[{bound = Ceiling[Sqrt[2 KMax/5]] + 4},
  trunc[Sum[(-1)^j q^bilateralExponent[alpha, j], {j, -bound, bound}]]
];

finiteJacobiTriple[alpha_Integer, n_Integer] := Module[
  {zpow, bound = n, base = q^5},
  zpow[j_] := If[alpha == 0, q^(2 j), q^j];
  trunc[
    qpoch5[n] Sum[
      (-1)^j zpow[j] (q^5)^(j (j - 1)/2) qbin[2 n, n + j, base],
      {j, -bound, bound}
    ]
  ]
];

qpoch5[n_Integer] := Product[1 - q^(5 j), {j, 1, n}];

finiteJacobiProduct[alpha_Integer, n_Integer] := Module[{z = If[alpha == 0, q^2, q]},
  trunc[
    Product[1 - z (q^5)^r, {r, 0, n - 1}]
    Product[1 - (q^5)^(r + 1)/z, {r, 0, n - 1}]
    qpoch5[n]
  ]
];

schurCandidate[alpha_Integer, n_Integer, shift_Integer] := Module[
  {bound = n + 4},
  trunc[
    Sum[
      (-1)^j q^bilateralExponent[alpha, j] qbin[n, Floor[(n + shift - 5 j)/2], q],
      {j, -bound, bound}
    ]
  ]
];

wrongBilateral[] := Module[{bound = Ceiling[Sqrt[2 KMax/5]] + 4},
  trunc[Sum[(-1)^j q^(j (5 j - 5)/2), {j, -bound, bound}]]
];

candidateRows = {{"candidate", "alpha", "N", "parameter", "first_nonzero_k", "max_abs_coeff"}};
residualRows = {{"candidate", "alpha", "N", "parameter", "k", "residual"}};

appendCandidate[name_, alpha_, n_, parameter_, diff_] := (
  candidateRows = Append[candidateRows, {name, alpha, n, parameter, firstNonzero[diff], maxAbsCoeff[diff]}];
  residualRows = Join[
    residualRows,
    Table[{name, alpha, n, parameter, k, coeff[diff, k]}, {k, 0, KMax}]
  ];
);

Do[
  Do[
    appendCandidate[
      "H_alpha_N_minus_plain_bilateral_limit",
      alpha,
      n,
      "plain",
      trunc[h[alpha, n] - bilateralPlain[alpha]]
    ];
    appendCandidate[
      "H_alpha_N_minus_finite_jacobi_triple",
      alpha,
      n,
      "same_N",
      trunc[h[alpha, n] - finiteJacobiTriple[alpha, n]]
    ];
    Do[
      appendCandidate[
        "H_alpha_N_minus_schur_gaussian_window",
        alpha,
        n,
        shift,
        trunc[h[alpha, n] - schurCandidate[alpha, n, shift]]
      ],
      {shift, 0, 6}
    ];
    ,
    {n, 0, NMax}
  ],
  {alpha, 0, 1}
];

Do[
  appendCandidate[
    "negative_shifted_alpha2_minus_alpha0_bilateral",
    2,
    n,
    "alpha2_vs_alpha0",
    trunc[h[2, n] - bilateralPlain[0]]
  ];
  appendCandidate[
    "negative_alpha0_minus_wrong_z_q5",
    0,
    n,
    "wrong_z_q5",
    trunc[h[0, n] - wrongBilateral[]]
  ];
  ,
  {n, 0, NMax}
];

recurrenceRows = {{"check", "alpha", "N", "first_nonzero_k", "max_abs_coeff"}};
Do[
  If[n == 0,
    Null,
    Module[{diff = trunc[h[alpha, n] - (1 - q^n) h[alpha, n - 1] - q^(n^2 + alpha n)]},
      recurrenceRows = Append[recurrenceRows, {"H_recurrence", alpha, n, firstNonzero[diff], maxAbsCoeff[diff]}]
    ]
  ],
  {alpha, 0, 2}, {n, 0, NMax}
];

Do[
  Module[{diff = trunc[finiteJacobiProduct[alpha, n] - finiteJacobiTriple[alpha, n]]},
    recurrenceRows = Append[recurrenceRows, {"finite_Jacobi_product_minus_sum", alpha, n, firstNonzero[diff], maxAbsCoeff[diff]}]
  ],
  {alpha, 0, 1}, {n, 0, NMax}
];

Export[FileNameJoin[{OutDir, "product_transform_candidates.csv"}], candidateRows, "CSV"];
Export[FileNameJoin[{OutDir, "product_transform_residuals.csv"}], residualRows, "CSV"];
Export[FileNameJoin[{OutDir, "product_transform_recurrence.csv"}], recurrenceRows, "CSV"];

bestSchur = SortBy[
  Select[Rest[candidateRows], #[[1]] == "H_alpha_N_minus_schur_gaussian_window" && #[[3]] == NMax &],
  {#[[2]] &, If[IntegerQ[#[[5]]], -#[[5]], -KMax - 1] &}
];

Print["KMax=", KMax];
Print["NMax=", NMax];
Print["H recurrence max residual: ", Max[Last /@ Rest[recurrenceRows]]];
Print["Finite Jacobi identity max residual: ",
  Max[Last /@ Select[Rest[recurrenceRows], #[[1]] == "finite_Jacobi_product_minus_sum" &]]
];
Do[
  Module[{diff = trunc[h[alpha, NMax] - bilateralPlain[alpha]]},
    Print["H alpha=", alpha, " N=", NMax, " minus plain bilateral first nonzero: ", firstNonzero[diff]]
  ],
  {alpha, 0, 1}
];
Do[
  Module[{diff = trunc[h[alpha, NMax] - finiteJacobiTriple[alpha, NMax]]},
    Print["H alpha=", alpha, " N=", NMax, " minus finite Jacobi triple first nonzero: ", firstNonzero[diff]]
  ],
  {alpha, 0, 1}
];
Print["Best Schur-window candidates at NMax:"];
Scan[Print, bestSchur];
Print["Wrote outputs in ", OutDir];
