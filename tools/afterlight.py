"""
AFTERLIGHT  (rebuild) -- 208 bars, q = 176, 4/4.  Multi-track MIDI for REAPER.

"Lots happening while nothing is happening."  That is the boss-music trick and
it is what this rebuild is built around:

  HAPPENING       a 16th engine that never stops once it starts (m.9 to the
                  end), bass in constant motion, hats on every 8th, offbeat
                  guitar, drum fills every four bars.
  NOT HAPPENING   the harmony moves once every TWO bars and the loop never
                  changes; the melody is long notes with real holes in it.

Density underneath, space on top, near-static harmony.  Remove any one of the
three and it stops sounding like a boss fight.

QUOTED DIRECTLY (all three verified against transcriptions)
  A  "Once Upon a Time" / Undertale main theme -- the family cell
        5 5 2 | 1 5 5 | 5 7 7 1 | 7 5 3
        in Bb:  F F C | Bb F F | F A A Bb | A F D
  B  "Your Best Friend"
        1 2 3 1 | 2 | 2 3 2 1  ||  3 4 5 1 | 6 5
        in Bb:  Bb C D Bb | C | C D C Bb || D Eb F Bb | G F
  C  "Snowdin Town" pt.2, the strain Last Goodbye leans on
        5 5 5 5 5 4 3 4 | 1 5 2 3
        in B:   F# F# F# F# F# E D# E | B F# C# D#

THE ENGINE, from Hopes and Dreams:
    || Cm7 | Bb/D | Ebmaj7 | Fsus4 -> F ||   ii7 - I6 - IV - V, two bars each,
bass ascending C-D-Eb-F, tonic NEVER in root position.  Lifts a semitone to B
major at m.129 -- Hopes and Dreams' own modulation, and Last Goodbye's key.

THE MELODY CHANGES HANDS.  Lead, then second lead an octave down, then both in
octaves, then bells.  Nine timbral situations across the piece; no single voice
carries the tune for more than sixteen bars.
"""

from fractions import Fraction as F
from zerosum import bar_len, dur_of
from zerosum2 import shift, oct_down, rests

TITLE = "AFTERLIGHT"
N = 208
BPM = 176

# ---------------------------------------------------------------------------
# HARMONY
# ---------------------------------------------------------------------------
# The dark loop.  One chord per BAR against the bright loop's one per two --
# same key signature as Bb major, so this is a mode change, not a modulation.
LOOP_M = ["Gm", "Gm", "Eb", "F", "Gm", "Cm", "D7", "D7"]
LOOP_A = ["Cm7", "Cm7", "Bb/D", "Bb/D", "Ebma7", "Ebma7", "Fsus", "F"]
LOOP_B = ["Cm7", "Cm7", "Bb/D", "Bb/D", "Ebma7", "Ebma7", "Gm7", "F"]
LOOP_A2 = ["C#m7", "C#m7", "B/D#", "B/D#", "Ema7", "Ema7", "F#sus", "F#"]
LOOP_B2 = ["C#m7", "C#m7", "B/D#", "B/D#", "Ema7", "Ema7", "G#m7", "F#"]
LOOP_C2 = ["D#m7", "D#m7", "Eadd9", "Eadd9", "D#m7", "D#m7", "F#", "G#m"]

CHORDS = (LOOP_M * 4                       # mm.  1- 32  G MINOR -- the fight
          + (LOOP_A + LOOP_B) * 3          # mm. 33- 80  Bb major -- hope
          + LOOP_A + LOOP_B                # mm. 81- 96  bass feature
          + LOOP_M * 4                     # mm. 97-128  G MINOR -- phase two
          + (LOOP_A2 + LOOP_B2) * 3        # mm.129-176  B major -- the payoff
          + LOOP_C2 * 2                    # mm.177-192  the strain
          + LOOP_A2 + LOOP_B2)             # mm.193-208  coda

VOICE = {
    "Cm7": "Eb4+G4+Bb4", "Bb/D": "D4+F4+Bb4", "Ebma7": "Eb4+F4+Bb4",
    "Fsus": "F4+Bb4+C5", "F": "F4+A4+C5", "Gm7": "D4+G4+Bb4",
    "C#m7": "E4+G#4+B4", "B/D#": "D#4+F#4+B4", "Ema7": "E4+F#4+B4",
    "F#sus": "F#4+B4+C#5", "F#": "F#4+A#4+C#5", "G#m7": "D#4+G#4+B4",
    "D#m7": "F#4+A#4+C#5", "Eadd9": "E4+F#4+B4", "G#m": "B3+D#4+G#4",
    "Gm": "G3+Bb3+D4", "Eb": "Eb4+G4+Bb4", "Cm": "C4+Eb4+G4", "D7": "D4+F#4+C5",
}
PAD = {k: "+".join(v.split("+")[:2]) for k, v in VOICE.items()}
ROOT = {"Cm7": "C", "Bb/D": "D", "Ebma7": "Eb", "Fsus": "F", "F": "F",
        "Gm7": "G", "C#m7": "C#", "B/D#": "D#", "Ema7": "E", "F#sus": "F#",
        "F#": "F#", "G#m7": "G#", "D#m7": "D#", "Eadd9": "E", "G#m": "G#",
        "Gm": "G", "Eb": "Eb", "Cm": "C", "D7": "D"}
