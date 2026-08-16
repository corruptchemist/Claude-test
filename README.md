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
    score/zero-sum.html the deliverable

## Verify

    cd tools && python3 zerosum2.py

Checks that all 150 measures exist across all 7 parts and that every measure sums
exactly to its meter, then reports where the withheld elements first appear.

## Render

    cd tools && python3 render.py ../score/zero-sum.html
