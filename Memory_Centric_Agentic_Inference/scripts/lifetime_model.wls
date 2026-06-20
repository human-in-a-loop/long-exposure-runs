(* created: 2026-05-11T12:35:00Z
   cycle: 1
   run_id: run-2026-05-11T121649Z
   agent: worker
   milestone: M-LIFE-1
*)

SetDirectory[DirectoryName[$InputFileName] <> "/.."];

specialOut = "data/lifetime_model_special_cases.csv";
gridOut = "data/lifetime_regime_grid.csv";

kvLive[T_, Tmax_, skv_] := skv*Min[T, Tmax];
prefixReuseProb[lambda_, He_] := 1 - Exp[-lambda*He];
prefixValue[lambda_, He_, Cprefill_, Cresidency_] := prefixReuseProb[lambda, He]*Cprefill - Cresidency;
branchLive[f_, ps_, sb_, dv_, pm_, dmerge_] := f*ps*sb*(dv + pm*dmerge);
durableLive[D0_, gd_, H_] := D0 + gd*H;
plain[expr_] := ToString[expr, InputForm];

specialRows = {
  {"linear_kv_growth", "context_saturation_T_equals_Tmax", plain[kvLive[Tmax, Tmax, skv]], "KV live bytes saturate at the context cap.", "Weakens agentic-specific claim when only KV and weights remain."},
  {"linear_kv_growth", "pre_cap_T_less_than_Tmax", plain[kvLive[T, Tmax, skv] /. Min[T, Tmax] -> T], "Before saturation KV grows linearly with token count.", "Matches ordinary serving behavior."},
  {"prefix_reuse_value", "lambda_equals_0", plain[Simplify[prefixValue[0, He, Cprefill, Cresidency]]], "No reuse leaves only symbolic residency cost.", "Weakens prefix-cache memory-centric benefit."},
  {"prefix_reuse_probability", "infinite_or_pinned_reuse", plain[Limit[prefixReuseProb[lambda, He], He -> Infinity, Assumptions -> lambda > 0]], "Pinned or infinite-horizon reusable prefix has hit probability one.", "Strengthens reuse-oriented placement for common prefixes."},
  {"branch_live_bytes", "p_s_equals_0", plain[Simplify[branchLive[f, 0, sb, dv, pm, dmerge]]], "No surviving branches means no retained branch state.", "Collapses branch-conditioned pressure."},
  {"branch_live_bytes", "p_m_equals_0", plain[Simplify[branchLive[f, ps, sb, dv, 0, dmerge]]], "No merge tail leaves verifier-delay residency only.", "Branch pressure still exists if survival and verifier delay are nonzero."},
  {"branch_live_bytes", "f_equals_1", plain[Simplify[branchLive[1, ps, sb, dv, pm, dmerge]]], "Single candidate removes fanout scaling.", "Reduces to verification state rather than multi-branch state."},
  {"durable_workspace_live_bytes", "g_d_equals_0", plain[Simplify[durableLive[D0, 0, H]]], "Zero artifact growth leaves only initial workspace bytes.", "Weakens durability hypothesis unless D0 is significant."},
  {"durable_workspace_live_bytes", "context_saturated_but_H_positive", plain[{kvLive[Tmax, Tmax, skv], durableLive[D0, gd, H]}], "Durable bytes persist independently of a saturated context window.", "Strengthens durable-state argument when gd or H is nonzero."}
};

Export[specialOut, Prepend[specialRows, {"expression", "special_point", "symbolic_result", "interpretation", "memory_centric_implication"}], "CSV"];

fanouts = {1, 2, 4, 8};
survivals = {0, 0.25, 0.5, 0.75};
reuseRates = {0, 0.05, 0.2};
horizons = {0, 8, 32};

skvN = 1.0;
Tn = 4096;
TmaxN = 8192;
sbN = 1800;
dvN = 4;
pmN = 0.35;
dmergeN = 3;
D0N = 2000;
gdN = 220;
prefixN = 800;
HeN = 10;

dominant[kv_, branch_, durable_, prefix_] := Module[{vals, names},
  vals = {kv, branch, durable, prefix};
  names = {"KV", "branch_state", "durable_workspace", "prefix_cache"};
  names[[First[Ordering[vals, -1]]]]
];

gridRows = Flatten[
  Table[
    Module[{kv, branch, durable, prefix, total, dom, regime},
      kv = N[kvLive[Tn, TmaxN, skvN]];
      branch = N[branchLive[f, ps, sbN, dvN, pmN, dmergeN]];
      durable = N[durableLive[D0N, gdN, H]];
      prefix = N[prefixN*prefixReuseProb[lambda, HeN]];
      total = kv + branch + durable + prefix;
      dom = dominant[kv, branch, durable, prefix];
      regime = If[f == 1 && ps == 0 && lambda == 0 && H == 0, "control_single_turn_or_batch", If[dom == "branch_state", "branch_dominated", If[dom == "durable_workspace", "durable_dominated", "kv_or_prefix_dominated"]]];
      {f, ps, lambda, H, kv, branch, durable, prefix, total, dom, regime}
    ],
    {f, fanouts}, {ps, survivals}, {lambda, reuseRates}, {H, horizons}
  ],
  3
];

Export[gridOut, Prepend[gridRows, {"fanout", "branch_survival", "reuse_rate_lambda", "durability_horizon", "kv_live_bytes", "branch_live_bytes", "durable_live_bytes", "prefix_expected_bytes", "total_expected_retained_bytes", "dominant_state", "regime_label"}], "CSV"];

Print["wrote ", specialOut, " rows=", Length[specialRows]];
Print["wrote ", gridOut, " rows=", Length[gridRows]];
Print["special_points=", StringRiffle[specialRows[[All, 2]], ", "]];
