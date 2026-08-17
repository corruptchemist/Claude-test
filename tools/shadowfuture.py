"""
SHADOW OF THE FUTURE -- 208 bars, q = 182, 4/4.  Twelve tracks.

The last encounter ever.  A boss theme built on Hopes and Dreams, and on the
one theorem that says it cannot end well.

THE GAME
  "The shadow of the future" is Axelrod's term for the only reason cooperation
  is ever rational: the game continues, so defecting today costs you tomorrow.
  Lengthen the shadow and nice strategies win.  His round-robin tournament --
  reproduced below, honestly, in tournament() -- is won by TIT FOR TAT.

  But a FINITELY repeated game with a known last round unravels.  In the final
  round there is no tomorrow, so defect.  Knowing that, defect in the second to
  last.  Induct backwards and cooperation dies all the way to round one.  This
  piece is the last encounter ever.  The shadow is zero.  The mathematics says
  despair, and it says so as a proof.

  So the form is a real match -- TIT FOR TAT against PROBER, played out move by
  move -- and the last three rounds are handed to backward induction, which
  collapses them.  Then, in the final sixteen bars, the piece refuses its own
  theorem and cooperates anyway.  That refusal is marked in exactly one place
  in the code, and it is the only unearned event in the score.

THE ARGUMENT IS ONE PITCH: F versus E.
  COOPERATE is the real Hopes and Dreams engine, ii7 - I6 - IV - V:
        || Cm7 | Bb/D | Ebma7 | F ||
  bass ascending C-D-Eb-F, tonic never in root position.
  DEFECT keeps that ascending bass and rots the dominant into bV:
        || C*7 | D*7 | Eb*7 | E7 ||
  E is the tritone above Bb -- the dominant that cannot go home.  Every round
  is decided by whether bar 15 of it lands on F or on E.  The last bar of the
  piece is an F chord, and it is F because the music chose it, not because the
  game did.

QUOTED DIRECTLY
  Hopes and Dreams / Once Upon a Time -- the family cell, in Bb:
        5 5 2 | 1 5 5 | 5 7 7 1 | 7 5 3
        F F C | Bb F F | F A A Bb | A F D
  verified against the published letter notes (f f c A f f f a a A a f d ...,
  uppercase = black key, so A = Bb).  Bb major, ~170 bpm, 4/4.

IT GETS MORE COMPLICATED, AND THAT IS ENFORCED
  Thirteen rounds of sixteen bars.  Every round is rhythmically busier than the
  one before it -- verify() counts attacks and fails the build if the count
  ever falls.  The ladder runs plain half notes -> eighths -> sixteenths ->
  continuous sixteenth runs -> canon at eight bars -> four -> two -> stretto at
  one -> inversion against the subject -> thirty-seconds.  Complexity rises
  monotonically the whole way; CONSONANCE is what oscillates with the game.
  So the collapse at rounds 10-11 is the busiest music yet and the bleakest.

KEYS   Bb (R0-R5) -> B (R6-R11) -> C (R12).  Two semitone lifts; the first is
       Hopes and Dreams' own move, the second is the one it never gets to make.
"""

from fractions import Fraction as F
from zerosum import bar_len, dur_of
from zerosum2 import shift, rests, to_midi, from_midi
from afterlight import DRUM_LIB, GROOVES, FILLS

TITLE = "SHADOW OF THE FUTURE"
BPM = 182
RLEN = 16                 # bars per round
ROUNDS = 13
N = RLEN * ROUNDS         # 208


# ===========================================================================
# 1.  GAME THEORY -- real strategies, a real round robin
# ===========================================================================
# Axelrod's payoffs: T > R > P > S and 2R > T + S.
PAYOFF = {("C", "C"): (3, 3), ("C", "D"): (0, 5),
          ("D", "C"): (5, 0), ("D", "D"): (1, 1)}


def tit_for_tat(me, opp):
    """Nice, retaliatory, forgiving.  Winner of both of Axelrod's tournaments."""
    return "C" if not opp else opp[-1]


def grim_trigger(me, opp):
    """Nice until crossed once, then never forgives."""
    return "D" if "D" in opp else "C"


def always_defect(me, opp):
    return "D"


def always_cooperate(me, opp):
    return "C"


def pavlov(me, opp):
    """Win-stay, lose-shift."""
    if not me:
        return "C"
    return me[-1] if PAYOFF[(me[-1], opp[-1])][0] >= 3 else \
        ("D" if me[-1] == "C" else "C")


