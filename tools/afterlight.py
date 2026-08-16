"""
AFTERLIGHT -- 200 bars, q = 176, 4/4.  For REAPER (multi-track MIDI).

Modelled closely on "Hopes and Dreams" and "Last Goodbye".  Those two share a
key world, and the piece uses that: it starts in Hopes and Dreams' B-flat major
and lifts a semitone at m.129 into Last Goodbye's B major.

THE ENGINE (from Hopes and Dreams, verified by note-level analysis):
    || Cm7 | Bb/D | Ebmaj7 | Fsus4 -> F ||    ii7 - I6 - IV - V
    ONE CHORD PER TWO BARS.  Bass ascends C - D - Eb - F.
    The tonic NEVER appears in root position -- it is always Bb/D.  That single
    voicing decision is why the loop feels like it is climbing and never
    arriving, and it is the whole reason the track reads as hopeful at speed.
    Fast pulse + slow harmonic rhythm = heroic rather than panicked.

THE THEME is the "Undertale family" cell -- the scale-degree contour shared by
"Once Upon a Time", "Memory" and the Undertale main theme:
    5 5 2 | 1 5 5 | 5 7 7 1 | 7 5 3
    in Bb:  F F C | Bb F F | F A A Bb | A F D
Stated in LONG values, high, over a fast bed -- Hopes and Dreams' formula.

GETTING MORE COMPLICATED, STILL MANAGEABLE
Complexity arrives by ADDING LAYERS and by figurating the same theme, never by
making any one part harder.  Nine stages:

    1  mm.  1- 16   theme + arpeggio only.  No bass, no drums.
    2  mm. 17- 32   THE DROP -- bass enters, light kit
    3  mm. 33- 48   + counter-line, full kit
    4  mm. 49- 64   + sustained strings; theme grows 8th-note tails
    5  mm. 65- 80   + offbeat guitar; theme in 8ths
    6  mm. 81- 96   16th figuration around the theme's own notes
    7  mm. 97-128   everything, octave up
    8  mm.129-160   B MAJOR.  Semitone lift, no pivot chord.
    9  mm.161-184   the Last Goodbye strain -- iii - IV - iii - V -> vi
   coda mm.185-200   strips back to the opening texture, as Last Goodbye does
"""

from fractions import Fraction as F
from zerosum import bar_len
from zerosum2 import shift, oct_down, rests

TITLE = "AFTERLIGHT"
N = 200
BPM = 176

# ---------------------------------------------------------------------------
# HARMONY -- one loop, almost the whole way.  The interest is orchestration.
# ---------------------------------------------------------------------------
LOOP_A = ["Cm7", "Cm7", "Bb/D", "Bb/D", "Ebma7", "Ebma7", "Fsus", "F"]
LOOP_B = ["Cm7", "Cm7", "Bb/D", "Bb/D", "Ebma7", "Ebma7", "Gm7", "F"]
LOOP_A2 = ["C#m7", "C#m7", "B/D#", "B/D#", "Ema7", "Ema7", "F#sus", "F#"]
LOOP_B2 = ["C#m7", "C#m7", "B/D#", "B/D#", "Ema7", "Ema7", "G#m7", "F#"]
# the contrasting strain: bass oscillates instead of climbing
LOOP_C2 = ["D#m7", "D#m7", "Eadd9", "Eadd9", "D#m7", "D#m7", "F#", "G#m"]

CHORDS = ((LOOP_A + LOOP_B) * 8                     # mm.  1-128  Bb major
          + (LOOP_A2 + LOOP_B2) * 2                 # mm.129-160  B major
          + LOOP_C2 * 3                             # mm.161-184  the strain
          + LOOP_A2 + LOOP_B2)                      # mm.185-200  coda

