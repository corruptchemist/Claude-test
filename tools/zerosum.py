"""
ZERO-SUM  --  an original boss theme.  150 measures.

This module holds the complete score as data and verifies it.
Nothing here is generated at random; every bar is written out and checked.

TOKEN FORMAT
------------
    <pitch><octave>/<dur>     E5/8   Ab2/16   F#6/2
    R/<dur>                   rest
    a+b+c/<dur>               chord (D4+F4+A4/2)
    trailing ~                tie into the next note
    dur:  1 whole  2 half  4 quarter  8 eighth  16 sixteenth  32  64
          '.' dots the value            (8. = dotted eighth = 0.75)
          'T' prefix = triplet          (T8 = triplet eighth = 1/3)

Every bar must total exactly the meter's beat count.  verify() asserts it.
"""

from fractions import Fraction as F

TITLE = "ZERO-SUM"
SUBTITLE = "Boss Theme"

# ---------------------------------------------------------------------------
# THE ARGUMENT
# ---------------------------------------------------------------------------
# One pitch runs the whole piece: Ab / G#, the tritone above D.
#
#   In the intro it is the note that poisons the bass groove.
#   In the boss theme it is the blue b5 -- the Megalovania blue note.
#   In the F-major "Payoff" section it VANISHES completely (F major has no Ab).
#   In the collapse it comes back and breaks the key.
#   In the last four bars it is respelled G# and becomes the #11 of D major --
#   the brightest note in the final chord.
#
# Same pitch, four meanings.  The piece is the process of earning that respelling.
#
# THE CELL is built as A+B so the halves can be deployed separately:
#
#   alpha  (menace)  D - F  - Ab - A  ||  A - G - F - E - D     0,3,6,7  then falls
#   beta   (hope)    F - A  - C  - D  ||  D - C - Bb - A - G    0,4,7,9  then falls
#   omega  (blaze)   D - F# - G# - A  ||  A - B - C# - D        0,4,6,7  then RISES
#
# omega differs from alpha by exactly ONE note -- the third -- and by the
# direction of its tail.  The Ab never moves; it is reinterpreted.
#
# Withheld until m.143 (so the arrival is earned, per Schoenberg/Bartok practice):
#   * any D major triad          * F# over a D root
#   * the top octave (D6+)       * full tutti
#   * omega's rising tail

DUR = {"1": F(4), "2": F(2), "4": F(1), "8": F(1, 2),
       "16": F(1, 4), "32": F(1, 8), "64": F(1, 16)}


def dur_of(code):
    triplet = code.startswith("T")
    if triplet:
        code = code[1:]
    dots = 0
    while code.endswith("."):
        dots += 1
        code = code[:-1]
    v = DUR[code]
    add = v
    for _ in range(dots):
        add /= 2
        v += add
    if triplet:
        v = v * F(2, 3)
    return v


def bar_len(bar):
    total = F(0)
    for tok in bar.split():
        tok = tok.rstrip("~")
        total += dur_of(tok.split("/")[1])
    return total


def pitches_in(bar):
    out = []
    for tok in bar.split():
        head = tok.rstrip("~").split("/")[0]
        if head == "R":
            continue
        out.extend(head.split("+"))
    return out


# ---------------------------------------------------------------------------
# GENERATORS
# ---------------------------------------------------------------------------

# The fast ostinato.  16 sixteenths partitioned 6+6+4 -- the Spear of Justice
# tresillo, written at the dotted-eighth level.  Accents fall on sixteenth
# 0, 6 and 12, i.e. dotted-quarter / dotted-quarter / quarter.  Beat 3 is never
# struck: the note on 2& sustains straight through it.
#
# The seven pitches are alpha (D-F-Ab-A) welded to the Death by Glamour
# tail (C-B, the slurred b7->6).  Both source DNAs live in one bar.
OSTINATO_RHYTHM = ["8.", "8.", "8.", "8.", "8", "16", "16"]

