# DeHowl — Live Feedback Suppressor (Standalone Mac App)
### by Kwadwo Gyebi · Shamaapps

A standalone macOS app by **Kwadwo Gyebi (Shamaapps)** — with its own icon and GUI — that suppresses acoustic
feedback in real time — similar in concept to the Alpha Labs De-Feedback
plugin and hardware units like the dbx AFS or Behringer FBQ.

It works on two levels:

1. **Predictive AFC (v3.0):** an adaptive filter *models* the acoustic path
   from the loudspeakers back to the microphone and subtracts the predicted
   feedback before it can loop — the same principle modern conferencing
   systems use, adapted for live sound. A small frequency shift (default 5 Hz)
   on the output continuously breaks the feedback phase condition and keeps
   the model honest. Typically worth several extra dB of gain-before-feedback,
   with **no tonal holes**.
2. **Adaptive notch bank:** the classic approach — an FFT continuously
   analyses the input, detects the narrow sustained peaks characteristic of
   feedback ("howling"), and drops a narrow notch filter on each one
   automatically. This stays on as the safety net while the AFC model is
   still learning and after big changes in the room.

The audio path is pure IIR filtering plus a sample-by-sample subtraction, so
it adds **zero latency** — safe to put in a live signal chain.

The GUI shows the control knobs, big IN/OUT meters, a live AFC status
("cancelling X dB"), and a panel displaying every active notch with its
frequency and depth.

---

## Building on your Mac (Apple Silicon or Intel)

### 1. One-time setup

1. Install **Xcode Command Line Tools** (free):

       xcode-select --install

