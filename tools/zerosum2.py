"""ZERO-SUM -- sections II through VII (mm. 17-150), plus score assembly."""

from fractions import Fraction as F
from zerosum import (bar_len, ostinato, stabs, drums, pitches_in,
                     BASS_I, LEAD_I, COUNTER_I, WINDS_I, STABS_I, KEYS_I, DRUMS_I)

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
FLATSPELL = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
SHARPSPELL = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def to_midi(p):
    letter, i = p[0], 1
    acc = 0
    while i < len(p) and p[i] in "#b":
        acc += 1 if p[i] == "#" else -1
        i += 1
    return (int(p[i:]) + 1) * 12 + STEP[letter] + acc


def from_midi(m, sharp=False):
    tbl = SHARPSPELL if sharp else FLATSPELL
    return f"{tbl[m % 12]}{m // 12 - 1}"


def shift(bar, semitones, sharp=False):
    """Transpose a bar. Used for octave doublings and the semitone lift."""
    out = []
    for tok in bar.split():
        tie = "~" if tok.endswith("~") else ""
        head, dur = tok.rstrip("~").split("/")
        if head == "R":
            out.append(f"R/{dur}{tie}")
            continue
        ps = [from_midi(to_midi(p) + semitones, sharp) for p in head.split("+")]
        out.append(f"{'+'.join(ps)}/{dur}{tie}")
    return " ".join(out)


def oct_down(bar, n=1):
    return shift(bar, -12 * n)


def rests(n, meter=4):
    return ["R/1" if meter == 4 else "R/1 R/2"] * n


# H&D-style continuous sixteenth bed: one bar of 16ths, up and back down.
HD_ARP = {
    "Gm7":    ["G4", "Bb4", "D5", "F5", "G5", "F5", "D5", "Bb4"],
    "F/A":    ["A3", "C5", "F5", "A5", "C6", "A5", "F5", "C5"],
    "Bbma7":  ["Bb3", "D5", "F5", "A5", "Bb5", "A5", "F5", "D5"],
    "Csus4":  ["C4", "F4", "G4", "C5", "F5", "C5", "G4", "F4"],
    "C7":     ["C4", "E4", "G4", "Bb4", "C5", "Bb4", "G4", "E4"],
    "Abm7":   ["Ab4", "Cb5", "Eb5", "Gb5", "Ab5", "Gb5", "Eb5", "Cb5"],
    "Gb/Bb":  ["Bb3", "Db5", "Gb5", "Bb5", "Db6", "Bb5", "Gb5", "Db5"],
    "Cbma7":  ["Cb4", "Eb5", "Gb5", "Bb5", "Cb6", "Bb5", "Gb5", "Eb5"],
    "Dbsus4": ["Db4", "Gb4", "Ab4", "Db5", "Gb5", "Db5", "Ab4", "Gb4"],
    "Db7":    ["Db4", "F4", "Ab4", "Cb5", "Db5", "Cb5", "Ab4", "F4"],
}


def arp16(chord):
    ps = HD_ARP[chord]
    return " ".join(f"{p}/16" for p in ps * 2)


# ===========================================================================
# SECTION II -- "THE TELL"   mm. 17-24   4/4   quarter = 184
# ===========================================================================
# METRIC MODULATION, not an accelerando: the intro's EIGHTH becomes this
# section's QUARTER.  92 -> 184 exactly.  The listener's existing subdivision
# is promoted to the beat, so the new tempo arrives as inevitable, not as an edit.
#
# Then the Fox "ostinato introduction paradigm", strictly: riff alone for four
# bars, layers added four at a time, melody forbidden until the section ends.
CH_II = ["Dm", "C", "Bb", "Am"] * 2

BASS_II = [ostinato(c) for c in CH_II]

LEAD_II = rests(7) + [
    # m.24 -- three octaves of D half-whole octatonic, accelerating 32nds into
    # 64ths, launching the boss theme.  The intro's pitch field fires the gun.
    "R/2 R/4 D4/64 Eb4/64 F4/64 F#4/64 Ab4/64 A4/64 B4/64 C5/64 "
    "D5/64 Eb5/64 F5/64 F#5/64 Ab5/64 A5/64 B5/64 C6/64",
]

COUNTER_II = rests(4) + [shift(ostinato(c), 12) for c in CH_II[4:]]
WINDS_II = rests(6) + ["D4+A4/1", "D4+A4/1"]
STABS_II = rests(4) + [stabs(c, "offbeat") for c in CH_II[4:]]
KEYS_II = (rests(4) + [shift(ostinato(c), 24) for c in CH_II[4:7]]
           + ["R/2 D2/32 Eb2/32 F2/32 F#2/32 Ab2/32 A2/32 B2/32 C3/32 "
              "D3/64 Eb3/64 F3/64 F#3/64 Ab3/64 A3/64 B3/64 C4/64 "
              "D4/64 Eb4/64 F4/64 F#4/64 Ab4/64 A4/64 B4/64 C5/64"])
DRUMS_II = ["tacet", "tacet", "kickonly", "kickonly", "drive", "drive", "drive", "fill"]

# ===========================================================================
# SECTION III -- A "OPENING MOVE"   mm. 25-56   (32 bars)   D minor
# ===========================================================================
# i - bVII - bVI - v, all minor, descending lament tetrachord: Dm - C - Bb - Am.
# The v is MINOR.  No C# anywhere -- the leading tone is being saved for m.143.
CH_III = (["Dm", "C", "Bb", "Am"] * 4
          + ["Gm", "F", "Eb", "Dm"]
          + ["Bb", "C", "Dm", "Am"]
          + ["Dm", "C", "Bb", "Am"] * 2)

# alpha, at speed.  Bar shape 4+3+2+2+2+3 sixteenths: the dotted eighth at
# position 4 shoves the following stream off-grid, so beats 3 and 4 are never
# struck, and the three closing sixteenths re-sync the downbeat.
_A25 = "D5/16 F5/16 Ab5/16 A5/16 A5/8. G5/8 F5/8 E5/8 D5/16 C5/16 D5/16"
_A26 = "C5/16 E5/16 G5/16 A5/16 Ab5/8. G5/8 F5/8 E5/8 D5/16 C5/16 D5/16"
_A27 = "Bb4/16 D5/16 F5/16 A5/16 Ab5/8. G5/8 F5/8 D5/8 Bb4/16 C5/16 D5/16"
_A28 = "A4/16 C5/16 E5/16 A5/16 Ab5/8. G5/8 F5/8 E5/8 D5/16 E5/16 F5/16"

