-- M-DAW-SPIKE-1/gap-closure — GAP-2 fallback #2 (LV2 reverb).
--
-- Replaces the Surge XT Effects (VST3) reverb slot with ACE Reverb
-- (a-reverb.lv2), Ardour's own LV2 reverb. Authors dry/wet-mix
-- automation on the LV2 wet parameter and renders offline.
--
-- Success criterion: the offline render shows time-varying wet mix
-- driven by the LV2 automation curve (rising over 8 s). Compared
-- against the cycle-1 VST3 render where automation did NOT deliver.
--
-- Invocation: ardour8-lua scripts/daw_spike/gap_closure_lv2_reverb.lua
io.stdout:setvbuf("no")
io.stderr:setvbuf("no")

local ROOT      = "/home/user/long-exposure-runs/music-gen"
local SESS_DIR  = ROOT .. "/data/daw_spike/sessions/gap_closure_lv2"
local SESS_NAME = "gap_closure_lv2"
local STATE_OUT = ROOT .. "/data/daw_spike/gap_closure_lv2_state.json"
local SR        = 48000
local DUR_S     = 8.0
local N_SAMP    = math.floor(SR * DUR_S)

os.execute("rm -rf '" .. SESS_DIR .. "'")
os.execute("mkdir -p '" .. ROOT .. "/data/daw_spike/sessions'")
local s = create_session(SESS_DIR, SESS_NAME, SR)
if s == nil then io.write("FATAL: create_session\n"); error("create_session") end
Session = s

-- Stereo audio track "chain".
local tl = Session:new_audio_track(2, 2, nil, 1, "chain",
                                   ARDOUR.PresentationInfo.max_order,
                                   ARDOUR.TrackMode.Normal, true)
local track = nil
for t in tl:iter() do track = t end
assert(track, "audio track was not created")

-- Slot 0: SinGen LuaProcessor (220 Hz sine, -12 dB) — matched source
-- for direct comparison to cycle-1's Ardour render.
local singen = ARDOUR.LuaAPI.new_plugin(Session, "SinGen",
                                        ARDOUR.PluginType.Lua, "")
assert(not singen:isnil(), "SinGen not found")
track:add_processor_by_index(singen, 0, nil, true)
ARDOUR.LuaAPI.set_processor_param(singen, 0, 220.0)
ARDOUR.LuaAPI.set_processor_param(singen, 1, -12.0)

-- Slot 1: Surge XT Effects (VST3) chorus — same as cycle-1 for
-- as-close-to-baseline chain as possible before the reverb slot.
local fx_chorus = ARDOUR.LuaAPI.new_plugin(Session, "Surge XT Effects",
                                           ARDOUR.PluginType.VST3, "")
assert(not fx_chorus:isnil(), "Surge XT Effects VST3 not found")
track:add_processor_by_index(fx_chorus, 1, nil, true)

-- Slot 2: ACE Reverb (LV2) — the fallback. GAP-2 tests whether LV2
-- automation delivery to a-reverb.lv2's wet-mix modulates the render.
local fx_reverb = ARDOUR.LuaAPI.new_plugin(Session, "ACE Reverb",
                                           ARDOUR.PluginType.LV2, "")
assert(not fx_reverb:isnil(), "ACE Reverb LV2 not found")
track:add_processor_by_index(fx_reverb, 2, nil, true)

-- Resolve pointers.
local chorus_proc = track:nth_plugin(1)
local reverb_proc = track:nth_plugin(2)
assert(not chorus_proc:isnil() and not reverb_proc:isnil())

local chorus_plug = chorus_proc:to_insert():plugin(0)
local reverb_plug = reverb_proc:to_insert():plugin(0)

-- Set chorus FX Type + Output Mix (as in cycle-1).
local function find_param(plugin, needle)
  for i = 0, plugin:parameter_count() - 1 do
    if plugin:parameter_is_control(i) then
      local lbl = plugin:parameter_label(i)
      if lbl:lower():find(needle:lower(), 1, true) then return i end
    end
  end
  return -1
end
local chorus_fxtype_idx = find_param(chorus_plug, "FX Type")
local chorus_mix_idx    = find_param(chorus_plug, "Output Mix")
if chorus_fxtype_idx >= 0 then
  ARDOUR.LuaAPI.set_processor_param(chorus_proc, chorus_fxtype_idx, 0.28)
