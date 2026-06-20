(* created: 2026-05-15T01:05:00Z
   cycle: fork-88b3b9161814-clone-1
   run_id: run-2026-05-14T232311Z
   agent: worker-clone-1
   milestone: M2

   Recurrence-only modulo-5 / shifted-state diagnostics for
   H_{alpha,N}. This script does not use product-side coefficients to
   compute H; the bilateral sequence is used only as a final defect check.

   Optional env vars:
     KMAX=50
     NMAX=60
     OUTDIR=data/finite_experiments
     WMAX=12
*)

ClearAll["Global`*"];

env[name_, default_] := Module[{v = Environment[name]},
  If[StringQ[v] && StringLength[v] > 0, v, default]
];

KMax = ToExpression[env["KMAX", "50"]];
NMax = ToExpression[env["NMAX", ToString[KMax + 10]]];
WMax = ToExpression[env["WMAX", "12"]];
OutDir = env["OUTDIR", "data/finite_experiments"];
If[! DirectoryQ[OutDir], CreateDirectory[OutDir, CreateIntermediateDirectories -> True]];

hCoeff[alpha_Integer, n_Integer, k_Integer] /; k < 0 := 0;
hCoeff[alpha_Integer, n_Integer, k_Integer] /; n < 0 := 0;

Do[
  hCoeff[alpha, 0, k] = If[k == 0, 1, 0],
  {alpha, 0, 1}, {k, 0, KMax}
];

Do[
  hCoeff[alpha, n, k] =
    hCoeff[alpha, n - 1, k]
    - hCoeff[alpha, n - 1, k - n]
    + If[k == n^2 + alpha n, 1, 0],
  {alpha, 0, 1}, {n, 1, NMax}, {k, 0, KMax}
];

bilateralExponent[alpha_Integer, j_Integer] := j (5 j - (2 alpha + 1))/2;

predictedCoeff[alpha_Integer, k_Integer] := Module[
  {bound = Ceiling[Sqrt[2 KMax/5]] + 6},
  Sum[If[bilateralExponent[alpha, j] == k, (-1)^j, 0], {j, -bound, bound}]
];

predictedJs[alpha_Integer, k_Integer] := Module[
  {bound = Ceiling[Sqrt[2 KMax/5]] + 6, js},
  js = Select[Range[-bound, bound], bilateralExponent[alpha, #] == k &];
  If[Length[js] == 0, "", StringRiffle[ToString /@ js, ";"]]
];

region[n_Integer, k_Integer] := Which[
  k <= n, "stable_or_low",
  k <= 2 n, "boundary",
  True, "far"
];

stableAt[alpha_Integer, k_Integer] := hCoeff[alpha, Min[NMax, k + 1], k];

stateRows = {{"alpha", "N", "k", "h_alpha_N_k", "stable_c_alpha_k", "predicted_b_alpha_k", "defect", "N_mod_5", "k_mod_5", "offset_d_k_minus_N", "region", "predicted_j_values"}};

Do[
  c = stableAt[alpha, k];
  b = predictedCoeff[alpha, k];
  Do[
    stateRows = Append[
      stateRows,
      {alpha, n, k, hCoeff[alpha, n, k], c, b, c - b, Mod[n, 5], Mod[k, 5], k - n, region[n, k], predictedJs[alpha, k]}
    ],
    {n, 0, NMax}
  ],
  {alpha, 0, 1}, {k, 0, KMax}
];

transitionRows = {{"check", "alpha", "N", "d", "N_mod_5", "d_mod_5", "lhs", "rhs", "residual", "comment"}};

Do[
  lhs = hCoeff[alpha, n, n + d];
  rhs = hCoeff[alpha, n - 1, n + d]
    - hCoeff[alpha, n - 1, d]
    + If[d == n^2 + (alpha - 1) n, 1, 0];
  transitionRows = Append[
    transitionRows,
    {"diagonal_one_step", alpha, n, d, Mod[n, 5], Mod[d, 5], lhs, rhs, lhs - rhs, "T_N(d)=T_{N-1}(d+1)-h_{N-1}(d)+source"}
  ],
  {alpha, 0, 1}, {n, 1, NMax}, {d, 0, Min[WMax, KMax - n]}
];

Do[
  If[n >= 5 && n + d <= KMax,
    lhs = hCoeff[alpha, n, n + d];
    rhs = hCoeff[alpha, n - 5, n + d]
      - Sum[hCoeff[alpha, n - 1 - i, d + i], {i, 0, 4}]
      + Sum[If[d + i == (n - i)^2 + (alpha - 1) (n - i), 1, 0], {i, 0, 4}];
    transitionRows = Append[
      transitionRows,
      {"diagonal_five_step", alpha, n, d, Mod[n, 5], Mod[d, 5], lhs, rhs, lhs - rhs, "five-step expansion shifts terminal offset from d to d+5"}
    ];
  ],
  {alpha, 0, 1}, {n, 5, NMax}, {d, 0, Min[WMax, KMax - n]}
];

failureRows = {{"failure_type", "alpha", "N", "k_or_d", "value", "detail"}};

Do[
  If[k <= KMax && k <= NMax,
    Do[
      If[hCoeff[alpha, k, k] != stableAt[alpha, k],
        failureRows = Append[
          failureRows,
          {"N_equals_k_not_stable", alpha, k, k, hCoeff[alpha, k, k] - stableAt[alpha, k],
            "stabilization begins at N>k because the -q^N H_{N-1} term can change degree k"}
        ]
      ],
      {alpha, 0, 1}
    ]
  ],
  {k, 0, Min[KMax, NMax]}
];

Do[
  If[WMax + 1 <= KMax - n,
    failureRows = Append[
      failureRows,
      {"finite_offset_window_not_closed", alpha, n, WMax, hCoeff[alpha, n - 1, n + WMax],
        "one-step diagonal update for d=WMax requires T_{N-1}(WMax+1), outside the tracked finite window"}
    ]
  ],
  {alpha, 0, 1}, {n, 1, Min[NMax, KMax - WMax - 1]}
];

Do[
  c = stableAt[alpha, k];
  b = predictedCoeff[alpha, k];
  If[c != b,
    failureRows = Append[
      failureRows,
      {"stable_defect_nonzero", alpha, "", k, c - b, "recurrence-generated stable coefficient differs from predicted bilateral coefficient"}
    ]
  ],
  {alpha, 0, 1}, {k, 0, KMax}
];

Export[FileNameJoin[{OutDir, "mod5_state_tables.csv"}], stateRows, "CSV"];
Export[FileNameJoin[{OutDir, "mod5_transition_candidates.csv"}], transitionRows, "CSV"];
Export[FileNameJoin[{OutDir, "mod5_state_failures.csv"}], failureRows, "CSV"];

diagResidualMax = Max[Abs[Rest[transitionRows][[All, 9]]]];
defectRows = Select[Rest[failureRows], #[[1]] == "stable_defect_nonzero" &];
windowRows = Select[Rest[failureRows], #[[1]] == "finite_offset_window_not_closed" &];
notStableRows = Select[Rest[failureRows], #[[1]] == "N_equals_k_not_stable" &];

Print["KMax=", KMax];
Print["NMax=", NMax];
Print["WMax=", WMax];
Print["Diagonal recurrence max residual: ", diagResidualMax];
Print["Stable defects against corrected bilateral target: ", If[Length[defectRows] == 0, "none_through_KMax", Take[defectRows, UpTo[10]]]];
Print["N=k non-stability examples: ", Take[notStableRows, UpTo[10]]];
Print["Finite offset window obstruction rows: ", Length[windowRows]];
Print["Wrote outputs in ", OutDir];
