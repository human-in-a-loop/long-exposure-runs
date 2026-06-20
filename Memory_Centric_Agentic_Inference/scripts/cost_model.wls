(* created: 2026-05-11T13:02:00Z
   cycle: 3
   run_id: run-2026-05-11T121649Z
   agent: worker
   milestone: M-COST-1 *)

ClearAll["Global`*"];

ensureDir[path_] := If[! DirectoryQ[path], CreateDirectory[path, CreateIntermediateDirectories -> True]];
plain[x_] := ToString[x, InputForm];
boolText[x_] := If[TrueQ[x], "true", "false"];

ensureDir["data"];

lifetimeParams = Import["memory-centric-agentic/lifetime_parameters.csv", "Dataset"];
lifeGrid = Import["data/lifetime_regime_grid.csv", "Dataset"];

(* Symbolic cost terms. *)
cResidency = L*R*H;
cTransfer = X*M;
cBandwidthDelay = X/B + A*Naccess;
retainedValue = Preuse*Crecompute + Pcorrect*Closs;
placementCost = cResidency + cTransfer + cBandwidthDelay;
advantage = FullSimplify[retainedValue - placementCost];
kvUnsat = skv*T;
kvSat = skv*Tmax;

specialRows = {
  {"advantage", "zero_transfer_cost", plain[advantage /. M -> 0], "Movement penalty is removed; residency and bandwidth-delay still matter.", "weakens movement-centric claim if recommendations do not change"},
  {"bandwidth_delay", "infinite_bandwidth", plain[Limit[cBandwidthDelay, B -> Infinity]], "Streaming delay collapses to access latency only.", "isolates latency/residency from bandwidth pressure"},
  {"retained_value", "zero_reuse", plain[retainedValue /. Preuse -> 0], "Recompute avoidance disappears; only correctness-sensitive retention remains.", "controls should weaken unless correctness risk is active"},
  {"retained_value", "perfect_reuse_or_pinned_prefix", plain[retainedValue /. Preuse -> 1], "Pinned or always-reused state receives full recomputation-avoidance value.", "strengthens prefix and repeated tool-output placement"},
  {"durable_live", "zero_durable_state", plain[D0 + gd*H /. {D0 -> 0, gd -> 0}], "No durable workspace bytes remain.", "collapses durable workspace advantage"},
  {"tier_choice", "equal_tier_costs", plain[0], "All tiers have equal symbolic costs, so placement preference is undefined.", "rules out hard-coded tier preference"},
  {"kv_live", "context_cap_unsaturated", plain[kvUnsat], "KV bytes scale linearly before context cap.", "ordinary serving explanation remains sufficient"},
  {"kv_live", "context_cap_saturated", plain[kvSat], "KV bytes stop growing after context cap.", "durable/branch state can still grow outside KV cap"},
  {"retained_value", "correctness_sensitive_loss_zero", plain[retainedValue /. Closs -> 0], "Correctness/audit penalty is removed.", "tool/verifier/trajectory claims must then rely on recompute or transfer"},
  {"retained_value", "recomputation_cost_zero", plain[retainedValue /. Crecompute -> 0], "Recompute penalty is removed.", "remaining benefit must come from correctness or staleness risk"}
};

Export[
  "data/cost_model_special_cases.csv",
  Prepend[specialRows, {"expression", "special_point", "symbolic_result", "interpretation", "memory_centric_implication"}]
];

tiers = <|
  "HBM/GPU memory" -> <|"residency" -> 5., "transfer" -> 1., "bandwidth" -> 1., "correctnessFit" -> 0.4, "energy" -> 2.0, "dollar" -> 5.0|>,
  "CPU DRAM" -> <|"residency" -> 2.5, "transfer" -> 2., "bandwidth" -> 2., "correctnessFit" -> 0.7, "energy" -> 1.5, "dollar" -> 2.5|>,
  "CXL_or_pooled_memory" -> <|"residency" -> 2., "transfer" -> 3., "bandwidth" -> 3., "correctnessFit" -> 0.7, "energy" -> 1.8, "dollar" -> 2.0|>,
  "NVMe_local" -> <|"residency" -> 0.8, "transfer" -> 6., "bandwidth" -> 6., "correctnessFit" -> 0.85, "energy" -> 3.0, "dollar" -> 0.8|>,
  "remote_object_store" -> <|"residency" -> 0.5, "transfer" -> 9., "bandwidth" -> 9., "correctnessFit" -> 0.9, "energy" -> 4.5, "dollar" -> 0.5|>,
  "durable_workspace_store" -> <|"residency" -> 0.6, "transfer" -> 7., "bandwidth" -> 8., "correctnessFit" -> 1.0, "energy" -> 3.5, "dollar" -> 0.6|>,
  "semantic_cache" -> <|"residency" -> 1.2, "transfer" -> 5., "bandwidth" -> 5., "correctnessFit" -> 0.6, "energy" -> 2.5, "dollar" -> 1.2|>
