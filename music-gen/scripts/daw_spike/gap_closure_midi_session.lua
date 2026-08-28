-- Helper Lua: build the M-DAW-SPIKE-1/gap-closure MIDI-import session.
-- Bare-bones: one stereo audio track called "chain" with no processors.
-- The Python driver then hand-authors <Source>+<Region>+<Playlist>
-- referencing the pre-rendered fluidsynth WAV.
io.stdout:setvbuf("no")
io.stderr:setvbuf("no")

local ROOT      = "/home/user/long-exposure-runs/music-gen"
local SESS_DIR  = ROOT .. "/data/daw_spike/sessions/gap_closure_midi"
local SESS_NAME = "gap_closure_midi"
local SR        = 48000
local DUR_S     = 8.0
local N_SAMP    = math.floor(SR * DUR_S)

os.execute("rm -rf '" .. SESS_DIR .. "'")
os.execute("mkdir -p '" .. ROOT .. "/data/daw_spike/sessions'")
local s = create_session(SESS_DIR, SESS_NAME, SR)
if s == nil then io.write("create_session_nil\n"); error("create_session") end
Session = s

local tl = Session:new_audio_track(2, 2, nil, 1, "chain",
                                   ARDOUR.PresentationInfo.max_order,
                                   ARDOUR.TrackMode.Normal, true)
local track = nil
for t in tl:iter() do track = t end
assert(track, "audio track was not created")

Session:set_session_range_is_free(false)
if Session.set_session_extents then
  Session:set_session_extents(Temporal.timepos_t(0), Temporal.timepos_t(N_SAMP))
end
Session:save_state("")
close_session()
io.write("[DONE] gap_closure_midi_session.lua complete\n")
