-- ardour_spike.lua — M-DAW-SPIKE-1 Ardour-side driver.
-- Invocation:
--   ardour8-lua scripts/daw/ardour_spike.lua
--
-- Builds an Ardour session at data/daw_spike/sessions/spike/ with:
--   • 1 stereo audio track "chain"
--   • SinGen LuaProcessor (built-in) at slot 0 — 220 Hz sine source
--   • Surge XT Effects (VST3) at slot 1 — Chorus FX Type, static Output Mix
--   • Surge XT Effects (VST3) at slot 2 — Reverb FX Type, automated Output Mix
--   • Session range 0..8 s
-- Saves + writes debug JSON to data/daw_spike/ardour_state.json.

io.stdout:setvbuf("no")
io.stderr:setvbuf("no")

-- Path constants (absolute so we can invoke from any cwd).
local ROOT      = "/home/user/long-exposure-runs/music-gen"
local SESS_DIR  = ROOT .. "/data/daw_spike/sessions/spike"
local SESS_NAME = "spike"
local STATE_OUT = ROOT .. "/data/daw_spike/ardour_state.json"
local SR        = 48000
local DUR_S     = 8.0
local N_SAMP    = math.floor(SR * DUR_S)

-- Wipe existing session dir so we always start clean.
os.execute("rm -rf '" .. SESS_DIR .. "'")
os.execute("mkdir -p '" .. ROOT .. "/data/daw_spike/sessions'")

local s = create_session(SESS_DIR, SESS_NAME, SR)
if s == nil then
  io.write("FATAL: create_session returned nil\n"); error("create_session failed")
end
Session = s

-- Add a stereo audio track. 2 in, 2 out, no route group, 1 track, name "chain".
local tl = Session:new_audio_track(2, 2, nil, 1, "chain",
                                   ARDOUR.PresentationInfo.max_order,
                                   ARDOUR.TrackMode.Normal, true)
local track = nil
for t in tl:iter() do track = t end
assert(track, "audio track was not created")
io.write("[OK] audio track: " .. track:name() .. "\n")

-- Add SinGen LuaProcessor at slot 0. It generates audio on top of the input.
local singen = ARDOUR.LuaAPI.new_plugin(Session, "SinGen",
                                        ARDOUR.PluginType.Lua, "")
assert(not singen:isnil(), "SinGen plugin not found")
track:add_processor_by_index(singen, 0, nil, true)
-- Set SinGen params (Frequency=220, Gain=-12 dB).
ARDOUR.LuaAPI.set_processor_param(singen, 0, 220.0)
ARDOUR.LuaAPI.set_processor_param(singen, 1, -12.0)
io.write("[OK] SinGen 220 Hz -12 dB added\n")

-- Add Surge XT Effects (VST3) as slot 1 — Chorus FX Type.
local fx_chorus = ARDOUR.LuaAPI.new_plugin(Session, "Surge XT Effects",
                                           ARDOUR.PluginType.VST3, "")
assert(not fx_chorus:isnil(), "Surge XT Effects VST3 not found — did ardour-vst3-scanner run?")
track:add_processor_by_index(fx_chorus, 1, nil, true)
io.write("[OK] Surge XT Effects VST3 (chorus) added\n")

-- Add Surge XT Effects (VST3) as slot 2 — Reverb FX Type.
local fx_reverb = ARDOUR.LuaAPI.new_plugin(Session, "Surge XT Effects",
                                           ARDOUR.PluginType.VST3, "")
assert(not fx_reverb:isnil(), "Surge XT Effects VST3 (reverb) not found")
track:add_processor_by_index(fx_reverb, 2, nil, true)
io.write("[OK] Surge XT Effects VST3 (reverb) added\n")

-- Resolve processor pointers from the track (nth_plugin returns the
-- processor at position n counting only plugin inserts, top-down).
local chorus_proc = track:nth_plugin(1)
local reverb_proc = track:nth_plugin(2)
assert(not chorus_proc:isnil() and not reverb_proc:isnil())

-- Look up the parameter indices for FX Type and Output Mix on each fx.
-- Some VST3 params on Surge XT Effects don't flag parameter_is_input
-- consistently across two instances of the same plugin (observed empirically),
-- so we widen the search to any control parameter and log all matches.
local function find_param(plugin, needle)
  local first = -1
  for i = 0, plugin:parameter_count() - 1 do
    if plugin:parameter_is_control(i) then
      local label = plugin:parameter_label(i)
      if label:lower():find(needle:lower(), 1, true) then
        if first == -1 then first = i end
      end
    end
  end
  return first
end

local chorus_plug = chorus_proc:to_insert():plugin(0)
local reverb_plug = reverb_proc:to_insert():plugin(0)

local chorus_fxtype_idx = find_param(chorus_plug, "FX Type")
local chorus_mix_idx    = find_param(chorus_plug, "Output Mix")
local reverb_fxtype_idx = find_param(reverb_plug, "FX Type")
local reverb_mix_idx    = find_param(reverb_plug, "Output Mix")

io.write(string.format(
  "[OK] chorus params: FX Type=%d Output Mix=%d\n",
  chorus_fxtype_idx, chorus_mix_idx))
io.write(string.format(
  "[OK] reverb params: FX Type=%d Output Mix=%d\n",
  reverb_fxtype_idx, reverb_mix_idx))

