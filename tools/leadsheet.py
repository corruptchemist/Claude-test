"""Engrave the melody of a piece as a single-staff lead sheet.

    python3 leadsheet.py groundstate ../score/ground-state-melody

Writes <out>.musicxml and <out>.pdf.  The PDF is engraved in-process with
verovio, so no LilyPond or MuseScore install is needed.

The melody staff is whichever part the module names as its tune (LEAD), with
chord symbols over the top taken from the piece's own harmonic grid, its key
changes, and its rehearsal marks.
"""

import importlib
import io
import sys

from music21 import (stream, note, chord, meter, key, tempo, clef, harmony,
                     duration, expressions, bar, metadata)
from zerosum import dur_of

QUALITY = {"m": "m", "dim": "dim", "": ""}


def chord_figure(mod, name, measure):
    """The sounding chord symbol for a bar: root transposed into the key."""
    from music21 import pitch
    root = mod.ROOT[name]                       # e.g. "D3"
    k = mod.KEY_OF[measure]
    p = pitch.Pitch(root)
    if k:
        # music21 transposes to sharps by default; every key this piece visits
        # is a flat one, so a sharp-spelled root wants its flat enharmonic
        # (C# in Eb minor is really Db).
        p = p.transpose(k)
        if not mod.sharp_at(measure) and p.accidental and \
                p.accidental.name == "sharp":
            p = p.getEnharmonic()
    # test dim FIRST: "Bdim".endswith("m") is also True
    suffix = "dim" if name.endswith("dim") else ("m" if name.endswith("m") else "")
    return f"{p.name}{suffix}"


def parse_bar(s):
    for tok in s.split():
        head, d = tok.rstrip("~").split("/")
        du = duration.Duration(float(dur_of(d)))
        if head == "R":
            yield note.Rest(duration=du)
            continue
        names = head.split("+")
        n = note.Note(names[0]) if len(names) == 1 else chord.Chord(names)
        n.duration = du
        yield n


def build(mod, part_key="LEAD"):
    sc = stream.Score()
    sc.metadata = metadata.Metadata()
    sc.metadata.title = f"{mod.TITLE} — melody"
    sc.metadata.composer = "original composition; quotes Toby Fox"

    part = stream.Part(id="melody")
    part.partName = "Melody"
    bars = mod.PARTS[part_key]
    keymap = getattr(mod, "KEY_AT_XML", None) or {}
    prev_fig = None

    for i, raw in enumerate(bars):
        m = i + 1
        meas = stream.Measure(number=m)
        if m == 1:
            meas.clef = clef.TrebleClef()
            meas.timeSignature = meter.TimeSignature("4/4")
            meas.insert(0, tempo.MetronomeMark(
                number=mod.BPM, referent=note.Note(type="quarter")))
        if m in keymap:
            meas.insert(0, key.KeySignature(keymap[m]))
        if m in getattr(mod, "LABEL", {}):
            # section name only; the full labels ran off both page edges
            short = mod.LABEL[m].split(" - ")[0].upper()
            meas.insert(0, expressions.RehearsalMark(short))
        fig = chord_figure(mod, mod.CHORDS[i], m)
        if fig != prev_fig:
            cs = harmony.ChordSymbol(fig)
            cs.writeAsChord = False
            meas.insert(0, cs)
            prev_fig = fig
        for obj in parse_bar(raw):
            meas.append(obj)
        if m == len(bars):
            meas.rightBarline = bar.Barline("final")
        part.append(meas)

    sc.insert(0, part)
    return sc


# Verovio sets chord-symbol accidentals and the tempo note in SMuFL private-use
# codepoints in the Leipzig font.  cairosvg has no Leipzig, so they rasterise as
# empty boxes.  DejaVu Sans (which is installed) carries the real Unicode music
# characters, so swap codepoint and font before handing the SVG over.
SMUFL_TEXT = {
    "\uEA64": "\u266D",   # csymAccidentalFlat   -> MUSIC FLAT SIGN
    "\uEA66": "\u266F",   # csymAccidentalSharp  -> MUSIC SHARP SIGN
    "\uEA65": "\u266E",   # csymAccidentalNatural
    "\uE260": "\u266D",   # accidentalFlat
    "\uE261": "\u266E",   # accidentalNatural
    "\uE262": "\u266F",   # accidentalSharp
    "\uECA5": "\u2669",   # metNoteQuarterUp     -> QUARTER NOTE
    "\uECA3": "\u266A",   # metNote8thUp         -> EIGHTH NOTE
    "\uECA2": "\u2669",   # metNoteHalfUp
}


def fix_glyphs(svg):
    for a, b in SMUFL_TEXT.items():
        svg = svg.replace(a, b)
    svg = svg.replace('font-family="Leipzig"', 'font-family="DejaVu Sans"')
    # anything else left in the private use area would rasterise as a box
    return "".join(c for c in svg if not 0xE000 <= ord(c) <= 0xF8FF)


def engrave(xml_path, pdf_path):
    import verovio
    import cairosvg
    from pypdf import PdfWriter

    tk = verovio.toolkit()
    tk.setOptions({
        "pageWidth": 2100, "pageHeight": 2970,     # A4 in 1/10 mm
        "scale": 38,
        "adjustPageHeight": False,
        "footer": "none", "header": "auto",
        "spacingStaff": 10, "spacingSystem": 8,
        "lyricSize": 4.5,
    })
    if not tk.loadFile(xml_path):
        raise SystemExit(f"verovio could not load {xml_path}")
    pages = tk.getPageCount()
    writer = PdfWriter()
    for i in range(1, pages + 1):
        svg = fix_glyphs(tk.renderToSVG(i))
        buf = io.BytesIO()
        cairosvg.svg2pdf(bytestring=svg.encode("utf-8"), write_to=buf)
        buf.seek(0)
        writer.append(buf)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return pages


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "groundstate"
    out = sys.argv[2] if len(sys.argv) > 2 else f"../score/{name}-melody"
    mod = importlib.import_module(name)
    sc = build(mod)
    sc.write("musicxml", fp=f"{out}.musicxml")
    print("wrote", f"{out}.musicxml")
    pages = engrave(f"{out}.musicxml", f"{out}.pdf")
    print(f"wrote {out}.pdf  ({pages} pages)")