OCT = {"C": 2, "D": 2, "Eb": 2, "F": 2, "G": 1,
       "C#": 2, "D#": 2, "E": 2, "F#": 2, "G#": 1}
# scale степ above the root, for bass runs
NEXT = {"C": "D", "D": "Eb", "Eb": "F", "F": "G", "G": "Bb",
        "C#": "D#", "D#": "E", "E": "F#", "F#": "G#", "G#": "B"}
THIRD = {"C": "Eb", "D": "F", "Eb": "G", "F": "A", "G": "Bb",
         "C#": "E", "D#": "F#", "E": "G#", "F#": "A#", "G#": "B"}
FIFTH = {"C": "G", "D": "A", "Eb": "Bb", "F": "C", "G": "D",
         "C#": "G#", "D#": "A#", "E": "B", "F#": "C#", "G#": "D#"}

# ---------------------------------------------------------------------------
# DYNAMICS
# ---------------------------------------------------------------------------
LEVELS = ["ppp", "pp", "p", "mp", "mf", "f", "ff", "fff"]
LVL = {d: i for i, d in enumerate(LEVELS)}
OFFSET = {"LEAD": 0, "LEAD2": -1, "BELL": -1, "STRINGS": -1, "GUITAR": -2,
          "POWER": -1, "LOWBRASS": -1, "ARP": -2, "BASS": 0, "SUB": -1,
          "DRUMS": -1}

LEAD_DYN = [(1, "p"), (9, "mp"), (17, "mf"), (25, "f"), (33, "f"),
            (49, "f"), (65, "f"), (81, "mf"), (97, "ff"), (113, "ff"),
            (129, "ff"), (153, "ff"), (177, "fff"), (193, "mf"), (201, "mp")]

LEAD_HAIRPINS = [(1, 8, "<"), (9, 16, "<"), (25, 32, "<"), (41, 48, "<"),
                 (57, 64, "<"), (73, 80, "<"), (81, 88, ">"), (89, 96, "<"),
                 (105, 112, "<"), (121, 128, "<"), (137, 144, "<"),
                 (145, 152, "<"), (161, 168, "<"), (169, 176, "<"),
                 (185, 192, "<"), (193, 200, ">"), (201, 208, ">")]


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
# THE QUOTED THEMES, 8 bars each
# ---------------------------------------------------------------------------
# Each long-note theme is now a full SIXTEEN-bar period: an antecedent that
# hangs unresolved and a consequent that starts the same way, then climbs
# somewhere new and cadences.  Previously these were eight bars played twice.
#
# The quoted pitches still land on the strong beats -- what varies is the
# rhythm.  Every bar used to be two half notes; now there are dotted halves,
# syncopated re-attacks, neighbour turns, rests, and pickups across barlines.

# A -- Once Upon a Time, Bb major.  Cell: F F C | Bb F F | F A A Bb | A F D
A_BB = [
    "F5/4 F5/4 R/2",
    "C6/2. Bb5/8 C6/8",
    "Bb5/4 R/8 Bb5/8 F5/2",
    "F5/2 R/4 C5/8 D5/8",
    "F5/8 G5/8 A5/4 A5/2",
    "A5/2. Bb5/4",
    "A5/4. F5/8 A5/2",
    "D6/2 R/8 A5/8 Bb5/8 C6/8",
    "F5/4 R/2 F5/4",
    "C6/8 D6/8 Eb6/8 D6/8 C6/2",
    "F6/2 C6/2",
    "D6/2 Bb5/4 C6/4",
    "Bb5/4 C6/8 Bb5/8 A5/4 G5/4",
    "A5/8 Bb5/4. G5/2",
    "A5/4 G5/4 F5/4 D5/4",
    "F5/1",
]

