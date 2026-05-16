(* created: 2026-05-16T00:20:00Z *)
(* cycle: 14 *)
(* run_id: run-2026-05-15T153635Z *)
(* agent: worker *)
(* milestone: M5-extension-candidates *)

ClearAll[repoRoot, outPath, n, x, falling, normalizedExpression, coeffRow];

repoRoot = DirectoryName[DirectoryName[$InputFileName]];
outPath = FileNameJoin[{repoRoot, "data", "extension_candidates",
    "labelled_embedding_expansion_coefficients.csv"}];

falling[n_, k_Integer?NonNegative] := Product[n - j, {j, 0, k - 1}];

templates = {
   <|"template" -> "no_edge_control", "vertices" -> 2, "counts" -> {},
    "conflict" -> False, "description" -> "two free injective vertices"|>,
   <|"template" -> "single_edge_control", "vertices" -> 2, "counts" -> {1},
    "conflict" -> False, "description" -> "one forward labelled edge"|>,
   <|"template" -> "single_label_cycle", "vertices" -> 1, "counts" -> {1},
    "conflict" -> False, "description" -> "one labelled loop"|>,
   <|"template" -> "trace_pair_toy", "vertices" -> 3, "counts" -> {2, 2},
    "conflict" -> False, "description" -> "two trace-side cycles sharing a base vertex"|>,
   <|"template" -> "eight_word_cyclic_toy", "vertices" -> 8, "counts" -> {8},
    "conflict" -> False, "description" -> "eight-edge cyclic diagonal quotient"|>,
   <|"template" -> "eight_word_rank2_toy", "vertices" -> 7, "counts" -> {4, 4},
    "conflict" -> False, "description" -> "two four-edge labelled cycles sharing one vertex"|>,
   <|"template" -> "conflicting_domain", "vertices" -> 3, "counts" -> {},
    "conflict" -> True, "description" -> "one source forced to two targets"|>
   };

normalizedExpression[t_] := Module[{v, counts, c},
   If[TrueQ[t["conflict"]], Return[0]];
   v = t["vertices"];
   counts = t["counts"];
   c = Total[counts];
   FullSimplify[n^(c - v) falling[n, v]/Times @@ (falling[n, #] & /@ counts)]
   ];

coeffRow[t_] := Module[{exprN, exprX, series, coeffs, countsText},
   exprN = normalizedExpression[t];
   exprX = FullSimplify[exprN /. n -> 1/x];
   series = Normal[Series[exprX, {x, 0, 4}]];
   coeffs = Coefficient[series, x, #] & /@ Range[0, 4];
   countsText = If[Length[t["counts"]] == 0, "",
     StringRiffle[ToString /@ t["counts"], ";"]];
   Join[
    {
     t["template"],
     t["vertices"],
     Total[t["counts"]],
     countsText,
     ToString[InputForm[exprN]],
     ToString[InputForm[exprX]],
     ToString[InputForm[series]],
     If[TrueQ[t["conflict"]], "true", "false"],
     t["description"]
     },
    ToString[InputForm[#]] & /@ coeffs
    ]
   ];

header = {"template", "vertices", "constraint_total", "constraint_counts",
   "normalized_expression_n", "normalized_expression_x", "series_order4",
   "conflict", "description", "coeff_0", "coeff_1", "coeff_2",
   "coeff_3", "coeff_4"};

If[! DirectoryQ[DirectoryName[outPath]],
  CreateDirectory[DirectoryName[outPath], CreateIntermediateDirectories -> True]
  ];
Export[outPath, Prepend[coeffRow /@ templates, header], "CSV"];

If[! FileExistsQ[outPath], Print["failed to write ", outPath]; Exit[1]];
Print["wrote ", outPath];
Print["expanded ", Length[templates], " labelled-template observables through x^4"];
