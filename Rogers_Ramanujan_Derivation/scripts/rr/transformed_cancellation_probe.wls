(* created: 2026-05-15T00:45:00Z
   cycle: 4
   run_id: run-2026-05-14T232311Z
   agent: worker
   milestone: M2

   Signed-object diagnostics for transformed Rogers-Ramanujan sums.
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

weight[alpha_Integer, n_Integer, s_List] := n^2 + alpha n + Total[s];
sign[s_List] := (-1)^Length[s];
setString[s_List] := If[Length[s] == 0, "{}", "{" <> StringRiffle[ToString /@ s, ";"] <> "}"];
pentagonalExponent[alpha_Integer, j_Integer] := j (5 j - (2 alpha + 1))/2;

objectsFor[alpha_Integer, nmax_Integer] := Module[{rows = {}, base, allowed, subsets},
  Do[
    base = n^2 + alpha n;
    If[base <= KMax,
      allowed = Range[n + 1, nmax];
      subsets = Select[Subsets[allowed], base + Total[#] <= KMax &];
      rows = Join[
        rows,
        ({alpha, nmax, n, setString[#], Length[#], sign[#], weight[alpha, n, #]} & /@ subsets)
      ];
    ],
    {n, 0, nmax}
  ];
  rows
];

allObjectRows = Flatten[Table[objectsFor[alpha, nmax], {alpha, 0, 1}, {nmax, 0, NMax}], 2];
objectHeader = {"alpha", "N", "n", "S", "S_size", "sign", "exponent"};

coefficientRows = {{"alpha", "N", "exponent", "signed_coefficient", "positive_count", "negative_count", "is_pentagonal_exponent", "pentagonal_j_values"}};
survivorRows = {{"alpha", "N", "j", "exponent", "target_sign", "signed_coefficient", "object_count", "canonical_object"}};

Do[
  rows = Select[allObjectRows, #[[1]] == alpha && #[[2]] == nmax &];
  Do[
    atK = Select[rows, #[[7]] == k &];
    coeff = Total[atK[[All, 6]] /. {} -> {0}];
    pos = Count[atK[[All, 6]], 1];
    neg = Count[atK[[All, 6]], -1];
    js = Select[Range[-nmax - 2, nmax + 2], pentagonalExponent[alpha, #] == k &];
    coefficientRows = Append[
      coefficientRows,
      {alpha, nmax, k, coeff, pos, neg, Length[js] > 0, StringRiffle[ToString /@ js, ";"]}
    ],
    {k, 0, KMax}
  ];
  Do[
    exp = pentagonalExponent[alpha, j];
    If[0 <= exp <= KMax,
      atExp = Select[rows, #[[7]] == exp &];
      coeff = Total[atExp[[All, 6]] /. {} -> {0}];
      survivorRows = Append[
        survivorRows,
        {alpha, nmax, j, exp, (-1)^j, coeff, Length[atExp],
          If[Length[atExp] == 0, "none", "n=" <> ToString[atExp[[1, 3]]] <> ",S=" <> atExp[[1, 4]]]}
      ];
    ],
    {j, -nmax - 2, nmax + 2}
  ],
  {alpha, 0, 1}, {nmax, 0, NMax}
];

(* A deliberately narrow local move search.
   Increase n by r only if the selected elements at or below the new boundary
   have exactly the necessary base-weight difference and odd cardinality.
   Decrease n by r only if the missing elements between the new and old boundary
   have exactly the released base-weight difference and odd cardinality.
   This tests the natural "absorb/release boundary block" family; failures are
   obstructions to that family, not to all possible involutions. *)

parseSet[str_String] := If[str == "{}", {}, ToExpression[StringSplit[StringTrim[str, {"{", "}"}], ";"]]];

candidateMove[alpha_Integer, nmax_Integer, n_Integer, s_List] := Module[
  {incCandidates, decCandidates, r, forced, delta, newS, add, newN},
  incCandidates = Reap[
    Do[
      forced = Select[s, # <= n + r &];
      delta = r (2 n + alpha + r);
      If[Total[forced] == delta && OddQ[Length[forced]] && AllTrue[newS = Complement[s, forced], # > n + r &],
        Sow[{n + r, Sort[newS], "increase", r, forced}]
      ],
      {r, 1, nmax - n}
    ]
  ][[2]];
  If[Length[incCandidates] > 0, Return[First[First[incCandidates]]]];

  decCandidates = Reap[
    Do[
      newN = n - r;
      add = Complement[Range[newN + 1, n], s];
      delta = r (2 n + alpha - r);
      If[Total[add] == delta && OddQ[Length[add]] && AllTrue[Join[s, add], # > newN &],
        Sow[{newN, Sort[Join[s, add]], "decrease", r, add}]
      ],
      {r, 1, n}
    ]
  ][[2]];
  If[Length[decCandidates] > 0, Return[First[First[decCandidates]]]];
  Missing["NoMove"]
];

failureRows = {{"alpha", "N", "n", "S", "exponent", "failure_type", "candidate_n", "candidate_S", "detail"}};
pairSummaryRows = {{"alpha", "N", "objects_tested", "paired", "unpaired", "not_involutive", "not_weight_preserving", "not_sign_reversing"}};

Do[
  rows = Select[allObjectRows, #[[1]] == alpha && #[[2]] == nmax &];
  paired = 0; unpaired = 0; notInv = 0; notWt = 0; notSign = 0;
  Do[
    n = row[[3]]; s = parseSet[row[[4]]]; w = row[[7]];
    move = candidateMove[alpha, nmax, n, s];
    If[Head[move] === Missing,
      unpaired++;
      If[Length[failureRows] < 200,
        failureRows = Append[failureRows, {alpha, nmax, n, row[[4]], w, "no_local_absorb_release_move", "", "", "hard-filter found no boundary move"}]
      ],
      newN = move[[1]]; newS = move[[2]];
      back = candidateMove[alpha, nmax, newN, newS];
      If[weight[alpha, newN, newS] != w,
        notWt++;
        If[Length[failureRows] < 200,
          failureRows = Append[failureRows, {alpha, nmax, n, row[[4]], w, "not_weight_preserving", newN, setString[newS], move[[3]]}]
        ],
        If[sign[newS] == sign[s],
          notSign++;
          If[Length[failureRows] < 200,
            failureRows = Append[failureRows, {alpha, nmax, n, row[[4]], w, "not_sign_reversing", newN, setString[newS], move[[3]]}]
          ],
          If[Head[back] === Missing || back[[1]] != n || back[[2]] != s,
            notInv++;
            If[Length[failureRows] < 200,
              failureRows = Append[failureRows, {alpha, nmax, n, row[[4]], w, "not_involutive", newN, setString[newS], move[[3]]}]
            ],
            paired++;
          ]
        ]
      ]
    ],
    {row, rows}
  ];
  pairSummaryRows = Append[pairSummaryRows, {alpha, nmax, Length[rows], paired, unpaired, notInv, notWt, notSign}],
  {alpha, 0, 1}, {nmax, 0, NMax}
];

Export[FileNameJoin[{OutDir, "transformed_cancellation_objects.csv"}], Prepend[allObjectRows, objectHeader], "CSV"];
Export[FileNameJoin[{OutDir, "transformed_cancellation_coefficients.csv"}], coefficientRows, "CSV"];
Export[FileNameJoin[{OutDir, "transformed_cancellation_survivors.csv"}], survivorRows, "CSV"];
Export[FileNameJoin[{OutDir, "transformed_cancellation_failures.csv"}], failureRows, "CSV"];
Export[FileNameJoin[{OutDir, "transformed_cancellation_pair_summary.csv"}], pairSummaryRows, "CSV"];

Print["KMax=", KMax];
Print["NMax=", NMax];
Do[
  rows = Select[coefficientRows, #[[1]] === alpha && #[[2]] === NMax && #[[4]] != 0 &];
  Print["alpha=", alpha, " nonzero signed coefficient exponents at NMax: ",
    Take[rows[[All, 3]], UpTo[20]]
  ],
  {alpha, 0, 1}
];
Print["Local absorb/release summary at NMax:"];
Scan[Print, Select[Rest[pairSummaryRows], #[[2]] == NMax &]];
Print["Wrote outputs in ", OutDir];
