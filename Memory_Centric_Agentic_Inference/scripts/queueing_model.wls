(* created: 2026-05-11T15:08:00Z
   cycle: 8
   run_id: run-2026-05-11T121649Z
   agent: worker
   milestone: M-QUEUE-1 *)

ClearAll["Global`*"];

ensureDir[path_] := If[! DirectoryQ[path], CreateDirectory[path, CreateIntermediateDirectories -> True]];
plain[x_] := ToString[x, InputForm];

ensureDir["data"];

rho[lambda_, mu_] := lambda/mu;
wq[lambda_, mu_] := FullSimplify[rho[lambda, mu]/(mu - lambda), Assumptions -> {lambda >= 0, mu > lambda}];
q[ops_, lambda_, mu_] := FullSimplify[ops*wq[lambda, mu], Assumptions -> {ops >= 0, lambda >= 0, mu > lambda}];

qRegistry = q[Oregistry, lambdaRegistry, muRegistry];
qPolicy = q[Opolicy, lambdaPolicy, muPolicy];
qMigration = q[Omigration, lambdaMigration, muMigration];
qDag = q[Odag*DAGWidth, lambdaDag, muDag];
qVerifier = q[Overifier*VerifierDelay, lambdaVerifier, muVerifier];
qDurable = q[Odurable, lambdaDurable, muDurable];
qPreemption = q[Opreempt, lambdaPreempt, muPreempt];

incrementalB = FullSimplify[qRegistry + qPolicy + qMigration];
incrementalC = FullSimplify[qDag + qVerifier + qDurable + qPreemption];
netBMinusA = FullSimplify[BenefitObject - incrementalB];
netCMinusB = FullSimplify[BenefitDag - incrementalC];

thresholdBenefitObject = incrementalB;
thresholdBenefitDag = incrementalC;
thresholdMuRegistry = FullSimplify[
  (lambdaRegistry + Sqrt[lambdaRegistry^2 + 4*lambdaRegistry*Oregistry/BenefitObject])/2,
  Assumptions -> {BenefitObject > 0, Oregistry > 0, lambdaRegistry > 0}
];

specialRows = {
  {"queue_delay", "lambda_s_equals_0", plain[wq[0, mu]], "Idle coordination service contributes zero queueing delay.", "rules out fixed overhead when trace has no events"},
  {"queue_delay", "mu_s_to_infinity", plain[Limit[wq[lambda, mu], mu -> Infinity]], "Infinite service capacity removes queueing delay.", "low-overhead winners should match prior architecture boundary"},
  {"queue_delay", "lambda_s_approaches_mu_s", plain[Limit[wq[lambda, mu], lambda -> mu, Direction -> "FromBelow"]], "Queue delay diverges at saturation.", "object/DAG options must reverse near saturation"},
  {"option_b", "zero_metadata_latency", plain[BenefitObject - qMigration], "Registry and object-policy queues collapse; migration may still matter.", "isolates movement from metadata overhead"},
  {"option_b", "no_migrations", plain[BenefitObject - qRegistry - qPolicy], "Migration queue is removed from Option B incremental cost.", "tests object registry/policy alone"},
  {"option_c", "zero_branch_width", plain[BenefitDag - qVerifier - qDurable - qPreemption], "DAG coordination term collapses, verifier/durable/preemption may remain.", "controls and RAG should not require trajectory coordination"},
  {"option_c", "zero_verifier_delay", plain[BenefitDag - qDag - qDurable - qPreemption], "Verifier synchronization term collapses.", "verification-specific advantage must shrink if verifier waits vanish"},
  {"option_c", "zero_durable_writes", plain[BenefitDag - qDag - qVerifier - qPreemption], "Durable consistency queue is removed.", "durable overhead should not appear without durable events"},
  {"winner", "equal_retained_value_zero", plain[{-incrementalB, -incrementalC}], "With no retained-value difference, extra coordination only hurts.", "lower-overhead architecture should win"},
  {"option_b", "infinite_metadata_latency", "-Infinity", "Registry saturation drives Option B below Option A.", "rules out non-falsifiable object scheduling"},
  {"option_c", "saturated_dag_service", "-Infinity", "DAG saturation drives Option C below Option B.", "rules out non-falsifiable trajectory scheduling"}
};

thresholdRows = {
  {"B_beats_A", "object_reuse_threshold", plain[thresholdBenefitObject], "BenefitObject must exceed registry + policy + migration queue cost.", "derived"},
  {"C_beats_B", "dag_state_threshold", plain[thresholdBenefitDag], "BenefitDag must exceed DAG + verifier + durable + preemption queue cost.", "derived"},
  {"C_beats_A", "combined_threshold", plain[thresholdBenefitObject + thresholdBenefitDag], "Combined retained value must exceed all incremental coordination queues.", "derived"},
  {"registry_service_rate", "single_service_threshold", plain[thresholdMuRegistry], "Minimum registry service-rate root for one isolated M/M/1 registry queue.", "derived"}
};

Export[
  "data/queueing_special_cases.csv",
  Prepend[specialRows, {"expression", "special_point", "symbolic_result", "interpretation", "memory_centric_implication"}]
];

Export[
  "data/queueing_reversal_thresholds.csv",
  Prepend[thresholdRows, {"comparison", "threshold", "symbolic_result", "interpretation", "evidence_label"}]
];

Print["wrote data/queueing_special_cases.csv rows=", Length[specialRows]];
Print["wrote data/queueing_reversal_thresholds.csv rows=", Length[thresholdRows]];
