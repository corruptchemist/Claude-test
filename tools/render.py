"""Render ZERO-SUM as a readable score page."""

import html
from fractions import Fraction as F
import zerosum2 as Z
from zerosum import bar_len, dur_of, drums

EMPTY_CELL = '<span class="r">·</span>'

DUR_NAME = {"1": "whole", "2": "half", "4": "qtr", "8": "8th", "16": "16th",
            "32": "32nd", "64": "64th"}

MARKS = {
    1:   ("bass alone", "s"),
    9:   ("α in augmentation", "a"),
    14:  ("Petrushka polychord", "s"),
    17:  ("metric modulation ♪=♩", "s"),
    25:  ("boss theme — melody enters", "s"),
    57:  ("0.382 point — false peak", "s"),
    81:  ("bass removed", "s"),
    93:  ("GOLDEN SECTION — the drop", "g"),
    105: ("truck-driver lift → G♭", "s"),
    113: ("collapse", "s"),
    129: ("break — subito p", "s"),
    131: ("α + β simultaneously", "a"),
    139: ("minor-3rd cycle D–F–A♭–B", "s"),
    143: ("D MAJOR — A♭ becomes G♯", "g"),
    147: ("upward rush", "s"),
    149: ("final chord", "g"),
}


def split_beats(bar, beats):
    """Bucket tokens by the beat their onset falls in."""
    cells = [[] for _ in range(beats)]
    pos = F(0)
    for tok in bar.split():
        b = min(int(pos), beats - 1)
        cells[b].append(tok)
        pos += dur_of(tok.rstrip("~").split("/")[1])
    return cells


def fmt_tok(tok):
    tie = tok.endswith("~")
    head, d = tok.rstrip("~").split("/")
    dots = ""
    while d.endswith("."):
        dots += "."
        d = d[:-1]
    cls = "n"
    if head == "R":
        cls = "r"
        txt = "—"
    else:
        parts = []
        for p in head.split("+"):
            pc = p.rstrip("0123456789")
            k = ""
            if pc in ("Ab", "G#"):
                k = " sig"          # the note the whole piece is about
            elif pc in ("C#", "Db"):
                k = " lt"           # the withheld leading tone
            parts.append(f'<i class="p{k}">{html.escape(p)}</i>')
        txt = "+".join(parts)
    sup = f'<b>{DUR_NAME[d]}{dots}</b>'
    return f'<span class="{cls}">{txt}{sup}{"‿" if tie else ""}</span>'


DRUM_GLOSS = {"K": "kick", "S": "snare", "H": "hat", "O": "open hat", "C": "crash",
              "R": "ride", "T": "tom", "Z": "roll", "X": "choke"}


def fmt_drum_tok(tok):
    head, d = tok.rstrip("~").split("/")
    dots = ""
    while d.endswith("."):
        dots += "."
        d = d[:-1]
    if head == "R":
        return f'<span class="r">—<b>{DUR_NAME[d]}{dots}</b></span>'
    names = "+".join(DRUM_GLOSS.get(c, c) for c in head)
    return f'<span class="n"><i class="p">{names}</i><b>{DUR_NAME[d]}{dots}</b></span>'


PARTS = [
    ("LEAD", "Lead", "Trumpet in B♭ / 25% pulse lead", "melody"),
    ("COUNTER", "Counter", "Violin I / saw lead", "unison &amp; octave double, countermelody"),
    ("WINDS", "Sustain", "Horns + high strings", "pads, the H&amp;D lead timbre"),
    ("STABS", "Stabs", "Harpsichord + Horns, close position C4–C5", "offbeat chords"),
    ("KEYS", "Keys", "Piano", "ostinato doubling, 16th bed, arpeggios"),
    ("BASS", "Bass", "Electric bass + cello/contrabass 8vb", "the ostinato"),
    ("DRUMS", "Drums", "Rock kit", "kick locked to the ostinato's accents"),
]