def prober(me, opp):
    """D, C, C -- then exploit a pushover, otherwise fall back to tit for tat."""
    if len(me) < 3:
        return "DCC"[len(me)]
    if opp[1] == "C" and opp[2] == "C":
        return "D"
    return opp[-1]


STRATEGIES = {"TIT FOR TAT": tit_for_tat, "GRIM TRIGGER": grim_trigger,
              "PAVLOV": pavlov, "PROBER": prober,
              "ALWAYS COOPERATE": always_cooperate,
              "ALWAYS DEFECT": always_defect}


def play(sa, sb, n):
    """Run one match and return both move histories."""
    a, b = [], []
    for _ in range(n):
        ma, mb = sa(a, b), sb(b, a)
        a.append(ma)
        b.append(mb)
    return a, b


def tournament(n=60):
    """Full round robin, every strategy against every other including itself."""
    score = {k: 0 for k in STRATEGIES}
    names = list(STRATEGIES)
    for i, x in enumerate(names):
        for y in names[i:]:
            a, b = play(STRATEGIES[x], STRATEGIES[y], n)
            for ma, mb in zip(a, b):
                pa, pb = PAYOFF[(ma, mb)]
                score[x] += pa
                score[y] += pb
    return sorted(score.items(), key=lambda kv: -kv[1])


# --- the form of the piece is one real match, then the theorem, then hope ---
BI_HORIZON = 3            # rounds from the end where backward induction bites


def form():
    a, b = play(tit_for_tat, prober, ROUNDS)
    for r in range(ROUNDS - BI_HORIZON, ROUNDS):
        a[r] = b[r] = "D"          # backward induction: the shadow is zero
    a[-1] = b[-1] = "C"            # <-- THE REFUSAL.  the only unearned bar.
    return a, b


MOVES_A, MOVES_B = form()
OUTCOME = [MOVES_A[r] + MOVES_B[r] for r in range(ROUNDS)]


# ===========================================================================
# 2.  HARMONY -- cooperate resolves to F, defect rots it to E
# ===========================================================================
BASE_VOICE = {
    "ii7":  "Eb4+G4+Bb4",   "I6":   "D4+F4+Bb4",   "IV":  "Eb4+G4+D5",
    "iv":   "Eb4+Gb4+Bb4",  "vi7":  "D4+G4+Bb4",   "Vsus": "F4+Bb4+C5",
    "V":    "F4+A4+C5",
    "o1":   "C4+Eb4+Gb4",   "o2":   "D4+F4+Ab4",   "o3":   "Eb4+Gb4+A4",
    "bV7":  "E4+G#4+D5",
}
BASE_ROOT = {"ii7": "C2", "I6": "D2", "IV": "Eb2", "iv": "Eb2", "vi7": "G2",
             "Vsus": "F2", "V": "F2",
             "o1": "C2", "o2": "D2", "o3": "Eb2", "bV7": "E2"}


def up(p, semis, sharp=False):
    return from_midi(to_midi(p) + semis, sharp)


def stack(s, semis, sharp=False):
    return "+".join(up(p, semis, sharp) for p in s.split("+"))


def keyed(fn, k):
    return fn if not k else f"{fn}^{k}"


VOICE, ROOT = {}, {}
for _k in (0, 1, 2):
    _sh = (_k == 1)
    for _fn in BASE_VOICE:
        VOICE[keyed(_fn, _k)] = stack(BASE_VOICE[_fn], _k, _sh)
        ROOT[keyed(_fn, _k)] = up(BASE_ROOT[_fn], _k, _sh)
PAD = {k: "+".join(v.split("+")[:2]) for k, v in VOICE.items()}

# Two bars per chord when they agree; one bar per chord when they do not.
COOP_A = ["ii7", "ii7", "I6", "I6", "IV", "IV", "Vsus", "V"]
COOP_B = ["ii7", "ii7", "I6", "I6", "IV", "iv", "vi7", "V"]
DEFECT = ["o1", "o1", "o2", "o2", "o3", "o3", "bV7", "bV7"]
# a split round: the two players' harmonies alternate bar by bar, so the
# harmonic rhythm doubles and nothing sits still
MIXED = ["ii7", "o1", "I6", "o2", "IV", "o3", "Vsus", "bV7"]