# ---------------------------------------------------------------------------
# VOICINGS -- IV is a sus2/add9 stack, V is sus4 before it resolves.  Plain
# triads barely appear; nearly every chord is an added-note or slash voicing.
# ---------------------------------------------------------------------------
VOICE = {
    "Cm7":   "Eb4+G4+Bb4", "Bb/D": "D4+F4+Bb4", "Ebma7": "Eb4+F4+Bb4",
    "Fsus":  "F4+Bb4+C5",  "F": "F4+A4+C5",     "Gm7": "D4+G4+Bb4",
    "C#m7":  "E4+G#4+B4",  "B/D#": "D#4+F#4+B4", "Ema7": "E4+F#4+B4",
    "F#sus": "F#4+B4+C#5", "F#": "F#4+A#4+C#5", "G#m7": "D#4+G#4+B4",
    "D#m7":  "F#4+A#4+C#5", "Eadd9": "E4+F#4+B4", "G#m": "B3+D#4+G#4",
}
PAD = {k: "+".join(v.split("+")[:2]) for k, v in VOICE.items()}
ROOT = {"Cm7": "C", "Bb/D": "D", "Ebma7": "Eb", "Fsus": "F", "F": "F", "Gm7": "G",
        "C#m7": "C#", "B/D#": "D#", "Ema7": "E", "F#sus": "F#", "F#": "F#",
        "G#m7": "G#", "D#m7": "D#", "Eadd9": "E", "G#m": "G#"}
BASS_OCT = {"C": 2, "D": 2, "Eb": 2, "F": 2, "G": 1,
            "C#": 2, "D#": 2, "E": 2, "F#": 2, "G#": 1}

# ---------------------------------------------------------------------------
# DYNAMICS -- accompaniment strictly under the melody, as established.
# ---------------------------------------------------------------------------
LEVELS = ["ppp", "pp", "p", "mp", "mf", "f", "ff", "fff"]
LVL = {d: i for i, d in enumerate(LEVELS)}
OFFSET = {"LEAD": 0, "COUNTER": -1, "STRINGS": -2, "GUITAR": -3,
          "ARP": -2, "BASS": -1, "DRUMS": -1}

LEAD_DYN = [(1, "mp"), (9, "mf"), (17, "mf"), (25, "f"), (33, "f"), (41, "f"),
            (49, "f"), (57, "f"), (65, "f"), (73, "ff"), (81, "ff"), (89, "ff"),
            (97, "ff"), (113, "ff"), (129, "ff"), (145, "ff"),
            (161, "fff"), (177, "fff"), (185, "mf"), (193, "mp")]

LEAD_HAIRPINS = [(1, 8, "<"), (13, 16, "<"), (25, 32, "<"), (41, 48, "<"),
                 (57, 64, "<"), (73, 80, "<"), (89, 96, "<"), (105, 112, "<"),
                 (121, 128, "<"), (137, 144, "<"), (153, 160, "<"),
                 (169, 176, "<"), (177, 184, "<"), (185, 192, ">"),
                 (193, 200, ">")]


def dyn_for(part, measure):
    lead = LEAD_DYN[0][1]
    for m, d in LEAD_DYN:
        if m <= measure:
            lead = d
        else:
            break
    return LEVELS[max(0, min(7, LVL[lead] + OFFSET[part]))]


def dyn_changes(part):
    out, prev = [], None
    for m, _ in LEAD_DYN:
        d = dyn_for(part, m)
        if d != prev:
            out.append((m, d))
            prev = d
    return out


# ---------------------------------------------------------------------------
# THEME  --  the Undertale family cell, 8 bars, in long values.
# ---------------------------------------------------------------------------
THEME_BB = [
    "F5/2 F5/2", "C6/1", "Bb5/2 F5/2", "F5/1",
    "F5/2 A5/2", "A5/2 Bb5/2", "A5/2 F5/2", "D6/1",
]

# Stage by stage the SAME eight bars gain figuration.  The structural pitches
# stay on the strong beats throughout; only the space between them fills in.
STAGE = {}

STAGE[1] = THEME_BB                                    # plain

STAGE[2] = [                                           # passing quarters
    "F5/2 F5/4 G5/4", "C6/2 C6/2", "Bb5/2 F5/4 G5/4", "F5/1",
    "F5/2 A5/4 G5/4", "A5/2 Bb5/2", "A5/2 F5/4 A5/4", "D6/1",
]

STAGE[3] = [                                           # eighth-note tails
    "F5/2 F5/4 G5/8 F5/8", "C6/2 Bb5/8 C6/8 D6/4",
    "Bb5/2 F5/8 G5/8 A5/4", "F5/2 F5/4 D5/4",
    "F5/2 A5/8 G5/8 A5/4", "A5/2 Bb5/8 A5/8 G5/4",
    "A5/2 F5/8 A5/8 C6/4", "D6/2 C6/8 Bb5/8 A5/4",
]