LEAD_III = [
    # a1 -- the cell, plainly
    _A25, _A26, _A27, _A28,
    # a2 -- same head, the answer climbs instead of settling
    "D5/16 F5/16 Ab5/16 A5/16 A5/8. C6/8 Bb5/8 A5/8 G5/16 F5/16 E5/16",
    "C5/16 E5/16 G5/16 Bb5/16 C6/8. Bb5/8 A5/8 G5/8 E5/16 F5/16 G5/16",
    "Bb4/16 D5/16 F5/16 Bb5/16 C6/8. Bb5/8 A5/8 F5/8 D5/16 E5/16 F5/16",
    "A4/16 C5/16 E5/16 A5/16 Ab5/8. G5/8 F5/8 E5/8 D5/16 C5/16 D5/16",
    # a3 -- FRAGMENTATION: the head alone, doubled, then the tail
    "D5/16 F5/16 Ab5/16 A5/16 D5/16 F5/16 Ab5/16 A5/16 Bb5/8 A5/8 F5/8 D5/8",
    "C5/16 E5/16 G5/16 Ab5/16 C5/16 E5/16 G5/16 Ab5/16 Bb5/8 Ab5/8 G5/8 E5/8",
    "Bb4/16 D5/16 F5/16 Ab5/16 Bb4/16 D5/16 F5/16 Ab5/16 G5/8 F5/8 D5/8 Bb4/8",
    "A4/16 C5/16 E5/16 G5/16 A4/16 C5/16 E5/16 G5/16 Ab5/8 G5/8 E5/8 C5/8",
    # a4 -- wide-leap version, straight eighths
    "D5/8 A5/8 C6/8 A5/8 F5/8 Ab5/8 A5/8 D5/8",
    "C5/8 G5/8 C6/8 G5/8 E5/8 Ab5/8 G5/8 C5/8",
    "Bb4/8 F5/8 Bb5/8 F5/8 D5/8 Ab5/8 F5/8 D5/8",
    "A4/16 B4/16 C5/16 D5/16 E5/16 F5/16 G5/16 Ab5/16 A5/8 G5/8 F5/8 E5/8",
    # a5 -- the iv excursion.  alpha transposes: G-Bb-Db-D keeps the tritone.
    "G4/16 Bb4/16 Db5/16 D5/16 D5/8. C5/8 Bb4/8 A4/8 G4/16 F4/16 G4/16",
    "F4/16 A4/16 C5/16 D5/16 C5/8. Bb4/8 A4/8 G4/8 F4/16 G4/16 A4/16",
    "Eb5/16 G5/16 Bb5/16 C6/16 Bb5/8. Ab5/8 G5/8 F5/8 Eb5/16 F5/16 G5/16",
    _A25,
    # a6 -- arpeggiated ascent
    "Bb4/8 D5/8 F5/8 Bb5/8 A5/8 F5/8 D5/8 F5/8",
    "C5/8 E5/8 G5/8 C6/8 Bb5/8 G5/8 E5/8 G5/8",
    "D5/8 F5/8 A5/8 C6/8 Ab5/8 A5/8 F5/8 D5/8",
    "A4/16 C5/16 E5/16 G5/16 Ab5/16 A5/16 C6/16 A5/16 G5/8 E5/8 C5/8 A4/8",
    # a7 -- restatement, full texture
    _A25, _A26, _A27, _A28,
    # a8 -- turnaround; the chromatic climb hands over to section B
    _A25,
    "C5/16 E5/16 G5/16 Ab5/16 A5/8. G5/8 F5/8 E5/8 D5/16 C5/16 Bb4/16",
    "Bb4/16 C5/16 D5/16 E5/16 F5/16 G5/16 Ab5/16 A5/16 Bb5/8 A5/8 G5/8 F5/8",
    "E5/8 F5/8 G5/8 Ab5/8 A5/8 Bb5/8 B5/8 C6/8",
]

COUNTER_III = (
    rests(8)                                        # hold it back 8 bars
    + ["D4/2 F4/2", "E4/2 G4/2", "D4/2 F4/2", "C4/2 E4/2",
       "A4/2 F4/2", "G4/2 E4/2", "F4/2 D4/2", "E4/2 C4/2"]
    + ["G4/4 Bb4/4 D5/4 Bb4/4", "F4/4 A4/4 C5/4 A4/4",
       "Eb4/4 G4/4 Bb4/4 G4/4", "D4/4 F4/4 A4/4 F4/4",
       "Bb3/4 D4/4 F4/4 D4/4", "C4/4 E4/4 G4/4 E4/4",
       "D4/4 F4/4 A4/4 F4/4", "A3/4 C4/4 E4/4 G4/4"]
    + [oct_down(b) for b in LEAD_III[24:32]]        # octave doubling, tutti
)

WINDS_III = (rests(16)
             + ["G3+Bb3+D4/1", "F3+A3+C4/1", "Eb3+G3+Bb3/1", "D3+F3+A3/1",
                "Bb3+D4+F4/1", "C4+E4+G4/1", "D4+F4+A4/1", "A3+C4+E4/1"]
             + ["D4+F4+A4/1", "C4+E4+G4/1", "Bb3+D4+F4/1", "A3+C4+E4/1"] * 2)

STABS_III = ([stabs(c, "offbeat") for c in CH_III[:16]]
             + [stabs(c, "drive") for c in CH_III[16:24]]
             + [stabs(c, "offbeat") for c in CH_III[24:]])

KEYS_III = [shift(ostinato(c), 12) for c in CH_III]

BASS_III = [ostinato(c) for c in CH_III]

DRUMS_III = (["driveO"] + ["drive"] * 7
             + ["driveO"] + ["drive"] * 6 + ["fill"]
             + ["driveO"] + ["drive"] * 7
             + ["driveO"] + ["drive"] * 6 + ["fill"])

# ===========================================================================
# SECTION IV -- B "DEFECT"   mm. 57-80   (24 bars)
# ===========================================================================
# m.57 is the 0.382 point of 150 bars -- the false peak.  Mode darkens from
# Aeolian to PHRYGIAN: the bass oscillates D - Eb, a bare semitone, the bII
# against the tonic.  This is the Jaws device applied to a whole section.
CH_IV = (["Dm", "EbP", "Dm", "EbP"]
         + ["Dm", "EbP", "Gm", "A5"]
         + ["Dm", "EbP", "Dm", "EbP"]
         + ["Bb", "C", "Dm", "Dm"]
         + ["Gm", "EbP", "Dm", "EbP"]
         + ["Bb", "C", "Dm", "C7"])

