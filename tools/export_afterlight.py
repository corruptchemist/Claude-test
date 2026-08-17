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
    ("CHOIR",    "Choir (counter-melody)", 52, clef.TrebleClef),
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
TEXT_AT = {17: "counter-melody", 25: "poco piu luminoso", 57: "bass alone",
           65: "oscuro", 81: "up a semitone", 145: "back to the opening"}
MARKS = {1: "G MINOR", 9: "MAIN MELODY", 17: "+ counter-melody",
         25: "Bb MAJOR - choir takes it", 33: "lead", 41: "lead 2",
         49: "tutti", 57: "BASS FEATURE", 65: "G MINOR - phase two",
         73: "choir", 81: "B MAJOR", 89: "lead + bells", 97: "choir",
         105: "the strain", 113: "lead 2", 121: "climax", 129: "choir",
         137: "coda - bells", 145: "coda"}


def trill_notes(n):
    """Expand a trill into alternating 32nds so it is audible in the MIDI.
    The score keeps the trill SIGN; only the MIDI gets the realisation."""
    total = n.duration.quarterLength
    step = 0.125
    count = max(2, int(total / step))
    out = []
    for k in range(count):
        x = note.Note(n.pitch) if k % 2 == 0 else note.Note(n.pitch.midi + 2)
        x.duration = duration.Duration(step)
        out.append(x)
    used = step * count
    if total - used > 1e-6:
        x = note.Note(n.pitch)
        x.duration = duration.Duration(total - used)
        out.append(x)
    return out


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


def build(realize_trills=False):
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
            idx = 0
            for obj, tied in parse_bar(src, pkey == "DRUMS"):
                orn = A.ORNAMENTS.get((pkey, m, idx))
                idx += 1
                if orn == "trill" and isinstance(obj, note.Note):
                    if realize_trills:
                        for x in trill_notes(obj):
                            meas.append(x)
                            first_note.setdefault(m, x)
                            last_note[m] = x
                        continue
                    obj.expressions.append(expressions.Trill())
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
    mid = sys.argv[1] if len(sys.argv) > 1 else "../score/afterlight.mid"
    xml = sys.argv[2] if len(sys.argv) > 2 else "../score/afterlight.musicxml"
    build(realize_trills=True).write("midi", fp=mid)
    print("wrote", mid)
    build(realize_trills=False).write("musicxml", fp=xml)
    print("wrote", xml)
