# ZERO-SUM

An original 150-measure boss battle theme in the Toby Fox (Undertale / Deltarune) idiom.

- **Form** — 7 sections, 150 mm., ~3:57
- **Tempo** — ♩=92 (6/4) → ♩=184 (4/4) via 2:1 metric modulation
- **Tonal plan** — D minor → D major, through F major and an octatonic collapse
- **Parts** — Lead, Counter, Sustain, Stabs, Keys, Bass, Drums

The whole piece argues about one pitch: A♭, the tritone above D. It poisons the opening
bassline, colours the boss theme as the blue ♭5, vanishes entirely for the 25 bars of the
major-mode "Payoff Matrix", and returns respelled G♯ as the ♯11 of the final D major chord.

## Layout

    tools/zerosum.py    notation parser, ostinato/stab/drum generators, section I
    tools/zerosum2.py   sections II–VII, score assembly, verification
    tools/render.py     renders the complete note listing as an HTML score page
    tools/export_musicxml.py  exports MusicXML + MIDI from the same data
    score/zero-sum.html       readable note listing
    score/zero-sum.mxl        compressed MusicXML -- import this into Finale
    score/zero-sum.musicxml   uncompressed MusicXML
    score/zero-sum.mid        MIDI, for listening

## Verify

    cd tools && python3 zerosum2.py

Checks that all 150 measures exist across all 7 parts and that every measure sums
exactly to its meter, then reports where the withheld elements first appear.

## Render

    cd tools && python3 render.py ../score/zero-sum.html

## Import notes

Written at **concert pitch**. Set up transposing instruments in Finale after import.

Drums use General MIDI pitches on a percussion staff: 36 kick, 38 snare, 42 closed hat,
46 open hat, 47 tom, 49 crash, 51 ride. Rolls are notated as plain snare notes -- add
tremolo marks by hand.

    cd tools && python3 export_musicxml.py

---

# THREE FIGHTS

A medley-variation suite on three Toby Fox battle themes. 216 measures, ~6:30.
A fan arrangement — commercial release would need clearance.

| | mm. | key | tempo | source |
|---|---|---|---|---|
| I. FLOWER | 1–56 | F minor | ♩=95 | *Finale* |
| bridge A | 57–64 | E°7 = A♯°7 | | |
| II. GLAMOUR | 65–120 | B minor / E Dorian | ♩=148 | *Death by Glamour* |
| — bass break | 97–104 | | | |
| bridge B | 121–128 | E → E♭ → D | | |
| III. BAD TIME | 129–184 | D minor | ♩=126 | *MEGALOVANIA* |
| IV. QUODLIBET + coda | 185–216 | D minor | ♩=126 | all three |

## Quoted material

    Q1  MEGALOVANIA riff   D3 D3 D4 A3 Ab3 G3 F3 D3 F3 G3
                           durations 1 1 2 3 2 2 2 1 1 1 sixteenths
                           only the first two notes move: D-D, C-C, B-B, Bb-Bb
    Q2  MEGALOVANIA verse  A A G F E E D C  D E F G A G F E
    Q3  Your Best Friend   1 2 3 | 1 | 2 | 2 3 2 | 1 || 3 4 5 | 1 | 6 | 5
    Q4  Death by Glamour   E - G - D - C#   (D->C# slurred; the C# is the sound)

The **quodlibet** at mm.185–200 runs Q1 in the bass, Q3 in the lead and Q4's
♭7→6 slur in the counter — all three fights sounding at once in D minor.

## Balance

The lead is the reference; everything else is a fixed offset from it, enforced
in `verify()`. Stabs sit **three** steps under the melody and keys **two** —
and in movement I the keys also move an octave *below* the tune rather than
arpeggiating into its register, which was the real masking problem.

## What verify() checks

Bar lengths, chord-grid length, the dynamics rule (stabs strictly under the
melody by at least two steps, keys likewise), that ornaments land on notes of
a quarter or longer, that grace notes
are within a tone of what they decorate, and that glissandi span a third or more.

    cd tools && python3 threefights2.py && python3 export_threefights.py

---

# AFTERLIGHT

152 bars, ♩=176, **3:27**. Twelve tracks. Multi-track MIDI for REAPER.

## The melody changes hands

Four distinct melodic timbres — **Lead 1** (25% pulse), **Lead 2** (12.5% pulse),
**Choir**, **Bells**. `verify()` rejects any voice holding the tune for more
than sixteen unbroken bars.

    m9   lead              m73  lead 2 + choir
    m17  lead + COUNTER    m81  lead
    m25  lead 2 + choir    m89  lead + lead 2 + bells
    m33  lead              m97  lead 2 + choir
    m41  lead 2            m105 lead
    m49  all four          m113 lead 2
    m57  (bass feature)    m121 lead + choir + bells
    m65  lead + choir      m129 lead 2 + choir
                           m137 bells → m145 lead

## The counter-melody

Enters at **m.17**, directly after the main melody's first statement, on the
choir. A genuinely independent line — it moves where the theme rests, arcs in
contrary motion against it, and sits an octave lower. `verify()` fails if it
ever doubles the lead.

## Mode plan

| mm. | | |
|---|---|---|
| 1–24 | **G minor** | the fight |
| 25–56 | B♭ major | hope arrives |
| 57–64 | | bass feature |
| 65–80 | **G minor** | phase two |
| 81–152 | B major | payoff, strain, climax, coda |

G minor and B♭ major share a key signature, so the shift is modal; the dark
phases move harmonically twice as fast.

## Also enforced by verify()