OSTINATO_PITCHES = {
    # Only the first TWO attacks change across the 4-bar unit; attacks 3-7 are
    # literally identical every bar.  That is the Megalovania device.
    "Dm":  ["D2",  "D3",  "F2", "Ab2", "A2", "C3", "B2"],
    "C":   ["C2",  "C3",  "F2", "Ab2", "A2", "C3", "B2"],
    "Bb":  ["Bb1", "Bb2", "F2", "Ab2", "A2", "C3", "B2"],
    "Am":  ["A1",  "A2",  "F2", "Ab2", "A2", "C3", "B2"],
    # iv-region and other roots keep the shape, adapt the tail
    "Gm":  ["G1",  "G2",  "Bb2", "Db3", "D3", "F3", "E3"],
    "F":   ["F1",  "F2",  "A2",  "C3",  "C3", "E3", "D3"],
    "Eb":  ["Eb2", "Eb3", "G2",  "Bb2", "Bb2", "D3", "C3"],
    "A5":  ["A1",  "A2",  "E2",  "G2",  "A2", "C3", "B2"],
    # Phrygian bII
    "EbP": ["Eb2", "Eb3", "G2",  "Bb2", "B2", "Db3", "C3"],
    # the pivot into F major -- note there is no Ab here.  The signature
    # dissonance evaporates one bar before the Payoff section begins.
    "C7":  ["C2",  "C3",  "E2",  "G2",  "Bb2", "A2", "G2"],
}


def ostinato(chord):
    ps = OSTINATO_PITCHES[chord]
    return " ".join(f"{p}/{d}" for p, d in zip(ps, OSTINATO_RHYTHM))


# Offbeat stabs: close position C4-C5, staccatissimo, on every '&'.
STAB_VOICING = {
    "Dm":   "D4+F4+A4",     "C":    "C4+E4+G4",     "Bb":  "Bb3+D4+F4",
    "Am":   "A3+C4+E4",     "Gm":   "G3+Bb3+D4",    "F":   "F3+A3+C4",
    "Eb":   "Eb4+G4+Bb4",   "A5":   "A3+E4+A4",     "EbP": "Eb4+G4+Bb4",
    "Gm7":  "Bb3+D4+F4",    "F/A":  "A3+C4+F4",     "Bbma7": "Bb3+D4+A4",
    "Csus4": "C4+F4+G4",    "C7":   "C4+E4+Bb4",
    "Abm7": "Cb4+Eb4+Gb4",  "Gb/Bb": "Bb3+Db4+Gb4", "Cbma7": "Cb4+Eb4+Bb4",
    "Dbsus4": "Db4+Gb4+Ab4", "Db7":  "Db4+F4+Cb5",
    "D":    "D4+F#4+A4",    "A7":   "A3+C#4+G4",    "Gma7": "G3+B3+F#4",
}


def stabs(chord, pattern="offbeat"):
    """Chord stabs.  'offbeat' = on every &; 'four' = on every quarter."""
    v = STAB_VOICING[chord]
    if pattern == "offbeat":
        return " ".join(f"R/8 {v}/8" for _ in range(4))
    if pattern == "four":
        return " ".join(f"{v}/8 R/8" for _ in range(4))
    if pattern == "drive":       # 1& 2 2& 3 3& 4& -- beat 4 omitted, so it lurches
        return f"R/8 {v}/8 {v}/8 {v}/8 {v}/8 {v}/8 R/8 {v}/8"
    if pattern == "hold":
        return f"{v}/1"
    if pattern == "half":
        return f"{v}/2 {v}/2"
    raise ValueError(pattern)


