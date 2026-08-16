"""
THREE FIGHTS  (rebuild) -- a medley-variation suite on three Toby Fox themes.

  I.   FLOWER    (Finale)            mm.   1– 56   F minor       q=95
       bridge A  -- shared dim7       mm.  57– 64
  II.  GLAMOUR   (Death by Glamour)  mm.  65–120   B min/E Dorian q=148
       -- bass break                  mm.  97–104
       bridge B  -- chromatic descent mm. 121–128
  III. BAD TIME  (MEGALOVANIA)       mm. 129–184   D minor       q=126
  IV.  QUODLIBET + coda              mm. 185–216   D minor       q=126

This version QUOTES the source themes directly and then varies them, rather
than only borrowing their harmonic frames.  A fan arrangement -- releasing it
commercially would need clearance from Toby Fox / Materia.

THE QUOTED MATERIAL
-------------------
Q1  MEGALOVANIA riff.  One bar of sixteen sixteenths:
        D3 D3 D4 A3 Ab3 G3 F3 D3 F3 G3
        durations 1 1 2 3 2 2 2 1 1 1
    Across the four-bar unit only the FIRST TWO notes move: D-D, C-C, B-B,
    Bb-Bb, i.e. i - bVII - bVI - V.  Everything else is invariant.

Q2  MEGALOVANIA verse contour:
        A A G F E E D C  D E F G A G F E

Q3  "Your Best Friend" -- the tune Finale sets in minor with brass.
    Scale degrees:  1 2 3 | 1 | 2 | 2 3 2 | 1  ||  3 4 5 | 1 | 6 | 5
    In F minor:     F G Ab | F | G | G Ab G | F  ||  Ab Bb C | F | Db | C

Q4  Death by Glamour bass cell, E Dorian:
        E - G - D - C#     with D->C# slurred, never picked.
    The C# is the natural 6th.  Without it this is generic minor.

THE MOTTO (mine, welding the suite): b6 - 5 - 1.
    F minor Db-C-F   B minor G-F#-B   D minor Bb-A-D

QUODLIBET, mm.185-200: Q1 in the bass, Q3 in the lead, Q4's slur in the
counter -- all three fights at once, in D minor.  That is the point of the
whole piece.
"""

from fractions import Fraction as F
from zerosum import bar_len, dur_of
from zerosum2 import shift, oct_down, to_midi, from_midi, rests

TITLE = "THREE FIGHTS"
N = 216

# ---------------------------------------------------------------------------
# DYNAMICS
# ---------------------------------------------------------------------------
LEVELS = ["ppp", "pp", "p", "mp", "mf", "f", "ff", "fff"]
LVL = {d: i for i, d in enumerate(LEVELS)}
OFFSET = {"LEAD": 0, "COUNTER": -1, "SUSTAIN": -2, "STABS": -2,
          "KEYS": -1, "BASS": 0, "DRUMS": -1}     # BASS now equals the melody

LEAD_DYN = [
    (1, "f"), (5, "ff"), (9, "mf"), (17, "f"), (25, "mf"), (33, "ff"),
    (41, "ff"), (49, "f"), (53, "ff"),
    (57, "mf"), (61, "p"),
    (65, "mp"), (69, "mf"), (73, "f"), (81, "f"), (89, "ff"),
    (97, "mf"), (105, "f"), (113, "ff"),
    (121, "f"), (125, "mf"),
    (129, "mf"), (133, "f"), (137, "ff"), (145, "ff"), (153, "f"),
    (161, "ff"), (169, "ff"), (177, "ff"),
    (185, "ff"), (193, "fff"), (201, "fff"), (209, "fff"),
]

