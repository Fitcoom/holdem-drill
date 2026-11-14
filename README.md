# Hold'em Drill

**Play the player, not the chart.** An anti-GTO Texas Hold'em trainer, 6-max or 9-max (EN/FR). Classical (GTO-style) charts are the baseline; opponent profiles (GTO reg, TAG, Nit, LAG, Maniac, Calling station) show how real players deviate and how to exploit them. Drills: preflop opening ranges, defense vs opens (fold / call / 3-bet) against each profile (including isolating calling-station limps), an Opponents tab to study each profile, hand-vs-hand equity, pot odds and outs, showdown reading.

**Play / install:** https://fitcoom.github.io/holdem-drill/

- Android / PC (Chrome, Edge): open the link, then "Install app".
- iPhone (Safari): Share → "Add to Home Screen".

Works offline once installed. Stats are stored on each device.

## Development

`index.html` is the source. Run `python build_app.py` to build the installable PWA into `docs/` (served by GitHub Pages).
