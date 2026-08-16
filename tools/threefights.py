"""
THREE FIGHTS -- a variation suite after three Toby Fox battle themes.

  I.   FLOWER   (after "Finale")            mm.   1– 64   F minor    q=95
       bridge A -- the shared diminished 7th  mm.  65– 72
  II.  GLAMOUR  (after "Death by Glamour")  mm.  73–128   B min/E Dor q=148
       bridge B -- chromatic bass descent    mm. 129–136
  III. BAD TIME (after "MEGALOVANIA")       mm. 137–200   D minor    q=126

Original writing that develops each source's harmonic frame, bass shape and
rhythmic signature. No source melody is transcribed.

THE MOTTO that welds the suite together is three notes -- b6, 5, 1:
    F minor  Db - C  - F
    B minor  G  - F# - B
    D minor  Bb - A  - D
It opens the piece, marks both bridges, and closes the coda.

TRANSITIONS
  A: F minor's vii°7 is E°7 = {E, G, Bb, Db}.  Respelled that is
     {E, G, A#, C#} = A#°7, which is B minor's vii°7.  One chord, two homes.
     Sit on it, resolve it the other way.
  B: the E Dorian vamp's bass simply walks E -> Eb -> D.
"""

from fractions import Fraction as F
from zerosum import bar_len, dur_of
from zerosum2 import shift, oct_down, to_midi, from_midi, rests

TITLE = "THREE FIGHTS"

# ---------------------------------------------------------------------------
# DYNAMICS ENGINE  --  the main fix from the last piece.
# ---------------------------------------------------------------------------
# Two rules, both enforced mechanically further down:
#   1. Accompaniment never sits at or above the melody.  Stabs and pads run
#      TWO steps under the lead; bass, keys and drums run one step under.
#   2. Almost nothing changes level without a hairpin getting it there.
#      A bare dynamic change is allowed only where the drop is the point.
LEVELS = ["ppp", "pp", "p", "mp", "mf", "f", "ff", "fff"]
LVL = {d: i for i, d in enumerate(LEVELS)}

# offset from the LEAD's level, per part
OFFSET = {"LEAD": 0, "COUNTER": -1, "SUSTAIN": -2, "STABS": -2,
          "KEYS": -1, "BASS": -1, "DRUMS": -1}

# (measure, lead dynamic) -- everything else is derived from this spine
LEAD_DYN = [
    (1, "f"), (5, "ff"), (9, "ff"), (17, "f"), (25, "mf"), (33, "f"),
    (41, "ff"), (49, "ff"), (57, "f"), (61, "ff"),
    (65, "mf"), (69, "p"),                       # bridge A drains away
    (73, "mp"), (77, "mf"), (81, "f"), (89, "f"), (97, "mf"), (105, "f"),
    (113, "ff"), (121, "ff"),
    (129, "f"), (133, "mf"),                     # bridge B
    (137, "mf"), (141, "f"), (145, "ff"), (153, "ff"), (161, "f"),
    (169, "ff"), (177, "ff"), (185, "fff"), (193, "fff"),
]

# (start, end, "<" or ">") -- hairpins on the LEAD; parts inherit them
LEAD_HAIRPINS = [
    (1, 4, "<"), (13, 16, "<"), (21, 24, ">"), (29, 32, "<"), (37, 40, "<"),
    (45, 48, "<"), (53, 56, ">"), (57, 60, "<"), (61, 64, "<"),
    (65, 68, ">"), (69, 72, "<"),
    (77, 80, "<"), (85, 88, "<"), (93, 96, ">"), (101, 104, "<"),
    (109, 112, "<"), (117, 120, "<"), (125, 128, "<"),
    (129, 132, ">"), (133, 136, "<"),
    (141, 144, "<"), (149, 152, "<"), (157, 160, ">"), (165, 168, "<"),
    (173, 176, "<"), (181, 184, "<"), (189, 192, "<"), (197, 200, "<"),
]

# a handful of deliberate exceptions, where a bare level change IS the gesture
SUBITO = {69, 73, 137}


