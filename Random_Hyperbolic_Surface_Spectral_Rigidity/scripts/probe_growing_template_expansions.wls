(* created: 2026-05-16T01:20:00Z *)
(* cycle: 15 *)
(* run_id: run-2026-05-15T153635Z *)
(* agent: worker *)
(* milestone: M5-extension-candidates *)

ClearAll[repoRoot, coeffPath, summaryPath, n, x, falling, normalizedExpression,
  multiplyTruncated, factorCoefficients, inverseFactorCoefficients,
  profileRows, coeffRows, summaryRows, nearestScale, coefficientList];

repoRoot = DirectoryName[DirectoryName[$InputFileName]];
coeffPath = FileNameJoin[{repoRoot, "data", "extension_candidates",
    "growing_template_expansion_coefficients.csv"}];
summaryPath = FileNameJoin[{repoRoot, "data", "extension_candidates",
    "growing_template_expansion_summary.csv"}];

maxL = 40;
maxOrder = 8;

falling[n_, k_Integer?NonNegative] := Product[n - j, {j, 0, k - 1}];

profileRows[] := Module[{rows = {}, l, k, s},
   For[l = 1, l <= maxL, l++,
    AppendTo[rows, <|"family" -> "single_label_cycle_profile",
      "L" -> l, "V" -> l, "counts" -> {l},
      "description" -> "V=L and one label with L constraints; normalized expectation is exactly 1"|>];
    AppendTo[rows, <|"family" -> "single_label_path_profile",
      "L" -> l, "V" -> l + 1, "counts" -> {l},
      "description" -> "V=L+1 and one label with L constraints; normalized expectation is exactly 1-L x"|>];
    AppendTo[rows, <|"family" -> "rank2_balanced_profile",
      "L" -> l, "V" -> 2 l - 1, "counts" -> {l, l},
      "description" -> "two length-L labels sharing one vertex"|>];
    For[k = 2, k <= 3, k++,
     If[2 l - k >= 1,
      AppendTo[rows, <|"family" -> "rank2_deficit_k" <> ToString[k],
        "L" -> l, "V" -> 2 l - k, "counts" -> {l, l},
        "description" -> "two length-L labels with fixed vertex deficit k=" <> ToString[k]|>]
      ]
     ];
    For[s = 3, s <= 4, s++,
     If[4 l - s >= 1,
      AppendTo[rows, <|"family" -> "rank4_delocalization_toy_s" <> ToString[s],
        "L" -> l, "V" -> 4 l - s, "counts" -> {l, l, l, l},
        "description" -> "four-label fourth-moment toy profile with fixed deficit s=" <> ToString[s]|>]
      ]
     ];
    ];
   rows
   ];

normalizedExpression[p_] := Module[{v, counts, c},
   v = p["V"];
   counts = p["counts"];
   c = Total[counts];
   n^(c - v) falling[n, v]/Times @@ (falling[n, #] & /@ counts)
   ];

multiplyTruncated[a_, b_] := Table[
   Sum[a[[i + 1]] b[[r - i + 1]], {i, 0, r}],
   {r, 0, maxOrder}
   ];

factorCoefficients[j_Integer] := Join[{1, -j}, ConstantArray[0, maxOrder - 1]];

inverseFactorCoefficients[j_Integer] := Table[j^r, {r, 0, maxOrder}];

coefficientList[p_] := Module[{v, counts, coeffs, j, c},
   v = p["V"];
   counts = p["counts"];
   coeffs = Join[{1}, ConstantArray[0, maxOrder]];
   For[j = 1, j <= v - 1, j++,
    coeffs = multiplyTruncated[coeffs, factorCoefficients[j]]
    ];
   Do[
    For[j = 1, j <= c - 1, j++,
     coeffs = multiplyTruncated[coeffs, inverseFactorCoefficients[j]]
     ],
    {c, counts}
    ];
   coeffs
   ];

nearestScale[p_] := Module[{v, counts, maxRaw},
   v = p["V"];
   counts = p["counts"];
   maxRaw = Max[Join[{0, v - 1}, counts - 1]];
   If[p["family"] == "single_label_cycle_profile" || maxRaw <= 0, "",
    ToString[InputForm[1/maxRaw]]]
   ];

coeffRows[profiles_] := Flatten[
   Function[p,
     Module[{expr, coeffs, countsText, l1},
      expr = normalizedExpression[p];
      coeffs = coefficientList[p];
      countsText = StringRiffle[ToString /@ p["counts"], ";"];
      l1 = Total[Abs[coeffs]];
      Table[
       {
        p["family"], p["L"], p["V"], countsText, order,
        ToString[InputForm[coeffs[[order + 1]]]],
        ToString[InputForm[Abs[coeffs[[order + 1]]]]],
        ToString[InputForm[Factorial[order] coeffs[[order + 1]]]],
        ToString[InputForm[l1]],
        nearestScale[p],
        ToString[InputForm[expr]],
        p["description"]
        },
       {order, 0, maxOrder}
       ]
      ]
     ] /@ profiles,
   1];

summaryRows[profiles_] := Function[p,
    Module[{expr, coeffs, countsText, l1, maxAbs, maxDeriv},
     expr = normalizedExpression[p];
     coeffs = coefficientList[p];
     countsText = StringRiffle[ToString /@ p["counts"], ";"];
     l1 = Total[Abs[coeffs]];
     maxAbs = Max[Abs[coeffs]];
     maxDeriv = Max[Abs[Table[Factorial[r] coeffs[[r + 1]], {r, 0, maxOrder}]]];
     {
      p["family"], p["L"], p["V"], countsText, Total[p["counts"]],
      ToString[InputForm[l1]], ToString[InputForm[maxAbs]],
      ToString[InputForm[maxDeriv]], nearestScale[p],
      ToString[InputForm[normalizedExpression[p]]],
      p["description"]
      }
     ]
    ] /@ profiles;

profiles = profileRows[];

If[! DirectoryQ[DirectoryName[coeffPath]],
  CreateDirectory[DirectoryName[coeffPath], CreateIntermediateDirectories -> True]
  ];

coeffHeader = {"family", "L", "V", "constraint_counts", "order", "coefficient",
   "abs_coefficient", "derivative_at_zero", "coefficient_l1_norm_order_leq_8",
   "nearest_singularity_scale", "normalized_expression_n", "description"};
summaryHeader = {"family", "L", "V", "constraint_counts", "constraint_total",
   "coefficient_l1_norm_order_leq_8", "max_abs_coefficient_order_leq_8",
   "max_abs_derivative_order_leq_8", "nearest_singularity_scale",
   "normalized_expression_n", "description"};

Export[coeffPath, Prepend[coeffRows[profiles], coeffHeader], "CSV"];
Export[summaryPath, Prepend[summaryRows[profiles], summaryHeader], "CSV"];

If[! FileExistsQ[coeffPath] || ! FileExistsQ[summaryPath],
  Print["failed to write growing-template outputs"]; Exit[1]];
Print["wrote ", coeffPath];
Print["wrote ", summaryPath];
Print["expanded ", Length[profiles], " growing-template profiles through x^", maxOrder];