LEAD_IV = [
    "A4/16 D5/16 A4/16 D5/16 A4/16 D5/16 A4/16 D5/16 F5/8 E5/8 D5/4",
    "Bb4/16 Eb5/16 Bb4/16 Eb5/16 Bb4/16 Eb5/16 Bb4/16 Eb5/16 G5/8 F5/8 Eb5/4",
    "A4/16 D5/16 A4/16 D5/16 A4/16 D5/16 A4/16 D5/16 F5/8 G5/8 A5/4",
    # eight consecutive chromatic sixteenths, Bb5 down to Eb5
    "Bb5/16 A5/16 Ab5/16 G5/16 Gb5/16 F5/16 E5/16 Eb5/16 D5/8 Eb5/8 D5/8 C5/8",
    "D5/16 F5/16 Ab5/16 A5/16 D5/16 F5/16 Ab5/16 A5/16 Bb5/8 A5/8 F5/8 D5/8",
    "Eb5/16 G5/16 Bb5/16 B5/16 Eb5/16 G5/16 Bb5/16 B5/16 C6/8 Bb5/8 G5/8 Eb5/8",
    "G4/16 Bb4/16 D5/16 G5/16 Bb5/8 A5/8 G5/8 D5/8 Bb4/8 G4/8",
    "A4/16 C5/16 E5/16 G5/16 A5/16 C6/16 A5/16 G5/16 E5/8 C5/8 A4/8 E4/8",
    # b2 -- same four bars, register lifted
    "A5/16 D6/16 A5/16 D6/16 A5/16 D6/16 A5/16 D6/16 F5/8 E5/8 D5/4",
    "Bb5/16 Eb6/16 Bb5/16 Eb6/16 Bb5/16 Eb6/16 Bb5/16 Eb6/16 G5/8 F5/8 Eb5/4",
    "A4/16 D5/16 A4/16 D5/16 A4/16 D5/16 A4/16 D5/16 F5/8 G5/8 A5/4",
    "Bb5/16 A5/16 Ab5/16 G5/16 Gb5/16 F5/16 E5/16 Eb5/16 D5/8 Eb5/8 D5/8 C5/8",
    # b3 -- the build: bVI - bVII - i
    "Bb4/8 D5/8 F5/8 Bb5/8 D6/8 Bb5/8 F5/8 D5/8",
    "C5/8 E5/8 G5/8 C6/8 E6/8 C6/8 G5/8 E5/8",
    "D5/16 F5/16 Ab5/16 A5/16 D5/16 F5/16 Ab5/16 A5/16 D6/8 A5/8 F5/8 D5/8",
    "A5/16 Ab5/16 G5/16 F5/16 E5/16 D5/16 C5/16 Bb4/16 A4/8 D5/8 F5/8 A5/8",
    # b4
    "G4/16 Bb4/16 D5/16 G5/16 Bb5/16 D6/16 Bb5/16 G5/16 D5/8 Bb4/8 G4/8 D4/8",
    "Eb5/16 G5/16 Bb5/16 Eb6/16 D6/16 C6/16 Bb5/16 G5/16 Eb5/8 F5/8 G5/8 Bb5/8",
    "D5/16 F5/16 Ab5/16 A5/16 A5/8. G5/8 F5/8 E5/8 D5/16 C5/16 D5/16",
    "Eb5/8 D5/8 C5/8 Bb4/8 Ab4/8 G4/8 F4/8 Eb4/8",
    # b5 -- the last chromatic push, then Ab EVAPORATES on the C7
    "Bb4/16 D5/16 F5/16 Bb5/16 A5/8 F5/8 D5/8 F5/8 Bb5/8 D6/8",
    "C5/16 E5/16 G5/16 C6/16 Bb5/8 G5/8 E5/8 G5/8 C6/8 E6/8",
    "D5/16 F5/16 Ab5/16 A5/16 D6/16 Ab5/16 F5/16 D5/16 A4/8 D5/8 F5/8 A5/8",
    # no Ab, no Eb: the octatonic world is gone and F major is standing there
    "C5/16 E5/16 G5/16 Bb5/16 C6/8 Bb5/8 A5/8 G5/8 F5/8 E5/8",
]

COUNTER_IV = ([oct_down(b) for b in LEAD_IV[:8]]
              + rests(4)
              + [oct_down(b) for b in LEAD_IV[12:20]]
              + [oct_down(b) for b in LEAD_IV[20:]])

WINDS_IV = (["D4+A4/1", "Eb4+Bb4/1"] * 2
            + ["D4+A4/1", "Eb4+Bb4/1", "G3+D4/1", "A3+E4/1"]
            + ["D4+A4/1", "Eb4+Bb4/1"] * 2
            + ["Bb3+F4/1", "C4+G4/1", "D4+A4/1", "D4+A4/1"]
            + ["G3+D4/1", "Eb4+Bb4/1", "D4+A4/1", "Eb4+Bb4/1"]
            + ["Bb3+F4/1", "C4+G4/1", "D4+A4/1", "C4+G4+Bb4/1"])

STABS_IV = [stabs(c, "drive") for c in CH_IV]
KEYS_IV = [shift(ostinato(c), 12) for c in CH_IV]
BASS_IV = [ostinato(c) for c in CH_IV]
DRUMS_IV = (["driveO"] + ["drive"] * 7
            + ["driveO"] + ["drive"] * 6 + ["fill"]
            + ["liftC"] + ["lift"] * 6 + ["fill"])

# ===========================================================================
# SECTION V -- C "THE PAYOFF MATRIX"   mm. 81-112   (32 bars)   F MAJOR
# ===========================================================================
# The Hopes and Dreams engine, rebuilt from its principles rather than copied:
#   * ii7 - I6 - IV - V, ONE CHORD PER TWO BARS
#   * bass ASCENDS G - A - Bb - C
#   * the tonic F NEVER appears in root position, so the loop always climbs
#   * melody in HALF NOTES, high, range inside a sixth, over a 16th-note bed
#   * lead is SUSTAINED STRINGS, not a pulse lead (this is H&D's real timbre)
#   * STRICTLY DIATONIC -- zero accidentals.  Ab does not exist here.
#
# mm. 81-92 have NO BASS AT ALL: nothing sounds below F3 for twelve bars.
# m. 93 is the golden section of 150 bars (150 x 0.618 = 92.7) and is the
# drop -- bass enters on the IV chord, register opens above C6, full kit.
HD_LOOP = ["Gm7", "Gm7", "F/A", "F/A", "Bbma7", "Bbma7", "Csus4", "C7"]
GB_LOOP = ["Abm7", "Abm7", "Gb/Bb", "Gb/Bb", "Cbma7", "Cbma7", "Dbsus4", "Db7"]
CH_V = HD_LOOP * 2 + HD_LOOP + GB_LOOP

