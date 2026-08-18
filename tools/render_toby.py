"""Render a MIDI file with Toby Fox's MEGALOVANIA palette, not a chiptune one.

The other four pieces in this repo go through render_audio.py, which is an
NES-style synth: pulse, square, triangle, filtered noise.  MEGALOVANIA was not
made that way.  Toby Fox built it in FL Studio out of

    3xOsc                     stock three-oscillator synth, detuned saw and
                              square -- the leads
    Shreddage Bass: Picked    a sampled PICKED electric bass -- the riff
    Ollie Waton Drums         a sampled acoustic kit
    Violin Detache            bowed strings, short strokes

so this renderer models those four things instead.

    3xOsc      -> three oscillators per voice, detuned in cents and spread in
                  stereo, with randomised start phase (3xOsc's "phase rand")
    picked bass-> Karplus-Strong plucked string, which is what actually gives a
                  picked bass its bright transient and fast-decaying overtones.
                  A short bandpassed noise burst is mixed in front of it for the
                  pick itself, and the whole thing runs into a soft clipper for
                  amp saturation.
    drums      -> synthesised once at full length and then sliced per hit, the
                  way a sample library behaves, with real bodies rather than
                  noise bursts
    strings    -> bowed: slow attack, 5.5 Hz vibrato, bow noise

    python3 render_toby.py ../score/ground-state.mid ../score/ground-state.mp3
"""

import struct
import sys
import numpy as np

from render_audio import parse_midi, tick_to_sec, SR

RNG = np.random.default_rng(7)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def noise_band(n, lo, hi):
    """White noise shaped to a band, via the spectrum -- no filter state."""
    x = RNG.standard_normal(n)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1.0 / SR)
    X *= ((f >= lo) & (f <= hi))
    return np.fft.irfft(X, n)