# Drum kit.  Notated on a percussion staff.
# K kick  S snare  H closed hat  O open hat  C crash  R ride  T tom  Z 32nd roll
def drums(pattern):
    P = {
        # -- slow 6/4 intro --
        "tacet6":  "R/1 R/2",
        "kick6":   "K/4 R/4 R/4 K/4 R/4 R/4",
        "build6":  "KC/4 H/4 H/4 K/4 H/4 H/8 H/8",
        "roll6":   "K/4 H/4 H/4 K/4 Z/4 Z/4",
        "stop6":   "KC/4 R/4 R/4 R/4 R/4 R/4",
        "cut6":    "Z/4 Z/4 Z/4 Z/4 Z/4 CX/4",
        # -- fast 4/4 --
        "tacet":   "R/1",
        "kickonly": "K/4 R/4 K/4 R/4",
        # kick locked to the ostinato's own accents (1, 2&, 4); snare square on 2 and 4
        "drive":   "K/8 H/8 SH/8 K/8 H/8 H/8 SK/8 H/8",
        "driveO":  "KC/8 H/8 SH/8 K/8 H/8 H/8 SK/8 O/8",
        "half":    "K/4 R/4 S/4 R/4",
        # chorus lift: four-on-the-floor + snare on ALL FOUR offbeats (no downbeats)
        "lift":    "K/8 S/8 K/8 S/8 K/8 S/8 K/8 S/8",
        "liftC":   "KC/8 S/8 K/8 S/8 K/8 S/8 K/8 S/8",
        "fill":    "S/16 S/16 S/16 S/16 T/16 T/16 T/16 T/16 S/8 S/8 Z/4",
        "roll":    "Z/2 Z/2",
        "stop":    "C/4 R/4 R/4 R/4",
        "blaze":   "KC/8 S/8 K/8 S/8 K/8 S/8 KC/4",
        "final":   "KCZ/1",
    }
    return P[pattern]


# ---------------------------------------------------------------------------
# SECTION I  --  "OPENING BID"   mm. 1-16   6/4   quarter = 92
# ---------------------------------------------------------------------------
# Pitch field: D half-whole octatonic  =  D  Eb  F  F#  Ab  A  B  C
# That single collection contains alpha (D-F-Ab-A), the Death by Glamour bass
# cell (D-F-C-B), the b9 appoggiatura (Eb), and the Picardy seed (F#).
# Nothing in the intro leaves it.
#
# 6/4 is deliberate: six slow beats deny the ear a downbeat grid, so the 4/4
# at m.17 arrives like a floor appearing.

# The heavy bassline.  Death by Glamour's cell -- root, b3, b7, 6 with the
# b7->6 slurred -- transplanted to D and slowed to a menace.  Staccato with
# real rests: the weight is in the attack and the hole after it.
BASS_I = [
    # m.1-2  bass completely alone
    "D1/8 D2/8 R/16 D2/16 F2/8 R/8 C3/8 B2/4 R/8 D2/8 F2/8 Ab2/8",
    "D1/8 D2/8 R/16 D2/16 F2/8 R/8 C3/8 B2/8 Bb2/8 A2/4 Ab2/8 G2/8",
    # m.3-4  kick and tam join
    "D1/8 D2/8 R/16 D2/16 F2/8 R/8 C3/8 B2/4 R/8 D2/8 F2/8 Ab2/8",
    "D1/8 D2/8 R/16 D2/16 F2/8 R/8 C3/8 B2/8 Bb2/8 A2/4 Ab2/8 G2/8",
    # m.5-8  pedal layer arrives above; bass gets a shade busier
    "D1/8 D2/8 R/16 D2/16 F2/8 R/16 F2/16 C3/8 B2/4 R/8 D2/8 F2/8 Ab2/8",
    "D1/8 D2/8 R/16 D2/16 F2/8 R/16 F2/16 C3/8 B2/8 Bb2/8 A2/4 Ab2/8 G2/8",
    "D1/8 D2/8 R/16 D2/16 F2/8 R/16 F2/16 C3/8 B2/4 R/8 D2/8 F2/8 Ab2/8",
    "D1/8 D2/8 R/16 D2/16 F2/8 Ab2/16 F2/16 C3/8 B2/8 Bb2/8 A2/4 Ab2/8 G2/8",
    # m.9-12  under alpha's augmented statement
    "D1/8 D2/8 R/16 D2/16 F2/8 R/8 C3/8 B2/4 R/8 D2/8 F2/8 Ab2/8",
    "D1/8 D2/8 R/16 D2/16 F2/8 R/8 C3/8 B2/8 Bb2/8 A2/4 Ab2/8 G2/8",
    "D1/8 D2/8 R/16 D2/16 F2/8 R/8 C3/8 B2/4 R/8 D2/8 F2/8 Ab2/8",
    "D1/8 D2/8 R/16 D2/16 F2/8 Ab2/16 F2/16 C3/8 B2/8 Bb2/8 A2/4 Ab2/8 G2/8",
    # m.13-14  the crisis; bass abandons the groove for octave pounding
    "D1/8 D1/8 D1/8 D1/8 D1/8 D1/8 D1/8 D1/8 D1/8 D1/8 D1/8 D1/8",
    "D1/2 Ab1/2 D1/2",
    # m.15  chromatic climb into the modulation
    "D1/8 Eb1/8 F1/8 F#1/8 G1/8 Ab1/8 A1/8 Bb1/8 B1/8 C2/8 Db2/8 D2/8",
    # m.16  everything cuts to the bare tritone, then silence
    "D1+Ab1/1 R/2",
]