def dyn_for(part, measure):
    lead = None
    for m, d in LEAD_DYN:
        if m <= measure:
            lead = d
        else:
            break
    lvl = max(0, min(len(LEVELS) - 1, LVL[lead] + OFFSET[part]))
    return LEVELS[lvl]


def dyn_changes(part):
    """Measures where this part's dynamic actually changes."""
    out, prev = [], None
    for m, _ in LEAD_DYN:
        d = dyn_for(part, m)
        if d != prev:
            out.append((m, d))
            prev = d
    return out


# ---------------------------------------------------------------------------
# DRUMS -- far more involved than last time.  Fills every four bars, real tom
# work, ride/hat changes, and a kit that tracks each movement's genre.
# ---------------------------------------------------------------------------
DRUM_LIB = {
    "tacet":   "R/1",
    # -- I. FLOWER: brass-orchestral over breakcore.  Fast snare against a
    #    half-time backbeat, plus timpani-weight kick on the phrase heads.
    "fin_a":   "KC/8 H/8 S/16 S/16 H/8 K/8 S/8 H/16 K/16 S/8",
    "fin_b":   "K/8 H/16 K/16 S/8 H/8 K/8 S/16 S/16 S/8 H/8",
    "fin_c":   "KC/16 K/16 H/8 S/8 H/8 K/16 H/16 S/8 S/16 S/16 H/8",
    "fin_fill": "S/16 S/16 T/16 T/16 T/16 T/16 F/16 F/16 S/8 T/8 F/8 KC/8",
    "fin_half": "K/4 S/4 K/8 K/8 S/4",
    # -- II. GLAMOUR: disco.  Four-on-the-floor, clap on 2 and 4,
    #    open hat on every offbeat -- the classic strut.
    "dbg_a":   "KH/8 O/8 KS/8 O/8 KH/8 O/8 KS/8 O/8",
    "dbg_b":   "KH/8 O/8 KS/8 O/16 H/16 KH/8 O/8 KS/16 K/16 O/8",
    "dbg_ride": "KR/8 R/8 SR/8 R/8 KR/8 R/8 SR/8 R/8",
    "dbg_fill": "S/16 S/16 S/16 T/16 T/8 F/8 S/16 T/16 F/16 S/16 KC/8 O/8",
    "dbg_thin": "KH/8 H/8 SH/8 H/8 KH/8 H/8 SH/8 H/8",
    # -- III. BAD TIME: the kick lands on the ostinato's own anticipation
    #    sixteenths instead of fighting them; snare stays square on 2 and 4.
    "meg_a":   "K/8 H/8 SH/16 K/16 H/8 K/16 H/16 H/8 SK/8 H/8",
    "meg_b":   "K/8 H/8 SH/8 K/16 K/16 H/8 K/16 H/16 SK/8 O/8",
    "meg_c":   "KC/8 H/8 SH/16 K/16 H/8 K/8 H/8 SK/16 K/16 O/8",
    "meg_fill": "S/16 S/16 S/16 S/16 T/16 T/16 T/16 T/16 F/16 F/16 S/16 S/16 KC/8 S/8",
    "meg_big": "KC/8 S/8 K/8 S/8 K/8 S/8 K/16 K/16 SC/8",
    "roll":    "Z/2 Z/2",
    "crash":   "KC/1",
    "final":   "KCZ/1",
}


def drums2(name):
    return DRUM_LIB[name]


def drum_line(base, fill, n, start_crash=None):
    """n bars of `base`, with `fill` on every 4th bar."""
    out = []
    for i in range(n):
        if (i + 1) % 4 == 0:
            out.append(fill)
        elif i == 0 and start_crash:
            out.append(start_crash)
        else:
            out.append(base)
    return out