LEAD_HAIRPINS = [
    (1, 4, "<"), (9, 12, "<"), (13, 16, ">"), (21, 24, "<"), (29, 32, "<"),
    (37, 40, "<"), (45, 48, ">"), (49, 52, "<"), (53, 56, "<"),
    (57, 60, ">"), (61, 64, "<"),
    (69, 72, "<"), (77, 80, "<"), (85, 88, "<"), (93, 96, ">"),
    (97, 100, "<"), (101, 104, "<"), (109, 112, "<"), (117, 120, "<"),
    (121, 124, ">"), (125, 128, "<"),
    (133, 136, "<"), (141, 144, "<"), (149, 152, ">"), (157, 160, "<"),
    (165, 168, "<"), (173, 176, "<"), (181, 184, "<"),
    (189, 192, "<"), (197, 200, "<"), (205, 208, "<"), (213, 216, "<"),
]


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
# ORNAMENTS -- (measure, index of the note within that bar) -> kind
# ---------------------------------------------------------------------------
# Ornaments sit only on notes of a quarter or longer -- a trill on a sixteenth
# is unplayable and unreadable.  validate_ornaments() enforces that.
ORNAMENTS = {
    ("LEAD", 12, 0): "trill", ("LEAD", 16, 0): "trill", ("LEAD", 24, 0): "trill",
    ("LEAD", 40, 0): "trill", ("LEAD", 48, 0): "turn",  ("LEAD", 56, 4): "trill",
    ("LEAD", 88, 6): "trill", ("LEAD", 120, 0): "trill",
    ("LEAD", 152, 6): "turn", ("LEAD", 192, 0): "trill",
    ("LEAD", 200, 0): "trill", ("LEAD", 211, 0): "trill",
    ("BASS", 104, 10): "trill",
}
# Grace notes are neighbours of the note they lead into -- a semitone or a tone
# below it -- never a leap.
GRACE = {
    ("LEAD", 17): "E5",   ("LEAD", 33): "E6",   ("LEAD", 41): "C7",
    ("LEAD", 73): "D#5",  ("LEAD", 105): "D#5", ("LEAD", 113): "A#6",
    ("LEAD", 137): "G#5", ("LEAD", 169): "G#6", ("LEAD", 193): "C#6",
    ("BASS", 97): "D#1",  ("BASS", 101): "G#1",
}
# Glissandi only across a third or wider, and only into a note worth sliding to.
GLISS = [("LEAD", 32, 0), ("LEAD", 52, 2), ("LEAD", 96, 3),
         ("LEAD", 184, 5), ("LEAD", 208, 5),
         ("BASS", 100, 8), ("BASS", 104, 9)]

# ---------------------------------------------------------------------------
# Q1  --  the MEGALOVANIA riff, exact.
# ---------------------------------------------------------------------------
# The riff is TEN notes.  Only the first two change across the four-bar unit;
# sixteenths 3-16 -- starting with the octave D4 -- are identical every bar.
#   d d d a G g f d f g  |  c c d a G g f d f g  |  b b d ...  |  A A d ...
Q1_TAIL = ["D4", "A3", "Ab3", "G3", "F3", "D3", "F3", "G3"]
Q1_RHY = ["16", "16", "8", "8.", "8", "8", "8", "16", "16", "16"]
Q1_HEAD = {"Dm": "D3", "C": "C3", "Bb": "B2", "A5": "Bb2",
           "Am": "A2", "Gm": "G2", "F": "F2", "Eb": "Eb3"}


def q1(chord, oct_shift=0):
    h = Q1_HEAD[chord]
    line = " ".join(f"{p}/{d}" for p, d in zip([h, h] + Q1_TAIL, Q1_RHY))
    return shift(line, oct_shift) if oct_shift else line


# ---------------------------------------------------------------------------
# I.  FLOWER            mm. 1-56       F minor (4b)      q = 95
# ---------------------------------------------------------------------------
CH_I = (["Fm", "Fm", "Db", "Eb", "Fm", "Fm", "C7", "C7"]        # 1-8  intro
        + ["Fm", "Fm", "Db", "Eb", "Fm", "Fm", "C7", "Fm"]      # 9-16 Q3
        + ["Fm", "Fm", "Db", "Eb", "Db", "Eb", "C7", "Fm"]      # 17-24 Q3 varied
        + ["Db", "Eb", "Ab", "Cm", "Db", "Eb", "Fm", "C7"]      # 25-32 B
        + ["Fm", "Fm", "Db", "Eb", "Fm", "Fm", "C7", "Fm"]      # 33-40 Q3 ornamented
        + ["Db", "Eb", "Fm", "Cm", "Db", "Eb", "C7", "Fm"]      # 41-48
        + ["Fm", "Db", "Eb", "Fm", "Db", "Db", "C7", "C7"])     # 49-56 build