KEY_OF_ROUND = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2]


def round_chords(r):
    out, k = OUTCOME[r], KEY_OF_ROUND[r]
    if out == "CC":
        grid = COOP_A + COOP_B
    elif out == "DD":
        grid = DEFECT * 2
    else:
        grid = MIXED * 2
    return [keyed(fn, k) for fn in grid]


CHORDS = [c for r in range(ROUNDS) for c in round_chords(r)]


# ===========================================================================
# 3.  THE QUOTE, and its ladder of treatments
# ===========================================================================
# Hopes and Dreams / Once Upon a Time: F F C | Bb F F | F A A Bb | A F D
HD_PLAIN = [
    "F5/4 F5/4 C6/2",
    "C6/2 R/2",
    "Bb5/4 F5/4 F5/2",
    "F5/2 R/2",
    "F5/4 A5/4 A5/2",
    "A5/4 Bb5/4 Bb5/2",
    "A5/4 F5/4 D5/2",
    "D5/1",
]

HD_8TH = [
    "F5/4 F5/8 F5/8 C6/2",
    "C6/2. Bb5/8 C6/8",
    "Bb5/4 F5/8 F5/8 F5/2",
    "F5/2 R/4 C5/8 D5/8",
    "F5/8 G5/8 A5/4 A5/2",
    "A5/4 Bb5/8 A5/8 Bb5/2",
    "A5/8 G5/8 F5/4 D5/2",
    "D5/2. F5/8 A5/8",
]

HD_16 = [
    "F5/8 F5/16 G5/16 F5/8 A5/8 C6/2",
    "C6/4 Bb5/16 C6/16 D6/16 C6/16 Bb5/8 A5/8 C6/4",
    "Bb5/8 F5/16 G5/16 F5/8 D5/8 F5/2",
    "F5/4 C5/16 D5/16 Eb5/16 F5/16 G5/8 A5/8 F5/4",
    "F5/8 G5/16 A5/16 A5/8 C6/8 A5/2",
    "A5/8 Bb5/16 A5/16 Bb5/8 D6/8 Bb5/2",
    "A5/8 G5/16 F5/16 A5/8 F5/8 D5/2",
    "D5/16 F5/16 A5/16 D6/16 A5/8 F5/8 D5/2",
]

HD_RUN = [
    "F5/16 G5/16 A5/16 Bb5/16 C6/16 Bb5/16 A5/16 G5/16 "
    "F5/16 A5/16 C6/16 F6/16 C6/8 A5/8",
    "C6/16 D6/16 Eb6/16 F6/16 Eb6/16 D6/16 C6/16 Bb5/16 C6/4 A5/8 C6/8",
    "Bb5/16 C6/16 D6/16 F6/16 D6/16 C6/16 Bb5/16 A5/16 "
    "Bb5/16 F5/16 D5/16 Bb4/16 F5/8 F5/8",
    "F5/16 G5/16 A5/16 C6/16 F6/16 C6/16 A5/16 G5/16 F5/4 C5/8 D5/8",
    "F5/16 G5/16 A5/16 C6/16 A5/16 G5/16 F5/16 A5/16 A5/8 C6/8 A5/4",
    "A5/16 Bb5/16 C6/16 D6/16 Bb5/16 A5/16 G5/16 Bb5/16 Bb5/8 D6/8 Bb5/4",
    "A5/16 G5/16 F5/16 Eb5/16 D5/16 F5/16 A5/16 C6/16 A5/8 F5/8 D5/4",
    "D5/16 F5/16 A5/16 D6/16 F6/16 D6/16 A5/16 F5/16 D5/8 A5/8 D6/4",
]

