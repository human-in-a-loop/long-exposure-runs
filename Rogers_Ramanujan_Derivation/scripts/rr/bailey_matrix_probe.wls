(* created: 2026-05-15T02:40:00Z
   cycle: 8
   run_id: run-2026-05-14T232311Z
   agent: worker
   milestone: M2

   Derived Bailey-style triangular matrix diagnostics for the
   Rogers-Ramanujan proof. Optional env vars:
     KMAX=50
     NMAX=12
     OUTDIR=data/finite_experiments
*)

ClearAll["Global`*"];

env[name_, default_] := Module[{v = Environment[name]},
  If[StringQ[v] && StringLength[v] > 0, v, default]
];

workspace = DirectoryName[DirectoryName[DirectoryName[$InputFileName]]];
KMax = ToExpression[env["KMAX", "50"]];
NMax = ToExpression[env["NMAX", "12"]];
OutDir = env["OUTDIR", "data/finite_experiments"];
If[! AbsoluteFileNameQ[OutDir], OutDir = FileNameJoin[{workspace, OutDir}]];
If[! DirectoryQ[OutDir], CreateDirectory[OutDir, CreateIntermediateDirectories -> True]];

qpoch[n_Integer] := Product[1 - q^j, {j, 1, n}];
aqpoch[0, m_Integer] := qpoch[m];
aqpoch[1, m_Integer] := Product[1 - q^(j + 1), {j, 1, m}];

alphaCandidate[0, 0] := 1;
alphaCandidate[0, r_Integer?Positive] := (-1)^r q^(r (3 r - 1)/2) (1 + q^r);
alphaCandidate[1, r_Integer?NonNegative] := (-1)^r q^(r (3 r + 1)/2) Sum[q^j, {j, 0, 2 r}];

betaTarget[n_Integer] := 1/qpoch[n];
matrixEntry[alphaCase_Integer, n_Integer, r_Integer] := 1/(qpoch[n - r] aqpoch[alphaCase, n + r]);

trunc[expr_] := Normal[Series[expr, {q, 0, KMax}]] // Expand;
coeff[poly_, k_Integer] := Coefficient[poly, q, k];
coeffs[poly_] := Table[coeff[poly, k], {k, 0, KMax}];
maxAbsCoeff[poly_] := Max[Abs[coeffs[poly]]];
firstNonzero[poly_] := Module[{ks = Select[Range[0, KMax], coeff[poly, #] != 0 &]},
  If[Length[ks] == 0, "none_through_KMax", First[ks]]
];

clearedNumerator[expr_] := Expand[Numerator[Together[expr]]];

solvedAlpha[alphaCase_Integer, n_Integer, prior_List] := Module[
  {partial},
  partial = Sum[matrixEntry[alphaCase, n, r] prior[[r + 1]], {r, 0, n - 1}];
  FullSimplify[(betaTarget[n] - partial)/matrixEntry[alphaCase, n, n]]
];

alphaRows = {{"alpha_case", "r", "candidate", "solved", "cleared_difference"}};
transformRows = {{"check", "alpha_case", "n", "first_nonzero_k", "max_abs_coeff", "cleared_numerator"}};
limitRows = {{"check", "alpha_case", "r", "partial_s_max", "first_nonzero_k", "max_abs_coeff"}};

Do[
  Module[{prior = {}, solved, diff},
    Do[
      solved = solvedAlpha[alphaCase, n, prior];
      diff = clearedNumerator[solved - alphaCandidate[alphaCase, n]];
      alphaRows = Append[alphaRows, {
        alphaCase,
        n,
        ToString[InputForm[alphaCandidate[alphaCase, n]]],
        ToString[InputForm[FullSimplify[solved]]],
        ToString[InputForm[FullSimplify[diff]]]
      }];
      prior = Append[prior, alphaCandidate[alphaCase, n]]
    ,
      {n, 0, NMax}
    ];
  ],
  {alphaCase, 0, 1}
];

Do[
  Do[
    Module[{diff, cleared},
      diff = Sum[
        matrixEntry[alphaCase, n, r] alphaCandidate[alphaCase, r],
        {r, 0, n}
      ] - betaTarget[n];
      cleared = clearedNumerator[diff];
      transformRows = Append[transformRows, {
        "triangular_pair_residual",
        alphaCase,
        n,
        firstNonzero[trunc[cleared]],
        maxAbsCoeff[trunc[cleared]],
        ToString[InputForm[FullSimplify[cleared]]]
      }]
    ],
    {n, 0, NMax}
  ],
  {alphaCase, 0, 1}
];

innerLimitPartial[alphaCase_Integer, r_Integer, sMax_Integer] := Module[
  {a = If[alphaCase == 0, 1, q], z, partial},
  z = a q^(2 r + 1);
  partial = Sum[
    z^s q^(s (s - 1)) Product[1 - z q^(s + j), {j, 0, KMax + 2}]/qpoch[s],
    {s, 0, sMax}
  ];
  trunc[partial - 1]
];

Do[
  Do[
    Module[{diff = innerLimitPartial[alphaCase, r, KMax + 2]},
      limitRows = Append[limitRows, {
        "inner_limit_qbinomial_residual",
        alphaCase,
        r,
        KMax + 2,
        firstNonzero[diff],
        maxAbsCoeff[diff]
      }]
    ],
    {r, 0, Min[NMax, 6]}
  ],
  {alphaCase, 0, 1}
];

Export[FileNameJoin[{OutDir, "bailey_alpha_solve.csv"}], alphaRows, "CSV"];
Export[FileNameJoin[{OutDir, "bailey_transform_residuals.csv"}], transformRows, "CSV"];
Export[FileNameJoin[{OutDir, "bailey_limit_residuals.csv"}], limitRows, "CSV"];

Print["KMax=", KMax];
Print["NMax=", NMax];
Print["Alpha solve max residual: ",
  Max[If[#[[5]] == "0", 0, 1] & /@ Rest[alphaRows]]
];
Print["Triangular transform max residual: ",
  Max[ToExpression /@ (#[[5]] & /@ Rest[transformRows])]
];
Print["Limit inner residual max coefficient: ",
  Max[#[[6]] & /@ Rest[limitRows]]
];
Print["Wrote outputs in ", OutDir];
