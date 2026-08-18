"""Export GROUND STATE as multi-track MIDI for REAPER (+ MusicXML).

Track order sets the MIDI channels, and render_toby.py maps its voices by
channel, so this order is load-bearing: LEAD..SUB take 0-8 and the kit takes 9.
GM programs are chosen to name Toby Fox's actual MEGALOVANIA rig as closely as
General MIDI allows -- the real sounds come from render_toby.py, and in REAPER
you would load 3xOsc, Shreddage Bass: Picked and Ollie Waton Drums here.
"""

import sys
from music21 import (stream, note, chord, meter, key, tempo, clef, instrument,
                     duration, expressions, dynamics, tie, bar, metadata)

import groundstate as G
from zerosum import dur_of

PARTS = [
    ("LEAD",    "Lead 1 - 3xOsc saw",        81, clef.TrebleClef),
    ("LEAD2",   "Lead 2 - 3xOsc square",     80, clef.TrebleClef),
    ("STRINGS", "Violin detache",            48, clef.TrebleClef),
    ("ORGAN",   "Organ",                     18, clef.TrebleClef),
    ("STAB",    "Stabs",                     82, clef.TrebleClef),
    ("GUITAR",  "Guitar (distorted)",        30, clef.BassClef),
    ("BASS",    "BASS - Shreddage picked",   34, clef.BassClef),
    ("BASSOCT", "Bass 8va - picked",         39, clef.BassClef),
    ("SUB",     "Sub",                       87, clef.BassClef),
    ("DRUMS",   "Drums - Ollie Waton kit",    0, clef.PercussionClef),
]

DRUM_MIDI = {"K": 36, "S": 38, "H": 42, "O": 46, "C": 49, "R": 51,
             "T": 47, "F": 41, "Z": 38}

KEY_AT = {1: -1, 97: -6, 113: -4, 129: -1}   # D min, Eb min, F min, D min
MARKS = dict(G.LABEL)
TEXT_AT = {1: "bass alone - the ground", 65: "bass and drums only",
           81: "MEGALOVANIA", 97: "up a semitone", 113: "up a minor third",
           129: "back to the floor"}


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
    sc.metadata.title = G.TITLE
    sc.metadata.subtitle = "a last boss after MEGALOVANIA"
    sc.metadata.composer = "original composition; quotes Toby Fox"

    for chan, (pkey, pname, prog, clef_cls) in enumerate(PARTS):
        part = stream.Part(id=pname)
        part.partName = part.partAbbreviation = pname
        inst = instrument.Instrument()
        inst.partName = inst.instrumentName = pname
        # Assign channels EXPLICITLY.  Left to itself music21 hands two parts
        # that share a GM program the same channel, which merged the two bass
        # tracks and pushed the sub onto the picked-bass voice.
        if pkey == "DRUMS":
            inst.midiChannel = 9
            inst.midiProgram = 0
        else:
            inst.midiChannel = chan
            inst.midiProgram = prog
        part.insert(0, inst)

        first_note, last_note = {}, {}
        pending_tie = False
        dyn_map = dict(G.dyn_changes(pkey))

        for i, raw in enumerate(G.PARTS[pkey]):
            m = i + 1
            meas = stream.Measure(number=m)
            if m == 1:
                meas.clef = clef_cls()
                meas.timeSignature = meter.TimeSignature("4/4")
            if m in KEY_AT and pkey != "DRUMS":
                meas.insert(0, key.KeySignature(KEY_AT[m]))
            if m == 1 and pkey == "LEAD":
                meas.insert(0, tempo.MetronomeMark(
                    number=G.BPM, referent=note.Note(type="quarter")))
            if m in MARKS and pkey == "BASS":
                meas.insert(0, expressions.RehearsalMark(MARKS[m]))
            if m in TEXT_AT and pkey == "BASS":
                meas.insert(0, expressions.TextExpression(TEXT_AT[m]))
            if m in dyn_map:
                meas.insert(0, dynamics.Dynamic(dyn_map[m]))

            src = G.DRUM_LIB[raw] if pkey == "DRUMS" else raw
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
            if m == G.N:
                meas.rightBarline = bar.Barline("final")
            part.append(meas)

        for a, b, direction in G.LEAD_HAIRPINS:
            s0, s1 = first_note.get(a), last_note.get(b)
            if s0 is None or s1 is None or s0 is s1:
                continue
            w = dynamics.Crescendo() if direction == "<" else dynamics.Diminuendo()
            w.addSpannedElements([s0, s1])
            part.insert(0, w)

        sc.insert(0, part)
    return sc


if __name__ == "__main__":
    mid = sys.argv[1] if len(sys.argv) > 1 else "../score/ground-state.mid"
    xml = sys.argv[2] if len(sys.argv) > 2 else "../score/ground-state.musicxml"
    sc = build()
    sc.write("midi", fp=mid)
    print("wrote", mid)
    sc.write("musicxml", fp=xml)
    print("wrote", xml)