# beta: F - A - C - D  ||  D - C - Bb - A - G.  Same contour as alpha, but the
# tritone is replaced by a major sixth and the mode is major.
LEAD_V = [
    # mm.81-88  bassless, mp, ceiling C6
    "F5/2 A5/2", "C6/2 A5/2", "Bb5/2 C6/2", "A5/1",
    "G5/2 Bb5/2", "A5/2 C6/2", "Bb5/2 A5/2", "G5/1",
    # mm.89-92  still bassless, cresc.
    "F5/2 A5/2", "C6/2 A5/2", "Bb5/2 C6/2", "A5/2 G5/2",
    # m.93 THE DROP -- octave leap, register opens
    "F6/1", "D6/2 F6/2", "E6/2 D6/2", "C6/1",
    # mm.97-104  same loop; alpha returns underneath in the counter
    "D6/2 F6/2", "G6/1", "F6/2 E6/2", "C6/1",
    "D6/2 F6/2", "Bb6/1", "A6/2 G6/2", "F6/2 E6/2",
    # mm.105-112  truck-driver lift: everything up a semitone, no pivot chord
    "Eb6/2 Gb6/2", "Ab6/1", "Gb6/2 F6/2", "Db6/1",
    "Eb6/2 Gb6/2", "Bb6/1", "Ab6/2 Gb6/2", "F6/2 Eb6/2",
]

# The second theme: alpha, made diatonic, dropped onto UNCHANGED harmony --
# faint at m.89 (buried, mp), full at m.97 (f).  Fox's exact device.
COUNTER_V = (
    rests(8)
    + ["F4/2 A4/2", "C5/2 A4/2", "Bb4/2 C5/2", "A4/2 G4/2"]
    + ["Bb4/2 D5/2", "F5/2 D5/2", "C5/2 E5/2", "G4/1"]
    # alpha, diatonicised (F-A-C-D instead of D-F-Ab-A), in full voice
    + ["F4/16 A4/16 C5/16 D5/16 D5/8. C5/8 Bb4/8 A4/8 G4/16 F4/16 G4/16",
       "G4/16 Bb4/16 D5/16 G5/16 F5/8. E5/8 D5/8 C5/8 Bb4/16 A4/16 Bb4/16",
       "A4/16 C5/16 F5/16 A5/16 G5/8. F5/8 E5/8 D5/8 C5/16 Bb4/16 C5/16",
       "F4/16 A4/16 C5/16 F5/16 E5/8. D5/8 C5/8 Bb4/8 A4/16 G4/16 A4/16",
       "Bb4/16 D5/16 F5/16 Bb5/16 A5/8. G5/8 F5/8 E5/8 D5/16 C5/16 D5/16",
       "D5/16 F5/16 Bb5/16 D6/16 C6/8. Bb5/8 A5/8 G5/8 F5/16 E5/16 F5/16",
       "C5/16 E5/16 G5/16 C6/16 Bb5/8. A5/8 G5/8 F5/8 E5/16 D5/16 E5/16",
       "C5/16 E5/16 G5/16 Bb5/16 A5/8. G5/8 F5/8 E5/8 D5/16 C5/16 D5/16"]
    + [shift(b, 1) for b in
       ["F4/16 A4/16 C5/16 D5/16 D5/8. C5/8 Bb4/8 A4/8 G4/16 F4/16 G4/16",
        "G4/16 Bb4/16 D5/16 G5/16 F5/8. E5/8 D5/8 C5/8 Bb4/16 A4/16 Bb4/16",
        "A4/16 C5/16 F5/16 A5/16 G5/8. F5/8 E5/8 D5/8 C5/16 Bb4/16 C5/16",
        "F4/16 A4/16 C5/16 F5/16 E5/8. D5/8 C5/8 Bb4/8 A4/16 G4/16 A4/16",
        "Bb4/16 D5/16 F5/16 Bb5/16 A5/8. G5/8 F5/8 E5/8 D5/16 C5/16 D5/16",
        "D5/16 F5/16 Bb5/16 D6/16 C6/8. Bb5/8 A5/8 G5/8 F5/16 E5/16 F5/16",
        "C5/16 E5/16 G5/16 C6/16 Bb5/8. A5/8 G5/8 F5/8 E5/16 D5/16 E5/16",
        "C5/16 E5/16 G5/16 Bb5/16 A5/8. G5/8 F5/8 E5/8 D5/16 C5/16 D5/16"]]
)

# high sustained strings -- the actual Hopes and Dreams lead timbre
WINDS_V = (["D5+G5/1", "D5+G5/1", "C5+F5/1", "C5+F5/1",
            "D5+F5/1", "D5+F5/1", "C5+F5/1", "C5+E5/1"] * 2
           + ["D5+G5/1", "D5+G5/1", "C5+F5/1", "C5+F5/1",
              "D5+F5/1", "D5+F5/1", "C5+F5/1", "C5+E5/1"]
           + [shift(b, 1) for b in
              ["D5+G5/1", "D5+G5/1", "C5+F5/1", "C5+F5/1",
               "D5+F5/1", "D5+F5/1", "C5+F5/1", "C5+E5/1"]])

STABS_V = (rests(8)
           + [stabs(c, "offbeat") for c in CH_V[8:]])

KEYS_V = [arp16(c) for c in CH_V]

# THE BASS HOLE.  Twelve bars of nothing, then continuous straight eighths
# alternating root and octave -- and it lands on IV, never on the tonic.
def _hd_bass(root):
    lo, hi = root
    return f"{lo}/8 {hi}/8 {lo}/8 {hi}/8 {lo}/8 {hi}/8 {lo}/8 {hi}/8"


HD_ROOTS = {"Gm7": ("G2", "G3"), "F/A": ("A2", "A3"), "Bbma7": ("Bb1", "Bb2"),
            "Csus4": ("C2", "C3"), "C7": ("C2", "C3"),
            "Abm7": ("Ab2", "Ab3"), "Gb/Bb": ("Bb2", "Bb3"),
            "Cbma7": ("Cb2", "Cb3"), "Dbsus4": ("Db2", "Db3"), "Db7": ("Db2", "Db3")}

BASS_V = (rests(12)
          + [_hd_bass(HD_ROOTS[c]) for c in CH_V[12:23]]
          # walk-up into the semitone lift
          + ["C2/8 D2/8 Eb2/8 F2/8 G2/8 A2/8 Bb2/8 B2/8"]
          + [_hd_bass(HD_ROOTS[c]) for c in CH_V[24:]])