|>;

scoreTier[size_, reuse_, recompute_, correct_, loss_, horizon_, tier_] := Module[
  {r, m, b, fit, keepValue, cost},
  r = tiers[tier]["residency"]; m = tiers[tier]["transfer"]; b = tiers[tier]["bandwidth"]; fit = tiers[tier]["correctnessFit"];
  keepValue = reuse*recompute + correct*loss*fit;
  cost = size*horizon*r/1000. + size*(m + b)/1000.;
  keepValue - cost
];

bestTier[size_, reuse_, recompute_, correct_, loss_, horizon_, allowed_] := First@MaximalBy[allowed, scoreTier[size, reuse, recompute, correct, loss, horizon, #] &];

dominantTerm[reuse_, recompute_, correct_, loss_, transfer_, bandwidth_, residency_] := First@First@ReverseSortBy[
  {{"recompute_avoidance", reuse*recompute}, {"correctness_sensitive_retention", correct*loss}, {"transfer_avoidance", transfer}, {"bandwidth_delay", bandwidth}, {"residency_pressure", residency}},
  Last
];

thesisLabel[scenario_, dom_, benefit_] := Which[
  StringContainsQ[scenario, "control"] && benefit < 10, "weakened",
  dom == "correctness_sensitive_retention" || dom == "transfer_avoidance" || dom == "recompute_avoidance", "strengthened",
  benefit < 5, "weakened",
  True, "ambiguous"
];

scenarioSpecs = {
  <|"scenario" -> "single-turn chat control", "object" -> "KV cache", "size" -> 4096., "reuse" -> 0.05, "recompute" -> 4., "correct" -> 0., "loss" -> 0., "horizon" -> 1., "fanout" -> 1, "verifierDelay" -> 0, "durableHorizon" -> 0, "allowed" -> {"HBM/GPU memory", "CPU DRAM"}|>,
  <|"scenario" -> "batch summarization/offline inference control", "object" -> "weights", "size" -> 12000., "reuse" -> 0.1, "recompute" -> 2., "correct" -> 0., "loss" -> 0., "horizon" -> 1., "fanout" -> 1, "verifierDelay" -> 0, "durableHorizon" -> 0, "allowed" -> {"HBM/GPU memory", "CPU DRAM", "NVMe_local"}|>,
  <|"scenario" -> "RAG with retrieved-context reuse", "object" -> "retrieved context", "size" -> 2500., "reuse" -> 0.45, "recompute" -> 16., "correct" -> 0.25, "loss" -> 12., "horizon" -> 4., "fanout" -> 1, "verifierDelay" -> 0, "durableHorizon" -> 2, "allowed" -> {"CPU DRAM", "NVMe_local", "remote_object_store", "semantic_cache"}|>,
  <|"scenario" -> "code-agent loop with tool outputs and durable workspace", "object" -> "tool output", "size" -> 5200., "reuse" -> 0.6, "recompute" -> 24., "correct" -> 0.5, "loss" -> 40., "horizon" -> 10., "fanout" -> 2, "verifierDelay" -> 2, "durableHorizon" -> 10, "allowed" -> {"CPU DRAM", "NVMe_local", "durable_workspace_store", "remote_object_store"}|>,
  <|"scenario" -> "verification-heavy agent", "object" -> "verifier state", "size" -> 3600., "reuse" -> 0.55, "recompute" -> 20., "correct" -> 0.75, "loss" -> 55., "horizon" -> 6., "fanout" -> 3, "verifierDelay" -> 5, "durableHorizon" -> 4, "allowed" -> {"CPU DRAM", "NVMe_local", "durable_workspace_store"}|>,
  <|"scenario" -> "multi-agent branch/merge run", "object" -> "branch state", "size" -> 7000., "reuse" -> 0.5, "recompute" -> 28., "correct" -> 0.35, "loss" -> 30., "horizon" -> 5., "fanout" -> 4, "verifierDelay" -> 3, "durableHorizon" -> 6, "allowed" -> {"HBM/GPU memory", "CPU DRAM", "CXL_or_pooled_memory", "NVMe_local", "durable_workspace_store"}|>
};

scenarioRows = Map[
  Function[s,
    Module[{transfer, bandwidth, residency, dom, tier, benefit, label, energyProxy, dollarProxy},
      transfer = s["size"]*(1 + s["fanout"])*0.004;
      bandwidth = s["size"]*(1 + s["verifierDelay"])*0.002;
      residency = s["size"]*Max[1, s["horizon"]]*0.003;
      dom = dominantTerm[s["reuse"], s["recompute"], s["correct"], s["loss"], transfer, bandwidth, residency];
      tier = bestTier[s["size"], s["reuse"], s["recompute"], s["correct"], s["loss"], s["horizon"], s["allowed"]];
      benefit = s["reuse"]*s["recompute"] + s["correct"]*s["loss"];
      label = thesisLabel[s["scenario"], dom, benefit];
      energyProxy = transfer*tiers[tier]["energy"] + residency*0.1*tiers[tier]["energy"];
      dollarProxy = residency*tiers[tier]["dollar"];
      {s["scenario"], s["object"], plain[s["size"]], plain[s["reuse"]], plain[s["fanout"]], plain[s["verifierDelay"]], plain[s["durableHorizon"]], dom, s["object"], tier, label, plain[N[benefit]], plain[N[energyProxy]], plain[N[dollarProxy]], "synthetic_placeholder"}
    ]
  ],
  scenarioSpecs
];

Export[
  "data/cost_model_scenarios.csv",
  Prepend[scenarioRows, {"scenario", "representative_object", "object_size_units", "reuse_probability", "branch_fanout", "verifier_delay", "durability_horizon", "dominant_cost_term", "dominant_object_class", "best_symbolic_tier_choice", "memory_centric_thesis", "retained_value_score", "energy_proxy_score", "dollar_proxy_score", "assumption_status"}]
];

reuseVals = {0., 0.3, 0.7};
transferVals = {0., 2., 6.};
recomputeVals = {0., 10., 30.};
fanoutVals = {1, 4};
verifierVals = {0, 4};
horizonVals = {0, 8};
lossVals = {0., 1., 3.};

sensitivityRows = Flatten[
  Table[
    Module[{size, correct, transferAvoid, recomputeAvoid, correctnessRet, residencyPenalty, net, driver, thesis},
      size = 1000.*fanout*(1 + verifierDelay/4. + horizon/8.);
      correct = If[verifierDelay > 0 || horizon > 0, 0.4, 0.0];
      transferAvoid = transferRatio*size/1000.;
      recomputeAvoid = reuse*recomputeRatio;
      correctnessRet = correct*lossMultiplier*20.;
      residencyPenalty = size*(1 + horizon/8.)/1000.;
      net = transferAvoid + recomputeAvoid + correctnessRet - residencyPenalty;
      driver = dominantTerm[reuse, recomputeRatio, correct, lossMultiplier*20., transferAvoid, 0., residencyPenalty];
      thesis = If[net <= 0.5, "no_material_benefit", driver];
      {plain[reuse], plain[transferRatio], plain[recomputeRatio], plain[fanout], plain[verifierDelay], plain[horizon], plain[lossMultiplier], plain[N[net]], thesis}
    ],
    {reuse, reuseVals}, {transferRatio, transferVals}, {recomputeRatio, recomputeVals}, {fanout, fanoutVals}, {verifierDelay, verifierVals}, {horizon, horizonVals}, {lossMultiplier, lossVals}
  ],
  6
];

Export[
  "data/cost_model_sensitivity.csv",
  Prepend[sensitivityRows, {"reuse_probability", "transfer_cost_ratio", "recompute_cost_ratio", "branch_fanout", "verifier_delay", "durability_horizon", "correctness_loss_multiplier", "net_memory_centric_benefit", "dominant_benefit_driver"}]
];

Print["read lifetime parameter rows=", Length[Normal[lifetimeParams]] - 1];
Print["read lifetime regime rows=", Length[Normal[lifeGrid]] - 1];
Print["wrote data/cost_model_special_cases.csv rows=", Length[specialRows]];
Print["wrote data/cost_model_scenarios.csv rows=", Length[scenarioRows]];
Print["wrote data/cost_model_sensitivity.csv rows=", Length[sensitivityRows]];