2. Install **Homebrew** if needed (https://brew.sh), then:

       brew install cmake

### 2. Build

In Terminal, `cd` into this folder (the one containing `CMakeLists.txt`):

    cmake -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build --config Release -j8

- The first configure downloads the JUCE framework automatically (needs
  internet, a few minutes). After that it's cached.
- Full first build: roughly 5–10 minutes.

### 3. Install & run

The finished app is at:

    build/DeHowl_artefacts/Release/Standalone/DeHowl.app

Drag it into **/Applications** like any normal app. It has its own icon
(notch-curve logo, generated from `Assets/icon.png`).

First launch:
- macOS asks for **microphone permission** — allow it.
- Open **Options → Audio/MIDI Settings** inside the app to pick your audio
  interface (input = the mic/desk feed, output = toward the PA).

Because you built it on your own machine, no code-signing or notarization is
needed.

### Want the DAW plug-in versions too?

Edit one line in `CMakeLists.txt`:

    FORMATS Standalone        →        FORMATS Standalone AU VST3

Rebuild, and the AU/VST3 are compiled and auto-copied into
`~/Library/Audio/Plug-Ins/`.

---

## Using it live

Feed the signal you want protected through the app (e.g., interface input →
DeHowl → interface output → PA), or rebuild as a plugin and insert it on the
vocal channel / main bus.

| Control       | What it does                                                                  |
|---------------|-------------------------------------------------------------------------------|
| Sensitivity   | How aggressively it flags feedback. Higher = catches howls faster, but may occasionally notch a sustained musical note. 60–75 is a good live setting. |
| Max Notches   | How many simultaneous notch filters it may use (up to 12). 8 is typical.       |
| Max Depth     | Deepest cut allowed per notch, in dB. 18 dB handles most rooms.                |
| Width (Q)     | Higher Q = narrower, more surgical notches (less audible). 30 is a good start. |
| Mode          | **Latch** (recommended live): notches stay once set. **Auto Release**: notches fade ~8 s after the feedback stops — useful for soundcheck. |
| Clear Notches | Wipes all notches (e.g., after moving mics or speakers).                       |
| Output        | Makeup gain. The meter at the top-right shows output level.                    |
| AFC Predict   | **v3.0** — predictive feedback cancellation. Turn on, let people talk ~30 s, watch the status go green: "cancelling X dB". Then raise the gain. |
| Reset Model   | Forgets the learned room model. Use after moving speakers or the mic walks far. |
| Shift slider  | The decorrelating frequency shift, 1–12 Hz (default 5). Higher = stronger anti-feedback; on sustained organ/piano pull it down to 2–3 Hz if anything sounds slightly "chorused". Invisible on speech. |

**Soundcheck tip ("ringing out the room"):** set Mode to Latch, slowly raise
the master fader until the system just starts to ring, let DeHowl notch it,
and repeat 3–4 times. You gain several dB of headroom before feedback.
**With AFC on**, do this *after* the model has learned (status shows
"cancelling") — the ring point will already be noticeably higher.

---

## Project layout

    CMakeLists.txt            Build config (fetches JUCE 8 automatically, sets app icon)
    Assets/icon.png           App icon (1024 px) — replace to rebrand
    Assets/icon_small.png     App icon (512 px)
    make_icon.py              Script that generated the icons (optional)
    Source/Afc.h              v3.0: predictive AFC engine (NLMS canceller + frequency shifter)
    Source/PluginProcessor.*  DSP: AFC + FFT feedback detection + adaptive notch bank
    Source/PluginEditor.*     GUI: custom look-and-feel, knobs, meters, AFC status, notch display

## How the predictive AFC works (short version — v3.0)

1. Every output sample (the exact speaker feed) is stored in a reference
   history. A 2048-tap adaptive filter (~43 ms of room response at 48 kHz)
   learns, via NLMS, how that output comes back into the microphone.
2. Each mic sample has the *predicted* feedback subtracted before anything
   else — prediction instead of reaction, so converged feedback never
   becomes audible at all.
3. Because the reference is the app's own output (a closed loop), a naive
   adaptive filter would start cancelling the talker's voice. Three defences:
   a small single-sideband frequency shift on the output decorrelates the
   loop; the adaptation is deliberately slow and gated; and a divergence
   guard retreats the model if "cleaned" ever gets louder than raw.
4. The status row shows the live ERLE — how many dB of feedback the model is
   currently removing.

## How the notch detection works (short version)

1. A 4096-point FFT runs on a mono mix of the input every ~43 ms.
2. A bin becomes a feedback *candidate* when it is a local spectral maximum
   standing 12–30 dB (depending on Sensitivity) above the surrounding spectrum.
3. A candidate persisting ~3 frames (~130 ms) is treated as feedback — music
   almost never holds a single dominant pure tone that way; feedback does.
4. A narrow peaking-EQ cut is placed at the interpolated frequency, starting
   at −12 dB and biting deeper (up to Max Depth) if the howl persists.
5. In Auto Release mode, notches fade away ~8 s after their frequency goes quiet.



## Audio interfaces & device selection

Click the **Audio Devices** button in the app to choose your input and output
device, sample rate, and buffer size — without leaving the main window.

**No drivers are bundled, because macOS doesn't work that way.** All audio
interfaces talk to macOS through Apple's **Core Audio** system, and the app
automatically sees every device Core Audio sees. That includes:

- **Focusrite** Scarlett / Clarett / Vocaster — class-compliant, plug-and-play
- **Solid State Logic (SSL)** SSL 2 / 2+ / 12 — class-compliant
- **PreSonus** AudioBox / Studio series / Quantum
- **Universal Audio** Volt (plug-and-play) and Apollo (install UA software)
- **Behringer** UMC / X32 card, **MOTU** M-series, **RME** (install RME driver),
  **Audient**, **Zoom**, **Steinberg/Yamaha**, mixers with USB audio, etc.
- The Mac's built-in mic/output, and **Aggregate Devices** you create in
  Audio MIDI Setup (to combine interfaces)

Rule of thumb: if the interface shows up in **System Settings → Sound**, it
shows up in DeHowl. The few brands that need a vendor driver (RME, UA Apollo,
some older units) install it system-wide from the manufacturer's website —
after that, the device appears in DeHowl like any other.

The app remembers your device selection between launches.

## Performance notes (v1.1 optimisations)

- **Silence gate:** the FFT analyser shuts off entirely below ~-80 dBFS input,
  so the app idles at near-zero CPU between songs/speech. Filtering and
  auto-release keep working.
- **O(1) spectral averaging:** peak detection uses prefix sums instead of a
  96-bin loop per peak.
- **Zero-latency audio path unchanged:** up to 24 biquads total — negligible.
- **GUI only repaints on change** and fully pauses when the window is hidden
  or minimised. Keep the window minimised during the service for minimum CPU.
- **macOS specifics:** JUCE's FFT automatically uses Apple's Accelerate
  (vDSP) framework, and release builds use -O3 + link-time optimisation.

Detection quality also improved:
- A peak that **grows 9+ dB** is treated as a howl building up and is notched
  after ~85 ms instead of ~130 ms (feedback grows; music doesn't).
- A peak with **strong 2nd/3rd harmonics** is treated as a held musical note
  and needs ~340 ms of persistence — far fewer false notches on vocals,
  organ, and sustained instruments.

Practical tips for lowest CPU on the Mac:
- Use a hardware buffer size of 256 samples in Audio/MIDI Settings (lower
  buffers raise CPU with no benefit — the suppressor itself adds no latency).
- 48 kHz is the sweet spot; 96 kHz doubles the work for no audible gain here.
- Keep the app window minimised once it's set up.

## License note

JUCE 8 is free under its standard license for personal use and companies under
the revenue threshold (a small JUCE splash shows on first window open), or
under GPLv3. See https://juce.com/legal/juce-8-licence/