HD_32 = [
    "F5/32 G5/32 A5/32 Bb5/32 C6/32 D6/32 Eb6/32 F6/32 "
    "C6/16 A5/16 F5/8 F5/16 A5/16 C6/16 F6/16 C6/8 A5/8",
    "C6/32 D6/32 Eb6/32 F6/32 G6/32 F6/32 Eb6/32 D6/32 "
    "C6/16 Bb5/16 A5/16 C6/16 C6/4 A5/8 C6/8",
    "Bb5/32 C6/32 D6/32 Eb6/32 F6/32 G6/32 A6/32 Bb6/32 "
    "F6/16 D6/16 Bb5/16 F5/16 D5/8 F5/8 F5/4",
    "F5/32 G5/32 A5/32 Bb5/32 C6/32 D6/32 Eb6/32 F6/32 "
    "C6/16 A5/16 F5/16 C5/16 F5/8 A5/8 C6/4",
    "F5/32 G5/32 A5/32 C6/32 F6/32 C6/32 A5/32 G5/32 "
    "A5/16 C6/16 F6/16 A6/16 F6/8 C6/8 A5/4",
    "A5/32 Bb5/32 C6/32 D6/32 F6/32 D6/32 C6/32 Bb5/32 "
    "Bb5/16 D6/16 F6/16 Bb6/16 F6/8 D6/8 Bb5/4",
    "A5/32 G5/32 F5/32 Eb5/32 D5/32 C5/32 Bb4/32 A4/32 "
    "D5/16 F5/16 A5/16 D6/16 A5/8 F5/8 D5/4",
    "D5/32 F5/32 A5/32 D6/32 F6/32 A6/32 F6/32 D6/32 "
    "A5/16 F5/16 D5/16 A4/16 D5/8 A5/8 D6/4",
]

# --- diatonic inversion of the subject, for the stretto rounds -------------
BB_STEPS = ["Bb", "C", "D", "Eb", "F", "G", "A"]
_IDX = {n: i for i, n in enumerate(BB_STEPS)}


def _to_step(p):
    """Pitch name -> diatonic step in Bb major, counting Bb4 as 0.

    The scale runs Bb4 C5 D5 Eb5 F5 G5 A5 Bb5, so every degree above Bb sits
    in the NEXT octave number -- hence the two cases.
    """
    i = 1
    while i < len(p) and p[i] in "#b":
        i += 1
    name, octv = p[:i], int(p[i:])
    if name not in _IDX:
        return None
    d = _IDX[name]
    return (octv - 4) * 7 if d == 0 else (octv - 5) * 7 + d


def _from_step(s):
    d = s % 7
    name = BB_STEPS[d]
    octv = s // 7 + 4 if d == 0 else (s - d) // 7 + 5
    return f"{name}{octv}"


def invert(bar, axis=4):
    """Diatonic inversion about F5 (step 4) inside Bb major."""
    out = []
    for tok in bar.split():
        head, d = tok.rstrip("~").split("/")
        if head == "R":
            out.append(tok)
            continue
        ps = []
        for p in head.split("+"):
            s = _to_step(p)
            ps.append(_from_step(2 * axis - s) if s is not None else p)
        out.append(f"{'+'.join(ps)}/{d}")
    return " ".join(out)


def block(bars, k, sharp=None):
    """Transpose an 8-bar block into the round's key."""
    if not k:
        return list(bars)
    sh = (k == 1) if sharp is None else sharp
    return [shift(b, k, sh) for b in bars]


# ===========================================================================
# 4.  WHAT EACH ROUND IS MADE OF
# ===========================================================================
# theme ladder, canon delay in bars, how many tracks are live
LADDER = [
    # r   theme      canon  voices  label
    (0,  HD_PLAIN,   0,  4, "the first move"),
    (1,  HD_8TH,     0,  5, "retaliation"),
    (2,  HD_16,      0,  6, "cooperation holds"),
    (3,  HD_16,      0,  7, "and pays"),
    (4,  HD_RUN,     8,  8, "canon at eight"),
    (5,  HD_RUN,     4,  9, "canon at four"),
    (6,  HD_RUN,     4, 10, "B major"),
    (7,  HD_RUN,     2, 11, "canon at two"),
    (8,  HD_RUN,     2, 11, "inversion"),
    (9,  HD_32,      1, 12, "stretto at one"),
    (10, HD_32,      1, 12, "the shadow is zero"),
    (11, HD_32,      1, 12, "backward induction"),
    (12, HD_RUN,     2, 12, "HOPE"),
]
THEME = {r: t for r, t, _c, _v, _l in LADDER}
CANON = {r: c for r, _t, c, _v, _l in LADDER}
VOICES_AT = {r: v for r, _t, _c, v, _l in LADDER}
LABEL = {r: l for r, _t, _c, _v, l in LADDER}

# The finale states the tune plainly on top and blazes underneath: LEAD keeps
# the singable sixteenth setting, everyone else moves to thirty-seconds.
UNDER = {r: (HD_32 if r == 12 else THEME[r]) for r in range(ROUNDS)}

