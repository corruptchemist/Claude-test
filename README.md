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

208 bars, ♩=176, ~4:46. Eleven tracks. Multi-track MIDI for REAPER.

## Mode plan — hope is arrived at, not sat in

| mm. | mode | what |
|---|---|---|
| 1–32 | **G minor** | the fight. Distorted guitar chugging, low brass, no bells |
| 33–96 | B♭ major | hope arrives. Power guitar drops to offbeats |
| 81–96 | | bass feature, everything else out of the way |
| 97–128 | **G minor** | phase two. Dark again, chug returns |
| 129–208 | B major | the payoff, then coda |

G minor and B♭ major share a key signature, so the shift is **modal, not a
modulation** — and the dark phases move harmonically twice as fast (one chord
per bar against one per two), which is most of why they read as agitated.

`verify()` asserts the bells never sound in a minor phase and the distorted
guitar is always chugging there rather than sitting on offbeats.

## The long-note themes

Each is a full **sixteen-bar period** — an antecedent that hangs and a
consequent that starts the same way, then climbs somewhere new and cadences.
They were previously eight bars played twice.

The quoted pitches still land on the strong beats; what varies is rhythm.
Every bar used to be two half notes. Now all sixteen bars of every theme carry
a **distinct rhythmic profile** — dotted halves, syncopated re-attacks,
neighbour turns, rests, pickups across barlines. `verify()` rejects any theme
whose consequent literally repeats its antecedent, or that falls below
thirteen distinct rhythms in sixteen bars.

## Drums

Four variants of every groove, six fills, rotating so no pattern repeats bar to
bar, and a fill every **four** bars rather than every eight. 22 distinct
patterns across the piece; longest identical run is 3 bars (it was 7).

## Ornaments

The long-note sections carry **20 trills** on notes of a dotted half or longer,
and **9 written-out glissandi** at phrase peaks. The glissandi are real
chromatic runs, not notation symbols — a shortened head note plus sixteenths
sliding into the target — so they sound in any player, which is what you want
for a synth lead anyway.

Trills are notated as signs in the MusicXML and **expanded into alternating
32nds in the MIDI**, so the preview renders them.

## Depth

Three layers exist purely for weight: **distorted rhythm guitar** (root-and-fifth
power chords, chugging 16ths in the dark phases), **low brass**, and a **sub-bass**
octave under the bass. Toby spent his only paid samples on bass and rhythm rock
guitar — leaving the distorted guitar out was the main reason the previous
version read as a win screen.

## Balance

Offsets: pad and low brass and distorted guitar at −1, offbeat guitar and arp
at −2, bass level with the melody. In the preview render the pad, arp and
guitars were raised substantially and the bell and bass pulled back — the
middle of the picture was inaudible before.

    cd tools && python3 afterlight.py && python3 export_afterlight.py
    python3 render_audio.py ../score/afterlight.mid ../score/afterlight.mp3
