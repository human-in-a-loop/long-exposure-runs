(* created: 2026-05-15T01:05:00Z
   cycle: 5
   run_id: run-2026-05-14T232311Z
   agent: worker-clone-0
   milestone: M2

   Nonlocal subset-sum transfer diagnostics for transformed signed objects.
   Optional env vars:
     KMAX=40
     NMAX=12
     OUTDIR=data/finite_experiments
*)

ClearAll["Global`*"];

env[name_, default_] := Module[{v = Environment[name]},
  If[StringQ[v] && StringLength[v] > 0, v, default]
];

KMax = ToExpression[env["KMAX", "40"]];
NMax = ToExpression[env["NMAX", "12"]];
OutDir = env["OUTDIR", "data/finite_experiments"];
If[! DirectoryQ[OutDir], CreateDirectory[OutDir, CreateIntermediateDirectories -> True]];
nVals = If[env["ALL_N", "0"] == "1", Range[0, NMax], {NMax}];

weight[alpha_Integer, n_Integer, s_List] := n^2 + alpha n + Total[s];
sgn[s_List] := (-1)^Length[s];
setString[s_List] := If[Length[s] == 0, "{}", "{" <> StringRiffle[ToString /@ Sort[s], ";"] <> "}"];
pentagonalExponent[alpha_Integer, j_Integer] := j (5 j - (2 alpha + 1))/2;
predictedQ[alpha_Integer, k_Integer] := Length[Select[Range[-NMax - 5, NMax + 5], pentagonalExponent[alpha, #] == k &]] > 0;

lexKeyDescending[s_List] := Reverse[Sort[s, Greater]];
chooseSubset[subsets_List, tie_String] := Module[{sorted},
  sorted = SortBy[subsets, lexKeyDescending];
  If[tie == "lex_largest", Last[sorted], First[sorted]]
];

subsetSums[list_List, target_Integer] := Module[{xs = Sort[list], rec},
  rec[_, 0] := {{}};
  rec[{}, t_] := If[t == 0, {{}}, {}];
  rec[ys_List, t_] := Module[{x = First[ys], rest = Rest[ys], without, with},
    If[t < 0, Return[{}]];
    without = rec[rest, t];
    with = If[x <= t, Prepend[#, x] & /@ rec[rest, t - x], {}];
    Join[without, with]
  ];
  rec[xs, target]
];

objectsFor[alpha_Integer, nmax_Integer] := Module[{rows = {}, base, allowed, subsets},
  Do[
    base = n^2 + alpha n;
    If[base <= KMax,
      allowed = Range[n + 1, nmax];
      subsets = Select[Subsets[allowed], base + Total[#] <= KMax &];
      rows = Join[rows, ({alpha, nmax, n, Sort[#], weight[alpha, n, #], sgn[#]} & /@ subsets)];
    ],
    {n, 0, nmax}
  ];
  rows
];

upMoves[alpha_Integer, nmax_Integer, n_Integer, s_List] := Module[
  {moves = {}, forced, optional, delta, valid},
  Do[
    delta = r (2 n + alpha + r);
    forced = Select[s, # <= n + r &];
    optional = Select[s, # > n + r &];
    If[Total[forced] <= delta,
      valid = Select[subsetSums[optional, delta - Total[forced]], OddQ[Length[Join[forced, #]]] &];
      moves = Join[moves, ({r, "up", Sort[Join[forced, #]]} & /@ valid)];
    ],
    {r, 1, nmax - n}
  ];
  moves
];

downMoves[alpha_Integer, nmax_Integer, n_Integer, s_List] := Module[
  {moves = {}, pool, delta, valid},
  Do[
    delta = r (2 n + alpha - r);
    pool = Complement[Range[n - r + 1, nmax], s];
    valid = Select[subsetSums[pool, delta], OddQ[Length[#]] &];
    moves = Join[moves, ({r, "down", Sort[#]} & /@ valid)],
    {r, 1, n}
  ];
  moves
];

canonicalMove[alpha_Integer, nmax_Integer, n_Integer, s_List, tie_String] := Module[
  {moves, minR, atR, upAtR, downAtR, chosen, a, newN, newS},
  moves = Join[upMoves[alpha, nmax, n, s], downMoves[alpha, nmax, n, s]];
  If[Length[moves] == 0, Return[Missing["NoMove"]]];
  minR = Min[moves[[All, 1]]];
  atR = Select[moves, #[[1]] == minR &];
  upAtR = Select[atR, #[[2]] == "up" &];
  downAtR = Select[atR, #[[2]] == "down" &];
  (* Prefer absorption when both directions are available at the same minimal r.
     This is deterministic; if it creates a failure, the failure table records it. *)
  If[Length[upAtR] > 0,
    chosen = {minR, "up", chooseSubset[upAtR[[All, 3]], tie]},
    chosen = {minR, "down", chooseSubset[downAtR[[All, 3]], tie]}
  ];
  a = chosen[[3]];
  If[chosen[[2]] == "up",
    newN = n + minR; newS = Sort[Complement[s, a]],
    newN = n - minR; newS = Sort[Union[s, a]]
  ];
  {newN, newS, chosen[[2]], minR, a, Length[atR], Length[upAtR], Length[downAtR]}
];

classifyObject[alpha_Integer, nmax_Integer, n_Integer, s_List, tie_String] := Module[
  {w, move, newN, newS, back, class, detail},
  w = weight[alpha, n, s];
  move = canonicalMove[alpha, nmax, n, s, tie];
  If[Head[move] === Missing,
    class = If[predictedQ[alpha, w], "fixed_predicted", "no_admissible_move"];
    Return[{class, "", "", "", "", "", "", ""}];
  ];
  newN = move[[1]]; newS = move[[2]];
  If[weight[alpha, newN, newS] != w, Return[{"weight_failure", newN, setString[newS], move[[3]], move[[4]], setString[move[[5]]], move[[6]], "weight changed"}]];
  If[sgn[newS] == sgn[s], Return[{"sign_failure", newN, setString[newS], move[[3]], move[[4]], setString[move[[5]]], move[[6]], "sign did not change"}]];
  If[! AllTrue[newS, # > newN &], Return[{"tail_condition_failure", newN, setString[newS], move[[3]], move[[4]], setString[move[[5]]], move[[6]], "new tail contains forbidden part"}]];
  back = canonicalMove[alpha, nmax, newN, newS, tie];
  If[Head[back] === Missing || back[[1]] != n || back[[2]] != s,
    detail = If[Head[back] === Missing, "back move missing", "back maps to n=" <> ToString[back[[1]]] <> ",S=" <> setString[back[[2]]]];
    Return[{"involution_failure", newN, setString[newS], move[[3]], move[[4]], setString[move[[5]]], move[[6]], detail}];
  ];
  {If[move[[3]] == "up", "paired_up", "paired_down"], newN, setString[newS], move[[3]], move[[4]], setString[move[[5]]], move[[6]], "ok"}
];

candidateRows = {{"tie_breaker", "alpha", "N", "n", "S", "S_size", "sign", "exponent", "classification", "candidate_n", "candidate_S", "direction", "r", "transfer_subset", "moves_at_min_r", "detail"}};
failureRows = {{"tie_breaker", "alpha", "N", "n", "S", "S_size", "sign", "exponent", "classification", "candidate_n", "candidate_S", "direction", "r", "transfer_subset", "moves_at_min_r", "detail"}};
fixedRows = {{"tie_breaker", "alpha", "N", "n", "S", "S_size", "sign", "exponent", "classification", "predicted_pentagonal"}};
summaryRows = {{"tie_breaker", "alpha", "N", "objects", "paired_up", "paired_down", "fixed_predicted", "no_admissible_move", "involution_failure", "weight_failure", "sign_failure", "tail_condition_failure"}};

Do[
  rows = objectsFor[alpha, nmax];
  Do[
    counts = AssociationThread[{"paired_up", "paired_down", "fixed_predicted", "no_admissible_move", "involution_failure", "weight_failure", "sign_failure", "tail_condition_failure"}, ConstantArray[0, 8]];
    Do[
      n = row[[3]]; s = row[[4]]; w = row[[5]];
      cls = classifyObject[alpha, nmax, n, s, tie];
      counts[cls[[1]]] = counts[cls[[1]]] + 1;
      out = {tie, alpha, nmax, n, setString[s], Length[s], row[[6]], w, cls[[1]], cls[[2]], cls[[3]], cls[[4]], cls[[5]], cls[[6]], cls[[7]], cls[[8]]};
      candidateRows = Append[candidateRows, out];
      If[! MemberQ[{"paired_up", "paired_down", "fixed_predicted"}, cls[[1]]] && Length[failureRows] < 500,
        failureRows = Append[failureRows, out]
      ];
      If[MemberQ[{"fixed_predicted", "no_admissible_move"}, cls[[1]]],
        fixedRows = Append[fixedRows, {tie, alpha, nmax, n, setString[s], Length[s], row[[6]], w, cls[[1]], predictedQ[alpha, w]}]
      ],
      {row, rows}
    ];
    summaryRows = Append[summaryRows, Join[{tie, alpha, nmax, Length[rows]}, Lookup[counts, {"paired_up", "paired_down", "fixed_predicted", "no_admissible_move", "involution_failure", "weight_failure", "sign_failure", "tail_condition_failure"}]]],
    {tie, {"lex_largest", "lex_smallest"}}
  ],
  {alpha, 0, 1}, {nmax, nVals}
];

Export[FileNameJoin[{OutDir, "nonlocal_involution_candidates.csv"}], candidateRows, "CSV"];
Export[FileNameJoin[{OutDir, "nonlocal_involution_failures.csv"}], failureRows, "CSV"];
Export[FileNameJoin[{OutDir, "nonlocal_involution_fixed_points.csv"}], fixedRows, "CSV"];
Export[FileNameJoin[{OutDir, "nonlocal_involution_summary.csv"}], summaryRows, "CSV"];

Print["KMax=", KMax];
Print["NMax=", NMax];
Print["Summary at NMax:"];
Scan[Print, Select[Rest[summaryRows], #[[3]] == NMax &]];
Print["First failures:"];
Scan[Print, Take[Rest[failureRows], UpTo[12]]];
Print["Wrote outputs in ", OutDir];
