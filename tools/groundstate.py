"""
GROUND STATE -- 144 bars, q = 120, 4/4, D minor.  Ten tracks.

A last-boss theme after MEGALOVANIA, and the bass is the protagonist.

THE PRINCIPLE, TAKEN FROM MEGALOVANIA
  MEGALOVANIA's riff is one bar of sixteen sixteenths, and across its four-bar
  unit ONLY THE FIRST TWO NOTES MOVE:

        D3 D3 | D4 A3 Ab3 G3 F3 D3 F3 G3
        1  1  |  2  3   2  2  2  1  1  1      (sixteenths)
        head        invariant tail
        heads: D - C - B - Bb

  The tail never changes.  That invariance is the whole engine: the riff is a
  floor, and the harmony is whatever you build on top of it.  This piece takes
  that to its limit.  The bass NEVER RESTS -- not one bar in 144 -- and every
  bar of it carries the same ten-attack rhythm.  Only the head transposes.
  verify() fails the build if the bass ever rests, ever drops below ten
  attacks, or ever deviates from the riff rhythm.

  That is what "ground state" means here: the lowest level, the one the rest of
  the piece is measured against.  It opens alone, it never stops, and the last
  sixteen bars strip everything else away again to leave it exactly where it
  started.

THE GROUND RIFF (mine, built on MEGALOVANIA's principle, not its pitches)

        R2 R2 | D3 A2 G2 F2 E2 D2 F2 A2
        1  1  |  2  3  2  2  2  1  1  1
        heads: D - C - Bb - A     i - bVII - bVI - V

  Same rhythm as the model, an homage; the tail descends where MEGALOVANIA's
  turns, and it sits an octave lower, down where a picked bass actually bites.

QUOTED DIRECTLY, at the climax (mm.81-96)
  The real MEGALOVANIA riff, heads D - C - B - Bb, tail D4 A3 Ab3 G3 F3 D3 F3
  G3, over the lead playing the verse contour A A G F E E D C | D E F G A G F E.
  A fan arrangement: commercial release would need clearance.

THE SOUNDS ARE NOT THE OTHER PIECES' SOUNDS
  ZERO-SUM, THREE FIGHTS, AFTERLIGHT and SHADOW OF THE FUTURE all render
  through the NES-style chiptune synth in render_audio.py -- pulse, square,
  triangle, noise.  This one does not.  It renders through render_toby.py,
  which models what Toby Fox actually used on MEGALOVANIA:

        3xOsc                     three detuned oscillators, saw and square
        Shreddage Bass: Picked    a picked electric bass  -> Karplus-Strong
        Ollie Waton Drums         a sampled acoustic kit
        Violin Detache            bowed strings, short strokes

KEYS   D minor -> Eb minor (m.97) -> F minor (m.113) -> D minor (m.129).
       Two lifts and a return: the ground state is where it ends.
"""

from fractions import Fraction as F
from zerosum import bar_len, dur_of
from zerosum2 import shift, rests, to_midi, from_midi
from afterlight import DRUM_LIB, GROOVES, FILLS

TITLE = "GROUND STATE"
BPM = 120
N = 144


# ===========================================================================
# 1.  THE RIFF -- rhythm invariant, head transposing
# ===========================================================================
# durations in sixteenths: 1 1 | 2 3 2 2 2 1 1 1   (sums to 16)
RIFF_CODES = ["16", "16", "8", "8.", "8", "8", "8", "16", "16", "16"]
RIFF_TAIL = ["D3", "A2", "G2", "F2", "E2", "D2", "F2", "A2"]
RIFF_HEADS = ["D2", "C2", "Bb1", "A1"]

# the real MEGALOVANIA riff, for the quotation at mm.81-96
MEGA_TAIL = ["D4", "A3", "Ab3", "G3", "F3", "D3", "F3", "G3"]
MEGA_HEADS = ["D3", "C3", "B2", "Bb2"]


def riff(head, tail, k=0, sharp=False):
    """One bar: two sixteenths on the moving head, then the invariant tail."""
    ps = [head, head] + tail
    bar = " ".join(f"{p}/{c}" for p, c in zip(ps, RIFF_CODES))
    return shift(bar, k, sharp) if k else bar