LEAD_I = [
    # 1-8  the motto, brass, grand
    "R/2 Db5/4 C5/4", "F5/1~", "F5/2 Db5/4 C5/4", "F5/4 Ab5/4 C6/2",
    "C6/2 Db6/4 C6/4", "F6/1~", "F6/2 C6/4 Ab5/4", "G5/2 R/4 C5/8 Db5/8",
    # 9-16  Q3 -- "Your Best Friend", stated plainly in F minor
    "F5/8 G5/8 Ab5/4 F5/2",
    "G5/4 G5/8 Ab5/8 G5/4 F5/4",
    "Ab5/8 Bb5/8 C6/4 F5/2",
    "Db6/4 C6/2 R/8 C5/8",
    "F5/8 G5/8 Ab5/4 F5/2",
    "G5/4 G5/8 Ab5/8 G5/4 F5/4",
    "Ab5/8 Bb5/8 C6/4 Db6/4 C6/4",
    "F5/1",
    # 17-24  Q3 again, but Toby-ised: leaps, 16ths, blue notes, register jumps
    "F5/16 G5/16 Ab5/16 C6/16 F6/8 C6/8 Ab5/4 F5/4",
    "G5/16 Ab5/16 G5/16 F5/16 G5/8 Bb5/8 G5/4 Eb5/4",
    "Ab5/16 Bb5/16 C6/16 Eb6/16 F6/8 Eb6/8 C6/4 Ab5/4",
    "Db6/16 C6/16 Bb5/16 Ab5/16 G5/8 F5/8 C6/4 F6/4",
    "Db6/8 Ab5/8 F6/8 Db6/8 C6/8 Ab5/8 Eb6/8 C6/8",
    "Eb6/8 Bb5/8 G6/8 Eb6/8 Db6/8 Bb5/8 F6/8 Db6/8",
    "C6/16 Db6/16 C6/16 Bb5/16 Ab5/8 G5/8 E5/4 G5/4",
    "F6/2 C6/4 Ab5/4",
    # 25-32  B -- the lyrical strain, mf, thinner
    "Ab5/4 Db6/4 C6/2",
    "Bb5/4 Eb6/4 Db6/2",
    "C6/8 Eb6/8 Ab6/4 G6/4 Eb6/4",
    "C6/2 G5/4 Eb5/4",
    "Db6/8 Eb6/8 F6/4 Ab6/2",
    "Bb6/8 Ab6/8 G6/4 Eb6/2",
    "F6/16 Eb6/16 Db6/16 C6/16 Bb5/8 Ab5/8 G5/4 Bb5/4",
    "E5/2 G5/8 Bb5/8 C6/8 E6/8",
    # 33-40  Q3, top octave, ff, with runs between the phrases
    "F6/8 G6/8 Ab6/4 F6/2",
    "G6/4 G6/8 Ab6/8 G6/4 F6/4",
    "Ab6/8 Bb6/8 C7/4 F6/2",
    "Db7/4 C7/4 Bb6/16 Ab6/16 G6/16 F6/16 Eb6/16 Db6/16 C6/16 Bb5/16",
    "F5/8 G5/8 Ab5/4 F5/2",
    "G5/4 G5/8 Ab5/8 G5/4 F5/4",
    "Ab5/16 Bb5/16 C6/16 Db6/16 Eb6/16 F6/16 G6/16 Ab6/16 C7/4 Ab6/4",
    "F6/1",
    # 41-48
    "Db7/4 C7/4 Ab6/4 F6/4",
    "Eb7/4 Db7/4 Bb6/4 G6/4",
    "C7/8 Ab6/8 F6/4 C6/2",
    "G6/16 Ab6/16 G6/16 F6/16 Eb6/8 C6/8 G5/4 Eb6/4",
    "Db6/8 F6/8 Ab6/8 Db7/8 C7/4 Ab6/4",
    "Eb6/8 G6/8 Bb6/8 Eb7/8 Db7/4 Bb6/4",
    "C7/16 Bb6/16 Ab6/16 G6/16 F6/16 Eb6/16 Db6/16 C6/16 Bb5/8 G5/8 E5/8 G5/8",
    "F6/2 C6/4 F5/4",
    # 49-56  build into bridge A
    "F5/8 Ab5/8 C6/8 F6/8 Ab6/4 F6/4",
    "Db6/8 F6/8 Ab6/8 Db7/8 C7/2",
    "Eb6/8 G6/8 Bb6/8 Eb7/8 Db7/2",
    "F6/16 Ab6/16 C7/16 F7/16 C7/8 Ab6/8 F6/4 C6/4",
    "Db6/4 Db7/4 C7/2",
    "Db6/8 F6/8 Ab6/8 C7/8 Db7/4 Ab6/4",
    "E6/8 G6/8 Bb6/8 Db7/8 E7/4 Db7/4",
    "Bb6/16 G6/16 E6/16 Db6/16 Bb5/4 R/2",
]

