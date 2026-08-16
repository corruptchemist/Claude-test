"""Render a MIDI file to WAV with a small chiptune synth.

No soundfont needed -- square/pulse/saw/triangle oscillators plus filtered
noise for the kit, which is the right palette for this music anyway.

    python3 render_audio.py ../score/afterlight.mid ../score/afterlight.wav
"""

import struct
import sys
import numpy as np

SR = 32000


# ---------------------------------------------------------------------------
# MIDI parsing
# ---------------------------------------------------------------------------
def read_varlen(b, i):
    v = 0
    while b[i] & 0x80:
        v = (v << 7) | (b[i] & 0x7F)
        i += 1
    return (v << 7) | b[i], i + 1


def parse_midi(path):
    d = open(path, "rb").read()
    assert d[:4] == b"MThd"
    _fmt, ntrk, div = struct.unpack(">HHH", d[8:14])
    pos = 14
    events = []                # (tick, chan, pitch, vel, on)
    tempos = []                # real tempo events only
    for _ in range(ntrk):
        ln = struct.unpack(">I", d[pos + 4:pos + 8])[0]
        body = d[pos + 8:pos + 8 + ln]
        pos += 8 + ln
        i, tick, running = 0, 0, None
        while i < len(body):
            dt, i = read_varlen(body, i)
            tick += dt
            b = body[i]
            if b == 0xFF:
                mt = body[i + 1]
                i += 2
                l, i = read_varlen(body, i)
                if mt == 0x51:
                    tempos.append((tick, int.from_bytes(body[i:i + 3], "big")))
                i += l
            elif b in (0xF0, 0xF7):
                i += 1
                l, i = read_varlen(body, i)
                i += l
            else:
                if b & 0x80:
                    running = b
                    i += 1
                st = running
                hi, ch = st & 0xF0, st & 0x0F
                if hi in (0x90, 0x80):
                    p, v = body[i], body[i + 1]
                    events.append((tick, ch, p, v, hi == 0x90 and v > 0))
                    i += 2
                elif hi in (0xC0, 0xD0):
                    i += 1
                else:
                    i += 2
    # keep the LAST tempo written at any given tick, and only fall back to
    # 120 bpm if the file genuinely never states one
    tempos.sort(key=lambda x: x[0])
    dedup = {}
    for t, us in tempos:
        dedup[t] = us
    tempos = sorted(dedup.items())
    if not tempos or tempos[0][0] != 0:
        tempos.insert(0, (0, 500000))
    return events, div, tempos


def tick_to_sec(tick, div, tempos):
    sec, last_t, last_us = 0.0, 0, tempos[0][1]
    for t, us in tempos[1:]:
        if t >= tick:
            break
        sec += (t - last_t) / div * (last_us / 1e6)
        last_t, last_us = t, us
    return sec + (tick - last_t) / div * (last_us / 1e6)


# ---------------------------------------------------------------------------
# oscillators
# ---------------------------------------------------------------------------
def osc(kind, freq, n):
    t = np.arange(n) / SR
    ph = (t * freq) % 1.0
    if kind == "pulse25":
        return np.where(ph < 0.25, 1.0, -1.0)
    if kind == "pulse12":
        return np.where(ph < 0.125, 1.0, -1.0)
    if kind == "square":
        return np.where(ph < 0.5, 1.0, -1.0)
    if kind == "saw":
        return 2.0 * ph - 1.0
    if kind == "tri":
        return 4.0 * np.abs(ph - 0.5) - 1.0
    return np.sin(2 * np.pi * freq * t)