DRUMS_V = (["tacet"] * 4 + ["half"] * 4
           + ["half", "half", "half", "roll"]
           + ["liftC"] + ["lift"] * 3
           + ["liftC"] + ["lift"] * 6 + ["fill"]
           + ["liftC"] + ["lift"] * 6 + ["fill"])

# ===========================================================================
# SECTION VI -- D "MIXED STRATEGY"   mm. 113-130   (18 bars)
# ===========================================================================
# The Gb world shatters.  First the Cave Story / Gaster device Fox names
# outright: hold the upper structure and walk the bass down chromatically.
# Then the octatonic collection returns and the harmony lurches by minor
# thirds -- D, F, Ab, B -- without ever leaving the pitch set.
CH_VI = ["Db7", "Db7", "Db7", "Db7",
         "Ddim", "Fdim", "Abdim", "Bdim",
         "Ddim", "Fdim", "Abdim", "Bdim",
         "WT", "WT", "WT", "WT",
         "STOP", "STOP"]

LEAD_VI = [
    # mm.113-116  the upper structure holds while the floor drops away
    "Db6+F6/1~", "Db6+F6/2 C6+E6/2", "B5+Eb6/1~", "B5+Eb6/2 Bb5+D6/2",
    # mm.117-124  octatonic arpeggios, minor-third cycle, spiralling up
    "D5/16 F5/16 Ab5/16 B5/16 D6/16 B5/16 Ab5/16 F5/16 D5/8 F5/8 Ab5/8 B5/8",
    "F5/16 Ab5/16 B5/16 D6/16 F6/16 D6/16 B5/16 Ab5/16 F5/8 Ab5/8 B5/8 D6/8",
    "Ab5/16 B5/16 D6/16 F6/16 Ab6/16 F6/16 D6/16 B5/16 Ab5/8 B5/8 D6/8 F6/8",
    "B5/16 D6/16 F6/16 Ab6/16 B6/16 Ab6/16 F6/16 D6/16 B5/8 D6/8 F6/8 Ab6/8",
    "D5/32 Eb5/32 F5/32 F#5/32 Ab5/32 A5/32 B5/32 C6/32 D6/32 Eb6/32 F6/32 F#6/32 "
    "Ab6/32 A6/32 B6/32 C7/32 Ab6/8 F6/8 D6/8 B5/8",
    "F5/16 Ab5/16 B5/16 D6/16 F6/8 D6/8 B5/8 Ab5/8 F5/8 D5/8",
    "Ab5/16 B5/16 D6/16 F6/16 Ab6/8 F6/8 D6/8 B5/8 Ab5/8 F5/8",
    "B5/16 D6/16 F6/16 Ab6/16 B6/8 Ab6/8 F6/8 D6/8 B5/8 Ab5/8",
    # mm.125-128  whole-tone: no perfect fifth anywhere, so no tonic gravity.
    # Phrase rhythm compresses 2+2 into 1+1+1+1 as the form itself speeds up.
    "D6/8 E6/8 F#6/8 Ab6/8 Bb6/8 Ab6/8 F#6/8 E6/8",
    "D6/8 E6/8 F#6/8 Ab6/8 Bb6/8 C7/8 Bb6/8 Ab6/8",
    "Eb6/8 F6/8 G6/8 A6/8 B6/8 A6/8 G6/8 F6/8",
    "Eb6/16 F6/16 G6/16 A6/16 B6/16 Db7/16 B6/16 A6/16 G6/8 F6/8 Eb6/8 Db6/8",
    # mm.129-130  everything stops.  Bare tritone, subito p -- m.16 again.
    "D5+Ab5/1", "D5+Ab5/2 R/2",
]

COUNTER_VI = ([oct_down(b) for b in LEAD_VI[:4]]
              + [oct_down(b) for b in LEAD_VI[4:12]]
              + rests(4)
              + ["D4+Ab4/1", "D4+Ab4/2 R/2"])

WINDS_VI = (["Db5+F5+Ab5/1"] * 4
            + ["D4+F4+Ab4+B4/1", "F4+Ab4+B4+D5/1", "Ab4+B4+D5+F5/1", "B4+D5+F5+Ab5/1"] * 2
            + ["D4+E4+F#4+Ab4/1", "D4+E4+F#4+Ab4/1",
               "Eb4+F4+G4+A4/1", "Eb4+F4+G4+A4/1"]
            + ["D4+Ab4/1", "D4+Ab4/2 R/2"])

STABS_VI = (["R/8 Db4+F4+Ab4/8 R/8 Db4+F4+Ab4/8 R/8 Db4+F4+Ab4/8 R/8 Db4+F4+Ab4/8",
             "R/8 C4+F4+Ab4/8 R/8 C4+F4+Ab4/8 R/8 C4+F4+Ab4/8 R/8 C4+F4+Ab4/8",
             "R/8 B3+Eb4+Ab4/8 R/8 B3+Eb4+Ab4/8 R/8 B3+Eb4+Ab4/8 R/8 B3+Eb4+Ab4/8",
             "R/8 Bb3+D4+Ab4/8 R/8 Bb3+D4+Ab4/8 R/8 Bb3+D4+Ab4/8 R/8 Bb3+D4+Ab4/8"]
            # 3+3+2 hemiola stabs -- the accompaniment lurches against the 4/4
            + ["D4+F4+Ab4+B4/4. D4+F4+Ab4+B4/4. D4+F4+Ab4+B4/4",
               "F4+Ab4+B4+D5/4. F4+Ab4+B4+D5/4. F4+Ab4+B4+D5/4",
               "Ab4+B4+D5+F5/4. Ab4+B4+D5+F5/4. Ab4+B4+D5+F5/4",
               "B4+D5+F5+Ab5/4. B4+D5+F5+Ab5/4. B4+D5+F5+Ab5/4"] * 2
            + ["D4+E4+F#4+Ab4/4. D4+E4+F#4+Ab4/4. D4+E4+F#4+Ab4/4",
               "D4+E4+F#4+Ab4/4. D4+E4+F#4+Ab4/4. D4+E4+F#4+Ab4/4",
               "Eb4+F4+G4+A4/4. Eb4+F4+G4+A4/4. Eb4+F4+G4+A4/4",
               "Eb4+F4+G4+A4/4. Eb4+F4+G4+A4/4. Eb4+F4+G4+A4/4"]
            + rests(2))