# ---------------------------------------------------------------------------
# I.  FLOWER            mm. 1-64        F minor (4b)      q = 95
# ---------------------------------------------------------------------------
CH_I = (["Fm", "Fm", "Db", "Eb", "Fm", "Fm", "C7", "C7"]        # intro
        + ["Fm", "Db", "Eb", "Fm", "Fm", "Db", "Eb", "C7"]      # A1
        + ["Fm", "Db", "Eb", "Fm", "Db", "Eb", "Fm", "Fm"]      # A2
        + ["Db", "Eb", "Fm", "Cm", "Db", "Eb", "Ab", "Ab"]      # B1
        + ["Db", "Eb", "Fm", "Cm", "Db", "Eb", "C7", "C7"]      # B2
        + ["Fm", "Db", "Eb", "Fm", "Fm", "Db", "Eb", "Fm"]      # A3
        + ["Db", "Eb", "Fm", "Cm", "Db", "Eb", "Fm", "Fm"]      # A4
        + ["Fm", "Fm", "Db", "Db", "Eb", "Eb", "C7", "C7"])     # build

LEAD_I2 = [
    # mm.1-8  THE MOTTO, stated bare and grand: Db - C - F
    "R/2 Db5/4 C5/4", "F5/1~", "F5/2 Db5/4 C5/4", "F5/2 C5/4 Db5/4",
    "C5/2 F5/4 Ab5/4", "C6/1~", "C6/2 Bb5/4 Ab5/4", "G5/2 R/4 C5/8 Db5/8",
    # mm.9-16  A1 -- the theme
    "F5/4 Ab5/8 C6/8 Db6/4 C6/4",
    "Ab5/2 F5/4 Ab5/4",
    "G5/4 Bb5/8 Eb6/8 Db6/4 Bb5/4",
    "C6/2 Ab5/2",
    "F5/4 Ab5/8 C6/8 Db6/4 C6/4",
    "Ab5/2 Db6/4 C6/4",
    "Bb5/4 C6/8 Db6/8 Eb6/4 F6/4",
    "E5/2 C6/2",
    # mm.17-24  A2 -- answered an octave down, then climbing back
    "F5/8 G5/8 Ab5/8 Bb5/8 C6/4 Ab5/4",
    "Db6/4 C6/8 Bb5/8 Ab5/4 F5/4",
    "Eb5/8 F5/8 G5/8 Ab5/8 Bb5/4 G5/4",
    "F5/2 C6/4 Ab5/4",
    "Db6/4 C6/4 Bb5/4 Ab5/4",
    "Eb6/4 Db6/4 C6/4 Bb5/4",
    "Ab5/8 C6/8 F6/4 Eb6/8 Db6/8 C6/4",
    "F6/2 C6/4 Ab5/4",
    # mm.25-32  B -- the lyrical strain, thinner, mf
    "Ab5/2 F5/4 Db5/4",
    "Eb5/2 G5/4 Bb5/4",
    "Ab5/4 C6/4 F5/2",
    "G5/2 Eb5/4 G5/4",
    "Ab5/4 Bb5/8 C6/8 Db6/2",
    "Eb6/4 Db6/8 C6/8 Bb5/4 G5/4",
    "Ab5/4 C6/4 Eb6/4 Ab6/4",
    "G6/2 Eb6/4 C6/4",
    # mm.33-40  B2 -- the same, escalating
    "Db6/2 Ab5/4 F5/4",
    "Eb6/2 Bb5/4 G5/4",
    "C6/4 F6/4 Ab6/2",
    "G6/4 Eb6/8 C6/8 G5/4 Bb5/4",
    "Db6/8 Eb6/8 F6/4 Ab6/4 F6/4",
    "Eb6/8 Db6/8 C6/4 Bb5/4 Ab5/4",
    "G5/8 Ab5/8 Bb5/8 C6/8 Db6/8 Eb6/8 F6/8 G6/8",
    "Ab6/2 G6/4 F6/4",
    # mm.41-48  A3 -- theme returns, top octave, ff
    "F6/4 Ab6/8 C7/8 Db7/4 C7/4",
    "Ab6/2 F6/4 Ab6/4",
    "G6/4 Bb6/8 Eb7/8 Db7/4 Bb6/4",
    "C7/2 Ab6/2",
    "F6/4 Ab6/8 C7/8 Db7/4 C7/4",
    "Ab6/2 Db7/4 C7/4",
    "Bb6/4 C7/8 Db7/8 Eb7/4 F7/4",
    "E6/2 C7/2",
    # mm.49-56  A4
    "Db7/4 C7/4 Bb6/4 Ab6/4",
    "Eb7/4 Db7/4 C7/4 Bb6/4",
    "Ab6/8 C7/8 F7/4 Eb7/8 Db7/8 C7/4",
    "G6/2 C7/4 Eb7/4",
    "Db7/4 Ab6/4 F6/4 Db6/4",
    "Eb7/4 Bb6/4 G6/4 Eb6/4",
    "F6/8 G6/8 Ab6/8 Bb6/8 C7/4 Ab6/4",
    "F6/2 R/4 C6/8 Db6/8",
    # mm.57-64  build into bridge A
    "C6/4 Db6/4 C6/4 F6/4",
    "C6/4 Db6/4 C6/4 F6/4",
    "Db6/2 Ab6/2",
    "Db6/4 F6/4 Ab6/4 Db7/4",
    "Eb6/2 Bb6/2",
    "Eb6/4 G6/4 Bb6/4 Eb7/4",
    "E6/8 G6/8 Bb6/8 Db7/8 E7/4 Db7/4",
    "Bb6/8 G6/8 E6/8 Db6/8 Bb5/4 R/4",
]

