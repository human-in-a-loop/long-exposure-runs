(* created: 2026-05-13T09:18:00Z
   cycle: 3
   run_id: run-2026-05-13T015136Z
   agent: worker
   milestone: M-REOPEN-1 *)

output = "physicalized-weights/data/symbolic_reopen_thresholds.json";

ineq = Hfixed + Veff*HperReq + Hcontrol < Bfixed + V*BperReq + Bcontrol;
vEffThreshold = FullSimplify[
  Reduce[ineq && HperReq < 0 && V >= 0, Veff, Reals]
];

results = <|
  "schema_version" -> 1,
  "milestone_id" -> "M-REOPEN-1",
  "inequality" -> "H_fixed + Veff * H_per_req + H_control < B_fixed + V * B_per_req + B_control",
  "special_points" -> <|
    "Veff_equals_0" -> "no accepted fast-path credit; reopen requires H_fixed + H_control < B_fixed + V * B_per_req + B_control without per-request hybrid amortization",
    "V_equals_0" -> "zero request volume leaves no workload amortization; fixed/control terms dominate under current architecture boundary",
    "H_per_req_ge_B_per_req" -> "if hybrid per-request cost is no better than baseline, increasing accepted fast-path volume cannot create a per-request advantage",
    "H_fixed_gt_0" -> "positive fixed substrate cost requires nonzero useful volume or lower non-volume terms before a finite threshold can exist",
    "fallback_frequency_equals_1" -> "all fallback implies Veff = 0, so accepted fast-path volume cannot reopen the claim"
  |>,
  "solved_condition" -> ToString[vEffThreshold, InputForm]
|>;

Export[output, results, "RawJSON"];
Print["wrote " <> output];
Print["fallback_frequency_equals_1: all fallback implies Veff = 0"];