KEYS_VI = (["Db4/16 F4/16 Ab4/16 Cb5/16 Db5/16 Cb5/16 Ab4/16 F4/16 "
              "Db4/16 F4/16 Ab4/16 Cb5/16 Db5/16 Cb5/16 Ab4/16 F4/16",
              "C4/16 F4/16 Ab4/16 Cb5/16 C5/16 Cb5/16 Ab4/16 F4/16 "
              "C4/16 F4/16 Ab4/16 Cb5/16 C5/16 Cb5/16 Ab4/16 F4/16",
              "B3/16 Eb4/16 Ab4/16 B4/16 Eb5/16 B4/16 Ab4/16 Eb4/16 "
              "B3/16 Eb4/16 Ab4/16 B4/16 Eb5/16 B4/16 Ab4/16 Eb4/16",
              "Bb3/16 D4/16 Ab4/16 Bb4/16 D5/16 Bb4/16 Ab4/16 D4/16 "
              "Bb3/16 D4/16 Ab4/16 Bb4/16 D5/16 Bb4/16 Ab4/16 D4/16"]
           + [oct_down(b) for b in LEAD_VI[4:12]]
           + [oct_down(b) for b in LEAD_VI[12:16]]
           + rests(2))

BASS_VI = [
    # the chromatic collapse: one semitone per bar under a held upper structure
    "Db2/8 Db2/8 Db2/8 Db2/8 Db2/8 Db2/8 Db2/8 Db2/8",
    "C2/8 C2/8 C2/8 C2/8 C2/8 C2/8 C2/8 C2/8",
    "B1/8 B1/8 B1/8 B1/8 B1/8 B1/8 B1/8 B1/8",
    "Bb1/8 Bb1/8 Bb1/8 Bb1/8 Bb1/8 Bb1/8 Bb1/8 Bb1/8",
    # 3+3+2 hemiola on the minor-third cycle
    "D1/4. D2/4. D1/4", "F1/4. F2/4. F1/4",
    "Ab1/4. Ab2/4. Ab1/4", "B1/4. B2/4. B1/4",
    "D1/4. D2/4. D1/4", "F1/4. F2/4. F1/4",
    "Ab1/4. Ab2/4. Ab1/4", "B1/4. B2/4. B1/4",
    "D1/8 E1/8 F#1/8 Ab1/8 Bb1/8 C2/8 D2/8 E2/8",
    "F#2/8 Ab2/8 Bb2/8 C3/8 D3/8 C3/8 Bb2/8 Ab2/8",
    "Eb1/8 F1/8 G1/8 A1/8 B1/8 Db2/8 Eb2/8 F2/8",
    "G2/8 A2/8 B2/8 Db3/8 Eb3/8 Db3/8 B2/8 A2/8",
    "D1+Ab1/1", "D1+Ab1/2 R/2",
]

DRUMS_VI = (["half"] * 4
            + ["driveO"] + ["drive"] * 3
            + ["liftC"] + ["lift"] * 3
            + ["liftC", "lift", "liftC", "fill"]
            + ["stop", "tacet"])

# ===========================================================================
# SECTION VII -- E "NASH EQUILIBRIUM"   mm. 131-150   (20 bars)
# ===========================================================================
# mm.131-138  alpha and beta sound SIMULTANEOUSLY for the first time, D minor.
# mm.139-142  the minor-third cycle returns as a RISING sequence: D, F, Ab, B.
#             The dim7 that broke the key in section VI is now the engine.
# mm.143-146  D MAJOR.  C# appears for the first time in the entire piece.
#             F natural becomes F#; Ab is respelled G# and is now the #11.
#             omega's tail RISES where alpha's fell.
# mm.147-150  upward rush into the final chord, held, hard collective cutoff.
CH_VII = (["Dm", "C", "Bb", "Am", "Dm", "C", "Bb", "Am"]
          + ["Dm", "F", "Abm", "Bm"]
          + ["D", "Gma7", "D", "A7"]
          + ["D", "D", "D", "FINAL"])

LEAD_VII = [
    # beta in the lead, fff, top voice
    "F6/2 A6/2", "G6/1", "F6/2 D6/2", "C6/2 E6/2",
    "F6/2 A6/2", "Bb6/1", "A6/2 F6/2", "D6/2 E6/2",
    # rising minor-third sequence -- the octatonic cycle, ascending
    "D6/16 F6/16 Ab6/16 A6/16 A6/8. G6/8 F6/8 E6/8 D6/16 C6/16 D6/16",
    "F6/16 Ab6/16 B6/16 C7/16 C7/8. Bb6/8 Ab6/8 G6/8 F6/16 Eb6/16 F6/16",
    "Ab5/16 B5/16 D6/16 Eb6/16 Eb6/8. Db6/8 B5/8 Bb5/8 Ab5/16 Gb5/16 Ab5/16",
    "B5/16 D6/16 F6/16 F#6/16 F#6/8. E6/8 D6/8 C#6/8 B5/16 A5/16 B5/16",
    # ---- m.143: D MAJOR.  omega.  One note changes; everything changes. ----
    "D5/16 F#5/16 G#5/16 A5/16 A5/8. B5/8 C#6/8 D6/8 E6/16 F#6/16 G#6/16",
    "A6/2 G#6/2",
    "D6/16 F#6/16 G#6/16 A6/16 A6/8. B6/8 C#7/8 D7/8 R/8.",
    "A6/16 G#6/16 F#6/16 E6/16 D6/16 C#6/16 B5/16 A5/16 G#5/8 A5/8 B5/8 C#6/8",
    # ---- the upward rush.  Bartok revised the Concerto for Orchestra
    # specifically to end with an ascent instead of a plunge.  Two octaves of
    # D LYDIAN -- the mode in which G#, the note that has been poison since
    # bar 1, is simply a scale degree.
    "D5/16 E5/16 F#5/16 G#5/16 A5/16 B5/16 C#6/16 D6/16 "
    "E6/16 F#6/16 G#6/16 A6/16 B6/16 C#7/16 D7/16 E7/16",
    # peak, then one full beat of silence before the chord lands
    "F#7/2 R/2",
    # Dmaj13(#11).  Lead takes only the consonant top skeleton, fff.
    "D6+F#6+A6/1~", "D6+F#6+A6/1",
]