# ---------------------------------------------------------------------------
# BRIDGE A              mm. 65-72       the shared diminished seventh
# ---------------------------------------------------------------------------
# E°7 = {E, G, Bb, Db}.  Respelled: {E, G, A#, C#} = A#°7.
# It is vii°7 of F minor AND vii°7 of B minor.  We arrive expecting F and
# leave in B.  The motto crosses the seam: Db-C-F becomes G-F#-B.
CH_BR_A = ["Edim7", "Edim7", "Edim7", "Edim7",
           "A#dim7", "A#dim7", "F#7", "F#7"]

LEAD_BR_A = [
    "Db6/2 C6/2",                       # the motto, F-minor spelling
    "E6/4 G6/4 Bb6/4 Db7/4",
    "Bb6/4 G6/4 E6/4 Db6/4",
    "E6/1~",
    "E6/2 G6/4 A#6/4",                  # same pitches, respelled
    "C#7/4 A#6/4 G6/4 E6/4",
    "G5/2 F#5/2",                       # the motto again, B-minor spelling
    "R/2 F#5/8 G5/8 F#5/8 E5/8",
]

# ---------------------------------------------------------------------------
# II. GLAMOUR           mm. 73-128      B minor / E Dorian (2#)   q = 148
# ---------------------------------------------------------------------------
# The groove parks on iv (Em7) and treats it as E DORIAN -- b3 with a natural
# 6th.  The C# is the whole sound; without it this is generic minor.
CH_II2 = (["Em7", "Em7", "Em7", "Em7", "Em7", "Em7", "A", "A"]        # bass alone -> layers
          + ["Em7", "Em7", "A", "A", "Em7", "Em7", "F#7", "F#7"]      # A1
          + ["Em7", "Em7", "A", "A", "G", "G", "F#7", "F#7"]          # A2
          + ["Em7", "Em7", "A", "A", "C", "C", "B7", "B7"]            # B1
          + ["Em7", "Em7", "A", "A", "G", "F#7", "Em7", "Em7"]        # B2
          + ["Em7", "Em7", "A", "A", "G", "G", "F#7", "B7"]           # A3
          + ["Em7", "Em7", "A", "A", "C", "B7", "Em7", "Em7"])        # A4