STAGE[4] = [                                           # the eighth cascade
    "F5/4 G5/8 F5/8 F5/4 C6/4", "C6/2 D6/8 C6/8 Bb5/8 A5/8",
    "Bb5/4 C6/8 Bb5/8 F5/2", "F5/4 A5/8 F5/8 D5/4 F5/4",
    "F5/4 G5/8 A5/8 A5/2", "A5/4 Bb5/8 C6/8 Bb5/2",
    "A5/4 Bb5/8 A5/8 F5/4 A5/4",
    "D6/8 Bb5/8 A5/8 F5/8 D5/8 C5/8 Bb4/8 F4/8",   # the documented cascade
]

STAGE[5] = [                                           # eighths throughout
    "F5/8 G5/8 F5/8 Eb5/8 F5/4 C6/4", "C6/8 D6/8 C6/8 Bb5/8 C6/2",
    "Bb5/8 C6/8 D6/8 C6/8 Bb5/4 F5/4", "F5/8 G5/8 A5/8 G5/8 F5/2",
    "F5/8 G5/8 A5/8 Bb5/8 A5/4 F5/4", "A5/8 Bb5/8 C6/8 Bb5/8 A5/2",
    "A5/8 G5/8 F5/8 G5/8 A5/4 C6/4",
    "D6/8 Bb5/8 A5/8 F5/8 D5/8 F5/8 A5/8 C6/8",
]

STAGE[6] = [                                           # 16ths around the theme
    "F5/16 G5/16 F5/16 Eb5/16 F5/8 A5/8 C6/4 F5/4",
    "C6/16 D6/16 C6/16 Bb5/16 C6/8 Eb6/8 D6/4 C6/4",
    "Bb5/16 C6/16 D6/16 F6/16 D6/8 Bb5/8 F5/4 Bb5/4",
    "F5/16 G5/16 A5/16 C6/16 A5/8 F5/8 F5/2",
    "F5/16 G5/16 A5/16 Bb5/16 A5/8 F5/8 A5/4 C6/4",
    "A5/16 Bb5/16 C6/16 Eb6/16 C6/8 A5/8 Bb5/2",
    "A5/16 G5/16 F5/16 G5/16 A5/8 C6/8 F6/4 C6/4",
    "D6/16 C6/16 Bb5/16 A5/16 F5/16 D5/16 C5/16 Bb4/16 F5/4 A5/4",
]

STAGE[7] = [shift(b, 12) for b in STAGE[6]]            # octave up, full


