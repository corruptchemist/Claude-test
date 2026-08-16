"""THREE FIGHTS -- bass, accompaniment, assembly, verification."""

from fractions import Fraction as F
from zerosum import bar_len
from zerosum2 import shift, oct_down, rests
import threefights as T

N = T.N   # 216

# ===========================================================================
# DRUMS
# ===========================================================================
DRUM_LIB = {
    "tacet":    "R/1",
    "fin_a":    "KC/8 H/8 S/16 S/16 H/8 K/8 S/8 H/16 K/16 S/8",
    "fin_b":    "K/8 H/16 K/16 S/8 H/8 K/8 S/16 S/16 S/8 H/8",
    "fin_c":    "KC/16 K/16 H/8 S/8 H/8 K/16 H/16 S/8 S/16 S/16 H/8",
    "fin_fill": "S/16 S/16 T/16 T/16 T/16 T/16 F/16 F/16 S/8 T/8 F/8 KC/8",
    "fin_half": "K/4 S/4 K/8 K/8 S/4",
    "dbg_a":    "KH/8 O/8 KS/8 O/8 KH/8 O/8 KS/8 O/8",
    "dbg_b":    "KH/8 O/8 KS/8 O/16 H/16 KH/8 O/8 KS/16 K/16 O/8",
    "dbg_ride": "KR/8 R/8 SR/8 R/8 KR/8 R/8 SR/8 R/8",
    "dbg_fill": "S/16 S/16 S/16 T/16 T/8 F/8 S/16 T/16 F/16 S/16 KC/8 O/8",
    "dbg_thin": "KH/8 H/8 SH/8 H/8 KH/8 H/8 SH/8 H/8",
    # under the bass break the kit gets out of the way -- rim/hat only
    "brk":      "H/8 H/8 SH/8 H/8 H/8 H/8 SH/8 H/8",
    "brk2":     "H/8 H/8 SH/8 H/16 H/16 H/8 H/8 SH/8 H/8",
    "meg_a":    "K/8 H/8 SH/16 K/16 H/8 K/16 H/16 H/8 SK/8 H/8",
    "meg_b":    "K/8 H/8 SH/8 K/16 K/16 H/8 K/16 H/16 SK/8 O/8",
    "meg_c":    "KC/8 H/8 SH/16 K/16 H/8 K/8 H/8 SK/16 K/16 O/8",
    "meg_fill": "S/16 S/16 S/16 S/16 T/16 T/16 T/16 T/16 F/16 F/16 S/16 S/16 KC/8 S/8",
    "roll":     "Z/2 Z/2",
    "crash":    "KC/1",
    "final":    "KCZ/1",
}

# ===========================================================================
# BASS  --  the part that got the biggest promotion in this rebuild.
# ===========================================================================
ROOTS = {
    "Fm":  ("F1", "F2", "C2", "Ab1", "E1"),   "Db": ("Db2", "Db3", "Ab2", "F2", "C2"),
    "Eb":  ("Eb2", "Eb3", "Bb2", "G2", "D2"), "C7": ("C2", "C3", "G2", "E2", "B1"),
    "Cm":  ("C2", "C3", "G2", "Eb2", "B1"),   "Ab": ("Ab1", "Ab2", "Eb2", "C2", "G1"),
    "Em7": ("E1", "E2", "B1", "G1", "D#1"),   "A":  ("A1", "A2", "E2", "C#2", "G#1"),
    "F#7": ("F#1", "F#2", "C#2", "A#1", "F1"), "G":  ("G1", "G2", "D2", "B1", "F#1"),
    "B7":  ("B1", "B2", "F#2", "D#2", "A#1"), "C":  ("C2", "C3", "G2", "E2", "B1"),
    "Dm":  ("D2", "D3", "A2", "F2", "C#2"),   "Bb": ("Bb1", "Bb2", "F2", "D2", "A1"),
    "A5":  ("A1", "A2", "E2", "C#2", "G#1"),  "Gm": ("G1", "G2", "D2", "Bb1", "F#1"),
    "F":   ("F1", "F2", "C2", "A1", "E1"),
    "Edim7": ("E1", "E2", "Bb1", "G1", "D#1"),
    "A#dim7": ("A#1", "A#2", "E2", "C#2", "A1"),
    "Ebdim7": ("Eb2", "Eb3", "A2", "Gb2", "D2"),
}