COUNTER_VII = [
    # alpha underneath beta -- the two faces of the cell, at once
    "D5/16 F5/16 Ab5/16 A5/16 A5/8. G5/8 F5/8 E5/8 D5/16 C5/16 D5/16",
    "C5/16 E5/16 G5/16 A5/16 Ab5/8. G5/8 F5/8 E5/8 D5/16 C5/16 D5/16",
    "Bb4/16 D5/16 F5/16 A5/16 Ab5/8. G5/8 F5/8 D5/8 Bb4/16 C5/16 D5/16",
    "A4/16 C5/16 E5/16 A5/16 Ab5/8. G5/8 F5/8 E5/8 D5/16 E5/16 F5/16",
    "D5/16 F5/16 Ab5/16 A5/16 A5/8. G5/8 F5/8 E5/8 D5/16 C5/16 D5/16",
    "C5/16 E5/16 G5/16 A5/16 Ab5/8. G5/8 F5/8 E5/8 D5/16 C5/16 D5/16",
    "Bb4/16 D5/16 F5/16 A5/16 Ab5/8. G5/8 F5/8 D5/8 Bb4/16 C5/16 D5/16",
    "A4/16 C5/16 E5/16 A5/16 Ab5/8. G5/8 F5/8 E5/8 D5/16 E5/16 F5/16",
    "D5/2 A5/2", "F5/2 C6/2", "Ab5/2 Eb6/2", "B5/2 F#6/2",
    "D5/2 A5/2", "B4/2 G5/2", "D5/2 A5/2", "C#5/2 A5/2",
    "D4/16 E4/16 F#4/16 G#4/16 A4/16 B4/16 C#5/16 D5/16 "
    "E5/16 F#5/16 G#5/16 A5/16 B5/16 C#6/16 D6/16 E6/16",
    "F#6/2 R/2",
    # the two colour tones, one dynamic step under the brass
    "E5+G#5/1~", "E5+G#5/1",
]

WINDS_VII = (["D4+F4+A4/1", "C4+E4+G4/1", "Bb3+D4+F4/1", "A3+C4+E4/1"] * 2
             + ["D4+F4+A4/1", "F4+Ab4+C5/1", "Ab4+B4+Eb5/1", "B4+D5+F#5/1"]
             + ["D4+F#4+A4/1", "G3+B3+D4+F#4/1", "D4+F#4+A4/1", "A3+C#4+E4+G4/1"]
             + ["D4+F#4+A4/1", "D4+F#4+A4/2 R/2",
                # consonant skeleton only, brass, fff
                "D3+A3+D4+F#4/1~", "D3+A3+D4+F#4/1"])

STABS_VII = ([stabs(c, "offbeat") for c in ["Dm", "C", "Bb", "Am"] * 2]
             + ["D4+F4+A4/4. D4+F4+A4/4. D4+F4+A4/4",
                "F4+Ab4+C5/4. F4+Ab4+C5/4. F4+Ab4+C5/4",
                "Ab4+B4+Eb5/4. Ab4+B4+Eb5/4. Ab4+B4+Eb5/4",
                "B4+D5+F#5/4. B4+D5+F#5/4. B4+D5+F#5/4"]
             + [stabs("D", "offbeat"), stabs("Gma7", "offbeat"),
                stabs("D", "offbeat"), stabs("A7", "offbeat")]
             + [stabs("D", "four"), "D4+F#4+A4/2 R/2",
                "A4+C#5/1~", "A4+C#5/1"])

KEYS_VII = ([shift(ostinato(c), 12) for c in ["Dm", "C", "Bb", "Am"] * 2]
            + ["D4/16 F4/16 Ab4/16 A4/16 D5/16 F5/16 Ab5/16 A5/16 "
               "D6/16 A5/16 Ab5/16 F5/16 D5/16 A4/16 Ab4/16 F4/16",
               "F4/16 Ab4/16 B4/16 C5/16 F5/16 Ab5/16 B5/16 C6/16 "
               "F6/16 C6/16 B5/16 Ab5/16 F5/16 C5/16 B4/16 Ab4/16",
               "Ab4/16 B4/16 D5/16 Eb5/16 Ab5/16 B5/16 D6/16 Eb6/16 "
               "Ab6/16 Eb6/16 D6/16 B5/16 Ab5/16 Eb5/16 D5/16 B4/16",
               "B4/16 D5/16 F5/16 F#5/16 B5/16 D6/16 F6/16 F#6/16 "
               "B6/16 F#6/16 F6/16 D6/16 B5/16 F#5/16 F5/16 D5/16"]
            + ["D4/16 F#4/16 A4/16 C#5/16 D5/16 F#5/16 A5/16 C#6/16 "
               "D6/16 C#6/16 A5/16 F#5/16 D5/16 C#5/16 A4/16 F#4/16",
               "G4/16 B4/16 D5/16 F#5/16 G5/16 B5/16 D6/16 F#6/16 "
               "G6/16 F#6/16 D6/16 B5/16 G5/16 F#5/16 D5/16 B4/16",
               "D4/16 F#4/16 A4/16 C#5/16 D5/16 F#5/16 A5/16 C#6/16 "
               "D6/16 C#6/16 A5/16 F#5/16 D5/16 C#5/16 A4/16 F#4/16",
               "A3/16 C#4/16 E4/16 G4/16 A4/16 C#5/16 E5/16 G5/16 "
               "A5/16 G5/16 E5/16 C#5/16 A4/16 G4/16 E4/16 C#4/16"]
            + ["D4/16 E4/16 F#4/16 G#4/16 A4/16 B4/16 C#5/16 D5/16 "
               "E5/16 F#5/16 G#5/16 A5/16 B5/16 C#6/16 D6/16 E6/16",
               "F#6/16 G#6/16 A6/16 B6/16 C#7/16 D7/16 R/8 R/2",
               "D1+D2+A2+D3+A3+D4+F#4+A4+C#5+E5+G#5+D6+F#6+A6/1~",
               "D1+D2+A2+D3+A3+D4+F#4+A4+C#5+E5+G#5+D6+F#6+A6/1"])

BASS_VII = ([ostinato(c) for c in ["Dm", "C", "Bb", "Am"] * 2]
            + ["D1/4. D2/4. D1/4", "F1/4. F2/4. F1/4",
               "Ab1/4. Ab2/4. Ab1/4", "B1/4. B2/4. B1/4"]
            + ["D1/8 D2/8 A1/8 D2/8 F#2/8 D2/8 A1/8 D2/8",
               "G1/8 G2/8 D2/8 G2/8 B2/8 G2/8 D2/8 G2/8",
               "D1/8 D2/8 A1/8 D2/8 F#2/8 D2/8 A1/8 D2/8",
               "A1/8 A2/8 E2/8 A2/8 C#3/8 A2/8 E2/8 A2/8"]
            + ["D1/8 D2/8 D1/8 D2/8 D1/8 D2/8 D1/8 D2/8",
               "D1/16 E1/16 F#1/16 G#1/16 A1/16 B1/16 C#2/16 D2/16 R/2",
               # pure octaves and fifths, no third anywhere below D4
               "D1+D2+A2+D3/1~", "D1+D2+A2+D3/1"])

