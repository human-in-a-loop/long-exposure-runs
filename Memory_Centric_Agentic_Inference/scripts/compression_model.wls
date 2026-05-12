(* created: 2026-05-11T15:38:00Z
   cycle: 9
   run_id: run-2026-05-11T121649Z
   agent: worker
   milestone: M-COMP-1 *)

ClearAll["Global`*"];

ensureDir[path_] := If[! DirectoryQ[path], CreateDirectory[path, CreateIntermediateDirectories -> True]];
plain[x_] := ToString[x, InputForm];

ensureDir["data"];

net = FullSimplify[
  BytesSaved*CapacityPressure + TransferAvoided + QueueRelief -
    ReconstructionCost - MetadataCost -
    ProvenanceFailProbability*ProvenanceLossCost -
    CorrectnessSensitive*LossProbability*CorrectnessLossCost
];

benefitOnly = FullSimplify[BytesSaved*CapacityPressure + TransferAvoided + QueueRelief];
penaltyOnly = FullSimplify[
  ReconstructionCost + MetadataCost +
    ProvenanceFailProbability*ProvenanceLossCost +
    CorrectnessSensitive*LossProbability*CorrectnessLossCost
];

lossyValid = FullSimplify[
  ! (LossyStrategy && CorrectnessSensitive == 1 && ProvenancePointer == 0 && ValidationPath == 0)
];

specialRows = {
  {"net_value", "zero_reuse", plain[net /. {TransferAvoided -> 0, QueueRelief -> 0, ReconstructionCost -> 0}], "Only capacity pressure can justify compression if reuse-driven transfer and queue relief vanish.", "rules out reuse overcounting"},
  {"net_value", "perfect_reuse", plain[net /. {ReuseProbability -> 1}], "Perfect reuse leaves the boundary governed by byte, transfer, queue, and correctness terms.", "does not override safety gate"},
  {"net_value", "zero_correctness_sensitivity", plain[net /. {CorrectnessSensitive -> 0}], "Correctness loss term vanishes for correctness-insensitive objects.", "scratch-like objects may use lossy summaries"},
  {"net_value", "infinite_correctness_loss", "-Infinity unless Valid_i_s is false before scoring", "Lossy correctness-sensitive state is rejected as invalid, not ranked by score.", "hard safety gate"},
  {"net_value", "zero_provenance_risk", plain[net /. {ProvenanceFailProbability -> 0}], "Provenance penalty collapses when pointer and validation are preserved.", "summary-plus-pointer can be viable"},
  {"validity", "missing_provenance_pointer", plain[lossyValid /. {LossyStrategy -> True, CorrectnessSensitive -> 1, ProvenancePointer -> 0, ValidationPath -> 0}], "Lossy strategy is invalid without provenance pointer or validation path.", "protects verifier/trajectory/tool/durable state"},
  {"net_value", "zero_reconstruction_cost", plain[net /. {ReconstructionCost -> 0}], "Reconstruction penalty collapses.", "lossless/offload become more attractive if restore is cheap"},
  {"net_value", "infinite_reconstruction_cost", "-Infinity", "Any strategy needing reconstruction is dominated when reconstruction cost diverges.", "keep-hot or exact hot state remains"},
  {"net_value", "zero_capacity_pressure", plain[net /. {CapacityPressure -> 0}], "Byte savings alone vanish; transfer or queue relief must justify the strategy.", "rules out capacity-only claims under no pressure"},
  {"net_value", "saturated_queue_relief", plain[net /. {QueueRelief -> QueueThreshold}], "Queue relief can offset metadata/reconstruction only up to the reversal threshold.", "ties compression to M-QUEUE-1"},
  {"net_value", "queue_relief_zero", plain[net /. {QueueRelief -> 0}], "Compression becomes a local byte/transfer tradeoff if it does not affect queues.", "scopes down disconnected compression claims"}
};

boundaryRows = {
  {"compression_beats_keep_hot", "general_threshold", plain[FullSimplify[benefitOnly > penaltyOnly]], "Compression is beneficial only when byte, transfer, and queue benefits exceed reconstruction, metadata, provenance, and correctness penalties.", "derived"},
  {"capacity_only", "capacity_pressure_threshold", plain[FullSimplify[CapacityPressure > (penaltyOnly - TransferAvoided - QueueRelief)/BytesSaved]], "Minimum capacity pressure for a byte-saving strategy with positive BytesSaved.", "derived"},
  {"queue_only", "queue_relief_threshold", plain[FullSimplify[QueueRelief > penaltyOnly - BytesSaved*CapacityPressure - TransferAvoided]], "Minimum queue relief needed after capacity and transfer terms.", "derived"},
  {"lossy_validity", "hard_invalidity_rule", plain[lossyValid], "Lossy correctness-sensitive state requires pointer or validation path.", "derived"},
  {"summary_plus_pointer", "pointer_overhead_threshold", plain[FullSimplify[BytesSaved*CapacityPressure + TransferAvoided + QueueRelief > ReconstructionCost + MetadataCost + PointerChaseCost]], "Pointer-preserving summary wins only if relief exceeds reconstruction, metadata, and pointer chasing.", "derived"}
};

Export[
  "data/compression_special_cases.csv",
  Prepend[specialRows, {"expression", "special_point", "symbolic_result", "interpretation", "memory_centric_implication"}]
];

Export[
  "data/compression_boundary_inequalities.csv",
  Prepend[boundaryRows, {"comparison", "threshold", "symbolic_result", "interpretation", "evidence_label"}]
];

Print["wrote data/compression_special_cases.csv rows=", Length[specialRows]];
Print["wrote data/compression_boundary_inequalities.csv rows=", Length[boundaryRows]];