def bp(chord, kind, nxt=None):
    r1, r2, fifth, third, appr = ROOTS[chord]
    nx = ROOTS[nxt][4] if nxt else appr
    return {
        "hit":  f"{r1}/4 R/8 {r1}/8 {r2}/4 R/8 {nx}/8",
        "a":    f"{r1}/8 {r2}/8 {fifth}/8 {r2}/8 {r1}/8 {r2}/8 {third}/8 {fifth}/8",
        "b":    f"{r1}/8 {r1}/16 {r2}/16 {fifth}/8 {r2}/8 {r1}/8 {third}/8 {fifth}/16 {r2}/16 {nx}/8",
        "c":    f"{r1}/16 {r1}/16 {r2}/8 {fifth}/16 {third}/16 {r2}/8 {r1}/8 {r2}/8 {fifth}/8 {nx}/8",
        # a real bass fill, not just a walk
        "fill": f"{r1}/16 {third}/16 {fifth}/16 {r2}/16 {fifth}/16 {third}/16 {r1}/16 {third}/16 "
                f"{fifth}/8 {r2}/8 {fifth}/16 {third}/16 {r1}/16 {nx}/16",
        "walk": f"{r1}/8 {third}/8 {fifth}/8 {r2}/8 {fifth}/8 {third}/8 {r1}/8 {nx}/8",
    }[kind]


# Q4 -- the Death by Glamour cell.  Two densities, exactly as the source does:
# an 8-attack intro cell and a busier 10-attack cell for the second half.
DBG = {
    "Em7_a": "E1/8 R/16 E1/16 G1/8 R/16 E1/16 D2/8. C#2/16 E1/8 R/8",
    "Em7_b": "E1/8 E1/16 E2/16 G1/8 E1/16 G1/16 D2/16 C#2/16 D2/16 C#2/16 D2/8 A1/8",
    "A_a":   "A1/8 R/16 A1/16 C#2/8 R/16 A1/16 G2/8. F#2/16 A1/8 R/8",
    "A_b":   "A1/8 A1/16 A2/16 C#2/8 A1/16 C#2/16 G2/16 F#2/16 G2/16 F#2/16 G2/8 E2/8",
    "G_a":   "G1/8 R/16 G1/16 B1/8 R/16 G1/16 F2/8. E2/16 G1/8 R/8",
    "G_b":   "G1/8 G1/16 G2/16 B1/8 G1/16 B1/16 F2/16 E2/16 F2/16 E2/16 D2/8 B1/8",
    "F#7_a": "F#1/8 R/16 F#1/16 A#1/8 R/16 F#1/16 E2/8. D#2/16 F#1/8 R/8",
    "F#7_b": "F#1/8 F#1/16 F#2/16 A#1/8 F#1/16 A#1/16 E2/16 D#2/16 E2/16 C#2/16 B1/8 F#1/8",
    "B7_a":  "B1/8 R/16 B1/16 D#2/8 R/16 B1/16 A2/8. G#2/16 B1/8 R/8",
    "B7_b":  "B1/16 B1/16 B2/8 D#2/16 F#2/16 A2/8 G#2/16 F#2/16 D#2/8 B1/16 A#1/16 B1/8",
    "C_a":   "C2/8 R/16 C2/16 E2/8 R/16 C2/16 Bb2/8. A2/16 C2/8 R/8",
    "C_b":   "C2/8 C2/16 C3/16 E2/8 C2/16 E2/16 Bb2/16 A2/16 Bb2/16 A2/16 G2/8 E2/8",
}

