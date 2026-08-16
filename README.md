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
