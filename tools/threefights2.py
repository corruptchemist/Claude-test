"""THREE FIGHTS -- accompaniment parts, assembly, verification."""

from fractions import Fraction as F
from zerosum import bar_len, pitches_in
from zerosum2 import shift, oct_down, to_midi, from_midi, rests
import threefights as T

# ===========================================================================
# BASS  --  promoted to the foreground.  In movement II it IS the tune.
# ===========================================================================
# (low root, octave root, fifth, third, chromatic approach from below)
ROOTS = {
    "Fm":  ("F1", "F2", "C2", "Ab1", "E1"),   "Db": ("Db2", "Db3", "Ab2", "F2", "C2"),
    "Eb":  ("Eb2", "Eb3", "Bb2", "G2", "D2"), "C7": ("C2", "C3", "G2", "E2", "B1"),
    "Cm":  ("C2", "C3", "G2", "Eb2", "B1"),   "Ab": ("Ab1", "Ab2", "Eb2", "C2", "G1"),
    "Em7": ("E1", "E2", "B1", "G1", "D#1"),   "A":  ("A1", "A2", "E2", "C#2", "G#1"),
    "F#7": ("F#1", "F#2", "C#2", "A#1", "F1"), "G":  ("G1", "G2", "D2", "B1", "F#1"),
    "B7":  ("B1", "B2", "F#2", "D#2", "A#1"), "C":  ("C2", "C3", "G2", "E2", "B1"),
    "Dm":  ("D2", "D3", "A2", "F2", "C#2"),   "Bb": ("Bb1", "Bb2", "F2", "D2", "A1"),
    "Am":  ("A1", "A2", "E2", "C2", "G#1"),   "Gm": ("G1", "G2", "D2", "Bb1", "F#1"),
    "F":   ("F1", "F2", "C2", "A1", "E1"),    "A5": ("A1", "A2", "E2", "A2", "G#1"),
    "Edim7": ("E1", "E2", "Bb1", "G1", "D#1"),
    "A#dim7": ("A#1", "A#2", "E2", "C#2", "A1"),
    "Ebdim7": ("Eb2", "Eb3", "A2", "Gb2", "D2"),
}


def bass_pat(chord, name, nxt=None):
    r1, r2, fifth, third, appr = ROOTS[chord]
    nx = ROOTS[nxt][4] if nxt else appr
    P = {
        # -- I. FLOWER: driving 8ths, octave leaps, chromatic pickups
        "fin_a": f"{r1}/8 {r2}/8 {fifth}/8 {r2}/8 {r1}/8 {r2}/8 {third}/8 {fifth}/8",
        "fin_b": f"{r1}/8 {r1}/16 {r2}/16 {fifth}/8 {r2}/8 {r1}/8 {third}/8 {fifth}/16 {r2}/16 {nx}/8",
        "fin_c": f"{r1}/16 {r1}/16 {r2}/8 {fifth}/16 {third}/16 {r2}/8 {r1}/8 {r2}/8 {fifth}/8 {nx}/8",
        "fin_hit": f"{r1}/4 R/8 {r1}/8 {r2}/4 R/8 {nx}/8",
        # -- III. BAD TIME: the ostinato (see below) plus counter-figures
        "meg_x": f"{r1}/8 {r2}/8 {fifth}/8 {r2}/8 {third}/8 {fifth}/8 {r2}/8 {nx}/8",
    }
    return P[name]


# The movement III ostinato.  16 sixteenths, partitioned 2+2+3+3+3+1+1+1.
# Beats 3 and 4 are never struck -- the notes on 2& and 3& sustain through
# them -- and three closing sixteenths re-sync the downbeat.  Across the
# four-bar unit only the first TWO attacks change pitch.
MEG_TAIL = ["A2", "F2", "E2", "D2", "C2", "D2"]
MEG_RHY = ["8", "8", "8.", "8.", "8.", "16", "16", "16"]
MEG_HEADS = {"Dm": ("D2", "D3"), "C": ("C2", "C3"), "Bb": ("Bb1", "Bb2"),
             "Am": ("A1", "A2"), "Gm": ("G1", "G2"), "F": ("F1", "F2"),
             "Eb": ("Eb2", "Eb3"), "A5": ("A1", "A2")}


def meg_ost(chord):
    lo, hi = MEG_HEADS[chord]
    ps = [lo, hi] + MEG_TAIL
    return " ".join(f"{p}/{d}" for p, d in zip(ps, MEG_RHY))