BLOCKS = N // 8           # 26 eight-bar blocks


def rng(r):
    return range(r * RLEN, (r + 1) * RLEN)


def brng(b):
    return range(b * 8, (b + 1) * 8)


# --- WHO HAS THE SUBJECT, by eight-bar block -------------------------------
# No voice may hold it for more than sixteen unbroken bars, so the lead works
# in pairs of blocks and then hands off.  Every block is covered by someone.
LEAD_ON = [b % 3 != 2 for b in range(BLOCKS)]
LEAD2_ON = {2, 4, 7, 8, 10, 13, 14, 16, 19, 20, 22, 24, 25}
CHOIR_ON = {2: "T", 5: "T", 7: "C", 11: "T", 13: "C",
            17: "T", 19: "C", 23: "T", 25: "C"}
BELL_ON = {5, 11, 14, 17, 20, 24, 25}
INVERT_AT = {3, 21}       # A retaliates; and the theme turns over as it unravels


def theme_bar(r, i, src=None, inv=False, semis=0):
    """One bar of the round's subject, transposed into the round's key."""
    bars = src if src is not None else THEME[r]
    bar = bars[i % 8]
    if inv:
        bar = invert(bar)
    k = KEY_OF_ROUND[r]
    return shift(bar, k + semis, k == 1) if (k or semis) else bar


# --- LEAD: player A --------------------------------------------------------
LEAD = ["R/1"] * N
for _b in range(BLOCKS):
    if not LEAD_ON[_b]:
        continue
    _r = (_b * 8) // RLEN
    for _i in brng(_b):
        LEAD[_i] = theme_bar(_r, _i, inv=_b in INVERT_AT)

# --- LEAD2: player B.  A true canon where the ladder calls for one; a
#     contrary-motion second subject where it does not; the tune itself
#     whenever player A has stepped back. ----------------------------------
LEAD2 = ["R/1"] * N
for _b in sorted(LEAD2_ON):
    _r = (_b * 8) // RLEN
    _d = CANON[_r]
    for _i in brng(_b):
        if _d and _i - _d >= 0 and LEAD[_i - _d] != "R/1":
            LEAD2[_i] = shift(LEAD[_i - _d], -12)
        elif LEAD_ON[_b]:
            LEAD2[_i] = shift(theme_bar(_r, _i, UNDER[_r], inv=True), -12)
        else:
            LEAD2[_i] = shift(theme_bar(_r, _i, UNDER[_r]), -12)

# --- CHOIR: counter-subject, and the tune when the leads step back ---------
CM = ["Bb3/2 C4/4 D4/4", "Eb4/2. D4/4", "C4/4 D4/8 Eb4/8 F4/2",
      "G4/2 F4/4 Eb4/4", "D4/4 F4/4 Bb4/2", "A4/2. G4/4",
      "F4/8 G4/8 A4/4 Bb4/2", "G4/4 F4/4 D4/2"]
CHOIR = ["R/1"] * N
for _b, _role in CHOIR_ON.items():
    _r = (_b * 8) // RLEN
    _k = KEY_OF_ROUND[_r]
    for _i in brng(_b):
        if _role == "T":
            CHOIR[_i] = shift(theme_bar(_r, _i, UNDER[_r]), -12)
        else:
            cm = CM[_i % 8] if _b % 2 else invert(CM[_i % 8], -3)
            CHOIR[_i] = shift(cm, _k, _k == 1) if _k else cm

# --- BELL: the tune an octave up, only where the texture can carry it ------
def _top(bar):
    ps = [to_midi(p) for t in bar.split()
          for p in t.rstrip("~").split("/")[0].split("+") if p != "R"]
    return max(ps) if ps else 0


BELL = ["R/1"] * N
for _b in sorted(BELL_ON):
    _r = (_b * 8) // RLEN
    for _i in brng(_b):
        bar = theme_bar(_r, _i, UNDER[_r], semis=12)
        # the thirty-second settings run high enough to shriek up there; drop
        # the whole bar an octave rather than let single notes poke through
        BELL[_i] = shift(bar, -12) if _top(bar) > 100 else bar


# ===========================================================================
# 5.  THE ENGINE -- accompaniment generated from the grid
# ===========================================================================
def arp16(c):
    v = (VOICE[c].split("+") * 2)[:4]
    return " ".join(f"{p}/16" for p in (v + v[::-1]) * 2)