# THE BASS BREAK, mm.97-104.  Everything else drops to hat and rim; the bass
# plays the section on its own.  E Dorian throughout -- the C# is the point.
BASS_BREAK = [
    "E1/16 G1/16 A1/16 B1/16 D2/16 E2/16 D2/16 C#2/16 B1/16 A1/16 G1/16 E1/16 D1/8 E1/8",
    "E1/8 E2/16 D2/16 C#2/16 B1/16 A1/16 G1/16 E1/8 G1/8 A1/16 B1/16 C#2/16 D2/16",
    "E2/16 D2/16 C#2/16 A1/16 B1/8 G1/8 E1/16 F#1/16 G1/16 A1/16 B1/16 C#2/16 D2/16 E2/16",
    "F#2/16 E2/16 D2/16 C#2/16 B1/16 A1/16 G1/16 F#1/16 E1/4 B1/8 E2/8",
    "A1/16 C#2/16 E2/16 G2/16 F#2/16 E2/16 C#2/16 A1/16 E1/8 A1/8 C#2/8 E2/8",
    "G2/16 F#2/16 E2/16 D2/16 C#2/16 B1/16 A1/16 G1/16 F#1/8 A1/8 C#2/4",
    "E1/8 B1/8 E2/8 G2/8 D2/16 C#2/16 B1/16 A1/16 G1/8 E1/8",
    "E1/16 F#1/16 G1/16 A1/16 B1/16 C#2/16 D2/16 E2/16 D2/8. C#2/16 E1/4",
]

# Q1 in the bass -- the MEGALOVANIA riff, an octave down from the lead register
CHORDS = T.CH_I + T.CH_BR_A + T.CH_II + T.CH_BR_B + T.CH_III + T.CH_IV
LEAD = T.LEAD_I + T.LEAD_BR_A + T.LEAD_II + T.LEAD_BR_B + T.LEAD_III + T.LEAD_IV


def nxt(i):
    return CHORDS[i + 1] if i + 1 < N else CHORDS[i]


BASS = []
for i, c in enumerate(CHORDS):
    m = i + 1
    if m <= 8:                                    # Finale intro -- heavy hits
        BASS.append(bp(c, "hit", nxt(i)))
    elif m <= 56:                                 # I. FLOWER
        BASS.append(bp(c, "fill" if m % 8 == 0 else
                       ("c" if m % 4 == 0 else ("b" if m % 2 == 0 else "a")), nxt(i)))
    elif m <= 64:                                 # bridge A
        BASS.append(bp(c, "walk", nxt(i)) if m <= 62 else bp(c, "a", nxt(i)))
    elif m <= 72:                                 # II -- bass ALONE, the opening
        BASS.append(DBG["Em7_a"] if m % 2 else DBG["Em7_b"])
    elif m <= 96:
        BASS.append(DBG[f"{c}_a"] if m <= 88 else DBG[f"{c}_b"])
    elif m <= 104:                                # THE BASS BREAK
        BASS.append(BASS_BREAK[m - 97])
    elif m <= 120:
        BASS.append(DBG[f"{c}_b"])
    elif m <= 128:                                # bridge B -- E -> Eb -> D
        r1, r2, fifth, third, _ = ROOTS[c]
        BASS.append(f"{r1}/8 {r2}/8 {fifth}/8 {r2}/8 {third}/8 {fifth}/8 {r2}/8 {r1}/8")
    else:                                         # III + IV -- Q1, the riff
        BASS.append(T.q1(c, -12))
BASS[-1] = "D1+D2+A2+D3/1"
BASS[-2] = ("D1/16 E1/16 F1/16 G1/16 A1/16 Bb1/16 C2/16 D2/16 "
            "E2/16 F2/16 G2/16 A2/16 Bb2/16 C3/16 D3/8")

# ===========================================================================
# CHORD VOICINGS
# ===========================================================================
VOICE = {
    "Fm": "F4+Ab4+C5", "Db": "Ab4+Db5+F5", "Eb": "G4+Bb4+Eb5", "C7": "C4+E4+Bb4",
    "Cm": "C4+Eb4+G4", "Ab": "Ab4+C5+Eb5",
    "Em7": "G4+B4+D5", "A": "A4+C#5+E5", "F#7": "A#4+C#5+E5", "G": "G4+B4+D5",
    "B7": "B4+D#5+A4", "C": "C4+E4+G4",
    "Dm": "D4+F4+A4", "Bb": "Bb3+D4+F4", "A5": "A3+C#4+E4", "Gm": "G3+Bb3+D4",
    "F": "F3+A3+C4",
    "Edim7": "E4+G4+Bb4+Db5", "A#dim7": "E4+G4+A#4+C#5", "Ebdim7": "Eb4+Gb4+A4+C5",
}
PAD = {k: "+".join(v.split("+")[:2]) for k, v in VOICE.items()}


