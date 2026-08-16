"""Export ZERO-SUM to MusicXML (+ MIDI) from the verified score data.

Written at CONCERT PITCH. Set up any transposing instruments in Finale after import.
"""

import sys
from fractions import Fraction as F
from music21 import (stream, note, chord, meter, key, tempo, clef, instrument,
                     duration, expressions, dynamics, tie, bar, metadata)

import zerosum2 as Z
from zerosum import dur_of, drums

# --- part setup -------------------------------------------------------------
# midi program, clef, staff name
PARTS = [
    ("LEAD",    "Lead",    81, clef.TrebleClef),      # square / pulse lead
    ("COUNTER", "Counter", 82, clef.TrebleClef),      # saw lead
    ("SUSTAIN", "Sustain", 51, clef.TrebleClef),      # synth strings
    ("STABS",   "Stabs",    6, clef.TrebleClef),      # harpsichord
    ("KEYS",    "Keys",     0, clef.TrebleClef),      # piano
    ("BASS",    "Bass",    38, clef.BassClef),        # synth bass
    ("DRUMS",   "Drums",    0, clef.PercussionClef),
]
SRC_KEY = {"LEAD": "LEAD", "COUNTER": "COUNTER", "SUSTAIN": "WINDS",
           "STABS": "STABS", "KEYS": "KEYS", "BASS": "BASS", "DRUMS": "DRUMS"}

# General MIDI drum map
DRUM_MIDI = {"K": 36, "S": 38, "H": 42, "O": 46, "C": 49, "R": 51, "T": 47,
             "Z": 38, "X": 49}

# measure -> (numerator, denominator)
METER_AT = {1: (6, 4), 17: (4, 4)}
TEMPO_AT = {1: 92, 17: 184}
# measure -> sharps(+) / flats(-)
KEY_AT = {1: -1, 105: -6, 113: -1, 143: 2}

MARKS = {1: "I. OPENING BID", 17: "II. THE TELL", 25: "III. OPENING MOVE",
         57: "IV. DEFECT", 81: "V. THE PAYOFF MATRIX", 93: "the drop",
         113: "VI. MIXED STRATEGY", 131: "VII. NASH EQUILIBRIUM",
         143: "D major", 147: "allargando"}

DYN_AT = {1: "ff", 3: "mp", 9: "mf", 13: "f", 17: "mf", 25: "ff",
          57: "ff", 81: "mp", 93: "ff", 105: "ff", 113: "f",
          129: "p", 131: "fff", 147: "fff"}


def parse_bar(bar_str, is_drums):
    """Yield (music21 object, tied_forward) for one measure."""
    for tok in bar_str.split():
        tied = tok.endswith("~")
        head, d = tok.rstrip("~").split("/")
        q = float(dur_of(d))
        du = duration.Duration(q)
        if head == "R":
            yield note.Rest(duration=du), False
            continue
        names = head.split("+")
        if is_drums:
            pitches = [DRUM_MIDI[c] for c in names[0]]
            if len(pitches) == 1:
                n = note.Note(pitches[0]); n.duration = du
            else:
                n = chord.Chord(pitches); n.duration = du
            n.stemDirection = "up"
            yield n, tied
            continue
        if len(names) == 1:
            n = note.Note(names[0]); n.duration = du
        else:
            n = chord.Chord(names); n.duration = du
        yield n, tied


def build():
    sc = stream.Score()
    sc.metadata = metadata.Metadata()
    sc.metadata.title = "ZERO-SUM"
    sc.metadata.subtitle = "Boss Theme · 150 measures"
    sc.metadata.composer = "original composition"

    # flatten all sections into one 150-measure lookup per part
    flat = {p: {} for p, *_ in PARTS}
    for s in Z.SECTIONS:
        for pkey, _, _, _ in PARTS:
            bars = s["parts"][SRC_KEY[pkey]]
            for i, b in enumerate(bars):
                flat[pkey][s["start"] + i] = b

    for pkey, pname, prog, clef_cls in PARTS:
        part = stream.Part(id=pname)
        part.partName = pname
        inst = instrument.Instrument()
        inst.partName = pname
        inst.instrumentName = pname
        if pkey == "DRUMS":
            inst.midiChannel = 9
            inst.midiProgram = 0
        else:
            inst.midiProgram = prog
        part.insert(0, inst)

        pending_tie = False
        for m in range(1, 151):
            meas = stream.Measure(number=m)
            if m == 1:
                meas.clef = clef_cls()
            if m in METER_AT:
                num, den = METER_AT[m]
                meas.timeSignature = meter.TimeSignature(f"{num}/{den}")
            if m in KEY_AT and pkey != "DRUMS":
                meas.insert(0, key.KeySignature(KEY_AT[m]))
            if m in TEMPO_AT and pkey == "LEAD":
                mm = tempo.MetronomeMark(number=TEMPO_AT[m], referent=note.Note(type="quarter"))
                meas.insert(0, mm)
            if m in MARKS and pkey == "LEAD":
                meas.insert(0, expressions.RehearsalMark(MARKS[m]))
            if m in DYN_AT:
                meas.insert(0, dynamics.Dynamic(DYN_AT[m]))

            src = flat[pkey][m]
            if pkey == "DRUMS":
                src = drums(src)
            for obj, tied in parse_bar(src, pkey == "DRUMS"):
                if pending_tie and isinstance(obj, (note.Note, chord.Chord)):
                    obj.tie = tie.Tie("stop")
                    pending_tie = False
                if tied:
                    obj.tie = tie.Tie("continue" if obj.tie else "start")
                    pending_tie = True
                meas.append(obj)
            if m == 150:
                meas.rightBarline = bar.Barline("final")
            part.append(meas)
        sc.insert(0, part)
    return sc


if __name__ == "__main__":
    sc = build()
    xml = sys.argv[1] if len(sys.argv) > 1 else "../score/zero-sum.musicxml"
    mid = sys.argv[2] if len(sys.argv) > 2 else "../score/zero-sum.mid"
    sc.write("musicxml", fp=xml)
    print("wrote", xml)
    sc.write("midi", fp=mid)
    print("wrote", mid)
