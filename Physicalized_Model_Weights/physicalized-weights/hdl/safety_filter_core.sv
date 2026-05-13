// Tiny fixed-weight safety-filter core for M-PROTO-1.
// Policy/version/health/audit/fallback logic intentionally stays outside HDL.
module safety_filter_core (
    input  signed [7:0] feature0,
    input  signed [7:0] feature1,
    input  signed [7:0] feature2,
    input  signed [7:0] feature3,
    input  signed [7:0] feature4,
    input  signed [7:0] feature5,
    input  signed [7:0] feature6,
    input  signed [7:0] feature7,
    output signed [15:0] score,
    output logic decision_block,
    output logic [15:0] margin,
    output logic [15:0] confidence
);
    localparam signed [7:0] W0 = 8'sd12;
    localparam signed [7:0] W1 = -8'sd7;
    localparam signed [7:0] W2 = 8'sd5;
    localparam signed [7:0] W3 = 8'sd9;
    localparam signed [7:0] W4 = -8'sd11;
    localparam signed [7:0] W5 = 8'sd4;
    localparam signed [7:0] W6 = 8'sd6;
    localparam signed [7:0] W7 = -8'sd3;
    localparam signed [15:0] BIAS = -16'sd10;
    localparam signed [15:0] THRESHOLD = 16'sd64;

    wire signed [15:0] p0 = feature0 * W0;
    wire signed [15:0] p1 = feature1 * W1;
    wire signed [15:0] p2 = feature2 * W2;
    wire signed [15:0] p3 = feature3 * W3;
    wire signed [15:0] p4 = feature4 * W4;
    wire signed [15:0] p5 = feature5 * W5;
    wire signed [15:0] p6 = feature6 * W6;
    wire signed [15:0] p7 = feature7 * W7;
    wire signed [15:0] diff = score - THRESHOLD;

    assign score = p0 + p1 + p2 + p3 + p4 + p5 + p6 + p7 + BIAS;

    always_comb begin
        decision_block = score >= THRESHOLD;
        margin = diff < 0 ? -diff : diff;
        confidence = margin;
    end
endmodule
