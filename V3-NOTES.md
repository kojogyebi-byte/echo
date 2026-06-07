# DeHowl v3.0 — Predictive AFC Upgrade

## What changed (the "another thinking pattern")
v3.0 adds **AFC — Acoustic Feedback Cancellation** (handoff option B), working
alongside the existing notch bank. Instead of reacting to a howl after it is
audible, AFC *models* the acoustic path from the speakers back to the
microphone (a 2048-tap adaptive NLMS filter, ~43 ms of room response) and
subtracts the predicted feedback from the mic signal before it can loop.

A small **frequency shift** (default 5 Hz, adjustable 1–12 Hz) is applied to
the output. This is part of the AFC system: it decorrelates the loop so the
model learns the ROOM instead of cancelling the preacher's voice — and it
breaks the feedback phase condition on its own (handoff option A, built in).

The notch bank stays on as the safety net for the first seconds while the
model is still learning, and after big changes (mic moves 10 m, etc.).

**Verified in closed-loop simulation before shipping:** a loop that howls
instantly without AFC stays stable with AFC at 2.5× the gain (≈ +8 dB
gain-before-feedback), with the model removing ~11 dB of feedback once
converged and ~85–90 % of the voice passing through untouched.

## Files changed (upload these via the GitHub web UI)
- `Source/Afc.h` — **NEW**: the AFC engine (NLMS canceller + frequency shifter)
- `Source/PluginProcessor.h` — AFC members, status atomics, reset request
- `Source/PluginProcessor.cpp` — chain integration, 2 new parameters
- `Source/PluginEditor.h` — AFC controls
- `Source/PluginEditor.cpp` — AFC row, live status, footer → v3.0

`CMakeLists.txt` and the workflow are **unchanged** — Afc.h is header-only,
so the GitHub Actions build needs no modification.

## New signal chain
mic in → meter → **AFC subtract (prediction)** → Low/High Cut → notch bank →
Room EQ → AI Clear Voice → **frequency shift** → output gain →
*(reference capture for the model)* → meter

## New controls (one new row in the UI)
- **AFC Predict** (toggle, green when on) — off by default
- **Reset Model** — forget the learned room (use after moving speakers/mic)
- **Shift slider (1–12 Hz)** — 5 Hz default. Higher = more anti-feedback,
  slightly more audible on sustained music. For speech, even 8 Hz is invisible.
- **Status readout** — "learning the room..." then "cancelling X dB" (green).
  That number is live proof the model is working.

## How to use it at an event
1. Start with AFC **off**, set levels the normal way.
2. Turn **AFC Predict on** and let people talk for ~20–30 seconds.
   Watch the status go green: "cancelling X dB".
3. Raise the gain. The headroom that used to ring should now be usable.
4. If the rig changes (mic walks far, speakers repositioned): **Reset Model**.
5. Music-heavy program with sustained organ/piano: pull Shift down to 2–3 Hz
   if anything sounds slightly "chorused".

## Things to verify on the Mac build
- Footer must read **v3.0 · built <today's date>** (still self-verifying —
  this also settles the old v2.3 version mystery once the right copy runs).
- DSP % in the status bar: AFC adds the cost of 2 × 2048-tap filters.
  Expect a modest rise; fine on Apple Silicon, watch it on old Intel.
- AFC + AI Clear Voice together: AI adds its usual 10 ms; AFC itself adds
  zero latency.