# ---------------------------------------------------------------------------
# BRIDGE A              mm. 57-64      E°7 = A#°7
# ---------------------------------------------------------------------------
CH_BR_A = ["Edim7"] * 4 + ["A#dim7"] * 2 + ["F#7"] * 2

LEAD_BR_A = [
    "Db6/2 C6/2",
    "E6/8 G6/8 Bb6/8 Db7/8 Bb6/8 G6/8 E6/8 Db6/8",
    "E6/16 G6/16 Bb6/16 Db7/16 E7/8 Db7/8 Bb6/4 G6/4",
    "E6/1~",
    "E6/2 G6/4 A#6/4",
    "C#7/8 A#6/8 G6/8 E6/8 C#6/4 A#5/4",
    "G5/2 F#5/2",
    "R/4 F#5/8 G5/8 F#5/8 E5/8 D#5/8 F#5/8",
]

# ---------------------------------------------------------------------------
# II. GLAMOUR           mm. 65-120     B minor / E Dorian (2#)   q = 148
# ---------------------------------------------------------------------------
CH_II = (["Em7"] * 8                                                   # 65-72 bass alone
         + ["Em7", "Em7", "A", "A", "Em7", "Em7", "F#7", "B7"]         # 73-80 A
         + ["Em7", "Em7", "A", "A", "G", "G", "F#7", "B7"]             # 81-88
         + ["Em7", "Em7", "A", "A", "C", "C", "F#7", "B7"]             # 89-96 B
         + ["Em7", "Em7", "Em7", "Em7", "A", "A", "Em7", "Em7"]        # 97-104 BASS BREAK
         + ["Em7", "Em7", "A", "A", "G", "G", "F#7", "B7"]             # 105-112 A'
         + ["Em7", "Em7", "A", "A", "C", "B7", "Em7", "Em7"])          # 113-120