def stage_bars(n, count):
    """Repeat a stage's eight bars to fill `count` bars."""
    return (STAGE[n] * ((count // 8) + 1))[:count]


# ---------------------------------------------------------------------------
# LEAD, 200 bars
# ---------------------------------------------------------------------------
LEAD = (stage_bars(1, 16) + stage_bars(2, 16) + stage_bars(3, 16)
        + stage_bars(4, 16) + stage_bars(5, 16) + stage_bars(6, 16)
        + stage_bars(7, 32))

# mm.129-160  B MAJOR.  Bar 128 ends on vi; bar 129 starts the same loop a
# semitone higher with no preparation.  Blunt on paper, overwhelming in practice.
LEAD += [shift(b, 1) for b in stage_bars(7, 32)]

# mm.161-184  the Last Goodbye strain: after 160 bars of ASCENDING bass, the
# progression oscillates instead, and the tune hammers a repeated 5-hat.
STRAIN = [
    "F#6/4 F#6/4 F#6/4 F#6/8 E6/8", "D#6/4 E6/4 F#6/2",
    "B6/4 F#6/4 C#6/4 D#6/4", "E6/2 D#6/4 C#6/4",
    "F#6/4 F#6/4 F#6/4 F#6/8 E6/8", "D#6/4 E6/4 F#6/2",
    "C#7/4 A#6/4 B6/4 D#6/4", "C#6/2 B5/2",
]
LEAD += (STRAIN * 3)[:24]

# mm.185-200  coda -- back to the opening texture, in the new key
LEAD += [shift(b, 1) for b in stage_bars(1, 16)]

# ---------------------------------------------------------------------------
# COUNTER -- enters at stage 3, an octave under the lead; in the strain it
# runs a real second voice rather than a doubling.
# ---------------------------------------------------------------------------
COUNTER = (rests(32)
           + [oct_down(b) for b in stage_bars(3, 16)]
           + [oct_down(b) for b in stage_bars(2, 16)]
           + [oct_down(b) for b in stage_bars(4, 16)]
           + [oct_down(b) for b in stage_bars(5, 16)]
           + [oct_down(b) for b in stage_bars(6, 32)]
           + [oct_down(shift(b, 1)) for b in stage_bars(6, 32)])
COUNTER += [
    "B4/2 C#5/2", "D#5/2 E5/2", "F#5/2 E5/2", "D#5/1",
    "B4/2 C#5/2", "D#5/2 F#5/2", "G#5/2 F#5/2", "E5/1",
] * 3
COUNTER = COUNTER[:184] + [oct_down(shift(b, 1)) for b in stage_bars(1, 16)]

# ---------------------------------------------------------------------------
# ARP -- the sixteenth bed.  Present from bar one; it is the only accompaniment
# for the first sixteen bars, so it starts in eighths and thickens later.
# ---------------------------------------------------------------------------
def arp(c, sixteenths=True, o=0):
    v = VOICE[c].split("+")
    seq = v + [v[-1]] if len(v) == 3 else v[:4]
    seq = (seq * 3)[:4]
    line = " ".join(f"{p}/16" for p in (seq + seq[::-1]) * 2) if sixteenths \
        else " ".join(f"{p}/8" for p in seq + seq[::-1])
    return shift(line, o) if o else line


ARP = []
for i, c in enumerate(CHORDS):
    m = i + 1
    if m <= 16:
        ARP.append(arp(c, False, -12))        # eighths, low -- the whole texture
    elif m <= 48:
        ARP.append(arp(c, False))
    else:
        ARP.append(arp(c))

# ---------------------------------------------------------------------------
# BASS -- silent for sixteen bars, then THE DROP.  Continuous straight eighths
# alternating root and octave, exactly as Hopes and Dreams does, with a
# stepwise walk-up at each sixteen-bar seam landing on the next root.
# ---------------------------------------------------------------------------
WALKUP = {"Bb": "G1/8 A1/8 Bb1/8 C2/8 D2/8 Eb2/8 F2/8 G2/8",
          "B":  "G#1/8 A#1/8 B1/8 C#2/8 D#2/8 E2/8 F#2/8 G#2/8"}

BASS = []
for i, c in enumerate(CHORDS):
    m = i + 1
    r = ROOT[c]
    o = BASS_OCT[r]
    lo, hi = f"{r}{o}", f"{r}{o+1}"
    if m <= 16:
        BASS.append("R/1")                                    # the hole
    elif m in (32, 64, 96, 128, 160):
        BASS.append(WALKUP["B" if m > 128 else "Bb"])
    elif m <= 48:
        BASS.append(f"{lo}/8 {hi}/8 {lo}/8 {hi}/8 {lo}/8 {hi}/8 {lo}/8 {hi}/8")
    elif m <= 96:
        BASS.append(f"{lo}/8 {hi}/8 {lo}/16 {lo}/16 {hi}/8 {lo}/8 {hi}/8 {lo}/8 {hi}/8")
    else:
        BASS.append(f"{lo}/8 {hi}/8 {lo}/16 {lo}/16 {hi}/8 {lo}/16 {hi}/16 "
                    f"{lo}/8 {hi}/16 {lo}/16 {hi}/8")
BASS[-1] = f"{ROOT[CHORDS[-1]]}1+{ROOT[CHORDS[-1]]}2/1"

# ---------------------------------------------------------------------------
# STRINGS -- sustained, from stage 4
# ---------------------------------------------------------------------------
STRINGS = rests(48) + [f"{PAD[c]}/1" for c in CHORDS[48:]]

# ---------------------------------------------------------------------------
# GUITAR -- offbeat upstrokes, from stage 5.  Three steps under the melody.
# ---------------------------------------------------------------------------
GUITAR = rests(64) + [f"R/8 {VOICE[c]}/8 R/8 {VOICE[c]}/8 "
                      f"R/8 {VOICE[c]}/8 R/8 {VOICE[c]}/8" for c in CHORDS[64:]]

# ---------------------------------------------------------------------------
# DRUMS -- tacet for sixteen bars, then a cymbal roll and fill into the drop.
# ---------------------------------------------------------------------------
DRUM_LIB = {
    "tacet": "R/1",
    "roll":  "Z/2 Z/2",
    "light": "K/4 H/8 H/8 S/4 H/8 H/8",
    "rock":  "K/8 H/8 S/8 H/8 K/16 K/16 H/8 S/8 H/8",
    "rockO": "KC/8 H/8 S/8 H/8 K/16 K/16 H/8 S/8 O/8",
    "busy":  "K/8 H/16 H/16 S/8 H/8 K/16 K/16 H/8 S/8 H/16 H/16",
    "busyO": "KC/8 H/16 H/16 S/8 H/8 K/16 K/16 H/8 S/8 O/8",
    "ride":  "KR/8 R/8 SR/8 R/8 KR/16 K/16 R/8 SR/8 R/8",
    "fill":  "S/16 S/16 T/16 T/16 F/16 F/16 S/8 T/8 F/8 KC/8 S/8",
    "bigfill": "S/16 S/16 S/16 S/16 T/16 T/16 T/16 T/16 F/16 F/16 F/16 F/16 KC/8 S/8",
    "final": "KCZ/1",
}

DRUMS = []
for i in range(N):
    m = i + 1
    if m <= 14:
        DRUMS.append("tacet")
    elif m <= 16:
        DRUMS.append("roll" if m == 15 else "bigfill")        # sets up the drop
    elif m <= 32:
        DRUMS.append("light" if m % 8 else "fill")
    elif m <= 64:
        DRUMS.append("rockO" if m % 16 == 1 else ("fill" if m % 8 == 0 else "rock"))
    elif m <= 96:
        DRUMS.append("busyO" if m % 16 == 1 else ("fill" if m % 8 == 0 else "busy"))
    elif m <= 128:
        DRUMS.append("busyO" if m % 16 == 1 else
                     ("bigfill" if m % 16 == 0 else ("fill" if m % 8 == 0 else "busy")))
    elif m <= 160:
        DRUMS.append("busyO" if m % 16 == 1 else
                     ("bigfill" if m % 16 == 0 else ("fill" if m % 8 == 0 else "busy")))
    elif m <= 184:
        DRUMS.append("busyO" if m % 8 == 1 else ("fill" if m % 8 == 0 else "busy"))
    else:
        DRUMS.append("ride" if m % 8 else "fill")             # coda thins out
DRUMS[-1] = "final"

PARTS = {"LEAD": LEAD, "COUNTER": COUNTER, "STRINGS": STRINGS,
         "GUITAR": GUITAR, "ARP": ARP, "BASS": BASS, "DRUMS": DRUMS}


def verify():
    p = []
    if len(CHORDS) != N:
        p.append(f"chord grid {len(CHORDS)} != {N}")
    for name, bars in PARTS.items():
        if len(bars) != N:
            p.append(f"{name}: {len(bars)} bars, want {N}")
            continue
        for i, b in enumerate(bars):
            src = DRUM_LIB[b] if name == "DRUMS" else b
            try:
                L = bar_len(src)
            except Exception as e:
                p.append(f"{name} m.{i+1}: parse {e} :: {b[:50]}")
                continue
            if L != F(4):
                p.append(f"{name} m.{i+1}: {L} beats :: {b[:50]}")
    for m in range(1, N + 1):
        lead = LVL[dyn_for("LEAD", m)]
        for acc in ("GUITAR", "ARP", "STRINGS"):
            if LVL[dyn_for(acc, m)] > lead - 2:
                p.append(f"m.{m}: {acc} not far enough under lead")
    # the layer count must never decrease before the coda
    prev = 0
    for m in range(1, 185):
        n = sum(1 for k, v in PARTS.items()
                if k != "DRUMS" and v[m - 1] != "R/1")
        if m % 16 == 1 and n < prev:
            p.append(f"m.{m}: texture thinned ({prev} -> {n}) before the coda")
        if m % 16 == 1:
            prev = n
    return p


if __name__ == "__main__":
    probs = verify()
    print(f"{len(probs)} PROBLEMS" if probs else
          f"OK -- {N} bars, {len(PARTS)} parts, every measure sums exactly.")
    for x in probs[:30]:
        print("  ", x)
    if not probs:
        print("  layers per stage:", [
            sum(1 for k, v in PARTS.items() if k != "DRUMS" and v[m - 1] != "R/1")
            for m in (1, 17, 33, 49, 65, 81, 97, 129, 161, 193)])
        secs = N * 4 * 60 / BPM
        print(f"  duration {int(secs//60)}:{int(secs%60):02d} at q={BPM}")