def env(n, a, d, s, r):
    """Simple ADSR in seconds, clamped to the note length."""
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    a = min(a, max(1, n // 4))
    d = min(d, max(1, n // 4))
    body = max(0, n - a - d)
    e = np.concatenate([
        np.linspace(0, 1, a, endpoint=False),
        np.linspace(1, s, d, endpoint=False),
        np.full(body, s),
    ])[:n]
    if len(e) < n:
        e = np.pad(e, (0, n - len(e)), constant_values=s)
    rel = min(r, n)
    if rel > 1:
        e[-rel:] *= np.linspace(1, 0, rel)
    return e


# channel -> (waveform, gain, attack, decay, sustain, release, pan)
VOICES = {
    0:  ("pulse25", 0.30, 0.004, 0.05, 0.80, 0.06,  0.00),   # Lead
    1:  ("saw",     0.16, 0.006, 0.06, 0.70, 0.06, -0.35),   # Counter
    2:  ("saw",     0.10, 0.120, 0.20, 0.85, 0.25,  0.25),   # Strings
    3:  ("pulse12", 0.11, 0.002, 0.04, 0.30, 0.05,  0.40),   # Guitar
    4:  ("tri",     0.13, 0.003, 0.04, 0.60, 0.05, -0.25),   # Arp
    5:  ("square",  0.26, 0.004, 0.07, 0.75, 0.06,  0.00),   # Bass
}

DRUMS = {36: ("kick", 0.55), 38: ("snare", 0.34), 41: ("tom", 0.30),
         42: ("hat", 0.13), 46: ("ohat", 0.16), 47: ("tom", 0.30),
         49: ("crash", 0.26), 51: ("ride", 0.15)}


def drum(kind, n):
    n = max(n, int(0.02 * SR))
    t = np.arange(n) / SR
    if kind == "kick":
        f = 110 * np.exp(-t * 28) + 42
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)
    if kind == "tom":
        f = 220 * np.exp(-t * 16) + 90
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)
    noise = np.random.default_rng(0).standard_normal(n)
    if kind == "snare":
        body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 26) * 0.5
        return (noise * np.exp(-t * 19) + body)
    if kind == "hat":
        return noise * np.exp(-t * 90)
    if kind == "ohat":
        return noise * np.exp(-t * 16)
    if kind == "ride":
        return noise * np.exp(-t * 22) * 0.7
    return noise * np.exp(-t * 5)          # crash


def render(midi_path, wav_path):
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
    total = max(n[4] for n in notes) + 2.5
    L = int(total * SR)
    out = np.zeros((L, 2), dtype=np.float32)

    for ch, p, vel, t0, t1 in notes:
        i0 = int(t0 * SR)
        n = max(int((t1 - t0) * SR), int(0.03 * SR))
        if i0 + n > L:
            n = L - i0
        if n <= 1:
            continue
        amp = (vel / 127.0) ** 1.4
        if ch == 9:
            kind, g = DRUMS.get(p, ("hat", 0.1))
            sig = drum(kind, min(n, int(0.9 * SR))) * g * amp
            n = len(sig)
            l = r = sig
        else:
            wf, g, a, d, s, rel, pan = VOICES.get(ch, ("square", 0.1, .005, .05, .7, .05, 0))
            f = 440.0 * 2 ** ((p - 69) / 12.0)
            sig = osc(wf, f, n) * env(n, a, d, s, rel) * g * amp
            l = sig * (1 - max(0.0, pan)) ** 0.5
            r = sig * (1 + min(0.0, pan)) ** 0.5
        out[i0:i0 + n, 0] += l[:n]
        out[i0:i0 + n, 1] += r[:n]

    # gentle limiter, then normalise
    out = np.tanh(out * 1.25) / 1.25
    out /= max(1e-9, np.abs(out).max())
    out *= 0.89
    pcm = (out * 32767).astype("<i2")

    data = pcm.tobytes()
    if wav_path.endswith(".mp3"):
        import lameenc
        enc = lameenc.Encoder()
        enc.set_bit_rate(160)
        enc.set_in_sample_rate(SR)
        enc.set_channels(2)
        enc.set_quality(2)
        blob = enc.encode(data) + enc.flush()
        open(wav_path, "wb").write(blob)
        size = len(blob)
    else:
        with open(wav_path, "wb") as f:
            f.write(b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVE")
            f.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, 2, SR, SR * 4, 4, 16))
            f.write(b"data" + struct.pack("<I", len(data)) + data)
        size = len(data)
    print(f"wrote {wav_path}  {int(total//60)}:{total%60:04.1f}  "
          f"{len(notes)} notes  {size/1e6:.1f} MB")


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else "../score/afterlight.mid",
           sys.argv[2] if len(sys.argv) > 2 else "../score/afterlight.wav")