# Movement II bass -- the feature.  Two cells, exactly as the source does it:
# an 8-attack intro cell and a busier 10-attack cell for the second half.
# The b7 -> 6 slur (D -> C#) is the signature; keep it slurred, never picked.
DBG = {
    "Em7_a":  "E1/8 R/16 E1/16 G1/8 R/16 E1/16 D2/8. C#2/16 E1/8 R/8",
    "Em7_b":  "E1/8 E1/16 E2/16 G1/8 E1/16 G1/16 D2/16 C#2/16 D2/16 C#2/16 D2/8 A1/8",
    "Em7_c":  "E1/16 E1/16 E2/8 G1/16 A1/16 B1/8 D2/16 C#2/16 B1/8 G1/16 E1/16 D1/8",
    "A_a":    "A1/8 R/16 A1/16 C#2/8 R/16 A1/16 G2/8. F#2/16 A1/8 R/8",
    "A_b":    "A1/8 A1/16 A2/16 C#2/8 A1/16 C#2/16 G2/16 F#2/16 G2/16 F#2/16 G2/8 E2/8",
    "G_a":    "G1/8 R/16 G1/16 B1/8 R/16 G1/16 F2/8. E2/16 G1/8 R/8",
    "G_b":    "G1/8 G1/16 G2/16 B1/8 G1/16 B1/16 F2/16 E2/16 F2/16 E2/16 D2/8 B1/8",
    "F#7_a":  "F#1/8 R/16 F#1/16 A#1/8 R/16 F#1/16 E2/8. D#2/16 F#1/8 R/8",
    "F#7_b":  "F#1/8 F#1/16 F#2/16 A#1/8 F#1/16 A#1/16 E2/16 D#2/16 E2/16 C#2/16 B1/8 F#1/8",
    "B7_a":   "B1/8 R/16 B1/16 D#2/8 R/16 B1/16 A2/8. G#2/16 B1/8 R/8",
    "B7_b":   "B1/16 B1/16 B2/8 D#2/16 F#2/16 A2/8 G#2/16 F#2/16 D#2/8 B1/16 A#1/16 B1/8",
    "C_a":    "C2/8 R/16 C2/16 E2/8 R/16 C2/16 Bb2/8. A2/16 C2/8 R/8",
    "C_b":    "C2/8 C2/16 C3/16 E2/8 C2/16 E2/16 Bb2/16 A2/16 Bb2/16 A2/16 G2/8 E2/8",
    # a genuine two-bar bass break at the section seam
    "solo1":  "E1/16 G1/16 A1/16 B1/16 D2/16 E2/16 D2/16 C#2/16 B1/16 A1/16 G1/16 E1/16 D1/8 E1/8",
    "solo2":  "E1/16 B1/16 E2/16 G2/16 F#2/16 E2/16 D2/16 C#2/16 B1/8 G1/8 E1/16 D1/16 E1/8",
}

# ===========================================================================
# CHORD VOICINGS  --  stabs stay in close position C4-C5 and never spread.
# ===========================================================================
VOICE = {
    "Fm": "F4+Ab4+C5", "Db": "Ab4+Db5+F5", "Eb": "G4+Bb4+Eb5", "C7": "C4+E4+Bb4",
    "Cm": "C4+Eb4+G4", "Ab": "Ab4+C5+Eb5",
    "Em7": "G4+B4+D5", "A": "A4+C#5+E5", "F#7": "A#4+C#5+E5", "G": "G4+B4+D5",
    "B7": "B4+D#5+A4", "C": "C4+E4+G4",
    "Dm": "D4+F4+A4", "Bb": "Bb3+D4+F4", "Am": "A3+C4+E4", "Gm": "G3+Bb3+D4",
    "F": "F3+A3+C4", "A5": "A3+E4+A4",
    "Edim7": "E4+G4+Bb4+Db5", "A#dim7": "E4+G4+A#4+C#5", "Ebdim7": "Eb4+Gb4+A4+C5",
}
PAD = {
    "Fm": "F4+C5", "Db": "Ab4+F5", "Eb": "Bb4+G5", "C7": "C5+Bb5", "Cm": "C5+G5",
    "Ab": "Ab4+Eb5", "Em7": "E4+B4", "A": "A4+E5", "F#7": "F#4+C#5", "G": "G4+D5",
    "B7": "B4+F#5", "C": "C5+G5", "Dm": "D4+A4", "Bb": "Bb3+F4", "Am": "A3+E4",
    "Gm": "G3+D4", "F": "F3+C4", "A5": "A3+E4",
    "Edim7": "E4+Bb4", "A#dim7": "E4+A#4", "Ebdim7": "Eb4+A4",
}


def stab(chord, kind):
    v = VOICE[chord]
    return {
        "off":   f"R/8 {v}/8 R/8 {v}/8 R/8 {v}/8 R/8 {v}/8",
        "ska":   f"R/8 {v}/16 {v}/16 R/8 {v}/8 R/8 {v}/16 {v}/16 R/8 {v}/8",
        "push":  f"R/8 {v}/8 {v}/8 R/8 R/8 {v}/8 {v}/8 R/8",
        "hold":  f"{v}/1",
        "half":  f"{v}/2 {v}/2",
        "quart": f"{v}/4 {v}/4 {v}/4 {v}/4",
    }[kind]


