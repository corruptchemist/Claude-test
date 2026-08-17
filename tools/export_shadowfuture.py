"""Export SHADOW OF THE FUTURE as multi-track MIDI for REAPER (+ MusicXML).

Track order matters: render_audio.py assigns its synth voices by MIDI channel,
and music21 hands out channels in part order (skipping 9, which is the kit).
"""

import sys
from music21 import (stream, note, chord, meter, key, tempo, clef, instrument,
                     duration, expressions, dynamics, tie, bar, metadata)

import shadowfuture as S
from zerosum import dur_of

# (part key, REAPER track name, GM program 0-indexed, clef)
PARTS = [
    ("LEAD",     "Lead 1 - player A (pulse 25%)",  80, clef.TrebleClef),
    ("LEAD2",    "Lead 2 - player B (pulse 12.5%)", 81, clef.TrebleClef),
    ("CHOIR",    "Choir (counter-subject)",        52, clef.TrebleClef),
    ("BELL",     "Bell / Glock",                    9, clef.TrebleClef),
    ("STRINGS",  "Chords (pad)",                   50, clef.TrebleClef),
    ("GUITAR",   "Guitar (offbeat)",               27, clef.TrebleClef),
    ("POWER",    "Guitar (distorted)",             30, clef.BassClef),
    ("LOWBRASS", "Low brass",                      58, clef.BassClef),
    ("ARP",      "Arp engine",                     11, clef.TrebleClef),
    ("BASS",     "Bass",                           38, clef.BassClef),
    ("SUB",      "Sub bass",                       87, clef.BassClef),
    ("DRUMS",    "Drums",                           0, clef.PercussionClef),
]

DRUM_MIDI = {"K": 36, "S": 38, "H": 42, "O": 46, "C": 49, "R": 51,
             "T": 47, "F": 41, "Z": 38}

TEMPO_AT = {1: S.BPM}
# Bb major and G minor share two flats; B major at m.97; C major at m.193
KEY_AT = {1: -2, 97: 5, 193: 0}

MARKS = {r * S.RLEN + 1: f"R{r} {S.OUTCOME[r]} - {S.LABEL[r]}"
         for r in range(S.ROUNDS)}
TEXT_AT = {
    1: "the last encounter",
    17: "A retaliates - subject inverted",
    33: "cooperation holds",
    65: "canon at eight bars",
    97: "up a semitone",
    145: "stretto - one bar apart",
    161: "the shadow is zero",
    177: "backward induction: defect",
    193: "and yet - cooperate",
}


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
    sc.metadata.title = S.TITLE
    sc.metadata.subtitle = "a last boss on Hopes and Dreams"
    sc.metadata.composer = "original composition; quotes Toby Fox"

    for pkey, pname, prog, clef_cls in PARTS:
        part = stream.Part(id=pname)
        part.partName = part.partAbbreviation = pname
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
        dyn_map = dict(S.dyn_changes(pkey))

        for i, raw in enumerate(S.PARTS[pkey]):
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

            src = S.DRUM_LIB[raw] if pkey == "DRUMS" else raw
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
            if m == S.N:
                meas.rightBarline = bar.Barline("final")
            part.append(meas)

        for a, b, direction in S.LEAD_HAIRPINS:
            s0, s1 = first_note.get(a), last_note.get(b)
            if s0 is None or s1 is None or s0 is s1:
                continue
            w = dynamics.Crescendo() if direction == "<" else dynamics.Diminuendo()
            w.addSpannedElements([s0, s1])
            part.insert(0, w)

        sc.insert(0, part)
    return sc


if __name__ == "__main__":
    mid = sys.argv[1] if len(sys.argv) > 1 else "../score/shadow-of-the-future.mid"
    xml = sys.argv[2] if len(sys.argv) > 2 else "../score/shadow-of-the-future.musicxml"
    sc = build()
    sc.write("midi", fp=mid)
    print("wrote", mid)
    sc.write("musicxml", fp=xml)
    print("wrote", xml)