LEAD_II2 = (rests(8)                    # bass and kit own the first eight bars
            + [
    # mm.81-88  A1 -- the strut.  Sax-ish lead, lazy behind the beat.
    "R/8 B4/8 D5/8 E5/8 G5/4 E5/4",
    "D5/8 E5/8 D5/8 B4/8 A4/4 R/4",
    "R/8 C#5/8 E5/8 F#5/8 A5/4 F#5/4",
    "E5/8 F#5/8 E5/8 C#5/8 B4/4 R/4",
    "R/8 B4/8 D5/8 E5/8 G5/8 A5/8 B5/4",
    "A5/8 G5/8 E5/8 D5/8 B4/4 D5/4",
    "F#5/8 A5/8 C#6/8 A5/8 F#5/4 E5/4",
    "D#5/8 F#5/8 A5/8 C#6/8 F#6/4 R/4",
    # mm.89-96  A2
    "R/8 E5/8 G5/8 B5/8 D6/4 B5/4",
    "A5/8 B5/8 A5/8 G5/8 E5/4 R/4",
    "R/8 E5/8 A5/8 C#6/8 E6/4 C#6/4",
    "B5/8 C#6/8 B5/8 A5/8 F#5/4 R/4",
    "G5/8 B5/8 D6/8 G6/8 F#6/4 D6/4",
    "B5/8 D6/8 G6/8 D6/8 B5/4 G5/4",
    "F#5/8 A#5/8 C#6/8 E6/8 F#6/8 E6/8 C#6/8 A#5/8",
    "F#5/4 C#6/4 F#6/2",
    # mm.97-104  B1 -- drops back to mf, the bass takes the foreground
    "R/1",
    "R/2 B4/8 D5/8 E5/8 F#5/8",
    "G5/4 E5/8 D5/8 B4/2",
    "R/2 D5/8 E5/8 F#5/8 A5/8",
    "C6/4 A5/8 G5/8 E5/2",
    "R/2 G5/8 A5/8 B5/8 C6/8",
    "D#6/4 B5/8 F#5/8 D#5/4 F#5/4",
    "B5/8 A5/8 F#5/8 D#5/8 B4/4 R/4",
    # mm.105-112  B2 -- lead climbs back over the busy bass
    "E5/16 G5/16 B5/16 E6/16 D6/8 B5/8 G5/4 E5/4",
    "D5/16 E5/16 G5/16 B5/16 A5/8 G5/8 E5/4 D5/4",
    "C#5/16 E5/16 A5/16 C#6/16 B5/8 A5/8 F#5/4 E5/4",
    "C#5/8 E5/8 A5/8 C#6/8 E6/4 C#6/4",
    "G5/16 B5/16 D6/16 G6/16 F#6/8 D6/8 B5/4 G5/4",
    "A#5/16 C#6/16 F#6/16 A#6/16 F#6/8 C#6/8 A#5/4 F#5/4",
    "E5/8 G5/8 B5/8 D6/8 E6/8 D6/8 B5/8 G5/8",
    "E5/4 B4/4 E5/2",
    # mm.113-120  A3 -- full, ff
    "B5/8 D6/8 E6/8 G6/8 B6/4 G6/4",
    "F#6/8 E6/8 D6/8 B5/8 A5/4 B5/4",
    "C#6/8 E6/8 A6/8 C#7/8 B6/4 A6/4",
    "G#6/8 F#6/8 E6/8 C#6/8 B5/4 C#6/4",
    "D6/8 G6/8 B6/8 D7/8 B6/4 G6/4",
    "D6/8 B5/8 G5/8 D5/8 B4/4 D5/4",
    "A#5/8 C#6/8 F#6/8 A#6/8 C#7/4 A#6/4",
    "F#6/8 E6/8 C#6/8 A#5/8 F#5/4 R/4",
    # mm.121-128  A4 -- into bridge B
    "E5/8 G5/8 B5/8 E6/8 G6/4 E6/4",
    "D6/8 B5/8 G5/8 E5/8 B4/4 D5/4",
    "E5/8 A5/8 C#6/8 E6/8 A6/4 F#6/4",
    "E6/8 C#6/8 A5/8 F#5/8 E5/4 R/4",
    "C6/8 E6/8 G6/8 C7/8 B6/4 G6/4",
    "F#6/8 D#6/8 B5/8 F#5/8 D#5/4 F#5/4",
    "G5/2 F#5/2",                       # the motto, B minor
    "B5/1",
])

# ---------------------------------------------------------------------------
# BRIDGE B              mm. 129-136     the bass walks E -> Eb -> D
# ---------------------------------------------------------------------------
CH_BR_B = ["Em7", "Em7", "Ebdim7", "Ebdim7", "Dm", "Dm", "A5", "A5"]