# ===========================================================================
# 2.  FORM
# ===========================================================================
#  name              mm.        key   what happens
SECTIONS = [
    ("ground",         1,  16, 0, "bass alone"),
    ("kit",           17,  32, 0, "the kit enters"),
    ("theme",         33,  48, 0, "lead takes the theme"),
    ("full",          49,  64, 0, "everything"),
    ("breakdown",     65,  80, 0, "bass and drums only"),
    ("megalovania",   81,  96, 0, "the quotation"),
    ("lift",          97, 112, 1, "Eb minor"),
    ("climax",       113, 128, 3, "F minor"),
    ("groundstate",  129, 144, 0, "stripped back to the floor"),
]
SEC_OF = {}
for _nm, _a, _b, _k, _d in SECTIONS:
    for _m in range(_a, _b + 1):
        SEC_OF[_m] = _nm
KEY_OF = {}
for _nm, _a, _b, _k, _d in SECTIONS:
    for _m in range(_a, _b + 1):
        KEY_OF[_m] = _k
SEC_START = {nm: a for nm, a, _b, _k, _d in SECTIONS}
LABEL = {a: f"{nm} - {d}" for nm, a, _b, _k, d in SECTIONS}

QUOTE = "megalovania"
# sections where nothing but bass, sub and kit sound
BARE = ("ground", "breakdown", "groundstate")


KEY_AT_XML = {1: -1, 97: -6, 113: -4, 129: -1}   # D min, Eb min, F min, D min


def sharp_at(m):
    # every key this piece visits is a flat one -- D minor (1b), Eb minor (6b),
    # F minor (4b) -- so nothing here is ever spelled with sharps.
    return False


# ===========================================================================
# 3.  BASS -- the protagonist.  Never rests.
# ===========================================================================
BASS = []
for _i in range(N):
    _m = _i + 1
    _k = KEY_OF[_m]
    if SEC_OF[_m] == QUOTE:
        BASS.append(riff(MEGA_HEADS[_i % 4], MEGA_TAIL, _k))
    else:
        BASS.append(riff(RIFF_HEADS[_i % 4], RIFF_TAIL, _k))

# doubled an octave up with the same pick attack -- this is what makes it
# read as HEAVY rather than merely low
BASSOCT = [shift(b, 12) if SEC_OF[i + 1] != "ground" else "R/1"
           for i, b in enumerate(BASS)]

# a sine an octave under the riff head, following the head only
SUB = []
for _i in range(N):
    _m = _i + 1
    _k = KEY_OF[_m]
    heads = MEGA_HEADS if SEC_OF[_m] == QUOTE else RIFF_HEADS
    _h = heads[_i % 4]
    # NOT an octave below the head: the heads already reach A1, and an octave
    # under that is subsonic -- it eats headroom without being audible.
    SUB.append("R/1" if SEC_OF[_m] == "ground" and _m <= 8
               else shift(f"{_h}/2 {_h}/4 {_h}/4", _k))


# ===========================================================================
# 4.  HARMONY
# ===========================================================================
VOICE = {"Dm": "D4+F4+A4", "C": "C4+E4+G4", "Bb": "Bb3+D4+F4",
         "A": "A3+C#4+E4", "Bdim": "B3+D4+F4"}
ROOT = {"Dm": "D3", "C": "C3", "Bb": "Bb2", "A": "A2", "Bdim": "B2"}
GRID = ["Dm", "C", "Bb", "A"]
GRID_Q = ["Dm", "C", "Bdim", "Bb"]       # under the MEGALOVANIA quote

CHORDS = [(GRID_Q if SEC_OF[i + 1] == QUOTE else GRID)[i % 4] for i in range(N)]


def sstack(s, k, sharp=False):
    """Transpose a bare pitch stack (no duration attached)."""
    return "+".join(from_midi(to_midi(x) + k, sharp) for x in s.split("+"))


def kv(name, m):
    k = KEY_OF[m]
    return sstack(VOICE[name], k, sharp_at(m)) if k else VOICE[name]


def kr(name, m, oct_shift=0):
    k = KEY_OF[m] + 12 * oct_shift
    return sstack(ROOT[name], k, sharp_at(m)) if k else ROOT[name]