def arp32(c):
    v = (VOICE[c].split("+") * 2)[:4]
    seq = (v + v[::-1]) * 2
    return " ".join(f"{p}/32" for p in seq + seq)


ARP = []
for _i, _c in enumerate(CHORDS):
    _r = _i // RLEN
    if VOICES_AT[_r] < 5:
        ARP.append("R/1")
    elif _r >= 9:
        ARP.append(arp32(_c))
    else:
        ARP.append(arp16(_c))

# The pad and the offbeat guitar carry the steady part of the accumulation:
# both subdivide further as the rounds go by and neither ever thins out.
PAD_SUB = [0, 1, 1, 2, 2, 2, 4, 8, 8, 8, 8, 8, 8]
GTR_SUB = [0, 0, 2, 2, 4, 4, 8, 8, 8, 8, 16, 16, 16]


def pulse(v, n):
    if not n:
        return "R/1"
    return " ".join([f"{v}/{ {1:'1', 2:'2', 4:'4', 8:'8', 16:'16'}[n] }"] * n)


def offbeat(v, n):
    if not n:
        return "R/1"
    if n == 16:
        return " ".join([f"{v}/16"] * 16)
    code = {2: "4", 4: "8", 8: "16"}[n]
    return " ".join([f"R/{code} {v}/{code}"] * n)