def stab(c, kind):
    v = VOICE[c]
    return {"off":  f"R/8 {v}/8 R/8 {v}/8 R/8 {v}/8 R/8 {v}/8",
            "ska":  f"R/8 {v}/16 {v}/16 R/8 {v}/8 R/8 {v}/16 {v}/16 R/8 {v}/8",
            "hold": f"{v}/1", "half": f"{v}/2 {v}/2",
            "quart": f"{v}/4 {v}/4 {v}/4 {v}/4"}[kind]


def arp(c, o=0):
    v = VOICE[c].split("+")
    seq = (v * 3)[:4]
    line = " ".join(f"{p}/16" for p in (seq + seq[::-1]) * 2)
    return shift(line, o) if o else line


STABS, SUSTAIN, KEYS, COUNTER = [], [], [], []
for i, c in enumerate(CHORDS):
    m = i + 1
    # ---- stabs: always two dynamic steps under the melody ----
    if m <= 8 or 65 <= m <= 72 or 97 <= m <= 104 or 129 <= m <= 136:
        STABS.append("R/1")                       # out of the way in every bare passage
    elif m <= 56:
        STABS.append(stab(c, "off" if m % 4 else "quart"))
    elif m <= 64:
        STABS.append(stab(c, "hold"))
    elif m <= 120:
        STABS.append(stab(c, "ska"))
    elif m <= 128:
        STABS.append(stab(c, "half"))
    else:
        STABS.append(stab(c, "off"))
    # ---- sustain ----
    if 65 <= m <= 104 or 129 <= m <= 152:
        SUSTAIN.append("R/1")
    else:
        SUSTAIN.append(f"{PAD[c]}/1")
    # ---- keys ----
    if m <= 8 or 65 <= m <= 72 or 97 <= m <= 104:
        KEYS.append("R/1")
    elif m <= 64:
        KEYS.append(arp(c, 12))
    elif m <= 128:
        KEYS.append(arp(c))
    else:
        KEYS.append(T.q1(c, 12))                  # Q1 doubled up an octave
    # ---- counter ----
    if m <= 16 or 57 <= m <= 88 or 97 <= m <= 104 or 121 <= m <= 160:
        COUNTER.append("R/1")
    elif 185 <= m <= 200:
        # the quodlibet's third strand: Q4's b7 -> 6 slur, now in D Dorian
        COUNTER.append("C5/8. B4/16 C5/8 D5/8 F5/8 D5/8 C5/8. B4/16")
    else:
        COUNTER.append(oct_down(LEAD[i]) if LEAD[i] != "R/1" else "R/1")
KEYS[-1] = "D4+F4+A4+D5+A5+D6/1"
COUNTER[-1] = "D4+A4+D5/1"

DRUMS = []
for i in range(N):
    m = i + 1
    if m <= 4:
        DRUMS.append("fin_half")
    elif m <= 56:
        DRUMS.append("fin_fill" if m % 8 == 0 else
                     ("fin_c" if m % 8 == 1 else ("fin_b" if m % 2 == 0 else "fin_a")))
    elif m <= 64:
        DRUMS.append("crash" if m == 57 else ("roll" if m >= 63 else "tacet"))
    elif m <= 72:
        DRUMS.append("tacet" if m <= 68 else "dbg_thin")
    elif m <= 96:
        DRUMS.append("dbg_fill" if m % 8 == 0 else ("dbg_b" if m % 2 == 0 else "dbg_a"))
    elif m <= 104:
        DRUMS.append("brk2" if m % 4 == 0 else "brk")     # kit steps back for the bass
    elif m <= 120:
        DRUMS.append("dbg_fill" if m % 8 == 0 else
                     ("dbg_ride" if m <= 112 else ("dbg_b" if m % 2 == 0 else "dbg_a")))
    elif m <= 128:
        DRUMS.append("fin_half" if m <= 124 else ("roll" if m == 128 else "meg_a"))
    else:
        DRUMS.append("meg_fill" if m % 8 == 0 else
                     ("meg_c" if m % 8 == 1 else ("meg_b" if m % 2 == 0 else "meg_a")))
