#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "Vsafety_filter_core.h"

struct Case {
    std::string id;
    int8_t f[8];
    int expected_score;
    int expected_decision;
    int expected_margin;
};

static int golden_score(const int8_t f[8]) {
    const int weights[8] = {12, -7, 5, 9, -11, 4, 6, -3};
    int score = -10;
    for (int i = 0; i < 8; ++i) {
        score += static_cast<int>(f[i]) * weights[i];
    }
    return score;
}

int main(int argc, char** argv) {
    const char* out_path = argc > 1 ? argv[1] : "physicalized-weights/data/hdl_sim_results.csv";
    std::vector<Case> cases = {
        {"all_zero_bias_allow", {0, 0, 0, 0, 0, 0, 0, 0}, -10, 0, 74},
        {"nominal_block_high_margin", {8, -4, 5, 6, -3, 2, 4, -1}, 261, 1, 197},
        {"nominal_allow_high_margin", {-4, 6, -3, 0, 8, -2, -5, 3}, -250, 0, 314},
        {"max_signed_features", {127, 127, 127, 127, 127, 127, 127, 127}, 1895, 1, 1831},
        {"min_signed_features", {-128, -128, -128, -128, -128, -128, -128, -128}, -1930, 0, 1994},
        {"threshold_equal", {6, 0, 1, 0, 0, 0, 0, 1}, 64, 1, 0},
        {"near_threshold_allow", {6, 0, 0, 0, 0, 1, 0, 1}, 63, 0, 1},
        {"near_threshold_block", {6, 0, 0, 0, 0, 0, 1, 1}, 65, 1, 1},
    };

    Vsafety_filter_core top;
    std::ofstream out(out_path);
    out << "case_id,score,decision_block,margin,confidence,expected_score,expected_decision,expected_margin,match\n";
    bool all_match = true;

    for (const auto& tc : cases) {
        top.feature0 = tc.f[0];
        top.feature1 = tc.f[1];
        top.feature2 = tc.f[2];
        top.feature3 = tc.f[3];
        top.feature4 = tc.f[4];
        top.feature5 = tc.f[5];
        top.feature6 = tc.f[6];
        top.feature7 = tc.f[7];
        top.eval();

        int score = static_cast<int16_t>(top.score);
        int decision = top.decision_block ? 1 : 0;
        int margin = static_cast<int>(top.margin);
        int confidence = static_cast<int>(top.confidence);
        int recomputed = golden_score(tc.f);
        bool match = score == tc.expected_score && score == recomputed &&
                     decision == tc.expected_decision &&
                     margin == tc.expected_margin && confidence == tc.expected_margin;
        all_match = all_match && match;
        out << tc.id << "," << score << "," << decision << "," << margin << ","
            << confidence << "," << tc.expected_score << "," << tc.expected_decision
            << "," << tc.expected_margin << "," << (match ? "true" : "false") << "\n";
    }

    std::cout << "hdl cases: " << cases.size() << "\n";
    std::cout << "all_match: " << (all_match ? "true" : "false") << "\n";
    return all_match ? 0 : 1;
}