def render_section(s):
    beats = 6 if s["meter"] == "6/4" else 4
    n = Z.SECTION_BARS[s["tag"]]
    start = s["start"]
    out = [f'<section class="sec" id="sec-{s["tag"]}">']
    out.append(f'''<div class="sec-head">
      <div class="sec-id"><span class="rn">{s["tag"]}</span><h2>{html.escape(s["name"])}</h2></div>
      <dl class="sec-meta">
        <div><dt>mm.</dt><dd>{start}–{start+n-1}</dd></div>
        <div><dt>Meter</dt><dd>{s["meter"]}</dd></div>
        <div><dt>Tempo</dt><dd>♩={s["bpm"]}</dd></div>
        <div><dt>Key</dt><dd>{s["key"]}</dd></div>
        <div><dt>Mode</dt><dd>{s["mode"]}</dd></div>
      </dl></div>''')

    if s["chords"]:
        out.append('<div class="scroll"><table class="grid"><thead><tr><th>m.</th>')
        out.append("".join(f"<th>{start+i}</th>" for i in range(n)))
        out.append('</tr></thead><tbody><tr><th>chord</th>')
        out.append("".join(f'<td>{html.escape(c)}</td>' for c in s["chords"]))
        out.append("</tr></tbody></table></div>")

    for key, label, inst, role in PARTS:
        bars = s["parts"][key]
        out.append(f'''<div class="part">
          <div class="part-head"><h3>{label}</h3>
            <p class="inst">{inst}</p><p class="role">{role}</p></div>
          <div class="scroll"><table class="score"><thead><tr><th class="mn">m.</th>''')
        out.append("".join(f'<th>{i+1}</th>' for i in range(beats)))
        out.append("</tr></thead><tbody>")
        for i, bar in enumerate(bars):
            m = start + i
            real = drums(bar) if key == "DRUMS" else bar
            cells = split_beats(real, beats)
            mk = MARKS.get(m)
            cls = f' class="mk-{mk[1]}"' if mk else ""
            out.append(f'<tr{cls}><th class="mn">{m}</th>')
            for c in cells:
                inner = " ".join((fmt_drum_tok if key == "DRUMS" else fmt_tok)(t) for t in c)
                out.append("<td>" + (inner or EMPTY_CELL) + "</td>")
            out.append("</tr>")
            if mk:
                out.append(f'<tr class="note-row"><td colspan="{beats+1}">'
                           f'<span class="flag flag-{mk[1]}">m.{m}</span> {html.escape(mk[0])}</td></tr>')
        out.append("</tbody></table></div></div>")
    out.append("</section>")
    return "\n".join(out)


FORM = [
    ("I", "Opening Bid", 16, "Heavy bassline alone. Octatonic dissonance stacked above a D pedal. 6/4 — no downbeat grid."),
    ("II", "The Tell", 8, "Metric modulation, not accelerando. Ostinato alone, layers added four bars at a time."),
    ("III", "Opening Move", 32, "The boss theme. i–♭VII–♭VI–v, all minor. α at speed."),
    ("IV", "Defect", 24, "Phrygian. Bass oscillates D–E♭, a bare semitone. The false peak."),
    ("V", "The Payoff Matrix", 32, "F major. Ascending ii7–I6–IV–V, tonic never in root position. The A♭ vanishes."),
    ("VI", "Mixed Strategy", 18, "Chromatic collapse, then the octatonic minor-third cycle. Whole-tone crisis."),
    ("VII", "Nash Equilibrium", 20, "α and β at once, then D major. The A♭ returns as G♯."),
]


