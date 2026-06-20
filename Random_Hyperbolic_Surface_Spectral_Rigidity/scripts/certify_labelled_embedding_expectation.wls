(* created: 2026-05-15T23:00:00Z
   cycle: 12
   run_id: run-2026-05-15T153635Z
   agent: worker
   milestone: M4-formal-certification *)

ClearAll[falling, normalizeEdge, constraintCounts, formulaExpectation, templateRow];

root = DirectoryName[DirectoryName[$InputFileName]];
outPath = FileNameJoin[{root, "data", "formal_certification", "labelled_embedding_expectation_symbolic.csv"}];

falling[n_, k_] := Product[n - i, {i, 0, k - 1}];

normalizeEdge[{src_, dst_, label_String}] := Module[{lower = ToLowerCase[label]},
  If[label === ToUpperCase[label], {dst, src, lower}, {src, dst, lower}]
];

constraintCounts[edges_] := Module[{normalized, labels, pairs, counts = <||>, failed = False},
  normalized = DeleteDuplicates[normalizeEdge /@ edges];
  If[Length[normalized] == 0, Return[<||>]];
  labels = DeleteDuplicates[normalized[[All, 3]]];
  Do[
    pairs = #[[1 ;; 2]] & /@ Select[normalized, #[[3]] === label &];
    If[Length[DeleteDuplicates[pairs[[All, 1]]]] =!= Length[pairs], failed = True];
    If[Length[DeleteDuplicates[pairs[[All, 2]]]] =!= Length[pairs], failed = True];
    If[failed, Break[]];
    counts[label] = Length[pairs],
    {label, labels}
  ];
  If[failed, Return[$Failed]];
  KeySort[counts]
];

formulaExpectation[vertexCount_, edges_, n_] := Module[{counts, expectation},
  If[IntegerQ[n] && n < vertexCount, Return[0]];
  counts = constraintCounts[edges];
  If[counts === $Failed, Return[0]];
  expectation = falling[n, vertexCount];
  Do[
    expectation = expectation / falling[n, count],
    {count, Values[counts]}
  ];
  FullSimplify[expectation]
];

templates = {
  <|"name" -> "no_edge", "vertices" -> 2, "edges" -> {}, "expected" -> falling[n, 2], "description" -> "two free injective vertices"|>,
  <|"name" -> "single_edge", "vertices" -> 2, "edges" -> {{0, 1, "a"}}, "expected" -> n - 1, "description" -> "one forward labelled edge"|>,
  <|"name" -> "same_label_path", "vertices" -> 3, "edges" -> {{0, 1, "a"}, {1, 2, "a"}}, "expected" -> n - 2, "description" -> "two compatible same-label constraints"|>,
  <|"name" -> "conflicting_domain", "vertices" -> 3, "edges" -> {{0, 1, "a"}, {0, 2, "a"}}, "expected" -> 0, "description" -> "one source forced to two targets"|>,
  <|"name" -> "conflicting_image", "vertices" -> 3, "edges" -> {{1, 0, "a"}, {2, 0, "a"}}, "expected" -> 0, "description" -> "two sources forced to one target"|>,
  <|"name" -> "inverse_edge", "vertices" -> 2, "edges" -> {{0, 1, "A"}}, "expected" -> n - 1, "description" -> "inverse label normalized by reversing orientation"|>,
  <|"name" -> "inverse_regression_pair", "vertices" -> 2, "edges" -> {{0, 1, "a"}, {0, 1, "A"}}, "expected" -> 1, "description" -> "Cycle 8 inverse-label regression case"|>,
  <|"name" -> "eight_word_cyclic_toy", "vertices" -> 8, "edges" -> Table[{i, Mod[i + 1, 8], "a"}, {i, 0, 7}], "expected" -> 1, "description" -> "eight-edge cyclic diagonal quotient"|>,
  <|"name" -> "eight_word_rank2_toy", "vertices" -> 7, "edges" -> {{0, 1, "a"}, {1, 2, "a"}, {2, 3, "a"}, {3, 0, "a"}, {0, 4, "b"}, {4, 5, "b"}, {5, 6, "b"}, {6, 0, "b"}}, "expected" -> falling[n, 7]/falling[n, 4]^2, "description" -> "two four-edge labelled cycles sharing one vertex"|>
};

templateRow[t_] := Module[{expr, expected, counts, checkGeneric, valueAt4, belowValue},
  expr = formulaExpectation[t["vertices"], t["edges"], n];
  expected = t["expected"];
  counts = constraintCounts[t["edges"]];
  checkGeneric = FullSimplify[expr == expected, n >= Max[1, t["vertices"]]];
  valueAt4 = formulaExpectation[t["vertices"], t["edges"], 4];
  belowValue = formulaExpectation[t["vertices"], t["edges"], Max[0, t["vertices"] - 1]];
  {
    t["name"],
    t["vertices"],
    Length[t["edges"]],
    If[counts === $Failed, "conflict", StringRiffle[KeyValueMap[ToString[#1] <> ":" <> ToString[#2] &, counts], " "]],
    ToString[expr, InputForm],
    ToString[expected, InputForm],
    ToString[checkGeneric, InputForm],
    ToString[valueAt4, InputForm],
    ToString[belowValue, InputForm],
    t["description"]
  }
];

rows = templateRow /@ templates;
header = {"template", "vertices", "raw_edges", "constraint_counts", "formula_expression", "expected_expression", "generic_check", "value_at_n4", "value_below_vertex_count", "description"};

checks = ToExpression /@ rows[[All, 7]];
If[!And @@ checks,
  Print[Select[rows, ToExpression[#[[7]]] =!= True &][[All, {1, 5, 6, 7}]] // TableForm];
  Print["symbolic check failed"];
  Exit[1]
];

If[!DirectoryQ[DirectoryName[outPath]], CreateDirectory[DirectoryName[outPath], CreateIntermediateDirectories -> True]];
Export[outPath, Prepend[rows, header], "CSV"];
Print["wrote " <> outPath];
Print["all symbolic special-point checks passed"];