The 16th engine never stops after m.5 · bass never under five attacks a bar
between the drop and the coda · bells barred from the minor phases · stabs and
arp at least two dynamic steps under the melody · every long-note theme has
13+ distinct rhythms in 16 bars and no consequent repeating its antecedent.

29 written-out glissandi. No trills.

    cd tools && python3 afterlight.py && python3 export_afterlight.py
    python3 render_audio.py ../score/afterlight.mid ../score/afterlight.mp3

---

# SHADOW OF THE FUTURE

208 bars, ♩=182, **4:37**. Twelve tracks. A last-boss theme built on
*Hopes and Dreams* — and on the one theorem that says it cannot end well.

A fan arrangement: it quotes Toby Fox directly, so commercial release would
need clearance.

## The game

**"The shadow of the future"** is Axelrod's term for the only reason
cooperation is ever rational: the game continues, so defecting today costs you
tomorrow. Lengthen the shadow and nice strategies win.

`tournament()` reproduces his round robin honestly — six real strategies, the
standard payoffs (T=5, R=3, P=1, S=0), every pairing — and TIT FOR TAT wins it.
`verify()` fails the build if it ever stops winning.

| | | |
|---|---|---|
| 1 | TIT FOR TAT | 1138 |
| 2 | PAVLOV | 1054 |
| 3 | GRIM TRIGGER | 1026 |
| 4 | ALWAYS COOPERATE | 906 |
| 5 | PROBER | 842 |
| 6 | ALWAYS DEFECT | 796 |

But a *finitely* repeated game with a known last round unravels. In the final
round there is no tomorrow, so defect. Knowing that, defect in the second to
last. Induct backwards and cooperation dies all the way to round one.

**This piece is the last encounter ever. The shadow is zero.** The mathematics
says despair, and it says so as a proof.

So the form is a real match — TIT FOR TAT against PROBER, played out move by
move — and the last three rounds are handed to backward induction, which
collapses them. Then, in the final sixteen bars, the piece refuses its own
theorem and cooperates anyway. That refusal is one line in `form()`:

    a[-1] = b[-1] = "C"            # <-- THE REFUSAL.  the only unearned bar.

## The argument is one pitch: F versus E

COOPERATE is the real *Hopes and Dreams* engine, ii7 – I6 – IV – V:

    || Cm7 | Bb/D | Ebma7 | F ||

bass ascending C–D–E♭–F, tonic never in root position. DEFECT keeps that
ascending bass and rots the dominant into ♭V:

    || C°7 | D°7 | Eb°7 | E7 ||

E is the tritone above B♭ — the dominant that cannot go home. Every round is
decided by whether its last bar lands on F or on E, and `verify()` checks that
only mutual cooperation is ever allowed to earn the F. The last chord of the
piece is an F chord, and it is F because the music chose it, not the game.

## Round by round

| | mm. | moves | key | cad. | canon | attacks | |
|---|---|---|---|---|---|---|---|
| R0 | 1 | CD | B♭ | E | — | 247 | the first move |
| R1 | 17 | DC | B♭ | E | — | 693 | retaliation |
| R2 | 33 | CC | B♭ | F | — | 843 | cooperation holds |
| R3 | 49 | CC | B♭ | F | — | 860 | and pays |
| R4 | 65 | CC | B♭ | F | 8 | 878 | canon at eight |
| R5 | 81 | CC | B♭ | F | 4 | 1263 | canon at four |
| R6 | 97 | CC | B | F | 4 | 1291 | B major |
| R7 | 113 | CC | B | F | 2 | 1322 | canon at two |
| R8 | 129 | CC | B | F | 2 | 1423 | inversion |
| R9 | 145 | CC | B | F | 1 | 1767 | stretto at one |
| R10 | 161 | **DD** | B | **E** | 1 | 1901 | the shadow is zero |
| R11 | 177 | **DD** | B | **E** | 1 | 1909 | backward induction |
| R12 | 193 | CC | C | F | 2 | 2186 | **HOPE** |

## It gets more complicated, and that is enforced

The ladder runs plain half notes → eighths → sixteenths → continuous sixteenth
runs → canon at eight bars → four → two → stretto at one → the subject against
its own inversion → thirty-seconds. The pad and the offbeat guitar subdivide
further every few rounds and never thin out.

`verify()` counts every attack in every part and **fails the build if any round
is less busy than the one before it** — the attacks column above is that count,
and it is strictly increasing from 247 to 2186.

Complexity rises monotonically the whole way; *consonance* is what oscillates
with the game. So the collapse at R10–R11 is the busiest music yet and also the
bleakest, and the finale states the tune plainly on top while everything
underneath blazes in thirty-seconds.

## Quoted material

*Hopes and Dreams* / *Once Upon a Time* — the family cell, in B♭:

    5 5 2 | 1 5 5 | 5 7 7 1 | 7 5 3
    F F C | Bb F F | F A A Bb | A F D

Verified against the published letter notes (`f f c A f f f a a A a f d ...`,
uppercase = black key, so `A` = B♭). B♭ major, ~170 bpm, 4/4 — which is also
why the two semitone lifts land where they do: B♭ → B is *Hopes and Dreams*'
own modulation, and B → C is the one it never gets to make.

## Also enforced by verify()

Every bar sums exactly to 4/4 · no melodic voice holds the subject for more
than sixteen unbroken bars · the canon never collapses into unison · the arp
engine never stops after round 0 · stabs and arp at least two dynamic steps
under the melody · backward induction really does collapse R10–R11 · the piece
really does choose hope in R12.

27 written-out glissandi.

    cd tools && python3 shadowfuture.py && python3 export_shadowfuture.py
    python3 render_audio.py ../score/shadow-of-the-future.mid \
                            ../score/shadow-of-the-future.mp3