def build():
    secs = "\n".join(render_section(s) for s in Z.SECTIONS)

    form_rows = []
    at = 1
    for tag, name, n, desc in FORM:
        form_rows.append(f'''<tr><th>{tag}</th><td class="fname">{name}</td>
          <td class="fbar">{at}–{at+n-1}</td><td class="fn">{n}</td>
          <td>{desc}</td></tr>''')
        at += n
    form_table = "\n".join(form_rows)

    total = 150
    bars_html = []
    at = 1
    for tag, name, n, _ in FORM:
        pct = n / total * 100
        bars_html.append(f'<a class="fseg f-{tag}" style="flex:{n}" href="#sec-{tag}">'
                         f'<span class="fseg-rn">{tag}</span>'
                         f'<span class="fseg-nm">{html.escape(name)}</span></a>')
        at += n
    form_map = "".join(bars_html)

    return TEMPLATE.replace("{{FORM_MAP}}", form_map) \
                   .replace("{{FORM_TABLE}}", form_table) \
                   .replace("{{SECTIONS}}", secs)


TEMPLATE = r"""<title>Zero-Sum</title>
<style>
:root{
  --paper:#F6F4F0; --panel:#FFFFFF; --panel2:#FAF9F6;
  --ink:#171A21; --muted:#666E7C; --faint:#8B93A0;
  --rule:#DFDBD4; --rule2:#EDEAE4;
  --accent:#C10B6B; --accent-bg:#FBE9F2;
  --struct:#0F7B84; --struct-bg:#E4F2F3;
  --gold:#8A5D0C; --gold-bg:#F7EEDC;
  --display:Georgia,"Iowan Old Style","Palatino Linotype",Palatino,"Times New Roman",serif;
  --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --paper:#0F1218; --panel:#161A22; --panel2:#12161D;
  --ink:#E9E7E2; --muted:#98A0AE; --faint:#727A88;
  --rule:#252A34; --rule2:#1D222B;
  --accent:#FF6BB0; --accent-bg:#38102A;
  --struct:#4FD0D9; --struct-bg:#0B2D31;
  --gold:#D8A445; --gold-bg:#332711;
}}
:root[data-theme="dark"]{
  --paper:#0F1218; --panel:#161A22; --panel2:#12161D;
  --ink:#E9E7E2; --muted:#98A0AE; --faint:#727A88;
  --rule:#252A34; --rule2:#1D222B;
  --accent:#FF6BB0; --accent-bg:#38102A;
  --struct:#4FD0D9; --struct-bg:#0B2D31;
  --gold:#D8A445; --gold-bg:#332711;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:var(--display);font-size:17px;line-height:1.6;
  -webkit-text-size-adjust:100%}
.wrap{max-width:1180px;margin:0 auto;padding:0 24px}
.prose{max-width:67ch}
h1,h2,h3,h4{text-wrap:balance;margin:0}
a{color:var(--accent)}

/* ---------- masthead ---------- */
header.top{border-bottom:1px solid var(--rule);padding:64px 0 40px;margin-bottom:48px}
.eyebrow{font-family:var(--sans);font-size:11px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--struct);font-weight:600;margin:0 0 20px}
h1{font-size:clamp(56px,12vw,124px);line-height:.86;letter-spacing:-.035em;
  font-weight:400;margin:0 0 4px}
h1 .zs{display:block}
.sub{font-family:var(--sans);font-size:13px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted);margin:18px 0 0}
.facts{display:flex;flex-wrap:wrap;gap:0;margin:36px 0 0;
  border-top:1px solid var(--rule)}
.facts div{flex:1 1 150px;padding:16px 20px 14px;border-right:1px solid var(--rule2)}
.facts div:last-child{border-right:0}
.facts dt{font-family:var(--sans);font-size:10px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--faint);margin:0 0 5px}
.facts dd{margin:0;font-size:19px;font-variant-numeric:tabular-nums}

/* ---------- prose blocks ---------- */
.block{margin:0 0 56px}
.block > h2{font-size:13px;font-family:var(--sans);letter-spacing:.14em;
  text-transform:uppercase;color:var(--struct);font-weight:600;
  padding-bottom:10px;border-bottom:1px solid var(--rule);margin-bottom:24px}
p{margin:0 0 18px}
.lede{font-size:21px;line-height:1.5}
strong{font-weight:700}
em.pitch{font-style:normal;color:var(--accent);font-weight:700;
  font-family:var(--mono);font-size:.94em}

/* ---------- motif cards ---------- */
.motifs{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(290px,1fr))}
.motif{background:var(--panel);border:1px solid var(--rule);padding:20px 22px}
.motif h3{font-size:15px;font-family:var(--sans);letter-spacing:.06em;
  text-transform:uppercase;margin:0 0 3px}
.motif .gk{font-size:26px;font-family:var(--display);color:var(--accent);
  float:right;line-height:1;margin-top:-2px}
.motif .when{font-family:var(--sans);font-size:11px;color:var(--faint);
  letter-spacing:.1em;text-transform:uppercase;margin:0 0 14px}
.notes{font-family:var(--mono);font-size:14px;letter-spacing:.02em;
  margin:0 0 12px;line-height:1.9}
.notes .sig{color:var(--accent);font-weight:700;background:var(--accent-bg);
  padding:1px 4px;border-radius:2px}
.notes .new{color:var(--struct);font-weight:700}
.motif p.g{font-size:14.5px;color:var(--muted);margin:0;line-height:1.55}
.iv{font-family:var(--mono);font-size:12px;color:var(--faint);margin:0 0 10px}

/* ---------- form map ---------- */
.fmap{display:flex;width:100%;height:74px;border:1px solid var(--rule);
  overflow:hidden;margin:0 0 20px}
.fseg{display:flex;flex-direction:column;justify-content:center;gap:3px;
  padding:0 10px;text-decoration:none;color:var(--ink);
  border-right:1px solid var(--rule);background:var(--panel);
  transition:background .15s;min-width:0}
.fseg:last-child{border-right:0}
.fseg:hover,.fseg:focus-visible{background:var(--struct-bg);outline:none}
.fseg-rn{font-family:var(--sans);font-size:10px;letter-spacing:.14em;
  color:var(--struct);font-weight:700}
.fseg-nm{font-size:12.5px;line-height:1.2;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap;color:var(--muted)}
.f-V{background:var(--gold-bg)}
.f-VII{background:var(--accent-bg)}

/* ---------- tables ---------- */
.scroll{overflow-x:auto;border:1px solid var(--rule);background:var(--panel)}
table{border-collapse:collapse;width:100%;font-family:var(--mono)}
th,td{text-align:left;vertical-align:top}
table.form{font-family:var(--display);font-size:15px}
table.form th,table.form td{padding:9px 12px;border-bottom:1px solid var(--rule2)}
table.form thead th{font-family:var(--sans);font-size:10px;letter-spacing:.13em;
  text-transform:uppercase;color:var(--faint);font-weight:600}
table.form tbody th{font-family:var(--sans);font-weight:700;color:var(--struct);
  font-size:12px;letter-spacing:.08em;width:44px}
.fname{font-weight:600;white-space:nowrap}
.fbar,.fn{font-family:var(--mono);font-size:13px;color:var(--muted);
  font-variant-numeric:tabular-nums;white-space:nowrap}

table.inst{font-family:var(--display);font-size:15px}
table.inst th,table.inst td{padding:9px 12px;border-bottom:1px solid var(--rule2)}
table.inst thead th{font-family:var(--sans);font-size:10px;letter-spacing:.13em;
  text-transform:uppercase;color:var(--faint);font-weight:600}
table.inst td.rg{font-family:var(--mono);font-size:13px;color:var(--muted);white-space:nowrap}

/* ---------- the score ---------- */
.sec{margin:0 0 12px;padding-top:8px;scroll-margin-top:44px}
.sec-head{position:sticky;top:41px;z-index:10;background:var(--paper);
  border-bottom:2px solid var(--ink);padding:14px 0 10px;margin-bottom:18px}
.sec-id{display:flex;align-items:baseline;gap:12px}
.rn{font-family:var(--sans);font-size:12px;font-weight:700;letter-spacing:.12em;
  color:var(--accent)}
.sec-head h2{font-size:26px;letter-spacing:-.01em;font-weight:400}
.sec-meta{display:flex;flex-wrap:wrap;gap:0 26px;margin:8px 0 0}
.sec-meta div{display:flex;gap:7px;align-items:baseline}
.sec-meta dt{font-family:var(--sans);font-size:10px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--faint)}
.sec-meta dd{margin:0;font-family:var(--mono);font-size:12.5px;color:var(--muted)}

.part{margin:0 0 20px}
.part-head{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin:0 0 7px}
.part-head h3{font-family:var(--sans);font-size:12px;font-weight:700;
  letter-spacing:.13em;text-transform:uppercase}
.inst{font-size:13.5px;color:var(--muted);margin:0}
.role{font-size:12.5px;color:var(--faint);margin:0;font-style:italic}

table.grid{font-size:12px}
table.grid th,table.grid td{padding:6px 9px;border-right:1px solid var(--rule2);
  white-space:nowrap}
table.grid thead th{color:var(--faint);font-weight:400;font-size:11px;
  border-bottom:1px solid var(--rule);font-variant-numeric:tabular-nums}
table.grid tbody th{color:var(--faint);font-weight:400;font-size:10px;
  text-transform:uppercase;letter-spacing:.1em;font-family:var(--sans)}
table.grid tbody td{color:var(--struct);font-weight:700}

table.score{font-size:12px}
table.score th,table.score td{padding:5px 9px;border-bottom:1px solid var(--rule2);
  border-right:1px solid var(--rule2)}
table.score thead th{background:var(--panel2);
  color:var(--faint);font-weight:400;font-size:10px;letter-spacing:.1em;
  border-bottom:1px solid var(--rule)}
table.score th.mn{width:46px;color:var(--faint);font-weight:400;
  font-variant-numeric:tabular-nums;text-align:right;
  background:var(--panel2);white-space:nowrap}
table.score td{min-width:118px}
table.score span{display:inline-block;margin:0 7px 0 0;white-space:nowrap}
table.score i.p{font-style:normal;color:var(--ink)}
table.score i.sig{color:var(--accent);font-weight:700}
table.score i.lt{color:var(--gold);font-weight:700}
table.score span.r i,table.score span.r{color:var(--faint)}
table.score b{font-weight:400;font-size:9.5px;color:var(--faint);
  margin-left:2px;letter-spacing:.02em}
tr.mk-g th.mn,tr.mk-g td{background:var(--accent-bg)}
tr.mk-a th.mn,tr.mk-a td{background:var(--struct-bg)}
tr.mk-s th.mn{color:var(--struct);font-weight:700}
tr.note-row td{background:var(--panel2);font-family:var(--sans);font-size:11px;
  color:var(--muted);letter-spacing:.02em;border-right:0;padding:5px 9px}
.flag{font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  font-size:10px;margin-right:8px;color:var(--struct)}
.flag-g{color:var(--accent)}

/* ---------- legend ---------- */
.legend{display:grid;gap:10px 28px;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));
  background:var(--panel);border:1px solid var(--rule);padding:20px 22px}
.legend div{font-size:14px;display:flex;gap:9px;align-items:baseline}
.legend code{font-family:var(--mono);font-size:12.5px;color:var(--struct);
  white-space:nowrap;font-weight:700}
.legend span{color:var(--muted)}

nav.jump{position:sticky;top:0;z-index:30;background:var(--paper);
  border-bottom:1px solid var(--rule);padding:11px 0;margin:0 0 34px}
nav.jump ul{list-style:none;display:flex;flex-wrap:wrap;gap:0 22px;margin:0;padding:0}
nav.jump a{font-family:var(--sans);font-size:11px;letter-spacing:.1em;
  text-transform:uppercase;text-decoration:none;color:var(--muted);font-weight:600}
nav.jump a:hover,nav.jump a:focus-visible{color:var(--accent)}
nav.jump b{color:var(--struct);margin-right:5px}

footer{border-top:1px solid var(--rule);margin-top:56px;padding:30px 0 70px;
  font-size:14px;color:var(--muted)}
ul.tight{margin:0 0 18px;padding-left:20px}
ul.tight li{margin:0 0 9px}
@media (max-width:640px){
  .facts div{flex:1 1 50%;border-bottom:1px solid var(--rule2)}
  .fseg-nm{display:none}
  header.top{padding:40px 0 28px}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>

<div class="wrap">

<header class="top">
  <p class="eyebrow">Original boss theme · complete note listing for engraving</p>
  <h1><span class="zs">ZERO-</span><span class="zs">SUM</span></h1>
  <p class="sub">150 measures · after Toby Fox</p>
  <dl class="facts">
    <div><dt>Length</dt><dd>150 mm. · 3:57</dd></div>
    <div><dt>Tempo</dt><dd>♩=92 → ♩=184</dd></div>
    <div><dt>Tonal plan</dt><dd>D minor → D major</dd></div>
    <div><dt>Parts</dt><dd>7</dd></div>
    <div><dt>Climax</dt><dd>m. 93</dd></div>
  </dl>
</header>

<div class="block prose">
  <p class="lede">The whole piece is an argument about one note: <em class="pitch">A♭</em>, the
  tritone above D. It is the note that poisons the opening bassline, the blue ♭5 that
  gives the boss theme its edge, the pitch that vanishes completely when hope arrives,
  and — respelled <em class="pitch">G♯</em> in the last four bars — the brightest tone in
  the final chord.</p>

  <p>Same pitch, four meanings. Nothing about it changes except what surrounds it. That
  is the Toby Fox move — take a fixed thing and let context rewrite what it means — applied
  to a single pitch class instead of a melody, and stretched across the whole form.</p>

  <p>Everything melodic grows from one cell, built with a seam so its halves can be
  deployed separately. Its three forms differ by almost nothing:</p>
</div>

<div class="block">
  <h2>The cell and its three faces</h2>
  <div class="motifs">
    <div class="motif">
      <span class="gk">α</span>
      <h3>Alpha · menace</h3>
      <p class="when">mm. 9–79, 131–142</p>
      <p class="notes">D · F · <span class="sig">A♭</span> · A &nbsp;‖&nbsp; A · G · F · E · D</p>
      <p class="iv">0 · 3 · 6 · 7 &nbsp;→&nbsp; tail falls</p>
      <p class="g">Minor third, then the tritone. The head climbs into the poison note;
      the tail collapses back down to the tonic.</p>
    </div>
    <div class="motif">
      <span class="gk">β</span>
      <h3>Beta · hope</h3>
      <p class="when">mm. 81–112</p>
      <p class="notes">F · A · C · D &nbsp;‖&nbsp; D · C · B♭ · A · G</p>
      <p class="iv">0 · 4 · 7 · 9 &nbsp;→&nbsp; tail falls</p>
      <p class="g">Same contour, same rhythm, major mode. The tritone is replaced by a
      major sixth and the A♭ is simply gone — F major does not contain it.</p>
    </div>
    <div class="motif">
      <span class="gk">ω</span>
      <h3>Omega · blaze</h3>
      <p class="when">mm. 143–150</p>
      <p class="notes">D · <span class="new">F♯</span> · <span class="sig">G♯</span> · A &nbsp;‖&nbsp; A · B · C♯ · D</p>
      <p class="iv">0 · 4 · 6 · 7 &nbsp;→&nbsp; tail <span class="new">RISES</span></p>
      <p class="g">One note changes from α — the third, F to F♯ — and the tail reverses
      direction. The A♭ never moves. It is now the ♯11 of D major.</p>
    </div>
  </div>
</div>

<div class="block prose">
  <p>Because the ending has to be earned rather than announced, four things are withheld
  across the whole piece and delivered only at the end: any <strong>D major triad</strong>,
  <strong>F♯ over a D root</strong>, the <strong>register above D7</strong>, and ω's
  <strong>rising tail</strong>. None of them occurs before m. 143.</p>

  <p>The A♭ is tracked in colour through every measure below, so you can watch it saturate
  the boss theme, disappear for the 25 bars of the Payoff Matrix, and come back
  transformed. The withheld leading tone C♯ is marked in <span style="color:var(--gold);font-weight:700">gold</span>.</p>
</div>

<div class="block">
  <h2>Form</h2>
  <div class="fmap">{{FORM_MAP}}</div>
  <div class="scroll"><table class="form">
    <thead><tr><th></th><th>Section</th><th>mm.</th><th>Bars</th><th>What happens</th></tr></thead>
    <tbody>{{FORM_TABLE}}</tbody>
  </table></div>
</div>

<div class="block prose">
  <p><strong>Three structural decisions worth flagging before you read the notes.</strong></p>
  <ul class="tight">
    <li><strong>The intro is in 6/4, the rest is in 4/4.</strong> Six slow beats deny the
    ear a downbeat grid, so when 4/4 arrives at m. 17 it lands like a floor appearing.</li>
    <li><strong>m. 17 is a metric modulation, not an accelerando.</strong> The intro's
    eighth note becomes the boss theme's quarter — exactly 92 → 184. The new tempo is
    already sounding before it arrives, so it reads as inevitable rather than as an edit.</li>
    <li><strong>m. 93 is the golden section</strong> (150 × 0.618 = 92.7) and carries the
    largest event: the bass, absent for twelve bars, drops back in on the IV chord while
    the melody leaps an octave and the register ceiling opens. Everything before it is
    setup for that bar.</li>
  </ul>
</div>

<div class="block">
  <h2>Instrumentation</h2>
  <div class="scroll"><table class="inst">
    <thead><tr><th>Staff</th><th>Instrument</th><th>Range used</th><th>Function</th></tr></thead>
    <tbody>
      <tr><th>Lead</th><td>Trumpet in B♭, doubled piccolo above D6</td><td class="rg">D4–F♯7</td><td>Melody. The 25% pulse-wave analogue.</td></tr>
      <tr><th>Counter</th><td>Violin I, non vibrato</td><td class="rg">A2–G♭6</td><td>Unison and octave doubling, countermelody.</td></tr>
      <tr><th>Sustain</th><td>2 Horns in F + high strings</td><td class="rg">D3–A♭5</td><td>Pads. Carries the lead in section V.</td></tr>
      <tr><th>Stabs</th><td>Harpsichord + Horns, close position</td><td class="rg">F3–A♭5</td><td>Offbeat chords, C4–C5 only.</td></tr>
      <tr><th>Keys</th><td>Piano</td><td class="rg">D1–D7</td><td>Ostinato doubling, 16th bed, arpeggios.</td></tr>
      <tr><th>Bass</th><td>Electric bass + cello/contrabass 8vb</td><td class="rg">D1–B♭3</td><td>The ostinato. The engine.</td></tr>
      <tr><th>Drums</th><td>Rock kit</td><td class="rg">—</td><td>Kick locked to the ostinato's own accents.</td></tr>
    </tbody>
  </table></div>
</div>

<div class="block">
  <h2>How to read the tables</h2>
  <div class="legend">
    <div><code>D5</code><span>pitch and octave (middle C = C4)</span></div>
    <div><code>whole half qtr</code><span>note value</span></div>
    <div><code>8th 16th 32nd 64th</code><span>shorter values</span></div>
    <div><code>8th.</code><span>a trailing dot dots the value</span></div>
    <div><code>D4+F4+A4</code><span>notes sounding together</span></div>
    <div><code>—</code><span>rest of the stated value</span></div>
    <div><code>·</code><span>nothing begins on this beat</span></div>
    <div><code>‿</code><span>tied into the next note</span></div>
    <div><code style="color:var(--accent)">A♭ G♯</code><span>the signature pitch</span></div>
    <div><code style="color:var(--gold)">C♯ D♭</code><span>the withheld leading tone</span></div>
  </div>
  <div class="prose" style="margin-top:20px">
    <p>A note appears in the column of the beat it <em>starts</em> on. A long note simply
    occupies the beats after it — that is why later beats often read <code
    style="font-family:var(--mono)">·</code>. Every measure has been machine-checked to sum
    to exactly its meter.</p>
  </div>
</div>

<nav class="jump"><ul>
  <li><a href="#sec-I"><b>I</b>Opening Bid</a></li>
  <li><a href="#sec-II"><b>II</b>The Tell</a></li>
  <li><a href="#sec-III"><b>III</b>Opening Move</a></li>
  <li><a href="#sec-IV"><b>IV</b>Defect</a></li>
  <li><a href="#sec-V"><b>V</b>Payoff Matrix</a></li>
  <li><a href="#sec-VI"><b>VI</b>Mixed Strategy</a></li>
  <li><a href="#sec-VII"><b>VII</b>Nash Equilibrium</a></li>
</ul></nav>

{{SECTIONS}}

<div class="block prose" style="margin-top:56px">
  <h2 style="font-size:13px;font-family:var(--sans);letter-spacing:.14em;text-transform:uppercase;color:var(--struct);font-weight:600;padding-bottom:10px;border-bottom:1px solid var(--rule);margin-bottom:24px">Performance notes</h2>
  <ul class="tight">
    <li><strong>Dynamics.</strong> Chip sources have no dynamic envelope, so players
    over-shape by default. Mark long stretches <em>senza cresc.</em> and <em>poco vib.</em>
    and save hairpins for the 8-bar orchestration seams. The mechanical evenness is the
    aesthetic.</li>
    <li><strong>Section I bass.</strong> Staccatissimo with real silence after every note.
    The weight is in the attack transient and the hole behind it — a sustained low note is
    mud. Do not let the kick double the bass one-for-one; the gap between them is the groove.</li>
    <li><strong>The ostinato</strong> is 16 sixteenths grouped 6+6+4. Beat 3 is never
    struck — the note on 2&amp; sustains through it. Across each 4-bar unit only the first
    two attacks change pitch; attacks 3–7 are literally identical every bar.</li>
    <li><strong>Section V is strictly diatonic.</strong> mm. 80–104 contain no accidentals
    at all. If an A♭ or E♭ appears there, it is an engraving error — the one deliberate
    exception is the chromatic walk-up in the bass at m. 104, which sets up the modulation.</li>
    <li><strong>The final chord</strong> is D maj13(♯11), voiced
    <code style="font-family:var(--mono);font-size:13px">D1–D2–A2–D3–A3–D4–F♯4–A4–C♯5–E5–G♯5–D6–F♯6–A6</code>.
    Wide at the bottom, tight at the top; no interval smaller than a minor third anywhere,
    and the tritone G♯5–D6 sits high where it reads as glare rather than grind. Consonant
    skeleton (D, F♯, A) in brass at <em>fff</em>; colour tones (C♯, E, G♯) one dynamic
    step softer in strings and keys. Timpani take D and A only. Crescendo into a hard
    collective cutoff with a cymbal choke.</li>
  </ul>
</div>

<footer>
  <p>Every measure verified to sum exactly to its meter. Section V checked for
  accidentals; register ceilings and the four withheld elements checked against
  their promised measures.</p>
</footer>

</div>
"""

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "../score/zero-sum.html"
    with open(out, "w") as f:
        f.write(build())
    print("wrote", out)