def adsr(n, a, d, s, r):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    a = min(a, max(1, n // 3))
    d = min(d, max(1, n // 3))
    body = max(0, n - a - d)
    e = np.concatenate([np.linspace(0, 1, a, endpoint=False),
                        np.linspace(1, s, d, endpoint=False),
                        np.full(body, s)])[:n]
    if len(e) < n:
        e = np.pad(e, (0, n - len(e)), constant_values=s)
    rel = min(r, n)
    if rel > 1:
        e[-rel:] *= np.linspace(1, 0, rel)
    return e


def wave(kind, ph):
    if kind == "saw":
        return 2.0 * ph - 1.0
    if kind == "square":
        return np.where(ph < 0.5, 1.0, -1.0)
    if kind == "pulse25":
        return np.where(ph < 0.25, 1.0, -1.0)
    return np.sin(2 * np.pi * ph)


def osc3(kind, freq, n, detune, spread, subosc=0.0):
    """3xOsc: three oscillators, detuned in cents, phases randomised.

    Returns (left, right) so the detuning also widens the image, which is what
    3xOsc's stereo detune does and a large part of why the leads sound big.
    """
    t = np.arange(n) / SR
    l = np.zeros(n)
    r = np.zeros(n)
    for i, cents in enumerate((-detune, 0.0, detune)):
        f = freq * (2.0 ** (cents / 1200.0))
        ph = (t * f + RNG.random()) % 1.0        # phase rand
        sig = wave(kind, ph)
        pan = (i - 1) * spread
        l += sig * (1.0 - max(0.0, pan))
        r += sig * (1.0 + min(0.0, pan))
    if subosc:
        ph = (t * freq * 0.5 + RNG.random()) % 1.0
        sub = wave("square", ph) * subosc
        l += sub
        r += sub
    k = 1.0 / (3.0 + subosc)
    return l * k, r * k


def pluck(freq, n, damp=0.996, bright=0.5):
    """Karplus-Strong.  Processed one period at a time, so it stays vectorised.

    This is the picked-bass core: a noise-filled delay line of one period,
    lowpass-averaged on every pass.  High partials die first, exactly like a
    real string, which is what a square wave can never do.
    """
    P = max(2, int(round(SR / freq)))
    buf = RNG.standard_normal(P)
    # 'bright' sets how much high content the pick leaves in the string
    if bright < 1.0:
        k = max(1, int(P * (1.0 - bright) * 0.5))
        if k > 1:
            buf = np.convolve(buf, np.ones(k) / k, mode="same")
    buf /= max(1e-9, np.abs(buf).max())
    out = np.empty(n)
    pos = 0
    while pos < n:
        take = min(P, n - pos)
        out[pos:pos + take] = buf[:take]
        buf = damp * 0.5 * (buf + np.roll(buf, -1))
        pos += P
    return out


def picked_bass(freq, n, gain_drive=2.6):
    """Shreddage-style picked bass: pick transient + string + amp saturation."""
    body = pluck(freq, n, damp=0.9975, bright=0.75)
    body *= adsr(n, 0.001, 0.05, 0.85, 0.04)
    # the pick itself -- a short bright scrape in front of the note
    pk = min(n, int(0.012 * SR))
    click = np.zeros(n)
    click[:pk] = noise_band(pk, 1200, 6000) * np.linspace(1, 0, pk) ** 2
    sig = body + click * 0.62
    # a little octave-down sine so the low notes have weight on small speakers
    t = np.arange(n) / SR
    sig += np.sin(2 * np.pi * freq * t) * adsr(n, 0.002, 0.12, 0.5, 0.05) * 0.26
    return np.tanh(sig * gain_drive) / np.tanh(gain_drive)


def bowed(freq, n):
    """Violin detache: slow-ish attack, vibrato, a breath of bow noise."""
    t = np.arange(n) / SR
    vib = 1.0 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t / 0.18, 0, 1)
    ph = np.cumsum(freq * vib) / SR
    sig = wave("saw", ph % 1.0)
    sig = sig - np.convolve(sig, np.ones(5) / 5, mode="same") * 0.35
    sig += noise_band(n, 2000, 7000) * 0.05
    return sig * adsr(n, 0.055, 0.10, 0.85, 0.09)


def organ(freq, n):
    """Drawbar-ish: fundamental, octave, twelfth, fifteenth."""
    t = np.arange(n) / SR
    sig = sum(a * np.sin(2 * np.pi * freq * m * t + RNG.random())
              for m, a in ((1, 1.0), (2, 0.5), (3, 0.3), (4, 0.22)))
    return sig * 0.45 * adsr(n, 0.012, 0.08, 0.9, 0.05)


# ---------------------------------------------------------------------------
# the kit -- built once at full length, then sliced, like a sample library
# ---------------------------------------------------------------------------
def _kick():
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    f = 120 * np.exp(-t * 34) + 44
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5)
    click = np.zeros(n)
    k = int(0.006 * SR)
    click[:k] = noise_band(k, 1500, 5000) * np.linspace(1, 0, k)
    return np.tanh((body + click * 0.35) * 1.6)


def _snare():
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    tone = (np.sin(2 * np.pi * 185 * t) + 0.7 * np.sin(2 * np.pi * 331 * t))
    tone *= np.exp(-t * 22) * 0.5
    wires = noise_band(n, 900, 9000) * np.exp(-t * 13)
    crack = np.zeros(n)
    k = int(0.004 * SR)
    crack[:k] = noise_band(k, 2000, 8000) * np.linspace(1, 0, k)
    return np.tanh((tone + wires * 0.9 + crack * 0.6) * 1.4)


def _tom(f0):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = f0 * np.exp(-t * 9) + f0 * 0.55
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    return body + noise_band(n, 400, 3000) * np.exp(-t * 30) * 0.12


def _metal(n, decay, lo, hi, ring):
    t = np.arange(n) / SR
    sig = noise_band(n, lo, hi) * np.exp(-t * decay)
    for f in ring:
        sig += np.sin(2 * np.pi * f * t + RNG.random()) * np.exp(-t * decay * 1.3) * 0.10
    return sig


KIT = {
    "kick":  _kick(),
    "snare": _snare(),
    "tom":   _tom(210),
    "tom2":  _tom(150),
    "hat":   _metal(int(0.10 * SR), 62, 6000, 14000, (7300, 9100, 11400)),
    "ohat":  _metal(int(0.55 * SR), 8.5, 5000, 14000, (7300, 9100, 11400)),
    "ride":  _metal(int(0.90 * SR), 4.2, 3000, 12000, (2400, 3900, 5300)),
    "crash": _metal(int(1.60 * SR), 2.3, 1200, 13000, (1900, 3100, 4700)),
}
for _k in KIT:
    KIT[_k] = KIT[_k] / max(1e-9, np.abs(KIT[_k]).max())

DRUM_MAP = {36: ("kick", 0.88), 38: ("snare", 0.74), 41: ("tom2", 0.60),
            42: ("hat", 0.32), 46: ("ohat", 0.36), 47: ("tom", 0.60),
            49: ("crash", 0.52), 51: ("ride", 0.34)}


# ---------------------------------------------------------------------------
# channel -> voice.  Track order in export_groundstate.py sets these.
# ---------------------------------------------------------------------------
#            builder     gain   pan   detune(cents) spread
VOICES = {
    0: ("saw3",   0.300,  0.00, 16.0, 0.30),   # Lead 1   3xOsc supersaw
    1: ("sq3",    0.180, -0.30, 11.0, 0.26),   # Lead 2   3xOsc square
    2: ("bow",    0.140,  0.22,  0.0, 0.00),   # Violin detache
    3: ("organ",  0.100,  0.30,  0.0, 0.00),   # Organ pad
    4: ("sq3",    0.110,  0.40,  9.0, 0.34),   # Stabs
    5: ("dist",   0.170, -0.38, 14.0, 0.22),   # Distorted guitar
    6: ("bass",   0.400,  0.00,  0.0, 0.00),   # PICKED BASS -- the protagonist
    7: ("bass",   0.200,  0.12,  0.0, 0.00),   # picked bass, octave up
    8: ("sine",   0.190,  0.00,  0.0, 0.00),   # sub
}
DELAY = {0: 0.20, 1: 0.10, 2: 0.10}


def build_note(ch, freq, n):
    kind, g, pan, det, spread = VOICES.get(
        ch, ("saw3", 0.10, 0.0, 10.0, 0.2))
    if kind == "bass":
        s = picked_bass(freq, n)
        return s, s
    if kind == "sine":
        t = np.arange(n) / SR
        s = np.sin(2 * np.pi * freq * t) * adsr(n, 0.006, 0.10, 0.9, 0.06)
        return s, s
    if kind == "bow":
        s = bowed(freq, n)
        return s, s
    if kind == "organ":
        s = organ(freq, n)
        return s, s
    if kind == "dist":
        l, r = osc3("saw", freq, n, det, spread, subosc=0.5)
        e = adsr(n, 0.002, 0.05, 0.80, 0.04)
        return np.tanh(l * 4.5) * e, np.tanh(r * 4.5) * e
    wf = "saw" if kind == "saw3" else "square"
    l, r = osc3(wf, freq, n, det, spread)
    e = adsr(n, 0.006, 0.07, 0.78, 0.06)
    return l * e, r * e


def render(midi_path, out_path):
    events, div, tempos = parse_midi(midi_path)
    notes, live = [], {}
    for tick, ch, p, v, on in events:
        if on:
            live.setdefault((ch, p), []).append((tick, v))
        else:
            st = live.get((ch, p))
            if st:
                t0, vel = st.pop(0)
                notes.append((ch, p, vel, tick_to_sec(t0, div, tempos),
                              tick_to_sec(tick, div, tempos)))
    total = max(n[4] for n in notes) + 3.0
    L = int(total * SR)
    out = np.zeros((L, 2), dtype=np.float32)
    wet = np.zeros((L, 2), dtype=np.float32)
    bpm = 60e6 / tempos[0][1]

    for ch, p, vel, t0, t1 in notes:
        i0 = int(t0 * SR)
        n = max(int((t1 - t0) * SR), int(0.04 * SR))
        if i0 + n > L:
            n = L - i0
        if n <= 1:
            continue
        amp = (vel / 127.0) ** 1.3
        if ch == 9:
            kind, g = DRUM_MAP.get(p, ("hat", 0.2))
            src = KIT[kind]
            n = min(len(src), L - i0)
            l = r = src[:n] * g * amp
        else:
            _k, g, pan, _d, _s = VOICES.get(ch, ("saw3", 0.10, 0.0, 10.0, 0.2))
            f = 440.0 * 2 ** ((p - 69) / 12.0)
            l, r = build_note(ch, f, n)
            l = l * g * amp * (1 - max(0.0, pan)) ** 0.5
            r = r * g * amp * (1 + min(0.0, pan)) ** 0.5
        out[i0:i0 + n, 0] += l[:n]
        out[i0:i0 + n, 1] += r[:n]
        send = DELAY.get(ch)
        if send:
            wet[i0:i0 + n, 0] += l[:n] * send
            wet[i0:i0 + n, 1] += r[:n] * send

    for beats, gain in ((0.75, 0.36), (1.5, 0.16)):
        d = int(beats * 60.0 / bpm * SR)
        if d < L:
            out[d:] += wet[:L - d] * gain

    out = np.tanh(out * 1.2) / 1.2
    out /= max(1e-9, np.abs(out).max())
    out *= 0.89
    pcm = (out * 32767).astype("<i2")
    data = pcm.tobytes()

    if out_path.endswith(".mp3"):
        import lameenc
        enc = lameenc.Encoder()
        enc.set_bit_rate(192)
        enc.set_in_sample_rate(SR)
        enc.set_channels(2)
        enc.set_quality(2)
        blob = enc.encode(data) + enc.flush()
        open(out_path, "wb").write(blob)
        size = len(blob)
    else:
        with open(out_path, "wb") as f:
            f.write(b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVE")
            f.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, 2, SR, SR * 4, 4, 16))
            f.write(b"data" + struct.pack("<I", len(data)) + data)
        size = len(data)
    print(f"wrote {out_path}  {int(total//60)}:{total%60:04.1f}  "
          f"{len(notes)} notes  {size/1e6:.1f} MB")


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else "../score/ground-state.mid",
           sys.argv[2] if len(sys.argv) > 2 else "../score/ground-state.wav")