STRINGS = [pulse(PAD[c], PAD_SUB[i // RLEN]) for i, c in enumerate(CHORDS)]
GUITAR = [offbeat(VOICE[c], GTR_SUB[i // RLEN]) for i, c in enumerate(CHORDS)]


def power(c, kind):
    r = ROOT[c]
    ch = f"{r}+{up(r, 7)}"
    return {"chug":   " ".join([f"{ch}/8"] * 8),
            "chug16": (f"{ch}/16 {ch}/16 {ch}/8 {ch}/16 {ch}/16 {ch}/8 "
                       f"{ch}/16 {ch}/16 {ch}/8 {ch}/8 {ch}/8"),
            "gallop": " ".join([f"{ch}/8 {ch}/16 {ch}/16"] * 4),
            "hold":   f"{ch}/1"}[kind]


POWER = []
for _i, _c in enumerate(CHORDS):
    _r = _i // RLEN
    if VOICES_AT[_r] < 9:
        POWER.append("R/1")
    elif _r >= 10:
        POWER.append(power(_c, "gallop"))
    else:
        POWER.append(power(_c, "chug16" if _i % 2 else "chug"))

LOWBRASS = [f"{ROOT[c]}+{up(ROOT[c], 7)}/1" if VOICES_AT[i // RLEN] >= 7
            else "R/1" for i, c in enumerate(CHORDS)]


def bass_bar(c, kind, nxt):
    r = ROOT[c]
    hi, fi = up(r, 12), up(r, 7)
    th = up(r, 3)
    ap = up(ROOT[nxt], -1) if ROOT[nxt] != r else fi
    return {
        "hold":  f"{r}/4 {hi}/8 {r}/8 {fi}/4 {r}/4",
        "oct8":  " ".join([f"{r}/8 {hi}/8"] * 4),
        "drive": (f"{r}/8 {hi}/16 {r}/16 {hi}/8 {r}/8 "
                  f"{r}/8 {hi}/16 {r}/16 {hi}/8 {fi}/8"),
        "sixt":  (f"{r}/16 {r}/16 {hi}/16 {r}/16 {fi}/16 {r}/16 {hi}/16 {r}/16 "
                  f"{th}/16 {r}/16 {hi}/16 {r}/16 {fi}/16 {th}/16 {hi}/16 {ap}/16"),
        "fill":  (f"{r}/16 {th}/16 {fi}/16 {hi}/16 {fi}/16 {th}/16 {r}/16 {th}/16 "
                  f"{fi}/8 {hi}/8 {fi}/16 {th}/16 {r}/16 {ap}/16"),
    }[kind]


BASS = []
for _i, _c in enumerate(CHORDS):
    _r, _m = _i // RLEN, _i + 1
    _n = CHORDS[_i + 1] if _i + 1 < N else _c
    if _r == 0:
        BASS.append(bass_bar(_c, "hold" if _m <= 4 else "oct8", _n))
    elif _r <= 2:
        BASS.append(bass_bar(_c, "fill" if _m % 8 == 0 else "drive", _n))
    elif _r <= 8:
        BASS.append(bass_bar(_c, "fill" if _m % 8 == 0 else
                             ("sixt" if _m % 4 == 0 else "drive"), _n))
    else:
        BASS.append(bass_bar(_c, "fill" if _m % 8 == 0 else "sixt", _n))

SUB = [f"{up(ROOT[c], -12)}/1" if VOICES_AT[i // RLEN] >= 5 else "R/1"
       for i, c in enumerate(CHORDS)]


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
    _m, _r = _i + 1, _i // RLEN
    if _r == 0:
        DRUMS.append("halfO" if _m == 1 else ("half" if _m <= 8 else
                                              kit(_m, "rock")))
    elif _r <= 3:
        DRUMS.append(kit(_m, "rock"))
    elif _r <= 9:
        DRUMS.append(kit(_m, "busy"))
    elif _r <= 11:
        DRUMS.append(kit(_m, "busy"))
    else:
        DRUMS.append(kit(_m, "busy"))
DRUMS[-1] = "final"

PARTS = {"LEAD": LEAD, "LEAD2": LEAD2, "CHOIR": CHOIR, "BELL": BELL,
         "STRINGS": STRINGS, "GUITAR": GUITAR, "POWER": POWER,
         "LOWBRASS": LOWBRASS, "ARP": ARP, "BASS": BASS, "SUB": SUB,
         "DRUMS": DRUMS}
MELODIC = ("LEAD", "LEAD2", "CHOIR", "BELL")


# ===========================================================================
# 6.  DYNAMICS -- accompaniment strictly under the melody
# ===========================================================================
LEVELS = ["ppp", "pp", "p", "mp", "mf", "f", "ff", "fff"]
LVL = {d: i for i, d in enumerate(LEVELS)}
OFFSET = {"LEAD": 0, "LEAD2": -1, "CHOIR": -1, "BELL": -1, "STRINGS": -1,
          "GUITAR": -2, "POWER": -1, "LOWBRASS": -1, "ARP": -2, "BASS": 0,
          "SUB": -1, "DRUMS": -1}
ROUND_DYN = ["p", "mp", "mf", "mf", "f", "f", "f", "ff", "ff", "ff",
             "ff", "fff", "fff"]
LEAD_DYN = [(r * RLEN + 1, ROUND_DYN[r]) for r in range(ROUNDS)]
LEAD_HAIRPINS = [(r * RLEN + 1, (r + 1) * RLEN, "<" if r != 12 else ">")
                 for r in range(ROUNDS)]


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
# 7.  GLISSANDI -- written out, so they sound in any player
# ===========================================================================
def _dur_tokens(pitch, ql):
    table = [(F(4), "1"), (F(3), "2."), (F(2), "2"), (F(3, 2), "4."),
             (F(1), "4"), (F(3, 4), "8."), (F(1, 2), "8"), (F(1, 4), "16")]
    out, left = [], ql
    for v, code in table:
        while left >= v:
            out.append(f"{pitch}/{code}")
            left -= v
    return " ".join(out)


def glissify(bar, idx, sharp=False):
    toks = bar.split()
    if idx + 1 >= len(toks):
        return bar
    a, b = toks[idx].rstrip("~"), toks[idx + 1].rstrip("~")
    if a.startswith("R/") or b.startswith("R/"):
        return bar
    pa, da = a.split("/")
    pb = b.split("/")[0]
    if "+" in pa or "+" in pb:
        return bar
    span = dur_of(da)
    m0, m1 = to_midi(pa), to_midi(pb)
    steps = abs(m1 - m0)
    if steps < 3 or span < F(1):
        return bar
    n = min(steps - 1, 6)
    run = F(n, 4)
    if span - run < F(1, 2):
        return bar
    step = 1 if m1 > m0 else -1
    parts = [_dur_tokens(pa, span - run)]
    for k in range(1, n + 1):
        parts.append(f"{from_midi(m0 + step * k, sharp)}/16")
    toks[idx] = " ".join(parts)
    return " ".join(toks)


def place_glissandi(part):
    hits = []
    for i, b in enumerate(part):
        if b == "R/1":
            continue
        sh = KEY_OF_ROUND[i // RLEN] == 1
        for idx in range(len(b.split()) - 1):
            if glissify(b, idx, sh) != b:
                hits.append((i, idx))
                break
    for i, idx in hits:
        part[i] = glissify(part[i], idx, KEY_OF_ROUND[i // RLEN] == 1)
    return [i + 1 for i, _ in hits]


GLISS_BARS = sorted(place_glissandi(LEAD) + place_glissandi(CHOIR))
ORNAMENTS = {}


# ===========================================================================
# 8.  VERIFY
# ===========================================================================
def attacks(part, i):
    src = DRUM_LIB[part[i]] if part is DRUMS else part[i]
    return sum(1 for t in src.split() if not t.startswith("R/"))


def round_attacks(r):
    return sum(attacks(p, i) for p in PARTS.values() for i in rng(r))


def verify():
    p = []
    if len(CHORDS) != N:
        p.append(f"chord grid {len(CHORDS)} != {N}")
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

    # --- the brief, made checkable: it must keep getting more complicated ---
    counts = [round_attacks(r) for r in range(ROUNDS)]
    for r in range(1, ROUNDS):
        if counts[r] < counts[r - 1]:
            p.append(f"round {r} is simpler than round {r-1} "
                     f"({counts[r]} < {counts[r-1]} attacks)")

    # --- accompaniment must stay under the melody --------------------------
    for m in range(1, N + 1):
        lead = LVL[dyn_for("LEAD", m)]
        for acc in ("GUITAR", "ARP"):
            if LVL[dyn_for(acc, m)] > lead - 2:
                p.append(f"m.{m}: {acc} not under lead")

    # --- the game must actually be the game --------------------------------
    if tournament()[0][0] != "TIT FOR TAT":
        p.append("tit for tat did not win the tournament")
    for r in range(ROUNDS - BI_HORIZON, ROUNDS - 1):
        if OUTCOME[r] != "DD":
            p.append(f"round {r}: backward induction did not collapse it")
    if OUTCOME[-1] != "CC":
        p.append("the piece did not choose hope")

    # --- F versus E: the argument must land where it says it does ----------
    # only mutual cooperation earns the dominant; anything else rots to bV
    for r in range(ROUNDS):
        last = CHORDS[(r + 1) * RLEN - 1]
        wants_f = OUTCOME[r] == "CC"
        gets_f = last.startswith("V")
        if wants_f != gets_f:
            p.append(f"round {r}: cadence is {last}, outcome {OUTCOME[r]}")

    # --- the canon must be a real canon, not a unison ----------------------
    for r in range(ROUNDS):
        d = CANON[r]
        if not d:
            continue
        for i in rng(r):
            if LEAD2[i] != "R/1" and LEAD2[i] == LEAD[i]:
                p.append(f"m.{i+1}: canon collapsed into unison")
                break

    # --- no melodic voice may hold the tune for more than 16 unbroken bars --
    for v in MELODIC:
        run = 0
        for m in range(1, N + 1):
            run = run + 1 if PARTS[v][m - 1] != "R/1" else 0
            if run > 16:
                p.append(f"{v}: {run} unbroken bars by m.{m}")
                break

    # --- the engine never stops once it starts -----------------------------
    for m in range(RLEN + 1, N + 1):
        if ARP[m - 1] == "R/1":
            p.append(f"m.{m}: arp engine stopped")
            break
    return p


if __name__ == "__main__":
    probs = verify()
    print(f"{len(probs)} PROBLEMS" if probs else
          f"OK -- {N} bars, {len(PARTS)} parts, every measure sums exactly.")
    for x in probs[:25]:
        print("  ", x)
    if not probs:
        print("\n  Axelrod round robin:")
        for i, (nm, sc) in enumerate(tournament(), 1):
            print(f"    {i}. {nm:<18} {sc}")
        print("\n  the match, round by round:")
        counts = [round_attacks(r) for r in range(ROUNDS)]
        for r in range(ROUNDS):
            k = "Bb B C".split()[KEY_OF_ROUND[r]]
            cad = "F" if OUTCOME[r] == "CC" else "E"
            print(f"    R{r:<3} m.{r*RLEN+1:>4}  {OUTCOME[r]}  {k:<2} "
                  f"cad->{cad}  canon@{CANON[r]}  "
                  f"{counts[r]:>5} attacks   {LABEL[r]}")
        print(f"\n  glissandi: {len(GLISS_BARS)}")
        secs = N * 4 * 60 / BPM
        print(f"  duration {int(secs//60)}:{int(secs%60):02d}")