LEAD_I = [
    "R/1 R/2", "R/1 R/2", "R/1 R/2", "R/1 R/2",
    "R/1 R/2", "R/1 R/2", "R/1 R/2", "R/1 R/2",
    # m.9-12  ALPHA, in augmentation.  First hearing of the cell: slow, high,
    # unaccompanied by any harmony that would explain it.
    "D5/2. F5/2.",
    "Ab5/1~ Ab5/2",          # the tritone, held a whole bar, fp with cresc.
    "A5/2. G5/2.",
    "F5/2 E5/2 D5/2",
    # m.13-14  the cell fragments and the register tears open
    "D5/4 F5/4 Ab5/4 A5/4 Ab5/4 F5/4",
    "D6+Ab5/2. R/2 Ab5/8 A5/8",   # Petrushka impact: D over Ab
    # m.15  rising chromatic sweep, doubling the bass two octaves up
    "D4/8 Eb4/8 F4/8 F#4/8 G4/8 Ab4/8 A4/8 Bb4/8 B4/8 C5/8 Db5/8 D5/8",
    "Ab5/1 R/2",
]

COUNTER_I = [
    "R/1 R/2", "R/1 R/2", "R/1 R/2", "R/1 R/2",
    # m.5-8  the minor-9th pedal: D below, Eb a NINTH above (never a 2nd)
    "Eb4/1 R/2", "Eb4/1~ Eb4/2", "Eb4/1 R/2", "Eb4/1~ Eb4/2",
    # m.9-12  a slow chromatic counter-descent under alpha
    "B4/2. Bb4/2.", "A4/2. Ab4/2.", "G4/2. F#4/2.", "F4/2 E4/2 Eb4/2",
    # m.13-16
    "F4/4 F#4/4 G4/4 Ab4/4 A4/4 Bb4/4",
    "Ab4+C5+Eb5/2. R/2 R/4",           # upper triad of the polychord
    "F#4/8 G4/8 Ab4/8 A4/8 Bb4/8 B4/8 C5/8 Db5/8 D5/8 Eb5/8 E5/8 F5/8",
    "D4+Ab4/1 R/2",
]

WINDS_I = [
    "R/1 R/2", "R/1 R/2",
    # m.3-4  the tritone enters, pp, sul ponticello tremolo in the strings
    "D4+Ab4/1 R/2", "D4+Ab4/1~ D4+Ab4/2",
    # m.5-8  half-diminished "Herrmann" colour over the pedal: D-F-Ab-C
    "D4+F4+Ab4/1 R/2", "D4+F4+Ab4+C5/1~ D4+F4+Ab4+C5/2",
    "D4+F4+Ab4/1 R/2", "D4+F4+Ab4+C5/1~ D4+F4+Ab4+C5/2",
    # m.9-12  the field thickens toward full octatonic
    "D4+F4+Ab4+C5/2. Eb4+F#4+A4+C5/2.",
    "D4+F4+Ab4+B4/2. Eb4+F#4+A4+C5/2.",
    "D4+F4+Ab4+C5/2. D4+F4+A4+B4/2.",
    "Eb4+F#4+A4+C5/1~ Eb4+F#4+A4+C5/2",
    # m.13-16
    "D4+F4+Ab4+B4/1~ D4+F4+Ab4+B4/2",
    "Ab4+C5+Eb5/2. R/2.",
    "R/2 D4+F4+Ab4+B4/1",
    "D4+Ab4/1 R/2",
]

