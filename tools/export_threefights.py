"""Export THREE FIGHTS to MusicXML (+MIDI). Concert pitch."""

import sys
from music21 import (stream, note, chord, meter, key, tempo, clef, instrument,
                     duration, expressions, dynamics, tie, bar, metadata, spanner)

import threefights as T
import threefights2 as T2
from zerosum import dur_of

# GM programs, 0-indexed.  The lead is a SQUARE-WAVE synth lead -- the
# Undertale sound -- not a brass patch.
PARTS = [
    ("LEAD",    "Lead",    80, clef.TrebleClef),   # Lead 1 (square)
    ("COUNTER", "Counter", 81, clef.TrebleClef),   # Lead 2 (sawtooth)
    ("SUSTAIN", "Sustain", 51, clef.TrebleClef),   # Synth Strings 2
    ("STABS",   "Stabs",   27, clef.TrebleClef),   # Electric Guitar (clean)
    ("KEYS",    "Keys",     0, clef.TrebleClef),   # Acoustic Grand
    ("BASS",    "Bass",    38, clef.BassClef),     # Synth Bass 1
    ("DRUMS",   "Drums",    0, clef.PercussionClef),
]

DRUM_MIDI = {"K": 36, "S": 38, "H": 42, "O": 46, "C": 49, "R": 51,
             "T": 47, "F": 41, "Z": 38, "X": 49}

TEMPO_AT = {1: 95, 65: 148, 129: 126}
KEY_AT = {1: -4, 61: 2, 129: -1}
TEXT_AT = {63: "rit.", 65: "a tempo", 127: "poco rit.", 129: "a tempo",
           97: "bass break", 185: "all three themes together", 213: "allargando"}

MARKS = {1: "I. FLOWER", 9: "A — Your Best Friend", 25: "B", 33: "A′",
         49: "build", 57: "bridge", 61: "E°7 = A♯°7",
         65: "II. GLAMOUR", 73: "A", 89: "B", 97: "BASS BREAK", 105: "A′",
         121: "bridge", 129: "III. BAD TIME", 137: "A — the verse",
         153: "B", 161: "the riff, in the lead", 169: "A′",
         185: "IV. QUODLIBET", 201: "climax", 209: "coda"}


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
    sc.metadata.title = "THREE FIGHTS"
    sc.metadata.subtitle = ("variations on Toby Fox · "
                            "Finale / Death by Glamour / MEGALOVANIA")
    sc.metadata.composer = "arrangement"

    for pkey, pname, prog, clef_cls in PARTS:
        part = stream.Part(id=pname)
        part.partName = pname
        inst = instrument.Instrument()
        inst.partName = inst.instrumentName = pname
        if pkey == "DRUMS":
            inst.midiChannel = 9
            inst.midiProgram = 0
        else:
            inst.midiProgram = prog
        part.insert(0, inst)

        first_note, last_note, by_index = {}, {}, {}
        pending_tie = False
        dyn_map = dict(T.dyn_changes(pkey))
        bars = T2.PARTS[pkey]

        for i, raw in enumerate(bars):
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

            # grace note ahead of the downbeat
            g = T.GRACE.get((pkey, m))
            if g:
                meas.append(note.Note(g, type="eighth").getGrace())

            src = T2.DRUM_LIB[raw] if pkey == "DRUMS" else raw
            idx = 0
            for obj, tied in parse_bar(src, pkey == "DRUMS"):
                if pending_tie and isinstance(obj, (note.Note, chord.Chord)):
                    obj.tie = tie.Tie("stop")
                    pending_tie = False
                if tied:
                    obj.tie = tie.Tie("continue" if obj.tie else "start")
                    pending_tie = True
                orn = T.ORNAMENTS.get((pkey, m, idx))
                if orn and isinstance(obj, note.Note):
                    obj.expressions.append(
                        expressions.Trill() if orn == "trill" else expressions.Turn())
                meas.append(obj)
                if isinstance(obj, (note.Note, chord.Chord)):
                    first_note.setdefault(m, obj)
                    last_note[m] = obj
                    by_index[(m, idx)] = obj
                idx += 1
            if m == len(bars):
                meas.rightBarline = bar.Barline("final")
            part.append(meas)

        for a, b, direction in T.LEAD_HAIRPINS:
            s0, s1 = first_note.get(a), last_note.get(b)
            if s0 is None or s1 is None or s0 is s1:
                continue
            w = dynamics.Crescendo() if direction == "<" else dynamics.Diminuendo()
            w.addSpannedElements([s0, s1])
            part.insert(0, w)

        for gp, gm, gi in T.GLISS:
            if gp != pkey:
                continue
            a, b = by_index.get((gm, gi)), by_index.get((gm, gi + 1))
            if a is None or b is None:
                continue
            gl = spanner.Glissando()
            gl.addSpannedElements([a, b])
            part.insert(0, gl)

        sc.insert(0, part)
    return sc


if __name__ == "__main__":
    sc = build()
    xml = sys.argv[1] if len(sys.argv) > 1 else "../score/three-fights.musicxml"
    mid = sys.argv[2] if len(sys.argv) > 2 else "../score/three-fights.mid"
    sc.write("musicxml", fp=xml)
    print("wrote", xml)
    sc.write("midi", fp=mid)
    print("wrote", mid)