DRUMS_VII = (["liftC"] + ["lift"] * 3 + ["liftC"] + ["lift"] * 2 + ["fill"]
             + ["blaze"] * 4
             + ["liftC"] + ["lift"] * 2 + ["fill"]
             + ["blaze", "roll", "final", "final"])

# ===========================================================================
# ASSEMBLY
# ===========================================================================
SECTIONS = [
    dict(tag="I", name="OPENING BID", start=1, meter="6/4", bpm=92, key="D minor (1♭)",
         mode="D half-whole octatonic", chords=None,
         parts=dict(LEAD=LEAD_I, COUNTER=COUNTER_I, WINDS=WINDS_I,
                    STABS=STABS_I, KEYS=KEYS_I, BASS=BASS_I, DRUMS=DRUMS_I)),
    dict(tag="II", name="THE TELL", start=17, meter="4/4", bpm=184, key="D minor (1♭)",
         mode="D Aeolian", chords=CH_II,
         parts=dict(LEAD=LEAD_II, COUNTER=COUNTER_II, WINDS=WINDS_II,
                    STABS=STABS_II, KEYS=KEYS_II, BASS=BASS_II, DRUMS=DRUMS_II)),
    dict(tag="III", name="OPENING MOVE", start=25, meter="4/4", bpm=184, key="D minor (1♭)",
         mode="D Aeolian + ♭5", chords=CH_III,
         parts=dict(LEAD=LEAD_III, COUNTER=COUNTER_III, WINDS=WINDS_III,
                    STABS=STABS_III, KEYS=KEYS_III, BASS=BASS_III, DRUMS=DRUMS_III)),
    dict(tag="IV", name="DEFECT", start=57, meter="4/4", bpm=184, key="D minor (1♭)",
         mode="D Phrygian", chords=CH_IV,
         parts=dict(LEAD=LEAD_IV, COUNTER=COUNTER_IV, WINDS=WINDS_IV,
                    STABS=STABS_IV, KEYS=KEYS_IV, BASS=BASS_IV, DRUMS=DRUMS_IV)),
    dict(tag="V", name="THE PAYOFF MATRIX", start=81, meter="4/4", bpm=184,
         key="F major (1♭) → G♭ major (6♭)", mode="F Ionian", chords=CH_V,
         parts=dict(LEAD=LEAD_V, COUNTER=COUNTER_V, WINDS=WINDS_V,
                    STABS=STABS_V, KEYS=KEYS_V, BASS=BASS_V, DRUMS=DRUMS_V)),
    dict(tag="VI", name="MIXED STRATEGY", start=113, meter="4/4", bpm=184,
         key="none", mode="octatonic → whole-tone", chords=CH_VI,
         parts=dict(LEAD=LEAD_VI, COUNTER=COUNTER_VI, WINDS=WINDS_VI,
                    STABS=STABS_VI, KEYS=KEYS_VI, BASS=BASS_VI, DRUMS=DRUMS_VI)),
    dict(tag="VII", name="NASH EQUILIBRIUM", start=131, meter="4/4", bpm=184,
         key="D minor → D major (2♯)", mode="D Aeolian → D Lydian", chords=CH_VII,
         parts=dict(LEAD=LEAD_VII, COUNTER=COUNTER_VII, WINDS=WINDS_VII,
                    STABS=STABS_VII, KEYS=KEYS_VII, BASS=BASS_VII, DRUMS=DRUMS_VII)),
]

PART_ORDER = ["LEAD", "COUNTER", "WINDS", "STABS", "KEYS", "BASS", "DRUMS"]
SECTION_BARS = {"I": 16, "II": 8, "III": 32, "IV": 24, "V": 32, "VI": 18, "VII": 20}


def verify():
    problems = []
    total = 0
    for s in SECTIONS:
        want = SECTION_BARS[s["tag"]]
        beats = F(6) if s["meter"] == "6/4" else F(4)
        total += want
        if s["chords"] is not None and len(s["chords"]) != want:
            problems.append(f"{s['tag']}: chord grid {len(s['chords'])} != {want}")
        for pname in PART_ORDER:
            bars = s["parts"][pname]
            if len(bars) != want:
                problems.append(f"{s['tag']}/{pname}: {len(bars)} bars, want {want}")
                continue
            if pname == "DRUMS":
                for i, b in enumerate(bars):
                    try:
                        d = drums(b)
                    except Exception as e:
                        problems.append(f"{s['tag']}/DRUMS m.{s['start']+i}: {e}")
                        continue
                    if bar_len(d) != beats:
                        problems.append(
                            f"{s['tag']}/DRUMS m.{s['start']+i}: pattern '{b}' = "
                            f"{bar_len(d)} beats, want {beats}")
                continue
            for i, b in enumerate(bars):
                try:
                    L = bar_len(b)
                except Exception as e:
                    problems.append(f"{s['tag']}/{pname} m.{s['start']+i}: parse {e} :: {b[:60]}")
                    continue
                if L != beats:
                    problems.append(
                        f"{s['tag']}/{pname} m.{s['start']+i}: {L} beats, want {beats} :: {b[:60]}")
    if total != 150:
        problems.append(f"TOTAL BARS {total} != 150")
    return problems


def constraint_checks():
    """The compositional promises, checked mechanically."""
    out = []
    first_cs, first_dmaj, first_top = None, None, None
    for s in SECTIONS:
        for pname in PART_ORDER:
            if pname == "DRUMS":
                continue
            for i, b in enumerate(s["parts"][pname]):
                m = s["start"] + i
                for p in pitches_in(b):
                    pc = to_midi(p) % 12
                    if pc == 1 and (first_cs is None or m < first_cs):   # C#/Db
                        first_cs = m
                    if to_midi(p) >= to_midi("D7") and (first_top is None or m < first_top):
                        first_top = m
                if "F#" in b and pname in ("LEAD", "COUNTER", "KEYS", "BASS"):
                    if first_dmaj is None and s["tag"] == "VII":
                        first_dmaj = m
    out.append(("First C#/D♭ anywhere (Db is spelled in G♭ major, m.105)", first_cs))
    out.append(("First D major material (section VII)", first_dmaj))
    out.append(("First pitch at or above D7", first_top))
    return out


if __name__ == "__main__":
    probs = verify()
    if probs:
        print(f"{len(probs)} PROBLEMS")
        for p in probs[:60]:
            print("  ", p)
    else:
        print("OK -- 150 bars, all parts, every measure sums exactly.")
    for label, val in constraint_checks():
        print(f"  {label}: m.{val}")