# ===========================================================================
# 5.  THE THEME -- original, in the MEGALOVANIA idiom
# ===========================================================================
THEME = [
    "D5/8 F5/8 A5/4 G5/8 F5/8 E5/4",
    "E5/8 G5/8 C6/4 Bb5/8 A5/8 G5/4",
    "F5/8 A5/8 D6/4 C6/8 Bb5/8 A5/4",
    "C#5/8 E5/8 A5/4 G5/8 F5/8 E5/4",
    "D5/16 E5/16 F5/8 A5/8 D6/8 C6/8 A5/8 F5/4",
    "E5/16 F5/16 G5/8 C6/8 E6/8 D6/8 C6/8 G5/4",
    "F5/16 G5/16 A5/8 D6/8 F6/8 E6/8 D6/8 Bb5/4",
    "E5/8 C#5/8 E5/8 A5/8 C#6/4 A5/4",
]

THEME_HI = [
    "D6/16 C6/16 A5/16 F5/16 D5/8 F5/8 A5/8 D6/8 C6/8 A5/8",
    "E6/16 D6/16 C6/16 G5/16 E5/8 G5/8 C6/8 E6/8 D6/8 C6/8",
    "F6/16 E6/16 D6/16 Bb5/16 F5/8 A5/8 D6/8 F6/8 E6/8 D6/8",
    "E6/16 C#6/16 A5/16 E5/16 C#5/8 E5/8 A5/8 C#6/8 E6/4",
    "D6/8 A5/8 F5/8 D5/8 A4/4 D5/4",
    "C6/8 G5/8 E5/8 C5/8 G4/4 C5/4",
    "Bb5/8 F5/8 D5/8 Bb4/8 F4/4 Bb4/4",
    "A5/8 E5/8 C#5/8 A4/8 E4/4 A4/4",
]

# MEGALOVANIA verse contour: A A G F E E D C | D E F G A G F E
MEGA_VERSE = [
    "A5/8 A5/8 G5/8 F5/8 E5/8 E5/8 D5/8 C5/8",
    "D5/8 E5/8 F5/8 G5/8 A5/8 G5/8 F5/8 E5/8",
    "A5/8 A5/8 G5/8 F5/8 E5/8 E5/8 D5/8 C5/8",
    "D5/8 E5/8 F5/8 G5/8 A5/4 D5/4",
    "A5/16 G5/16 F5/16 E5/16 D5/8 F5/8 A5/8 D6/8 C6/8 A5/8",
    "D6/16 C6/16 Bb5/16 A5/16 G5/8 Bb5/8 D6/8 G6/8 F6/8 D6/8",
    "C6/16 Bb5/16 A5/16 G5/16 F5/8 A5/8 C6/8 F6/8 E6/8 C6/8",
    "D6/8 A5/8 F5/8 D5/8 A4/4 D5/4",
]


def theme_at(m, src, semis=0):
    k = KEY_OF[m] + semis
    b = src[(m - 1) % 8]
    return shift(b, k, sharp_at(m)) if k else b


# --- who plays what, by section -------------------------------------------
LEAD, LEAD2, STRINGS = [], [], []
for _i in range(N):
    _m, _s = _i + 1, SEC_OF[_i + 1]
    if _s in BARE:
        LEAD.append("R/1")
        LEAD2.append("R/1")
        STRINGS.append("R/1")
    elif _s == "kit":
        LEAD.append("R/1")
        LEAD2.append("R/1")
        STRINGS.append(f"{kv(CHORDS[_i], _m)}/1")
    elif _s == "theme":
        LEAD.append(theme_at(_m, THEME))
        LEAD2.append("R/1")
        STRINGS.append(f"{kv(CHORDS[_i], _m)}/1")
    elif _s == QUOTE:
        LEAD.append(theme_at(_m, MEGA_VERSE))
        LEAD2.append(shift(theme_at(_m, MEGA_VERSE), -12))
        STRINGS.append(f"{kv(CHORDS[_i], _m)}/2 {kv(CHORDS[_i], _m)}/2")
    else:                                   # full, lift, climax
        hi = _s in ("lift", "climax")
        LEAD.append(theme_at(_m, THEME_HI if hi else THEME))
        LEAD2.append(shift(theme_at(_m, THEME if hi else THEME_HI), -12))
        STRINGS.append(f"{kv(CHORDS[_i], _m)}/2 {kv(CHORDS[_i], _m)}/2")