LEAD_II = (rests(8)                       # the bass owns the first eight bars
           + [
    # 73-80  A -- Q4's shape lifted into the lead: root, b3, b7, octave
    "R/8 E5/8 G5/8 D5/8 E5/4 R/4",
    "R/8 E5/8 G5/8 D5/8 C#5/8 E5/8 G5/4",
    "R/8 A4/8 C#5/8 G5/8 A5/4 R/4",
    "R/8 A5/8 G5/8 E5/8 C#5/8 A4/8 E5/4",
    "R/8 E5/8 G5/8 B5/8 D6/4 B5/4",
    "A5/8 G5/8 E5/8 D5/8 B4/4 D5/4",
    "F#5/8 A#5/8 C#6/8 E6/8 C#6/4 A#5/4",
    "F#5/16 A#5/16 C#6/16 F#6/16 E6/8 C#6/8 B5/2",
    # 81-88
    "R/8 E5/8 G5/8 D5/8 E5/4 B4/8 D5/8",
    "E5/16 G5/16 B5/16 E6/16 D6/8 B5/8 G5/4 E5/4",
    "R/8 A4/8 C#5/8 G5/8 A5/4 E5/8 G5/8",
    "A5/16 C#6/16 E6/16 A6/16 G6/8 E6/8 C#6/4 A5/4",
    "G5/8 B5/8 D6/8 G6/8 F#6/4 D6/4",
    "B5/8 D6/8 G6/8 D6/8 B5/4 G5/4",
    "A#5/8 C#6/8 E6/8 F#6/8 A#6/4 F#6/4",
    "E6/16 D6/16 C#6/16 B5/16 A#5/8 F#5/8 B5/2",
    # 89-96  B -- ff, the tune climbs
    "E6/8 D6/8 B5/8 G5/8 E5/4 B5/4",
    "E6/16 F#6/16 G6/16 B6/16 A6/8 F#6/8 E6/4 B5/4",
    "A5/8 C#6/8 E6/8 A6/8 G6/4 E6/4",
    "C#6/16 E6/16 A6/16 C#7/16 B6/8 G6/8 E6/2",
    "C6/8 E6/8 G6/8 C7/8 B6/4 G6/4",
    "E6/16 G6/16 C7/16 E7/16 D7/8 B6/8 G6/2",
    "A#6/8 F#6/8 C#6/8 A#5/8 F#5/4 A#5/4",
    "B5/16 C#6/16 D6/16 F#6/16 B6/8 F#6/8 D6/4 B5/4",
    # 97-104  BASS BREAK -- lead out entirely, the bass takes the whole thing
    "R/1", "R/1", "R/1", "R/1", "R/1", "R/1", "R/1", "R/1",
    # 105-112  A' -- lead returns over the busier bass
    "R/8 E5/8 G5/8 D5/8 E5/4 G5/8 B5/8",
    "E6/16 D6/16 B5/16 G5/16 E5/8 B4/8 E5/4 G5/4",
    "R/8 A4/8 C#5/8 G5/8 A5/4 C#6/8 E6/8",
    "A6/16 G6/16 E6/16 C#6/16 A5/8 E5/8 A5/4 C#6/4",
    "G5/8 D6/8 G6/8 B6/8 A6/4 F#6/4",
    "D6/16 F#6/16 A6/16 D7/16 B6/8 G6/8 D6/2",
    "A#6/8 C#7/8 A#6/8 F#6/8 C#6/4 A#5/4",
    "F#5/16 A#5/16 C#6/16 F#6/16 A#6/16 C#7/16 F#7/8 E7/4 C#7/4",
    # 113-120
    "B6/8 A6/8 F#6/8 D6/8 B5/4 F#6/4",
    "E6/8 G6/8 B6/8 E7/8 D7/4 B6/4",
    "A6/8 C#7/8 E7/8 A6/8 G6/4 E6/4",
    "C#6/16 E6/16 A6/16 C#7/16 E7/8 C#7/8 A6/2",
    "C7/8 B6/8 G6/8 E6/8 C6/4 G6/4",
    "F#6/8 D#6/8 B5/8 F#5/8 D#5/4 F#5/4",
    "G5/2 F#5/2",
    "B5/1",
])

# ---------------------------------------------------------------------------
# BRIDGE B              mm. 121-128    E -> Eb -> D
# ---------------------------------------------------------------------------
CH_BR_B = ["Em7", "Em7", "Ebdim7", "Ebdim7", "Dm", "Dm", "A5", "A5"]

LEAD_BR_B = [
    "B5/8 A5/8 G5/8 F#5/8 E5/4 B4/4",
    "E5/16 G5/16 B5/16 E6/16 D6/8 B5/8 G5/4 E5/4",
    "Eb6/8 Db6/8 B5/8 A5/8 Gb5/4 Eb5/4",
    "Eb5/16 Gb5/16 A5/16 C6/16 Eb6/8 C6/8 A5/2",
    "Bb5/2 A5/2",
    "D5/1~",
    "D5/2 R/8 A4/8 Bb4/8 A4/8",
    "A4/16 Ab4/16 G4/16 F4/16 D4/8 F4/8 A4/4 R/4",
]

# ---------------------------------------------------------------------------
# III. BAD TIME         mm. 129-184    D minor (1b)      q = 126
# ---------------------------------------------------------------------------
CH_III = (["Dm", "C", "Bb", "A5"] * 2                            # 129-136 riff builds
          + ["Dm", "C", "Bb", "A5"] * 2                          # 137-144 Q2
          + ["Dm", "C", "Bb", "A5"] * 2                          # 145-152 Q2 varied
          + ["Gm", "F", "Eb", "Dm", "Bb", "C", "Dm", "A5"]       # 153-160 B
          + ["Dm", "C", "Bb", "A5"] * 2                          # 161-168
          + ["Dm", "C", "Bb", "A5"] * 2                          # 169-176
          + ["Dm", "C", "Bb", "A5"] * 2)                         # 177-184