DRUMS[128] = "tacet"
DRUMS[129] = "tacet"
DRUMS[-1] = "final"
DRUMS[-2] = "roll"

PARTS = {"LEAD": LEAD, "COUNTER": COUNTER, "SUSTAIN": SUSTAIN,
         "STABS": STABS, "KEYS": KEYS, "BASS": BASS, "DRUMS": DRUMS}


def verify():
    p = []
    for name, bars in PARTS.items():
        if len(bars) != N:
            p.append(f"{name}: {len(bars)} bars, want {N}")
            continue
        for i, b in enumerate(bars):
            src = DRUM_LIB[b] if name == "DRUMS" else b
            try:
                L = bar_len(src)
            except Exception as e:
                p.append(f"{name} m.{i+1}: parse {e} :: {b[:52]}")
                continue
            if L != F(4):
                p.append(f"{name} m.{i+1}: {L} beats :: {b[:52]}")
    if len(CHORDS) != N:
        p.append(f"chord grid {len(CHORDS)} != {N}")
    for m in range(1, N + 1):
        if T.LVL[T.dyn_for("STABS", m)] >= T.LVL[T.dyn_for("LEAD", m)]:
            p.append(f"m.{m}: stabs not under lead")
    # ornaments must land on a real note of a quarter or longer
    from zerosum import dur_of
    for (pt, m, idx), kind in T.ORNAMENTS.items():
        toks = PARTS[pt][m - 1].split()
        if idx >= len(toks):
            p.append(f"{kind} {pt} m.{m}: no note at index {idx}")
            continue
        tok = toks[idx].rstrip("~")
        if tok.startswith("R/"):
            p.append(f"{kind} {pt} m.{m}: lands on a rest")
        elif dur_of(tok.split("/")[1]) < F(1):
            p.append(f"{kind} {pt} m.{m}: note too short ({tok})")
    # grace notes must be within a tone of the note they decorate
    from zerosum2 import to_midi
    for (pt, m), g in T.GRACE.items():
        for tok in PARTS[pt][m - 1].split():
            if tok.startswith("R/"):
                continue
            tgt = tok.rstrip("~").split("/")[0].split("+")[0]
            if abs(to_midi(g) - to_midi(tgt)) > 2:
                p.append(f"grace {pt} m.{m}: {g} is a leap from {tgt}")
            break
    # glissandi need two real notes a third or more apart
    for (pt, m, idx) in T.GLISS:
        toks = [x for x in PARTS[pt][m - 1].split()]
        if idx + 1 >= len(toks):
            p.append(f"gliss {pt} m.{m}: no pair at {idx}")
            continue
        a, b = toks[idx].rstrip("~"), toks[idx + 1].rstrip("~")
        if a.startswith("R/") or b.startswith("R/"):
            p.append(f"gliss {pt} m.{m}: touches a rest")
        elif abs(to_midi(a.split("/")[0].split("+")[0])
                 - to_midi(b.split("/")[0].split("+")[0])) < 3:
            p.append(f"gliss {pt} m.{m}: interval too small")
    return p


if __name__ == "__main__":
    probs = verify()
    print(f"{len(probs)} PROBLEMS" if probs else
          f"OK -- {N} bars, {len(PARTS)} parts, every measure sums exactly.")
    for x in probs[:40]:
        print("  ", x)
    if not probs:
        act = sum(1 for b in BASS if b != "R/1")
        print(f"  bass sounds in {act}/{N} bars; lead rests in "
              f"{sum(1 for b in LEAD if b == 'R/1')} bars")