LEAD_BR_B = [
    "B5/8 A5/8 G5/8 F#5/8 E5/4 B4/4",
    "E5/8 G5/8 B5/8 E6/8 D6/4 B5/4",
    "Eb6/8 Db6/8 B5/8 A5/8 Gb5/4 Eb5/4",
    "Eb5/8 Gb5/8 A5/8 C6/8 Eb6/4 C6/4",
    "Bb5/2 A5/2",                       # the motto, D minor
    "D5/1~",
    "D5/2 R/4 A4/8 Bb4/8",
    "A4/8 Ab4/8 G4/8 F4/8 D4/4 R/4",   # the descent that opens movement III
]

# ---------------------------------------------------------------------------
# III. BAD TIME         mm. 137-200     D minor (1b)      q = 126
# ---------------------------------------------------------------------------
# i - bVII - bVI - v, all minor, descending lament tetrachord.
CH_III2 = (["Dm", "C", "Bb", "Am"] * 2                              # riff builds
           + ["Dm", "C", "Bb", "Am"] * 2                            # A1
           + ["Dm", "C", "Bb", "Am"] * 2                            # A2
           + ["Gm", "F", "Eb", "Dm", "Bb", "C", "Dm", "Am"]         # B
           + ["Dm", "C", "Bb", "Am"] * 2                            # A3
           + ["Dm", "C", "Bb", "Am", "Bb", "C", "Dm", "Dm"]         # converge
           + ["Bb", "Am", "Dm", "Dm", "Bb", "Am", "Dm", "Dm"]       # the motto
           + ["Bb", "C", "Dm", "Dm", "Bb", "A5", "Dm", "Dm"])       # coda