LEAD_III = (rests(8)
            + [
    # 137-144  Q2 -- the MEGALOVANIA verse contour, quoted
    "A5/8 A5/8 G5/8 F5/8 E5/4 E5/4",
    "D5/8 C5/8 D5/8 E5/8 F5/8 G5/8 A5/8 G5/8",
    "F5/4 E5/4 D5/2",
    "A5/16 G5/16 F5/16 E5/16 D5/8 F5/8 A5/4 D6/4",
    "A5/8 A5/8 G5/8 F5/8 E5/4 E5/4",
    "D5/8 C5/8 D5/8 E5/8 F5/8 G5/8 A5/8 C6/8",
    "D6/4 C6/4 A5/2",
    "F5/16 G5/16 A5/16 C6/16 D6/8 C6/8 A5/4 F5/4",
    # 145-152  Q2 up an octave, ornamented
    "A6/8 A6/8 G6/8 F6/8 E6/4 E6/4",
    "D6/8 C6/8 D6/8 E6/8 F6/8 G6/8 A6/8 G6/8",
    "F6/4 E6/4 D6/2",
    "A6/16 G6/16 F6/16 E6/16 D6/8 A5/8 D6/4 F6/4",
    "D6/16 F6/16 A6/16 D7/16 C7/8 A6/8 F6/4 D6/4",
    "C6/16 E6/16 G6/16 C7/16 Bb6/8 G6/8 E6/4 C6/4",
    "Bb5/16 D6/16 F6/16 Bb6/16 A6/8 F6/8 D6/4 Bb5/4",
    "A5/16 C#6/16 E6/16 A6/16 G6/8 E6/8 C#6/4 A5/4",
    # 153-160  B -- the iv region, Q2 sequenced
    "D6/8 D6/8 C6/8 Bb5/8 A5/4 A5/4",
    "G5/8 F5/8 G5/8 A5/8 Bb5/8 C6/8 D6/8 C6/8",
    "Bb5/4 A5/4 G5/2",
    "D6/16 C6/16 Bb5/16 A5/16 G5/8 Bb5/8 D6/4 F6/4",
    "Bb5/8 D6/8 F6/8 Bb6/8 A6/4 F6/4",
    "C6/8 E6/8 G6/8 C7/8 Bb6/4 G6/4",
    "D6/8 F6/8 A6/8 D7/8 C7/4 A6/4",
    "A5/16 B5/16 C#6/16 D6/16 E6/16 F6/16 G6/16 A6/16 C#7/4 A6/4",
    # 161-168  Q1 IN THE LEAD -- the riff itself, two octaves up, screaming
    ] + [q1(c, 24) for c in ["Dm", "C", "Bb", "A5", "Dm", "C", "Bb", "A5"]] + [
    # 169-176  Q2 combined with Q1's tail
    "A6/8 A6/8 G6/8 F6/8 E6/8 D6/8 F6/8 G6/8",
    "A6/8 A6/8 G6/8 F6/8 E6/8 C6/8 E6/8 G6/8",
    "Bb6/8 A6/8 G6/8 F6/8 D6/8 Bb5/8 D6/8 F6/8",
    "A6/16 Ab6/16 G6/16 F6/16 D6/8 F6/8 A6/4 C#7/4",
    "D7/8 A6/8 F6/8 D6/8 A5/8 D6/8 F6/8 A6/8",
    "C7/8 G6/8 E6/8 C6/8 G5/8 C6/8 E6/8 G6/8",
    "Bb6/8 F6/8 D6/8 Bb5/8 F5/8 Bb5/8 D6/8 F6/8",
    "A6/16 G6/16 F6/16 E6/16 D6/16 C#6/16 D6/16 E6/16 F6/8 A6/8 D7/4",
    # 177-184  full cry
    "D7/2 C7/4 A6/4", "Bb6/2 A6/2", "G6/4 F6/4 E6/2",
    "D6/16 E6/16 F6/16 G6/16 A6/16 Bb6/16 C7/16 D7/16 A6/4 F6/4",
    "D7/8 D7/8 C7/8 Bb6/8 A6/4 A6/4",
    "G6/8 F6/8 G6/8 A6/8 Bb6/8 C7/8 D7/8 C7/8",
    "Bb6/4 A6/4 G6/2",
    "A6/16 Bb6/16 C7/16 D7/16 E7/8 F7/8 A7/2",
])