def pad(chord, kind="hold"):
    v = PAD[chord]
    return f"{v}/1" if kind == "hold" else f"{v}/2 {v}/2"


def arp(chord, octv=0):
    v = VOICE[chord].split("+")
    seq = (v + v[::-1][1:] + [v[0]])[:8]
    while len(seq) < 8:
        seq.append(v[0])
    line = " ".join(f"{p}/16" for p in seq * 2)
    return shift(line, octv) if octv else line


# ===========================================================================
# ASSEMBLY
# ===========================================================================
CHORDS = T.CH_I + T.CH_BR_A + T.CH_II2 + T.CH_BR_B + T.CH_III2
LEAD = T.LEAD_I2 + T.LEAD_BR_A + T.LEAD_II2 + T.LEAD_BR_B + T.LEAD_III2
N = 200


def nxt(i):
    return CHORDS[i + 1] if i + 1 < N else CHORDS[i]


# ---- BASS -----------------------------------------------------------------
BASS = []
for i, c in enumerate(CHORDS):
    m = i + 1
    if m <= 64:                                   # I. FLOWER
        pat = "fin_hit" if m <= 4 else ("fin_c" if m % 4 == 0 else
              ("fin_b" if m % 2 == 0 else "fin_a"))
        BASS.append(bass_pat(c, pat, nxt(i)))
    elif m <= 72:                                 # bridge A
        r1, r2, fifth, third, _ = ROOTS[c]
        BASS.append(f"{r1}/8 {r2}/8 {fifth}/8 {third}/8 {r1}/8 {r2}/8 {fifth}/8 {third}/8"
                    if m <= 70 else f"{r1}/2 {r2}/2")
    elif m <= 128:                                # II. GLAMOUR -- the feature
        busy = m >= 97                            # second half gets the 10-attack cell
        if m in (96, 112):
            BASS.append(DBG["solo1"] if m == 96 else DBG["solo2"])
        else:
            BASS.append(DBG[f"{c}_{'b' if busy else 'a'}"])
    elif m <= 136:                                # bridge B -- E -> Eb -> D
        r1, r2, fifth, third, _ = ROOTS[c]
        BASS.append(f"{r1}/8 {r2}/8 {fifth}/8 {r2}/8 {third}/8 {fifth}/8 {r2}/8 {r1}/8")
    else:                                         # III. BAD TIME
        BASS.append(meg_ost(c) if m < 193 or m < 199 else
                    ("D1/8 D2/8 A1/8 D2/8 F2/8 D2/8 A1/8 D2/8" if m == 199
                     else "D1+D2+A2/1"))
BASS[-1] = "D1+D2+A2+D3/1"
BASS[-2] = "D1/16 E1/16 F1/16 G1/16 A1/16 Bb1/16 C2/16 D2/16 E2/16 F2/16 G2/16 A2/16 Bb2/16 C3/16 D3/8"

# ---- DRUMS ----------------------------------------------------------------
DRUMS = []
for i in range(N):
    m = i + 1
    if m <= 4:
        DRUMS.append("fin_half")
    elif m <= 64:
        DRUMS.append("fin_fill" if m % 8 == 0 else
                     ("fin_c" if m % 8 == 1 else ("fin_b" if m % 2 == 0 else "fin_a")))
    elif m <= 68:
        DRUMS.append("crash" if m == 65 else "tacet")
    elif m <= 72:
        DRUMS.append("roll" if m >= 71 else "fin_half")
    elif m <= 80:
        DRUMS.append("tacet" if m <= 74 else ("dbg_thin" if m <= 78 else "dbg_a"))
    elif m <= 128:
        DRUMS.append("dbg_fill" if m % 8 == 0 else
                     ("dbg_ride" if 97 <= m <= 104 else "dbg_b" if m % 2 == 0 else "dbg_a"))
    elif m <= 136:
        DRUMS.append("fin_half" if m <= 132 else ("roll" if m == 136 else "meg_a"))
    else:
        DRUMS.append("meg_fill" if m % 8 == 0 else
                     ("meg_c" if m % 8 == 1 else ("meg_b" if m % 2 == 0 else "meg_a")))
DRUMS[136] = "tacet"          # m.137 -- ostinato bare for one bar
DRUMS[137] = "tacet"
DRUMS[-1] = "final"
DRUMS[-2] = "roll"

