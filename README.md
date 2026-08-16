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

200 bars, ♩=176, 4/4, ~4:32. Built for REAPER — the deliverable is multi-track MIDI.

Modelled closely on *Hopes and Dreams* and *Last Goodbye*, which share a key
world: Hopes and Dreams is B♭ major and lifts a semitone to B major at its 2/3
point, and Last Goodbye is in B major. The piece starts in the first song's key
and arrives in the second's.

## The engine

    || Cm7 | Bb/D | Ebmaj7 | Fsus4 -> F ||     ii7 - I6 - IV - V

One chord per TWO bars. Bass ascends C–D–E♭–F. The tonic never appears in root
position — always B♭/D — which is why the loop climbs and never arrives.
Fast pulse plus slow harmonic rhythm is the whole "heroic, not panicked" formula.

The theme is the Undertale-family scale-degree cell `5 5 2 | 1 5 5 | 5 7 7 1 |
7 5 3`, stated in long values, high, over a fast bed.

## Getting more complicated, still manageable

Complexity arrives by adding layers and figurating the same eight bars — never
by making any single part harder. Structural pitches stay on the strong beats
at every stage; only the space between them fills in.

| stage | mm. | what arrives | layers |
|---|---|---|---|
| 1 | 1–16 | theme + arp only, no bass, no drums | 2 |
| 2 | 17–32 | **the drop** — bass enters, light kit | 3 |
| 3 | 33–48 | counter-line, full kit | 4 |
| 4 | 49–64 | strings; theme grows 8th tails | 5 |
| 5 | 65–80 | offbeat guitar; theme in 8ths | 6 |
| 6 | 81–96 | 16th figuration | 6 |
| 7 | 97–128 | tutti, octave up | 6 |
| 8 | 129–160 | **B major** — semitone lift, no pivot | 6 |
| 9 | 161–184 | the strain: iii–IV–iii–V→vi, bass oscillates | 6 |
| coda | 185–200 | strips back to the opening texture | 6 |

`verify()` checks bar lengths, the dynamics offsets, and that the texture never
thins before the coda.

    cd tools && python3 afterlight.py && python3 export_afterlight.py

## REAPER import

`afterlight.mid` is format-1 multi-track. Track names say which patch to load;
drums are on channel 10. Insert → Media file, and tick "import as new tracks".

## Hearing it without a soundfont

    cd tools && python3 render_audio.py ../score/afterlight.mid ../score/afterlight.mp3

`render_audio.py` is a small chiptune synth -- pulse/saw/triangle oscillators
plus filtered noise for the kit, per MIDI channel. No soundfont or external
tool needed. Writes .wav, or .mp3 if the filename ends in .mp3.