# neither lead may hold the tune for more than sixteen unbroken bars, so each
# steps out for two bars of every sixteen -- and they do it at opposite points
# in the phrase, so one of them always has it
for _i in range(N):
    if SEC_OF[_i + 1] in BARE:
        continue
    if (_i % 16) >= 14:
        LEAD[_i] = "R/1"
    if (_i % 16) in (6, 7):
        LEAD2[_i] = "R/1"

ORGAN = [f"{kv(CHORDS[i], i + 1)}/1" if SEC_OF[i + 1] not in BARE
         and SEC_OF[i + 1] != "kit" else "R/1" for i in range(N)]

STAB = []
for _i in range(N):
    _m, _s = _i + 1, SEC_OF[_i + 1]
    v = kv(CHORDS[_i], _m)
    if _s in BARE or _s == "kit":
        STAB.append("R/1")
    elif _s in ("full", "lift", "climax", QUOTE):
        STAB.append(" ".join([f"R/8 {v}/8"] * 4))
    else:
        STAB.append(f"R/4 {v}/4 R/4 {v}/4")


def power(name, m, kind):
    r = kr(name, m)
    ch = f"{r}+{from_midi(to_midi(r) + 7, sharp_at(m))}"
    return {"chug": " ".join([f"{ch}/8"] * 8),
            "gallop": " ".join([f"{ch}/8 {ch}/16 {ch}/16"] * 4),
            "hold": f"{ch}/1"}[kind]


GUITAR = []
for _i in range(N):
    _m, _s = _i + 1, SEC_OF[_i + 1]
    if _s in BARE or _s == "kit":
        GUITAR.append("R/1")
    elif _s in ("lift", "climax"):
        GUITAR.append(power(CHORDS[_i], _m, "gallop"))
    elif _s == "theme":
        GUITAR.append(power(CHORDS[_i], _m, "hold"))
    else:
        GUITAR.append(power(CHORDS[_i], _m, "chug"))


