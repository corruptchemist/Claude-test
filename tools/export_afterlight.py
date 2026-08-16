"""Export AFTERLIGHT as multi-track MIDI for REAPER (+ MusicXML for reading).

Track names say which patch to load, since REAPER shows them on import.
"""

import sys
from music21 import (stream, note, chord, meter, key, tempo, clef, instrument,
                     duration, expressions, dynamics, tie, bar, metadata)

import afterlight as A
from zerosum import dur_of

# (part key, REAPER track name, GM program 0-indexed, clef)
PARTS = [
    ("LEAD",     "Lead 1 (pulse 25%)",   80, clef.TrebleClef),
    ("LEAD2",    "Lead 2 (pulse 12.5%)", 81, clef.TrebleClef),
    ("BELL",     "Bell / Glock",          9, clef.TrebleClef),
    ("STRINGS",  "Chords (pad)",         50, clef.TrebleClef),
    ("GUITAR",   "Guitar (offbeat)",     27, clef.TrebleClef),
    ("POWER",    "Guitar (distorted)",   30, clef.BassClef),
    ("LOWBRASS", "Low brass",            58, clef.BassClef),
    ("ARP",      "Arp engine 16ths",     11, clef.TrebleClef),
    ("BASS",     "Bass",                 38, clef.BassClef),
    ("SUB",      "Sub bass",             87, clef.BassClef),
    ("DRUMS",    "Drums",                 0, clef.PercussionClef),
]

DRUM_MIDI = {"K": 36, "S": 38, "H": 42, "O": 46, "C": 49, "R": 51,
             "T": 47, "F": 41, "Z": 38}

TEMPO_AT = {1: A.BPM}
KEY_AT = {1: -2, 129: 5}   # G minor / Bb major share 2 flats; B major at 129
TEXT_AT = {33: "poco piu luminoso", 81: "bass alone",
           97: "oscuro", 129: "up a semitone", 193: "back to the opening"}
MARKS = {1: "G MINOR - the fight", 17: "theme, minor",
         33: "Bb MAJOR - hope arrives", 49: "tune moves to Lead 2",
         65: "+ Your Best Friend", 81: "BASS FEATURE",
         97: "G MINOR - phase two", 113: "minor build",
         129: "B MAJOR - the payoff", 153: "quodlibet", 177: "climax",
         193: "coda"}


def parse_bar(s, is_drums):
    for tok in s.split():
        tied = tok.endswith("~")
        head, d = tok.rstrip("~").split("/")
        du = duration.Duration(float(dur_of(d)))
        if head == "R":
            yield note.Rest(duration=du), False
            continue
        if is_drums:
            ps = [DRUM_MIDI[c] for c in head]
            n = note.Note(ps[0]) if len(ps) == 1 else chord.Chord(ps)
            n.duration = du
            n.stemDirection = "up"
            yield n, tied
            continue
        names = head.split("+")
        n = note.Note(names[0]) if len(names) == 1 else chord.Chord(names)
        n.duration = du
        yield n, tied


def build():
    sc = stream.Score()
    sc.metadata = metadata.Metadata()
    sc.metadata.title = "AFTERLIGHT"
    sc.metadata.subtitle = "after Hopes and Dreams / Last Goodbye"
    sc.metadata.composer = "original composition"

    for pkey, pname, prog, clef_cls in PARTS:
        part = stream.Part(id=pname)
        part.partName = pname
        part.partAbbreviation = pname
        inst = instrument.Instrument()
        inst.partName = inst.instrumentName = pname
        if pkey == "DRUMS":
            inst.midiChannel = 9
            inst.midiProgram = 0
        else:
            inst.midiProgram = prog
        part.insert(0, inst)

        first_note, last_note = {}, {}
        pending_tie = False
        dyn_map = dict(A.dyn_changes(pkey))

        for i, raw in enumerate(A.PARTS[pkey]):
            m = i + 1
            meas = stream.Measure(number=m)
            if m == 1:
                meas.clef = clef_cls()
                meas.timeSignature = meter.TimeSignature("4/4")
            if m in KEY_AT and pkey != "DRUMS":
                meas.insert(0, key.KeySignature(KEY_AT[m]))
            if m in TEMPO_AT and pkey == "LEAD":
                meas.insert(0, tempo.MetronomeMark(
                    number=TEMPO_AT[m], referent=note.Note(type="quarter")))
            if m in MARKS and pkey == "LEAD":
                meas.insert(0, expressions.RehearsalMark(MARKS[m]))
            if m in TEXT_AT and pkey == "LEAD":
                meas.insert(0, expressions.TextExpression(TEXT_AT[m]))
            if m in dyn_map:
                meas.insert(0, dynamics.Dynamic(dyn_map[m]))

            src = A.DRUM_LIB[raw] if pkey == "DRUMS" else raw
            for obj, tied in parse_bar(src, pkey == "DRUMS"):
                if pending_tie and isinstance(obj, (note.Note, chord.Chord)):
                    obj.tie = tie.Tie("stop")
                    pending_tie = False
                if tied:
                    obj.tie = tie.Tie("continue" if obj.tie else "start")
                    pending_tie = True
                meas.append(obj)
                if isinstance(obj, (note.Note, chord.Chord)):
                    first_note.setdefault(m, obj)
                    last_note[m] = obj
            if m == A.N:
                meas.rightBarline = bar.Barline("final")
            part.append(meas)

        for a, b, direction in A.LEAD_HAIRPINS:
            s0, s1 = first_note.get(a), last_note.get(b)
            if s0 is None or s1 is None or s0 is s1:
                continue
            w = dynamics.Crescendo() if direction == "<" else dynamics.Diminuendo()
            w.addSpannedElements([s0, s1])
            part.insert(0, w)

        sc.insert(0, part)
    return sc


if __name__ == "__main__":
    sc = build()
    mid = sys.argv[1] if len(sys.argv) > 1 else "../score/afterlight.mid"
    xml = sys.argv[2] if len(sys.argv) > 2 else "../score/afterlight.musicxml"
    sc.write("midi", fp=mid)
    print("wrote", mid)
    sc.write("musicxml", fp=xml)
    print("wrote", xml)