# ---- STABS  (always two dynamic steps under the lead) ---------------------
STABS = []
for i, c in enumerate(CHORDS):
    m = i + 1
    if m <= 8:
        STABS.append(stab(c, "half") if m > 4 else "R/1")
    elif m <= 64:
        STABS.append(stab(c, "quart" if m % 8 in (1, 2) else "off"))
    elif m <= 72:
        STABS.append(stab(c, "hold"))
    elif m <= 80:
        STABS.append("R/1" if m <= 78 else stab(c, "ska"))
    elif m <= 128:
        STABS.append(stab(c, "ska"))              # disco upstrokes
    elif m <= 136:
        STABS.append(stab(c, "half"))
    else:
        STABS.append("R/1" if m <= 144 else stab(c, "off"))

# ---- SUSTAIN --------------------------------------------------------------
SUSTAIN = []
for i, c in enumerate(CHORDS):
    m = i + 1
    if m <= 8:
        SUSTAIN.append(pad(c))
    elif m <= 64:
        SUSTAIN.append(pad(c) if m % 2 else pad(c, "half"))
    elif m <= 72:
        SUSTAIN.append(pad(c))
    elif m <= 96:
        SUSTAIN.append("R/1")
    elif m <= 128:
        SUSTAIN.append(pad(c))
    elif m <= 136:
        SUSTAIN.append(pad(c))
    else:
        SUSTAIN.append("R/1" if m <= 152 else pad(c))

# ---- KEYS -----------------------------------------------------------------
KEYS = []
for i, c in enumerate(CHORDS):
    m = i + 1
    if m <= 8:
        KEYS.append("R/1")
    elif m <= 64:
        KEYS.append(arp(c, 12))
    elif m <= 72:
        KEYS.append(arp(c, 12))
    elif m <= 80:
        KEYS.append("R/1" if m <= 76 else arp(c))
    elif m <= 128:
        KEYS.append(arp(c))
    elif m <= 136:
        KEYS.append(arp(c, 12))
    elif m <= 144:
        KEYS.append(shift(meg_ost(c), 24))        # ostinato doubled two octaves up
    else:
        KEYS.append(arp(c, 12))
KEYS[-1] = "D4+F4+A4+D5+A5+D6/1"

# ---- COUNTER --------------------------------------------------------------
COUNTER = []
for i, c in enumerate(CHORDS):
    m = i + 1
    if m <= 24 or (65 <= m <= 96) or (129 <= m <= 160):
        COUNTER.append("R/1")
    else:
        COUNTER.append(oct_down(LEAD[i]) if "R/1" != LEAD[i] else "R/1")
COUNTER[-1] = "D4+A4+D5/1"

PARTS = {"LEAD": LEAD, "COUNTER": COUNTER, "SUSTAIN": SUSTAIN,
         "STABS": STABS, "KEYS": KEYS, "BASS": BASS, "DRUMS": DRUMS}

MOVEMENTS = [
    ("I. FLOWER",   1,   64,  "F minor",          -4, 95,  "after “Finale”"),
    ("bridge A",    65,  72,  "shared dim7",      -4, 95,  "E°7 = A♯°7"),
    ("II. GLAMOUR", 73,  128, "B minor / E Dorian", 2, 148, "after “Death by Glamour”"),
    ("bridge B",    129, 136, "E → E♭ → D", 2, 148, "chromatic descent"),
    ("III. BAD TIME", 137, 200, "D minor",        -1, 126, "after “MEGALOVANIA”"),
]


def verify():
    p = []
    for name, bars in PARTS.items():
        if len(bars) != N:
            p.append(f"{name}: {len(bars)} bars, want {N}")
            continue
        for i, b in enumerate(bars):
            src = T.DRUM_LIB[b] if name == "DRUMS" else b
            try:
                L = bar_len(src)
            except Exception as e:
                p.append(f"{name} m.{i+1}: parse {e} :: {b[:50]}")
                continue
            if L != F(4):
                p.append(f"{name} m.{i+1}: {L} beats :: {b[:50]}")
    # the dynamics rule the last piece got wrong
    for m in range(1, N + 1):
        lead, stabs = T.dyn_for("LEAD", m), T.dyn_for("STABS", m)
        if T.LVL[stabs] >= T.LVL[lead]:
            p.append(f"m.{m}: stabs {stabs} not under lead {lead}")
    return p


if __name__ == "__main__":
    probs = verify()
    print(f"{len(probs)} PROBLEMS" if probs else
          f"OK -- {N} bars, {len(PARTS)} parts, every measure sums exactly.")
    for x in probs[:40]:
        print("  ", x)
    if not probs:
        for part in PARTS:
            print(f"  {part:8s} dyn: " +
                  ", ".join(f"m{m}:{d}" for m, d in T.dyn_changes(part)[:8]) + " ...")