STABS_I = [
    "R/1 R/2", "R/1 R/2", "R/1 R/2", "R/1 R/2",
    "R/1 R/2", "R/1 R/2",
    # m.7-8  first stabs -- on beats 2, 4, 6 only.  Sparse, brutal.
    "R/4 D4+F4+Ab4/4 R/4 D4+F4+Ab4/4 R/4 D4+F4+Ab4/4",
    "R/4 D4+F4+Ab4/4 R/4 D4+F4+Ab4/4 R/4 Eb4+G4+Bb4/4",
    "R/4 D4+F4+Ab4/4 R/4 D4+F4+Ab4/4 R/4 D4+F4+Ab4/4",
    "R/4 D4+F4+Ab4/4 R/4 D4+F4+Ab4/4 R/4 Eb4+G4+Bb4/4",
    "R/4 D4+F4+Ab4/4 R/4 D4+F4+Ab4/4 R/4 D4+F4+Ab4/4",
    "R/4 D4+F4+B4/4 R/4 D4+F4+B4/4 R/4 Eb4+F#4+A4/4",
    "D4+F4+Ab4/4 D4+F4+Ab4/4 D4+F4+Ab4/4 D4+F4+Ab4/4 D4+F4+Ab4/4 D4+F4+Ab4/4",
    "Ab4+C5+Eb5/2. R/2.",
    "R/1 R/2",
    "R/1 R/2",
]

KEYS_I = [
    "R/1 R/2", "R/1 R/2", "R/1 R/2", "R/1 R/2",
    "R/1 R/2", "R/1 R/2", "R/1 R/2", "R/1 R/2",
    # m.9-12  octatonic arpeggio filigree, pp, under the augmented cell
    "D4/8 F4/8 Ab4/8 B4/8 D5/8 B4/8 Ab4/8 F4/8 D4/8 F4/8 Ab4/8 B4/8",
    "Eb4/8 F#4/8 A4/8 C5/8 Eb5/8 C5/8 A4/8 F#4/8 Eb4/8 F#4/8 A4/8 C5/8",
    "D4/8 F4/8 Ab4/8 B4/8 D5/8 B4/8 Ab4/8 F4/8 D4/8 F4/8 Ab4/8 B4/8",
    "Eb4/16 F#4/16 A4/16 C5/16 Eb5/16 F#5/16 A5/16 C6/16 Eb6/16 C6/16 A5/16 F#5/16 "
    "Eb5/16 C5/16 A4/16 F#4/16 Eb4/16 F#4/16 A4/16 C5/16 Eb5/16 C5/16 A4/16 F#4/16",
    # m.13-16
    "D4/16 F4/16 Ab4/16 B4/16 D5/16 F5/16 Ab5/16 B5/16 D6/16 B5/16 Ab5/16 F5/16 "
    "D5/16 B4/16 Ab4/16 F4/16 D4/16 F4/16 Ab4/16 B4/16 D5/16 F5/16 Ab5/16 B5/16",
    "Ab4+C5+Eb5/2. R/2.",
    "D4/8 Eb4/8 F4/8 F#4/8 G4/8 Ab4/8 A4/8 Bb4/8 B4/8 C5/8 Db5/8 D5/8",
    "R/1 R/2",
]

DRUMS_I = [
    "tacet6", "tacet6", "kick6", "kick6",
    "kick6", "kick6", "build6", "build6",
    "build6", "build6", "build6", "build6",
    "roll6", "stop6", "roll6", "cut6",
]