# ---------------------------------------------------------------------------
# IV. QUODLIBET + CODA  mm. 185-216
# ---------------------------------------------------------------------------
# Q1 runs unchanged in bass and keys.  Q3 ("Your Best Friend") sits on top in
# D minor in long values.  The counter carries Q4's b7->6 slur, C->B, which in
# D Dorian is exactly the same interval it was in E Dorian.  Three fights, one bar.
CH_IV = (["Dm", "C", "Bb", "A5"] * 4                             # 185-200 quodlibet
         + ["Dm", "C", "Bb", "A5", "Gm", "C", "Dm", "A5"]        # 201-208 climax
         + ["Bb", "C", "Dm", "Dm", "Bb", "A5", "Dm", "Dm"])      # 209-216 coda

# Q3 in D minor:  D E F | D | E | E F E | D  ||  F G A | D | Bb | A
LEAD_IV = [
    "D6/8 E6/8 F6/4 D6/2",
    "E6/4 E6/8 F6/8 E6/4 D6/4",
    "F6/8 G6/8 A6/4 D6/2",
    "Bb6/4 A6/2 R/8 A5/8",
    "D6/8 E6/8 F6/4 D6/2",
    "E6/4 E6/8 F6/8 E6/4 D6/4",
    "F6/8 G6/8 A6/4 Bb6/4 A6/4",
    "D6/1",
    # 193-200  the same, doubled in octaves and ornamented, fff
    "D6/16 E6/16 F6/16 A6/16 D7/8 A6/8 F6/4 D6/4",
    "E6/16 F6/16 E6/16 D6/16 E6/8 G6/8 E6/4 C6/4",
    "F6/16 G6/16 A6/16 C7/16 D7/8 C7/8 A6/4 F6/4",
    "Bb6/16 A6/16 G6/16 F6/16 E6/8 D6/8 A6/4 D7/4",
    "D7/8 A6/8 F7/8 D7/8 C7/8 A6/8 E7/8 C7/8",
    "Bb6/8 F6/8 D7/8 Bb6/8 A6/8 F6/8 C7/8 A6/8",
    "G6/16 A6/16 Bb6/16 C7/16 D7/8 C7/8 Bb6/4 A6/4",
    "D7/2 A6/4 F6/4",
    # 201-208  climax -- Q2 and Q3 alternate bar by bar
    "A6/8 A6/8 G6/8 F6/8 E6/4 E6/4",
    "D6/8 C6/8 D6/8 E6/8 F6/8 G6/8 A6/8 C7/8",
    "D7/4 C7/4 Bb6/2",
    "A6/16 G6/16 F6/16 E6/16 D6/8 F6/8 A6/4 D7/4",
    "G6/8 Bb6/8 D7/8 G7/8 F7/4 D7/4",
    "C7/8 E7/8 G7/8 C7/8 Bb6/4 G6/4",
    "D7/8 F7/8 A7/8 D7/8 C7/4 A6/4",
    "A6/16 B6/16 C#7/16 D7/16 E7/8 F7/8 A7/2",
    # 209-216  coda -- the motto, then the riff one last time
    "Bb6/2 A6/2",
    "C7/2 A6/2",
    "D7/1~",
    "D7/2 A6/4 Bb6/4",
    "A6/8 Ab6/8 G6/8 F6/8 D6/4 F6/4",
    "A6/16 Ab6/16 G6/16 F6/16 E6/16 D6/16 C#6/16 D6/16 A6/2",
    "D5/16 F5/16 A5/16 D6/16 F6/16 A6/16 D7/16 F7/16 A7/2",
    "D5+A5+D6+A6+D7/1",
]