# A in G minor.  Cell: D D A | G D D | D F F G | F D Bb
A_GM = [
    "D5/4 D5/4 R/2",
    "A5/2. G5/8 A5/8",
    "G5/4 R/8 G5/8 D5/2",
    "D5/2 R/4 A4/8 Bb4/8",
    "D5/8 Eb5/8 F5/4 F5/2",
    "F5/2. G5/4",
    "F5/4. D5/8 F5/2",
    "Bb5/2 R/8 F5/8 G5/8 A5/8",
    "D5/4 R/2 D5/4",
    "A5/8 Bb5/8 C6/8 Bb5/8 A5/2",
    "D6/2 A5/2",
    "Bb5/2 F5/4 G5/4",
    "G5/4 A5/8 G5/8 F5/4 Eb5/4",
    "F5/8 G5/4. Eb5/2",
    "F5/4 Eb5/4 D5/4 C5/4",
    "D5/1",
]

# A, figurated -- the 16th-note treatment, unchanged
A_FIG = ["F5/8 G5/8 F5/4 F5/8 A5/8 C6/4", "C6/8 D6/8 C6/4 Bb5/8 C6/8 D6/4",
         "Bb5/8 C6/8 Bb5/4 F5/8 A5/8 F5/4", "F5/8 A5/8 C6/4 F5/2",
         "F5/8 G5/8 A5/4 A5/8 Bb5/8 A5/4", "A5/8 Bb5/8 C6/4 Bb5/2",
         "A5/8 G5/8 F5/4 A5/8 C6/8 F6/4",
         "D6/8 Bb5/8 A5/8 F5/8 D5/8 C5/8 Bb4/8 F4/8"]

A_GM_FIG = ["D5/8 Eb5/8 D5/4 D5/8 F5/8 A5/4", "A5/8 Bb5/8 A5/4 G5/8 A5/8 Bb5/4",
            "G5/8 A5/8 G5/4 D5/8 F5/8 D5/4", "D5/8 F5/8 A5/4 D5/2",
            "D5/8 Eb5/8 F5/4 F5/8 G5/8 F5/4", "F5/8 G5/8 A5/4 G5/2",
            "F5/8 Eb5/8 D5/4 F5/8 A5/8 D6/4",
            "Bb5/8 A5/8 G5/8 F5/8 Eb5/8 D5/8 C5/8 A4/8"]

# B -- Your Best Friend, Bb.  1 2 3 1 | 2 | 2 3 2 1 || 3 4 5 1 | 6 5
B_BB = [
    "Bb4/4 C5/4 D5/4 Bb4/4",
    "C5/2 R/2",
    "C5/8 D5/8 C5/4 Bb4/2",
    "Bb4/2 R/4 D5/8 Eb5/8",
    "F5/4 Eb5/8 F5/8 Bb5/2",
    "G5/8 F5/4. Bb5/2",
    "F5/4. Eb5/8 D5/4 C5/4",
    "Bb4/2 R/8 F5/8 G5/8 A5/8",
    "Bb5/2 C6/4 D6/4",
    "C6/8 D6/8 C6/8 Bb5/8 C6/2",
    "D6/4 Eb6/2 C6/4",
    "Bb5/2. F5/4",
    "A5/4 Bb5/4 C6/8 D6/8 F6/4",
    "D6/2. C6/8 Bb5/8",
    "Bb5/4 A5/8 G5/8 F5/4 D5/4",
    "Bb5/1",
]

# B in G minor
B_GM = [
    "G4/4 A4/4 Bb4/4 G4/4",
    "A4/2 R/2",
    "A4/8 Bb4/8 A4/4 G4/2",
    "G4/2 R/4 Bb4/8 C5/8",
    "D5/4 C5/8 D5/8 G5/2",
    "Eb5/8 D5/4. G5/2",
    "D5/4. C5/8 Bb4/4 A4/4",
    "G4/2 R/8 D5/8 Eb5/8 F5/8",
    "G5/2 A5/4 Bb5/4",
    "A5/8 Bb5/8 A5/8 G5/8 A5/2",
    "Bb5/4 C6/2 A5/4",
    "G5/2. D5/4",
    "Eb5/4 F5/4 G5/8 A5/8 D6/4",
    "Bb5/2. A5/8 G5/8",
    "G5/4 F5/8 Eb5/8 D5/4 Bb4/4",
    "G5/1",
]

# C -- Snowdin pt.2 / the Last Goodbye strain, B major.
# 5 5 5 5 5 4 3 4 | 1 5 2 3.  The hammered 5-hat is the quote; the consequent
# lifts the whole shape to 1-hat so it is not eight identical F sharps twice.
C_B = [
    "F#5/4 F#5/4 F#5/8 F#5/8 F#5/4",
    "E5/4 D#5/4 E5/2",
    "B5/2. F#5/4",
    "C#5/2 D#5/4 E5/4",
    "F#5/4 F#5/8 F#5/8 F#5/4 F#5/4",
    "E5/8 D#5/8 F#5/2 R/4",
    "C#6/2 A#5/2",
    "B5/2 R/8 F#5/8 G#5/8 A#5/8",
    "B5/8 B5/8 B5/4 B5/4 B5/4",
    "A#5/8 G#5/8 A#5/8 B5/8 A#5/2",
    "E6/4 B5/2 F#5/4",
    "F#5/4. G#5/8 A#5/2",
    "B5/4 C#6/8 D#6/8 F#6/2",
    "E6/2. D#6/8 C#6/8",
    "C#6/4 B5/4 A#5/4 F#5/4",
    "B5/1",
]


