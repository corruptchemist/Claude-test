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

A variation suite after three Toby Fox battle themes. 200 measures, ~6:00.

| | mm. | key | tempo | source |
|---|---|---|---|---|
| I. FLOWER | 1–64 | F minor | ♩=95 | *Finale* |
| bridge A | 65–72 | E°7 = A♯°7 | — | — |
| II. GLAMOUR | 73–128 | B minor / E Dorian | ♩=148 | *Death by Glamour* |
| bridge B | 129–136 | E → E♭ → D | — | — |
| III. BAD TIME | 137–200 | D minor | ♩=126 | *MEGALOVANIA* |

Original writing that develops each source's harmonic frame, bass shape and
rhythmic signature. No source melody is transcribed.

A three-note motto — ♭6, 5, 1 — welds the suite together: D♭–C–F in F minor,
G–F♯–B in B minor, B♭–A–D in D minor. It opens the piece, marks both bridges,
and closes the coda.

## Dynamics

Levels are derived from a single LEAD spine; every other part is offset from it
and the offsets are enforced in `verify()`, not eyeballed. Stabs and pads sit
**two** steps under the melody, bass/keys/drums one step. 26 hairpins carry the
level changes; only three bare changes remain, where the drop is the gesture.

    tools/threefights.py        motto, dynamics engine, drum library, melodies
    tools/threefights2.py       bass, accompaniment, assembly, verification
    tools/export_threefights.py MusicXML + MIDI export
    score/three-fights.mxl      import this into Finale