def kit(m, family):
    if m % 16 == 1:
        return f"{family}_O" if f"{family}_O" in DRUM_LIB else GROOVES[family][0]
    if m % 8 == 0:
        return FILLS[(m // 8) % len(FILLS)]
    if m % 4 == 0:
        return FILLS[((m // 4) + 3) % len(FILLS)]
    return GROOVES[family][m % 4]


DRUMS = []
for _i in range(N):
    _m, _s = _i + 1, SEC_OF[_i + 1]
    if _s == "ground":
        DRUMS.append("tacet")
    elif _s == "groundstate":
        DRUMS.append(kit(_m, "rock") if _m <= 136 else "tacet")
    elif _s == "breakdown":
        DRUMS.append(kit(_m, "rock"))
    elif _s in ("lift", "climax", QUOTE):
        DRUMS.append(kit(_m, "busy"))
    else:
        DRUMS.append(kit(_m, "rock"))
DRUMS[135] = "fill_c"

PARTS = {"LEAD": LEAD, "LEAD2": LEAD2, "STRINGS": STRINGS, "ORGAN": ORGAN,
         "STAB": STAB, "GUITAR": GUITAR, "BASS": BASS, "BASSOCT": BASSOCT,
         "SUB": SUB, "DRUMS": DRUMS}
MELODIC = ("LEAD", "LEAD2")


# ===========================================================================
# 6.  DYNAMICS -- the bass is the loudest thing that is not a drum
# ===========================================================================
LEVELS = ["ppp", "pp", "p", "mp", "mf", "f", "ff", "fff"]
LVL = {d: i for i, d in enumerate(LEVELS)}
OFFSET = {"LEAD": 0, "LEAD2": -1, "STRINGS": -2, "ORGAN": -2, "STAB": -2,
          "GUITAR": -1, "BASS": 0, "BASSOCT": -1, "SUB": -1, "DRUMS": -1}
SEC_DYN = {"ground": "f", "kit": "f", "theme": "f", "full": "ff",
           "breakdown": "f", "megalovania": "ff", "lift": "ff",
           "climax": "fff", "groundstate": "f"}
LEAD_DYN = [(a, SEC_DYN[nm]) for nm, a, _b, _k, _d in SECTIONS]
LEAD_HAIRPINS = [(a, b, ">" if nm == "groundstate" else "<")
                 for nm, a, b, _k, _d in SECTIONS]


def dyn_for(part, measure):
    lead = LEAD_DYN[0][1]
    for m, d in LEAD_DYN:
        if m <= measure:
            lead = d
        else:
            break
    return LEVELS[max(0, min(7, LVL[lead] + OFFSET[part]))]


def dyn_changes(part):
    out, prev = [], None
    for m, _ in LEAD_DYN:
        d = dyn_for(part, m)
        if d != prev:
            out.append((m, d))
            prev = d
    return out


# ===========================================================================
# 7.  VERIFY
# ===========================================================================
def codes_of(bar):
    return [t.rstrip("~").split("/")[1] for t in bar.split()]


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
                p.append(f"{name} m.{i+1}: parse {e} :: {b[:48]}")
                continue
            if L != F(4):
                p.append(f"{name} m.{i+1}: {L} beats :: {b[:48]}")

    # --- THE BASS IS THE POINT ---------------------------------------------
    for i, b in enumerate(BASS):
        if b == "R/1":
            p.append(f"m.{i+1}: the bass rested")
            break
    for i, b in enumerate(BASS):
        if len(b.split()) < 10:
            p.append(f"m.{i+1}: bass only {len(b.split())} attacks, want 10+")
            break
    for i, b in enumerate(BASS):
        if codes_of(b) != RIFF_CODES:
            p.append(f"m.{i+1}: bass rhythm deviates from the riff")
            break
    # only the head may move: the tail is invariant within each 4-bar unit
    for i in range(0, N - 3, 4):
        tails = {" ".join(BASS[i + j].split()[2:]) for j in range(4)}
        if len(tails) != 1:
            p.append(f"m.{i+1}: the riff tail changed inside its unit")
            break
    # and the bass must be the loudest thing that is not a drum
    for m in range(1, N + 1):
        bl = LVL[dyn_for("BASS", m)]
        for other in PARTS:
            if other in ("BASS", "DRUMS", "LEAD"):
                continue
            if LVL[dyn_for(other, m)] > bl:
                p.append(f"m.{m}: {other} is louder than the bass")
                break

    # --- accompaniment under the melody ------------------------------------
    for m in range(1, N + 1):
        lead = LVL[dyn_for("LEAD", m)]
        for acc in ("STAB", "STRINGS", "ORGAN"):
            if LVL[dyn_for(acc, m)] > lead - 2:
                p.append(f"m.{m}: {acc} not under lead")
                break

    # --- no melodic voice holds the tune too long --------------------------
    for v in MELODIC:
        run = 0
        for m in range(1, N + 1):
            run = run + 1 if PARTS[v][m - 1] != "R/1" else 0
            if run > 16:
                p.append(f"{v}: {run} unbroken bars by m.{m}")
                break

    # --- the piece must end where it started -------------------------------
    if SEC_OF[N] != "groundstate" or KEY_OF[N] != 0:
        p.append("the piece does not return to the ground state")
    return p


if __name__ == "__main__":
    probs = verify()
    print(f"{len(probs)} PROBLEMS" if probs else
          f"OK -- {N} bars, {len(PARTS)} parts, every measure sums exactly.")
    for x in probs[:25]:
        print("  ", x)
    if not probs:
        print("\n  form:")
        for nm, a, b, k, d in SECTIONS:
            key = ["D min", "Eb min", "", "F min"][k]
            live = sum(1 for n, pt in PARTS.items() if pt[a - 1] != "R/1")
            print(f"    m.{a:>4}-{b:<4} {nm:<13} {key:<7} "
                  f"{live:>2}/10 tracks   {d}")
        atk = sum(len(b.split()) for b in BASS)
        print(f"\n  bass: {atk} attacks over {N} bars, "
              f"{atk/N:.0f} per bar, zero rests")
        secs = N * 4 * 60 / BPM
        print(f"  duration {int(secs//60)}:{int(secs%60):02d}")