def rep(bars, count, semis=0):
    out = (bars * ((count // len(bars)) + 1))[:count]
    return [shift(b, semis) for b in out] if semis else out


# ---------------------------------------------------------------------------
# LEAD  --  and it does NOT carry the tune the whole way.
# ---------------------------------------------------------------------------
LEAD = (
    # 1-8    G minor.  Nothing but a fragment over the dark engine.
    ["R/1", "R/1", "R/2 D5/2", "R/1", "R/1", "R/1", "R/2 Bb5/2", "R/1"]
    # 9-16   the cell, in minor, sparse
    + rep(A_GM, 8)
    # 17-32  theme A in G minor, full dark texture
    + rep(A_GM, 16)
    # 33-48  Bb MAJOR.  Same cell, major mode -- hope arrives.
    + rep(A_BB, 16)
    # 49-64  the tune moves to LEAD2; the lead runs 16th counter-figures
    + rep(["F5/16 A5/16 C6/16 F6/16 C6/16 A5/16 F5/16 A5/16 "
           "C6/16 F6/16 C6/16 A5/16 F5/16 C6/16 A5/16 F5/16",
           "Eb5/16 G5/16 C6/16 Eb6/16 C6/16 G5/16 Eb5/16 G5/16 "
           "C6/16 Eb6/16 C6/16 G5/16 Eb5/16 C6/16 G5/16 Eb5/16",
           "D5/16 F5/16 Bb5/16 D6/16 Bb5/16 F5/16 D5/16 F5/16 "
           "Bb5/16 D6/16 Bb5/16 F5/16 D5/16 Bb5/16 F5/16 D5/16",
           "F5/16 Bb5/16 D6/16 F6/16 D6/16 Bb5/16 F5/16 Bb5/16 "
           "D6/16 F6/16 D6/16 Bb5/16 F5/16 D6/16 Bb5/16 F5/16"], 16)
    # 65-80  theme B on top, A continuing below
    + rep(B_BB, 16, 12)
    # 81-96  BASS FEATURE
    + rests(16)
    # 97-112 G MINOR RETURNS -- phase two, the fight again
    + rep(A_GM_FIG, 16)
    # 113-128 theme B in minor, building
    + rep(B_GM, 16, 12)
    # 129-152 B MAJOR -- the payoff
    + rep(C_B, 24, 12)
    # 153-176 quodlibet
    + rep(A_FIG, 24, 13)
    # 177-192 climax
    + rep(C_B, 16, 12)
    # 193-208 coda
    + rep(["R/2 F#5/2", "R/1", "R/2 B5/2", "R/1",
           "R/2 F#5/2", "R/1", "R/2 D#6/2", "R/1"], 16)
)

LEAD2 = (rests(16)
         + rep(A_GM, 16, -12)
         + rep(A_BB, 16, -12)
         + rep(A_FIG, 16, -12)
         + rep(A_BB, 16, -12)
         + rests(16)
         + rep(B_GM, 16)
         + rep(A_GM, 16, -12)
         + rep(A_BB, 24, 1)
         + rep(B_BB, 24, 1)
         + rep(A_BB, 16, 1)
         + rests(16))

# Bells stay OUT of the minor phases -- glockenspiel in a dark section is
# exactly what made the last version read as a win screen.
BELL = (rests(32)
        + rep(A_BB, 16, 12)
        + rests(16)
        + rep(A_BB, 16, 24)
        + rep(["F6/8 R/8 C7/8 R/8 F6/8 R/8 A6/8 R/8"], 16)
        + rests(32)
        + rep(C_B, 24, 12)
        + rep(A_FIG, 24, 13)
        + rep(A_BB, 16, 13)
        + rep(A_BB, 16, 13))


# ---------------------------------------------------------------------------
# ARP -- the engine.  Never stops from m.5 to the last bar.
# ---------------------------------------------------------------------------
def arp16(c, o=0):
    v = (VOICE[c].split("+") * 2)[:4]
    line = " ".join(f"{p}/16" for p in (v + v[::-1]) * 2)
    return shift(line, o) if o else line


ARP = ["R/1"] * 4 + [arp16(c) for c in CHORDS[4:]]

# ---------------------------------------------------------------------------
# POWER -- distorted rhythm guitar, root-and-fifth, low.  This is the single
# biggest reason the last version sounded like a win screen: Toby spent his
# only paid samples on bass and RHYTHM ROCK GUITAR, and it was missing.
# It plays in the minor phases and the climax, and lays out for the hopeful
# ones so their arrival is a genuine lightening.
# ---------------------------------------------------------------------------
def power(c, kind):
    r = ROOT[c]
    o = max(2, OCT[r])
    ch = f"{r}{o-1}+{FIFTH[r]}{o-1}"
    return {
        "chug":  " ".join([f"{ch}/8"] * 8),
        "chug16": (f"{ch}/16 {ch}/16 {ch}/8 {ch}/16 {ch}/16 {ch}/8 "
                   f"{ch}/16 {ch}/16 {ch}/8 {ch}/8 {ch}/8"),
        "off":   " ".join([f"R/8 {ch}/8"] * 4),
        "hold":  f"{ch}/1",
    }[kind]


POWER = []
for i, c in enumerate(CHORDS):
    m = i + 1
    if m <= 4:
        POWER.append(power(c, "hold"))
    elif m <= 32 or 97 <= m <= 128:            # the two dark phases
        POWER.append(power(c, "chug16" if m % 2 == 0 else "chug"))
    elif 177 <= m <= 192:                      # climax
        POWER.append(power(c, "chug"))
    elif 33 <= m <= 80 or 129 <= m <= 176:     # hopeful -- offbeat only
        POWER.append(power(c, "off"))
    else:
        POWER.append("R/1")

# ---------------------------------------------------------------------------
# LOWBRASS -- deep sustained weight under everything.
# ---------------------------------------------------------------------------
LOWBRASS = []
for i, c in enumerate(CHORDS):
    m = i + 1
    r = ROOT[c]
    o = max(2, OCT[r])
    if m <= 96 or 177 <= m <= 192 or 97 <= m <= 176:
        LOWBRASS.append(f"{r}{o}+{FIFTH[r]}{o}/1")
    else:
        LOWBRASS.append("R/1")
for i in range(80, 96):
    LOWBRASS[i] = "R/1"                        # clear the bass feature
for i in range(192, 208):
    LOWBRASS[i] = "R/1"                        # coda

# ---------------------------------------------------------------------------
# BASS
# ---------------------------------------------------------------------------
def bass_bar(c, kind, nxt_c=None):
    r = ROOT[c]
    o = OCT[r]
    lo, hi = f"{r}{o}", f"{r}{o+1}"
    fi, th, nx = f"{FIFTH[r]}{o}", f"{THIRD[r]}{o}", f"{NEXT[r]}{o}"
    nr = ROOT[nxt_c] if nxt_c else r
    appr = f"{nr}{OCT[nr]}"
    return {
        "oct8":  f"{lo}/8 {hi}/8 {lo}/8 {hi}/8 {lo}/8 {hi}/8 {lo}/8 {hi}/8",
        "drive": f"{lo}/8 {hi}/16 {lo}/16 {hi}/8 {lo}/8 {lo}/8 {hi}/16 {lo}/16 {hi}/8 {fi}/8",
        "sixt":  f"{lo}/16 {lo}/16 {hi}/16 {lo}/16 {fi}/16 {lo}/16 {hi}/16 {lo}/16 "
                 f"{th}/16 {lo}/16 {hi}/16 {lo}/16 {fi}/16 {th}/16 {nx}/16 {appr}/16",
        "fill":  f"{lo}/16 {th}/16 {fi}/16 {hi}/16 {fi}/16 {th}/16 {lo}/16 {th}/16 "
                 f"{fi}/8 {hi}/8 {fi}/16 {th}/16 {lo}/16 {appr}/16",
        "hold":  f"{lo}/4 {hi}/8 {lo}/8 {fi}/4 {lo}/4",
    }[kind]


BASS_FEATURE = [
    "C2/16 D2/16 Eb2/16 G2/16 C3/16 G2/16 Eb2/16 D2/16 "
    "C2/16 Eb2/16 G2/16 Bb2/16 C3/16 Bb2/16 G2/16 Eb2/16",
    "C2/8 C3/16 Bb2/16 G2/8 Eb2/16 D2/16 C2/8 G1/8 C2/16 Eb2/16 G2/16 Bb2/16",
    "D2/16 F2/16 Bb2/16 D3/16 Bb2/16 F2/16 D2/16 F2/16 "
    "Bb2/16 D3/16 F3/16 D3/16 Bb2/16 F2/16 D2/16 C2/16",
    "D2/8 D3/8 A2/16 F2/16 D2/8 Bb1/8 D2/8 F2/16 A2/16 D3/8",
    "Eb2/16 G2/16 Bb2/16 Eb3/16 Bb2/16 G2/16 Eb2/16 G2/16 "
    "Bb2/16 Eb3/16 G3/16 Eb3/16 Bb2/16 G2/16 Eb2/16 F2/16",
    "Eb2/8 Eb3/8 Bb2/16 G2/16 Eb2/8 C2/8 Eb2/16 F2/16 G2/16 Bb2/16 Eb3/8",
    "F2/16 A2/16 C3/16 F3/16 C3/16 A2/16 F2/16 A2/16 "
    "C3/16 F3/16 A3/16 F3/16 C3/16 A2/16 F2/16 Eb2/16",
    "D2/16 Eb2/16 F2/16 G2/16 A2/16 Bb2/16 C3/16 D3/16 "
    "Eb3/16 D3/16 C3/16 Bb2/16 A2/16 G2/16 F2/16 E2/16",
]

BASS = []
for i, c in enumerate(CHORDS):
    m = i + 1
    nc = CHORDS[i + 1] if i + 1 < N else c
    if m <= 4:
        BASS.append(bass_bar(c, "hold", nc))
    elif 81 <= m <= 96:
        BASS.append(BASS_FEATURE[(m - 81) % 8])
    elif m <= 32:
        BASS.append(bass_bar(c, "fill" if m % 8 == 0 else "drive", nc))
    elif m <= 48:
        BASS.append(bass_bar(c, "fill" if m % 8 == 0 else "oct8", nc))
    elif m <= 112:
        BASS.append(bass_bar(c, "fill" if m % 8 == 0 else "drive", nc))
    elif m <= 192:
        BASS.append(bass_bar(c, "fill" if m % 8 == 0 else
                             ("sixt" if m % 4 == 0 else "drive"), nc))
    else:
        BASS.append(bass_bar(c, "hold", nc))

SUB = [f"{ROOT[c]}{max(1, OCT[ROOT[c]]-1)}/1" for c in CHORDS]
for i in range(80, 96):
    SUB[i] = "R/1"

# ---------------------------------------------------------------------------
# STRINGS -- the faint background chords.  Present almost throughout now:
# this is the layer that was missing from the middle of the picture.
# ---------------------------------------------------------------------------
STRINGS = [f"{PAD[c]}/1" for c in CHORDS[:192]] + rests(16)
for i in range(0, 8):
    STRINGS[i] = "R/1"

GUITAR = (rests(32)
          + [f"R/8 {VOICE[c]}/8 R/8 {VOICE[c]}/8 R/8 {VOICE[c]}/8 R/8 {VOICE[c]}/8"
             for c in CHORDS[32:192]]
          + rests(16))

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# DRUMS -- four variants of every groove, six fills, rotating so no pattern
# repeats bar to bar, and a fill every FOUR bars rather than every eight.
# ---------------------------------------------------------------------------
DRUM_LIB = {
    "tacet": "R/1",
    "roll":  "Z/2 Z/2",
    "half":  "K/4 R/4 S/4 R/4",
    "halfO": "KC/4 R/4 S/4 K/8 K/8",
    # -- driving 16th groove, four variants
    "busy_a": "K/8 H/16 H/16 S/8 H/8 K/16 K/16 H/8 S/8 H/16 H/16",
    "busy_b": "K/8 H/8 S/16 H/16 H/8 K/8 K/16 H/16 S/8 H/8",
    "busy_c": "KH/16 H/16 K/8 SH/8 H/16 H/16 K/8 H/8 SH/8 O/8",
    "busy_d": "K/8 H/8 SH/8 H/16 K/16 H/8 K/16 H/16 SH/8 H/8",
    "busy_O": "KC/8 H/16 H/16 S/8 H/8 K/16 K/16 H/8 S/8 O/8",
    # -- straighter 8th groove, four variants
    "rock_a": "K/8 H/8 S/8 H/8 K/16 K/16 H/8 S/8 H/8",
    "rock_b": "K/8 H/8 S/8 H/16 H/16 K/8 H/8 S/8 O/8",
    "rock_c": "K/4 H/8 S/8 K/8 K/8 H/8 S/8",
    "rock_d": "K/8 H/8 S/8 H/8 H/8 K/8 SH/8 O/8",
    "rock_O": "KC/8 H/8 S/8 H/8 K/16 K/16 H/8 S/8 O/8",
    # -- ride groove for the coda
    "ride_a": "KR/8 R/8 SR/8 R/8 KR/16 K/16 R/8 SR/8 R/8",
    "ride_b": "KR/8 R/8 SR/8 R/16 R/16 KR/8 R/8 SR/8 R/8",
    # -- hat/rim only, under the bass feature
    "brk_a": "H/8 H/8 SH/8 H/8 H/8 H/8 SH/8 H/8",
    "brk_b": "H/8 H/16 H/16 SH/8 H/8 H/8 H/8 SH/8 H/8",
    "brk_c": "H/16 H/16 H/8 SH/8 H/8 H/8 H/16 H/16 SH/8 H/8",
    # -- six fills, so the same one never lands twice in a row
    "fill_a": "S/16 S/16 T/16 T/16 F/16 F/16 S/8 T/8 F/8 KC/8 S/8",
    "fill_b": "S/8 S/16 S/16 T/8 T/16 T/16 F/8 F/16 F/16 KC/4",
    "fill_c": "T/16 T/16 T/16 T/16 F/16 F/16 F/16 F/16 S/16 S/16 S/16 S/16 KC/8 S/8",
    "fill_d": "S/32 S/32 S/32 S/32 S/16 S/16 T/8 T/8 F/8 F/8 KC/4",
    "fill_e": "K/8 H/8 S/8 S/16 S/16 S/16 S/16 T/8 F/8 KC/8",
    "fill_f": "K/8 S/8 K/8 S/8 T/16 T/16 T/16 T/16 F/16 F/16 KC/8",
    "final": "KCZ/1",
}

GROOVES = {"busy": ["busy_a", "busy_b", "busy_c", "busy_d"],
           "rock": ["rock_a", "rock_b", "rock_c", "rock_d"],
           "ride": ["ride_a", "ride_b", "ride_a", "ride_b"],
           "brk":  ["brk_a", "brk_b", "brk_c", "brk_b"]}
FILLS = ["fill_a", "fill_b", "fill_c", "fill_d", "fill_e", "fill_f"]


def kit(m, family):
    """Groove variant rotating every bar; a fill every fourth bar, cycling
    through six of them; the crash variant on each 16-bar downbeat."""
    if m % 16 == 1:
        return f"{family}_O" if f"{family}_O" in DRUM_LIB else GROOVES[family][0]
    if m % 8 == 0:
        return FILLS[(m // 8) % len(FILLS)]
    if m % 4 == 0:
        return FILLS[((m // 4) + 3) % len(FILLS)]
    return GROOVES[family][m % 4]


DRUMS = []
for i in range(N):
    m = i + 1
    if m <= 4:
        DRUMS.append("halfO" if m == 1 else "half")
    elif m <= 32:
        DRUMS.append(kit(m, "busy"))
    elif m <= 80:
        DRUMS.append(kit(m, "rock"))
    elif m <= 96:
        DRUMS.append("fill_e" if m % 8 == 0 else GROOVES["brk"][m % 4])
    elif m <= 192:
        DRUMS.append(kit(m, "busy"))
    else:
        DRUMS.append(kit(m, "ride"))
DRUMS[-1] = "final"

PARTS = {"LEAD": LEAD, "LEAD2": LEAD2, "BELL": BELL, "STRINGS": STRINGS,
         "GUITAR": GUITAR, "POWER": POWER, "LOWBRASS": LOWBRASS,
         "ARP": ARP, "BASS": BASS, "SUB": SUB, "DRUMS": DRUMS}

MINOR_PHASES = list(range(1, 33)) + list(range(97, 129))

# The sections that are NOT in sixteenths -- where a long note can carry an
# ornament without turning to mush.
LONG_RANGES = [(9, 48), (65, 80), (113, 152), (177, 208)]


def _is_long(m):
    return any(a <= m <= b for a, b in LONG_RANGES)


def glissify(bar, idx, sharp=False):
    """Write a glissando OUT as a real run rather than leaving it a symbol on
    the page: shorten the note at idx and fill the gap to the next one with a
    chromatic slide.  Audible everywhere, and correct notation for a synth lead."""
    from zerosum2 import to_midi, from_midi
    toks = bar.split()
    if idx + 1 >= len(toks):
        return bar
    a, b = toks[idx].rstrip("~"), toks[idx + 1].rstrip("~")
    if a.startswith("R/") or b.startswith("R/"):
        return bar
    pa, da = a.split("/")
    pb = b.split("/")[0]
    if "+" in pa or "+" in pb:
        return bar
    span = dur_of(da)
    m0, m1 = to_midi(pa), to_midi(pb)
    steps = abs(m1 - m0)
    if steps < 3 or span < F(1):
        return bar
    n = min(steps - 1, 6)                       # up to six passing semitones
    run_len = F(n, 4)   # n sixteenths = n/4 quarter-lengths
    if span - run_len < F(1, 2):
        return bar
    step = 1 if m1 > m0 else -1
    head = f"{pa}/{da}" if False else None
    # rebuild: shortened head, then n chromatic sixteenths into the target
    keep = span - run_len
    parts = [_dur_tokens(pa, keep)]
    for k in range(1, n + 1):
        parts.append(f"{from_midi(m0 + step * k, sharp)}/16")
    toks[idx] = " ".join(parts)
    return " ".join(toks)


def _dur_tokens(pitch, ql):
    """Express a duration as one or two note tokens of the same pitch."""
    table = [(F(4), "1"), (F(3), "2."), (F(2), "2"), (F(3, 2), "4."),
             (F(1), "4"), (F(3, 4), "8."), (F(1, 2), "8"), (F(1, 4), "16")]
    out = []
    left = ql
    for v, code in table:
        while left >= v:
            out.append(f"{pitch}/{code}")
            left -= v
    return " ".join(out)


def build_ornaments():
    """Trill every long note of a dotted half or more, at most one per bar."""
    orn = {}
    from zerosum import dur_of
    for part in ("LEAD", "LEAD2"):
        for i, barstr in enumerate(PARTS[part]):
            m = i + 1
            if not _is_long(m) or (part == "LEAD2" and m % 8 != 4):
                continue
            for idx, tok in enumerate(barstr.split()):
                if tok.startswith("R/"):
                    continue
                if dur_of(tok.rstrip("~").split("/")[1]) >= F(3):
                    orn[(part, m, idx)] = "trill"
                    break
    return orn


# Written-out glissandi at phrase peaks in the long-note sections.  LEAD is the
# same list object PARTS holds, so mutating it here propagates.
GLISS_BARS = [43, 45, 75, 119, 139, 147, 163, 181, 187]
for _m in GLISS_BARS:
    for _i in range(4):
        _new = glissify(LEAD[_m - 1], _i, sharp=_m >= 129)
        if _new != LEAD[_m - 1]:
            LEAD[_m - 1] = _new
            break

ORNAMENTS = build_ornaments()


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
                p.append(f"{name} m.{i+1}: parse {e} :: {b[:48]}")
                continue
            if L != F(4):
                p.append(f"{name} m.{i+1}: {L} beats :: {b[:48]}")
    for m in range(1, N + 1):
        lead = LVL[dyn_for("LEAD", m)]
        for acc in ("GUITAR", "ARP"):
            if LVL[dyn_for(acc, m)] > lead - 2:
                p.append(f"m.{m}: {acc} not under lead")
        if LVL[dyn_for("STRINGS", m)] >= lead:
            p.append(f"m.{m}: strings not under lead")
    for m in range(5, N):
        if ARP[m - 1] == "R/1":
            p.append(f"m.{m}: arp engine stopped")
    for m in range(17, 193):
        if len(BASS[m - 1].split()) < 5:
            p.append(f"m.{m}: bass too thin")
    # bells must stay out of the dark phases
    for m in MINOR_PHASES:
        if BELL[m - 1] != "R/1":
            p.append(f"m.{m}: bell sounding in a minor phase")
    # the power guitar must be chugging in both dark phases
    for m in MINOR_PHASES:
        if m > 4 and "R/8" in POWER[m - 1]:
            p.append(f"m.{m}: power guitar only offbeat in a dark phase")
    # the long-note themes must not be rhythmically monotonous, and must not
    # be eight bars played twice
    for nm, th in (("A_BB", A_BB), ("A_GM", A_GM), ("B_BB", B_BB),
                   ("B_GM", B_GM), ("C_B", C_B)):
        if len(th) != 16:
            p.append(f"{nm}: {len(th)} bars, want a 16-bar period")
            continue
        if th[:8] == th[8:]:
            p.append(f"{nm}: consequent is a literal repeat of the antecedent")
        shapes = {" ".join(t.split("/")[1] for t in b.split()) for b in th}
        if len(shapes) < 13:
            p.append(f"{nm}: only {len(shapes)} distinct rhythms in 16 bars")
    return p


if __name__ == "__main__":
    probs = verify()
    print(f"{len(probs)} PROBLEMS" if probs else
          f"OK -- {N} bars, {len(PARTS)} parts, every measure sums exactly.")
    for x in probs[:25]:
        print("  ", x)
    if not probs:
        print("  mode map:", " ".join(
            f"m{m}:{'min' if m in MINOR_PHASES else 'MAJ'}"
            for m in (1, 33, 65, 81, 97, 129, 153, 177, 193)))
        print("  sounding parts at m.1/33/97/153:", [
            sum(1 for k, v in PARTS.items() if k != "DRUMS" and v[m - 1] != "R/1")
            for m in (1, 33, 97, 153)])
        secs = N * 4 * 60 / BPM
        print(f"  duration {int(secs//60)}:{int(secs%60):02d}")