end
if chorus_mix_idx >= 0 then
  ARDOUR.LuaAPI.set_processor_param(chorus_proc, chorus_mix_idx, 0.35)
end

-- Enumerate ACE Reverb params to find dry/wet mix.
io.write("---- ACE Reverb params ----\n")
local mix_idx = -1
for i = 0, reverb_plug:parameter_count() - 1 do
  if reverb_plug:parameter_is_control(i) then
    local lbl = reverb_plug:parameter_label(i)
    local is_in = reverb_plug:parameter_is_input(i)
    io.write(string.format("  [%d] in=%s '%s'\n", i, tostring(is_in), lbl))
    -- Look for a wet/dry-wet/wet-mix style parameter.
    local ll = lbl:lower()
    if mix_idx < 0 and is_in and (ll:find("wet") or ll:find("dry/wet") or ll:find("mix") or ll:find("blend")) then
      mix_idx = i
    end
  end
end
io.write(string.format("[OK] selected LV2 wet-mix idx = %d\n", mix_idx))

-- Set an initial wet value near 0 so the automation ramp has room.
if mix_idx >= 0 then
  ARDOUR.LuaAPI.set_processor_param(reverb_proc, mix_idx, 0.05)
end

-- Author automation on the LV2 wet parameter.
local automated_n = -1
do
  local n = 0
  for j = 0, reverb_plug:parameter_count() - 1 do
    if reverb_plug:parameter_is_control(j) and reverb_plug:parameter_is_input(j) then
      if j == mix_idx then automated_n = n end
      n = n + 1
    end
  end
end
io.write(string.format("[OK] LV2 wet control-input ordinal = %d\n", automated_n))

local automation_range_from, automation_range_to = 0.05, 0.90
if automated_n >= 0 then
  local al, ac, pd = ARDOUR.LuaAPI.plugin_automation(reverb_proc, automated_n)
  assert(not al:isnil(), "automation list for LV2 wet-mix is nil")
  al:clear(Temporal.timepos_t(0), Temporal.timepos_t(N_SAMP + SR))
  local n_points = 33
  for i = 0, n_points - 1 do
    local t_s = DUR_S * i / (n_points - 1)
    local v   = automation_range_from + (automation_range_to - automation_range_from) * (i / (n_points - 1))
    local pos = Temporal.timepos_t(math.floor(t_s * SR))
    al:editor_add(pos, v, false)
  end
  io.write(string.format("[OK] LV2 wet-mix automation populated %.2f -> %.2f, %d pts\n",
    automation_range_from, automation_range_to, n_points))
end

-- Keep the track-Amp static this time so the ONLY envelope shaping
-- comes from the LV2 wet-mix automation. That way the RMS profile
-- of the render is a direct probe of LV2 automation delivery.

Session:set_session_range_is_free(false)
if Session.set_session_extents then
  Session:set_session_extents(Temporal.timepos_t(0), Temporal.timepos_t(N_SAMP))
end
Session:save_state("")

local f = io.open(STATE_OUT, "w")
f:write(string.format([[{
  "session_dir": "%s/%s",
  "sr_hz": %d,
  "duration_s": %f,
  "track": "%s",
  "processors": [
    { "slot": 0, "kind": "Lua", "name": "SinGen", "params": { "Frequency": 220.0, "Gain_dB": -12.0 } },
    { "slot": 1, "kind": "VST3", "name": "Surge XT Effects", "fx_type_norm": 0.28, "output_mix": 0.35, "role": "chorus" },
    { "slot": 2, "kind": "LV2", "name": "ACE Reverb", "wet_mix_idx": %d, "wet_mix_ordinal": %d, "wet_start": %f, "wet_end": %f, "role": "reverb" }
  ],
  "automation": { "target": "ACE Reverb wet-mix (LV2)", "from": %f, "to": %f, "n_points": 33, "duration_s": %f, "track_amp_static": true }
}]],
  SESS_DIR, SESS_NAME, SR, DUR_S, track:name(),
  mix_idx, automated_n, automation_range_from, automation_range_to,
  automation_range_from, automation_range_to, DUR_S))
f:close()

close_session()
io.write("[DONE] gap_closure_lv2_reverb.lua complete\n")