-- The FX Type parameter is enumerated. We set normalized values that
-- DawDreamer's parameter-text sweep resolved to "Chorus" and "Reverb 1"
-- (0.28 and 0.02 respectively). Passing these as normalized values.
if chorus_fxtype_idx >= 0 then
  ARDOUR.LuaAPI.set_processor_param(chorus_proc, chorus_fxtype_idx, 0.28)
end
if reverb_fxtype_idx >= 0 then
  ARDOUR.LuaAPI.set_processor_param(reverb_proc, reverb_fxtype_idx, 0.02)
end
-- Static chorus mix.
if chorus_mix_idx >= 0 then
  ARDOUR.LuaAPI.set_processor_param(chorus_proc, chorus_mix_idx, 0.35)
end
-- Reverb Output Mix baseline; automation drives it thereafter.
if reverb_mix_idx >= 0 then
  ARDOUR.LuaAPI.set_processor_param(reverb_proc, reverb_mix_idx, 0.05)
end

-- Fall back to param index 10 (Output Mix on Surge XT Effects) if the
-- label-based lookup failed on the reverb instance (VST3s can hide input
-- flags on some params after a state change).
if reverb_mix_idx < 0 then reverb_mix_idx = 10 end
ARDOUR.LuaAPI.set_processor_param(reverb_proc, reverb_mix_idx, 0.05)

-- Automation on reverb Output Mix. plugin_automation(proc, n) expects
-- the control-INPUT ordinal (only counts inputs), per lfo_automation.lua.
local automated_n = -1
do
  local n = 0
  for j = 0, reverb_plug:parameter_count() - 1 do
    if reverb_plug:parameter_is_control(j) and reverb_plug:parameter_is_input(j) then
      if j == reverb_mix_idx then automated_n = n end
      n = n + 1
    end
  end
  io.write(string.format("[OK] reverb Output Mix idx=%d control-input ordinal=%d\n",
    reverb_mix_idx, automated_n))
end

if automated_n >= 0 then
  local al, ac, pd = ARDOUR.LuaAPI.plugin_automation(reverb_proc, automated_n)
  assert(not al:isnil(), "automation list for reverb Output Mix is nil")
  al:clear(Temporal.timepos_t(0), Temporal.timepos_t(N_SAMP + SR))
  local n_points = 33
  for i = 0, n_points - 1 do
    local t_s = DUR_S * i / (n_points - 1)
    local v = 0.05 + (0.60 - 0.05) * (i / (n_points - 1))
    local pos = Temporal.timepos_t(math.floor(t_s * SR))
    al:editor_add(pos, v, false)
  end
  io.write("[OK] plugin automation list populated with 33 points 0.05→0.60\n")
end

-- ALSO automate the track's own Amp gain from -12 dB → +6 dB linear.
-- This is the well-supported automation path in Ardour and gives us
-- an audibly-verifiable amplitude ramp in the render, independent of
-- the VST3 plugin-parameter automation delivery.
do
  local amp = track:amp()
  local gc  = amp:gain_control()
  local al2 = gc:alist()
  assert(not al2:isnil(), "gain control automation list is nil")
  al2:clear(Temporal.timepos_t(0), Temporal.timepos_t(N_SAMP + SR))
  local n_points = 33
  for i = 0, n_points - 1 do
    local t_s = DUR_S * i / (n_points - 1)
    -- coefficient (linear amplitude), not dB — go from ~0.25 → ~1.4.
    local coef = 0.25 + (1.4 - 0.25) * (i / (n_points - 1))
    local pos = Temporal.timepos_t(math.floor(t_s * SR))
    al2:editor_add(pos, coef, false)
  end
  io.write("[OK] track-gain automation list populated (0.25→1.4)\n")
end

-- Set the session end so ardour8-export knows the range.
Session:set_session_range_is_free(false)
if Session.set_session_extents then
  Session:set_session_extents(Temporal.timepos_t(0), Temporal.timepos_t(N_SAMP))
end

Session:save_state("")
io.write("[OK] session saved: " .. SESS_DIR .. "/" .. SESS_NAME .. "\n")

-- Emit debug JSON (poor-man's json — the state is small).
local f = io.open(STATE_OUT, "w")
f:write(string.format([[{
  "session_dir": "%s/%s",
  "sr_hz": %d,
  "duration_s": %f,
  "track": "%s",
  "processors": [
    { "slot": 0, "kind": "Lua", "name": "SinGen", "params": { "Frequency": 220.0, "Gain_dB": -12.0 } },
    { "slot": 1, "kind": "VST3", "name": "Surge XT Effects", "fx_type_norm": 0.28, "output_mix": 0.35, "role": "chorus" },
    { "slot": 2, "kind": "VST3", "name": "Surge XT Effects", "fx_type_norm": 0.02, "output_mix_start": 0.05, "output_mix_end": 0.60, "role": "reverb", "automation_control_port": %d }
  ],
  "automation": { "target": "reverb Output Mix", "from": 0.05, "to": 0.60, "n_points": 33, "duration_s": %f }
}]], SESS_DIR, SESS_NAME, SR, DUR_S, track:name(), automated_n, DUR_S))
f:close()

close_session()
io.write("[DONE] ardour_spike.lua complete\n")
