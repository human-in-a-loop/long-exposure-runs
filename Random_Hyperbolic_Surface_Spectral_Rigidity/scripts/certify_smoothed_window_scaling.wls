(* created: 2026-05-16T16:09:00Z
   cycle: 30
   run_id: run-2026-05-15T153635Z
   agent: worker
   milestone: M19-smoothed-window-paley-wiener-lemma *)

root = DirectoryName[DirectoryName[$InputFileName]];
out = FileNameJoin[{root, "data", "extension_candidates", "smoothed_window_symbolic_checks.csv"}];
If[! DirectoryQ[DirectoryName[out]], CreateDirectory[DirectoryName[out], CreateIntermediateDirectories -> True]];

Clear[lambda, Delta, r0, delta, r, t, u, R];

gaussianScaled = Exp[-((r - r0)/delta)^2/2];
fourierScaled = Assuming[delta > 0,
  FullSimplify[
    FourierTransform[gaussianScaled, r, t, FourierParameters -> {1, -1}]
  ]
];
expectedScaled = Assuming[delta > 0,
  FullSimplify[delta Exp[-I r0 t] Sqrt[2 Pi] Exp[-(delta t)^2/2]]
];
scalingCheck = Assuming[delta > 0, FullSimplify[fourierScaled == expectedScaled]];

deltaRExact = Sqrt[lambda + Delta - 1/4] - Sqrt[lambda - 1/4];
bulkSeries = Assuming[lambda > 1/4,
  Normal[Series[deltaRExact, {Delta, 0, 2}]]
];
bulkLeading = Assuming[lambda > 1/4,
  FullSimplify[Limit[deltaRExact/Delta, Delta -> 0, Direction -> "FromAbove"]]
];
edgeWidth = FullSimplify[deltaRExact /. lambda -> 1/4];
edgeCheck = FullSimplify[edgeWidth == Sqrt[Delta]];

gaussianTail[x_] := Erfc[x/Sqrt[2]];
tailAtInfinity = Limit[gaussianTail[R delta], R -> Infinity, Assumptions -> delta > 0];
tailAtZero = Limit[gaussianTail[R delta], delta -> 0, Assumptions -> R > 0];
tailAtWideWindow = Limit[gaussianTail[R delta], R -> Infinity, Assumptions -> delta > 0];

rows = {
  {"check", "result", "expression"},
  {"gaussian_fourier_scaling", ToString[scalingCheck, InputForm], ToString[fourierScaled, InputForm]},
  {"bulk_delta_r_series_to_second_order", "computed", ToString[bulkSeries, InputForm]},
  {"bulk_delta_r_leading_limit", ToString[FullSimplify[bulkLeading == 1/Sqrt[-1 + 4 lambda], lambda > 1/4], InputForm], ToString[bulkLeading, InputForm]},
  {"edge_delta_r_exact", ToString[edgeCheck, InputForm], ToString[edgeWidth, InputForm]},
  {"gaussian_tail_R_to_infinity", ToString[tailAtInfinity === 0, InputForm], ToString[tailAtInfinity, InputForm]},
  {"gaussian_tail_R_delta_to_zero", ToString[tailAtZero === 1, InputForm], ToString[tailAtZero, InputForm]},
  {"special_point_exact_delta_zero", ToString[FullSimplify[deltaRExact /. Delta -> 0] === 0, InputForm], ToString[FullSimplify[deltaRExact /. Delta -> 0], InputForm]}
};

Export[out, rows, "CSV"];
Print["wrote ", FileNameDrop[out, FileNameDepth[root]]];
