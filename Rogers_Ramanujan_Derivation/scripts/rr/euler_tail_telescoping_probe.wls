(* created: 2026-05-15T01:30:00Z
   cycle: 6
   run_id: run-2026-05-14T232311Z
   agent: worker
   milestone: M2

   Euler-tail double-sum telescoping probe for the Rogers-Ramanujan derivation.
   Optional env vars:
     KMAX=40
     NMAX=16
     DEGMAX=3
     OUTDIR=data/finite_experiments
*)

ClearAll["Global`*"];

env[name_, default_] := Module[{v = Environment[name]},
  If[StringQ[v] && StringLength[v] > 0, v, default]
];

KMax = ToExpression[env["KMAX", "40"]];
NMax = ToExpression[env["NMAX", "16"]];
DegMax = ToExpression[env["DEGMAX", "3"]];
OutDir = env["OUTDIR", "data/finite_experiments"];
If[! DirectoryQ[OutDir], CreateDirectory[OutDir, CreateIntermediateDirectories -> True]];

qpoch[k_Integer] := Product[1 - q^j, {j, 1, k}];
expn[alpha_Integer, n_Integer, k_Integer] := n^2 + alpha n + k n + k (k + 1)/2;
term[alpha_Integer, n_Integer, k_Integer] := (-1)^k q^expn[alpha, n, k]/qpoch[k];
pentagonalExp[alpha_Integer, j_Integer] := j (5 j - (2 alpha + 1))/2;
isPentagonal[alpha_Integer, e_Integer] := Module[{bound = 3 Ceiling[Sqrt[e + 2]] + 6},
  MemberQ[Table[pentagonalExp[alpha, j], {j, -bound, bound}], e]
];

firstNonzeroInPoly[poly_] := Module[{ks = Select[Range[0, KMax], Coefficient[poly, q, #] != 0 &]},
  If[Length[ks] == 0, "none_through_KMax", First[ks]]
];

monomialPairs[deg_Integer] := Flatten[Table[{i, j}, {i, 0, deg}, {j, 0, deg - i}], 1];
polyAnsatz[prefix_String, basis_] := Total[
  MapIndexed[Symbol[prefix <> ToString[First[#2]]] x^#[[1]] y^#[[2]] &, basis]
];

(* Forward divergence normalized by F_alpha(n,k):
   F = (U(n,k)-U(n+1,k)) + (V(n,k)-V(n,k+1)) + R.
   If U=A(q^n,q^k)F and V=B(q^n,q^k)F, then the normalized interior
   divergence is
     A - q^(alpha+1) x^2 y A(q x,y)
     + B + q x y/(1-q y) B(x,q y).
*)
normalizedDivergence[alpha_Integer, a_, b_] := Expand[
  a - q^(alpha + 1) x^2 y (a /. x -> q x)
  + b + q x y/(1 - q y) (b /. y -> q y)
];

solveAnsatz[alpha_Integer, deg_Integer, tag_String, selector_] := Module[
  {basis = Select[monomialPairs[deg], selector], a, b, vars, expr, num, poly,
   equations, sol, status, residual},
  a = polyAnsatz["a" <> ToString[alpha] <> tag, basis];
  b = polyAnsatz["b" <> ToString[alpha] <> tag, basis];
  vars = Join[Variables[a], Variables[b]];
  expr = Together[normalizedDivergence[alpha, a, b] - 1];
  num = Numerator[expr];
  poly = Collect[num, {x, y}, Together];
  equations = DeleteDuplicates[Thread[Flatten[CoefficientList[poly, {x, y}]] == 0]];
  sol = Quiet[Solve[equations, vars]];
  status = If[Length[sol] > 0, "solved", "no_solution"];
  residual = If[Length[sol] > 0,
    Together[expr /. First[sol]],
    Together[expr]
  ];
  {status, Length[basis], Length[vars], Length[equations], residual}
];

candidateRows = {{"alpha", "ansatz", "degree", "basis_terms", "unknowns", "equations", "status", "residual_zero"}};
Do[
 (
  specs = Join[
      {{"total_degree_polynomial", "tot" <> ToString[deg], (True &)}},
      Table[
      With[{aa = alpha, rr = res},
        {"mod5_slice_2n_plus_k_r" <> ToString[rr], "slice" <> ToString[deg] <> "r" <> ToString[rr],
          Function[pair, Mod[2 pair[[1]] + pair[[2]] + aa, 5] == rr]}
      ],
      {res, 0, 4}
    ]
  ];
  Do[
    name = spec[[1]];
    tag = spec[[2]];
    selector = spec[[3]];
    result = solveAnsatz[alpha, deg, tag, selector];
    candidateRows = Append[
      candidateRows,
      {alpha, name, deg, result[[2]], result[[3]], result[[4]], result[[1]], If[Together[Last[result]] === 0, "yes", "no"]}
    ];
    ,
    {spec, specs}
  ]
 ),
  {alpha, 0, 1}, {deg, 0, DegMax}
];

(* Finite lattice diagnostics: truncate the Euler-tail double sum and compare
   support against the corrected bilateral pentagonal exponents. *)
termsRows = {{"alpha", "n", "k", "exponent", "sign", "denominator_degree", "linear_mod5_2n_plus_k_alpha", "is_pentagonal_exponent"}};
Do[
  Do[
    Do[
      e = expn[alpha, n, k];
      If[e <= KMax,
        termsRows = Append[termsRows, {alpha, n, k, e, (-1)^k, k (k + 1)/2, Mod[2 n + k + alpha, 5], If[isPentagonal[alpha, e], 1, 0]}]
      ],
      {k, 0, NMax}
    ],
    {n, 0, NMax}
  ],
  {alpha, 0, 1}
];

residualRows = {{"alpha", "degree", "double_sum_coeff", "bilateral_coeff", "residual", "is_pentagonal_degree"}};
Do[
  partial = Normal[Series[Sum[term[alpha, n, k], {n, 0, NMax}, {k, 0, NMax}], {q, 0, KMax}]] // Expand;
  bound = Ceiling[Sqrt[2 KMax/5]] + 6;
  bilateral = Normal[Series[Sum[(-1)^j q^pentagonalExp[alpha, j], {j, -bound, bound}], {q, 0, KMax}]] // Expand;
  Do[
    residualRows = Append[
      residualRows,
      {alpha, degree, Coefficient[partial, q, degree], Coefficient[bilateral, q, degree],
       Coefficient[partial - bilateral, q, degree], If[isPentagonal[alpha, degree], 1, 0]}
    ],
    {degree, 0, KMax}
  ];
  ,
  {alpha, 0, 1}
];

Export[FileNameJoin[{OutDir, "euler_tail_terms.csv"}], termsRows, "CSV"];
Export[FileNameJoin[{OutDir, "euler_tail_certificate_candidates.csv"}], candidateRows, "CSV"];
Export[FileNameJoin[{OutDir, "euler_tail_residuals.csv"}], residualRows, "CSV"];

Print["KMax=", KMax];
Print["NMax=", NMax];
Print["DegMax=", DegMax];
Print["Certificate candidates tested: ", Length[candidateRows] - 1];
Print["Solved candidates: ", Count[Rest[candidateRows][[All, 7]], "solved"]];
Do[
  row = Select[Rest[residualRows], #[[1]] == alpha && #[[5]] != 0 &];
  Print["alpha=", alpha, " partial double sum minus bilateral first nonzero: ",
    If[Length[row] == 0, "none_through_KMax", row[[1, 2]]]
  ];
  ,
  {alpha, 0, 1}
];
Print["Wrote outputs in ", OutDir];