LEAD_III2 = (rests(8)                   # ostinato alone, then + bass
             + [
    # mm.145-152  A1
    "D5/16 F5/16 A5/16 D6/16 C6/8. A5/8 F5/8 D5/8 E5/16 F5/16 G5/16",
    "C5/16 E5/16 G5/16 C6/16 Bb5/8. A5/8 G5/8 E5/8 D5/16 C5/16 D5/16",
    "Bb4/16 D5/16 F5/16 Bb5/16 A5/8. G5/8 F5/8 D5/8 C5/16 Bb4/16 C5/16",
    "A4/16 C5/16 E5/16 A5/16 G5/8. F5/8 E5/8 C5/8 A4/16 B4/16 C5/16",
    "D5/16 F5/16 A5/16 D6/16 E6/8. D6/8 C6/8 A5/8 F5/16 E5/16 F5/16",
    "C5/16 E5/16 G5/16 C6/16 D6/8. C6/8 Bb5/8 G5/8 E5/16 D5/16 E5/16",
    "Bb4/16 D5/16 F5/16 Bb5/16 C6/8. Bb5/8 A5/8 F5/8 D5/16 C5/16 D5/16",
    "A4/16 E5/16 A5/16 C6/16 Bb5/8 A5/8 G5/8 F5/8 E5/8 D5/8",
    # mm.153-160  A2 -- the Megalovania gesture: 5 - b5 - 4 descending
    "D5/8 D5/8 D6/8 A5/8. Ab5/8 G5/8 F5/16 D5/16 F5/16",
    "C5/8 C5/8 C6/8 G5/8. Gb5/8 F5/8 E5/16 C5/16 E5/16",
    "Bb4/8 Bb4/8 Bb5/8 F5/8. E5/8 Eb5/8 D5/16 Bb4/16 D5/16",
    "A4/8 A4/8 A5/8 E5/8. Eb5/8 D5/8 C5/16 A4/16 C5/16",
    "D5/8 F5/8 A5/8 D6/8 F6/8 D6/8 A5/8 F5/8",
    "C5/8 E5/8 G5/8 C6/8 E6/8 C6/8 G5/8 E5/8",
    "Bb4/8 D5/8 F5/8 Bb5/8 D6/8 Bb5/8 F5/8 D5/8",
    "A4/16 C5/16 E5/16 A5/16 C6/16 E6/16 C6/16 A5/16 E5/8 C5/8 A4/4",
    # mm.161-168  B -- the iv region
    "G4/16 Bb4/16 D5/16 G5/16 Bb5/8. A5/8 G5/8 F5/8 D5/16 C5/16 D5/16",
    "F4/16 A4/16 C5/16 F5/16 A5/8. G5/8 F5/8 E5/8 C5/16 Bb4/16 C5/16",
    "Eb5/16 G5/16 Bb5/16 Eb6/16 D6/8. C6/8 Bb5/8 G5/8 Eb5/16 F5/16 G5/16",
    "D5/16 F5/16 A5/16 D6/16 C6/8. Bb5/8 A5/8 F5/8 D5/16 E5/16 F5/16",
    "Bb4/8 D5/8 F5/8 Bb5/8 A5/8 F5/8 D5/8 F5/8",
    "C5/8 E5/8 G5/8 C6/8 Bb5/8 G5/8 E5/8 G5/8",
    "D5/8 F5/8 A5/8 D6/8 C6/8 A5/8 F5/8 D5/8",
    "A4/16 B4/16 C5/16 D5/16 E5/16 F5/16 G5/16 Ab5/16 A5/8 G5/8 F5/8 E5/8",
    # mm.169-176  A3
    "D5/16 F5/16 A5/16 D6/16 C6/8. A5/8 F5/8 D5/8 E5/16 F5/16 G5/16",
    "C5/16 E5/16 G5/16 C6/16 Bb5/8. A5/8 G5/8 E5/8 D5/16 C5/16 D5/16",
    "Bb4/16 D5/16 F5/16 Bb5/16 A5/8. G5/8 F5/8 D5/8 C5/16 Bb4/16 C5/16",
    "A4/16 C5/16 E5/16 A5/16 G5/8. F5/8 E5/8 C5/8 A4/16 B4/16 C5/16",
    "D6/16 F6/16 A6/16 D7/16 C7/8. A6/8 F6/8 D6/8 E6/16 F6/16 G6/16",
    "C6/16 E6/16 G6/16 C7/16 Bb6/8. A6/8 G6/8 E6/8 D6/16 C6/16 D6/16",
    "Bb5/16 D6/16 F6/16 Bb6/16 A6/8. G6/8 F6/8 D6/8 C6/16 Bb5/16 C6/16",
    "A5/16 C6/16 E6/16 A6/16 G6/8 F6/8 E6/8 C6/8 A5/8 G5/8",
    # mm.177-184  CONVERGENCE -- all three movements' shapes at once.
    # Movement I's theme, in D minor, over Megalovania's ostinato.
    "D6/4 F6/8 A6/8 Bb6/4 A6/4",
    "F6/2 D6/4 F6/4",
    "E6/4 G6/8 C7/8 Bb6/4 G6/4",
    "A6/2 F6/2",
    # Movement II's Dorian b7-6 slur, in D
    "C6/8 B5/8 C6/8 D6/8 F6/8 D6/8 C6/8 B5/8",
    "C6/8 D6/8 F6/8 A6/8 C7/8 A6/8 F6/8 D6/8",
    "Bb6/4 A6/4 G6/4 F6/4",
    "E6/8 F6/8 G6/8 A6/8 Bb6/8 C7/8 D7/8 E7/8",
    # mm.185-192  the motto, fff, in octaves
    "Bb6/2 A6/2", "D7/1~", "D7/2 Bb6/4 A6/4", "D7/2 A6/4 Bb6/4",
    "A6/2 D6/4 F6/4", "A6/1~", "A6/2 G6/4 F6/4", "E6/8 F6/8 G6/8 A6/8 Bb6/4 C7/4",
    # mm.193-200  coda
    "D7/16 C7/16 Bb6/16 A6/16 G6/16 F6/16 E6/16 D6/16 C6/8 D6/8 E6/8 F6/8",
    "G6/16 A6/16 Bb6/16 C7/16 D7/16 E7/16 F7/16 G7/16 A7/4 F7/4",
    "Bb6/2 A6/2",
    "D7/1~",
    "D7/2 A6/4 Bb6/4",
    "A6/8 Ab6/8 G6/8 F6/8 E6/4 D6/4",
    "D5/16 F5/16 A5/16 D6/16 F6/16 A6/16 D7/16 F7/16 A7/2",
    "D5+A5+D6+A6+D7/1",
])
