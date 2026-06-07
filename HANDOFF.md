# DeHowl — Project Handoff Brief
**App:** DeHowl — Live Feedback Suppressor (standalone macOS app)
**Creator:** Kwadwo Gyebi · **Company:** Shamaapps
**Current version:** v3.0 (footer shows version + compile date — self-verifying builds)
**Status:** v3.0 source builds clean (verified against JUCE 8.0.4, zero warnings);
awaiting first live test of the new AFC engine.

---

## 1. What the app does
Real-time live-sound processor. Two independent anti-feedback systems:

- **Predictive AFC (NEW in v3.0):** 2048-tap NLMS adaptive filter models the
  loudspeaker→room→microphone path from the app's own output (the speaker
  feed) and subtracts the predicted feedback from the raw mic signal —
  prediction, not reaction. A single-sideband frequency shifter (Hilbert-pair
  allpass design, 1–12 Hz, default 5 Hz) on the output decorrelates the
  closed loop so the model learns the ROOM instead of cancelling the voice,
  and breaks the feedback phase condition on its own. Engine in Source/Afc.h
  (header-only, JUCE-free, unit-testable). Verified in closed-loop simulation:
  a loop that howls bare stays stable at 2.5× the gain (≈ +8 dB GBF), ~11 dB
  ERLE converged, ~85–90 % voice retention. Adaptation step kMu = 0.02 was
  tuned by sweep — DO NOT raise it casually; at 0.15 the closed-loop bias
  cancels ~half the voice. GUI: AFC Predict toggle, Reset Model, Shift
  slider, live status ("learning..." / "cancelling X dB" in green).
- **De-feedback notch bank:** FFT detection (8192-point, ~5.9 Hz/bin, 75 %
  overlap, ~43 ms reaction, parabolic interpolation for sub-Hz accuracy)
  drives up to 12 adaptive notch filters (double-precision biquads, Q up to
  200, self-centering on drifting feedback). Stays on as the safety net while
  the AFC model is learning. Zero-latency audio path (pure IIR).
- **AI Clear Voice:** RNNoise recurrent neural network (xiph/rnnoise v0.1.1,
  BSD, weights embedded, fully offline). 48 kHz only; 10 ms latency when on.
- **Room Learn EQ:** statistical learning of the room's long-term spectrum;
  up to 6 gentle wide cuts (max 6 dB, Q=4) on persistent resonances.
- **Vocal band:** clickable Low Cut (default 120 Hz) and High Cut (default
  9 kHz) toggles; filters run BEFORE the detector.
- **Other:** Bypass, Latch/Auto-Release, big IN/OUT meters with dB, system
  CPU % + audio DSP % readout, in-app Audio Devices panel, Legal page (click
  the footer credit), Shamaapps branding, custom dark GUI.

## 2. Signal chain (v3.0)
input meter → bypass? → **AFC subtract (prediction)** → vocal band HPF/LPF →
(analyser feed) → notch bank → room-EQ tones → RNNoise →
**AFC frequency shift** → output gain → *(AFC reference capture)* → output meter

The AFC subtraction runs FIRST on the untouched mic signal (the model maps
speaker feed → mic arrival, so it must see the mic as received). The
reference capture is the exact post-gain speaker feed. Detector and notch
bank therefore see pre-cleaned audio — fewer false notches.

## 3. Technical stack
- JUCE 8.0.4 via CMake FetchContent; C++20; formats: Standalone only
  (one-line change re-enables AU/VST3). Universal binary (arm64 + x86_64).
- RNNoise built from source as a static lib in CMakeLists.
- Afc.h is header-only — no CMakeLists change was needed for v3.0.
- Critical fix: JUCE standalone mutes audio input by default — the editor
  force-unmutes via StandalonePluginHolder::getMuteInputValue().setValue(false).
- Detection details: silence gate (-80 dBFS skips FFT), prefix-sum local
  averages, growth fast-trigger (9+ dB growth → notch in ~85 ms), harmonic
  check (peaks with strong 2f/3f treated as music, need ~340 ms).
- AFC implementation notes: double-written reference ring keeps the predict/
  update loops contiguous (vectorisable); 4-way unrolled dot product with
  double accumulators; adaptation gated on reference energy; update error
  clamped; tap leakage (~1 min forget); divergence guard halves taps if the
  "cleaned" signal is louder than raw for ~50 ms; prediction hard-clamped.

## 4. Build & deployment (no terminal — user requirement!)
The user (Faustina, working with Kwadwo) does NOT use Terminal or Xcode.
- Files uploaded via the GitHub web UI.
- GitHub Actions (macos-latest) builds on every push: configure → universal
  build → ad-hoc codesign → ditto zip → artifact named
  "DeHowl-macOS-build-N" (run number). Workflow: .github/workflows/build-macos.yml
  (a plain-text copy lives in github-workflow-COPY-THIS.txt).
- Install: download artifact → unzip twice → drag to Applications →
  first launch needs System Settings → Privacy & Security → Open Anyway.
- Always confirm the footer shows the expected version + today's compile date
  (this resolved the old "running app shows v2.3" mystery — a stale copy
  outside /Applications).

## 5. Open issues / next steps
- **First live test of AFC**: follow the test plan in V3-NOTES.md. Watch the
  DSP % readout — AFC adds two 2048-tap filters (fine on Apple Silicon,
  observe on older Intel).
- If voice ever sounds "thin" with AFC on: raise the Shift slightly (more
  decorrelation) or Reset Model; if sustained music sounds "chorused": lower
  the Shift to 2–3 Hz.
- 12/12 notches filled with low-frequency cluster during early testing —
  mitigated by the clickable Low Cut, and further by AFC pre-cleaning the
  detector input.
- JUCE free-tier license: splash shown; paid license needed if Shamaapps
  revenue exceeds the JUCE 8 EULA threshold. Legal docs: LICENSE.md,
  THIRD-PARTY-LICENSES.md, in-app Legal page (BSD notice for RNNoise
  legally required and included).
- Possible future directions: loop-gain limiter mode (ducking), one-knob
  AUTO mode choosing notch/shift/AFC per situation, browser (Web Audio) or
  iPad deliverable.

## 6. Repository contents
CMakeLists.txt · Source/ (Afc.h, PluginProcessor.h/.cpp, PluginEditor.h/.cpp,
SystemCpu.h) · Assets/ (icon.png, icon_small.png) · make_icon.py ·
.github/workflows/build-macos.yml · github-workflow-COPY-THIS.txt ·
LICENSE.md · THIRD-PARTY-LICENSES.md · README.md · V3-NOTES.md ·
BUILD-WITHOUT-TERMINAL.md (child-simple build guide) · .gitignore
