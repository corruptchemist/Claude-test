# Wi-Fi Strip Chart

A continuous Wi-Fi speed and latency recorder that runs in the browser, built to be opened
on an iPad and added to the Home Screen.

## What it shows

- **Six live graphs at once** - speed over the last 10 s, 30 s, 60 s and the full session,
  plus latency over the last 60 s and the full session. All on real time axes that scroll live.
- **Rolling averages** for the 10 s / 30 s / 60 s windows side by side.
- **A confidence readout** that says whether the current speed number can be trusted.
- **Every measurable variable**: speed distribution and a conservative lower bound;
  measurement quality (transfer window, bytes per burst, parallel streams, payload size,
  ballast); latency distribution, jitter and probe loss; DNS, TCP, TLS, transfer time,
  protocol and compression; whatever the browser reports about the connection; and session
  totals including projected hourly data use.
- History persists in `localStorage`. Light and dark themes.

## How the speed number is produced

The page is sandboxed and cannot reach any outside server, so there is no distant test node
to pull from. It measures by re-downloading **itself** from its own origin as fast as the
link allows, and timing the bytes.

Two things make that a real measurement rather than a guess:

1. **Ballast.** The page carries ~590 KB of incompressible random data. Without it the page
   is ~11 KB gzipped, and no arrangement of requests can saturate a fast link - the transfer
   finishes long before round-trip overhead stops dominating.
2. **A windowed, saturating measurement.** Many downloads are opened at once, sized from a
   running estimate of the link. The first 400 ms is discarded while connections ramp up,
   then bytes are counted over the next 900 ms via streaming reads. Only bytes arriving
   inside that window count, so a partly idle start or finish cannot drag the result down.

Because `fetch()` hands back decompressed bytes, counts are scaled by the measured
`encodedBodySize / decodedBodySize` ratio to recover actual bytes on the wire.

Latency is measured separately, once a second, with cheap **HEAD** requests that skip the
payload - and only between speed tests. A ping issued while a test is saturating the link
queues behind the app's own downloads and reports hundreds of milliseconds that have nothing
to do with the network.

### Verified against known link speeds

Chromium was throttled to fixed downlink rates via the Chrome DevTools Protocol and the app
was left recording for 26 s at each rate. Reported figures are the median burst, discarding
the first two while the estimator calibrates.

| True link | Reported | Error | Confidence |
| ---: | ---: | ---: | :--- |
| 5 Mbps | 4.7 | -6.0% | high |
| 10 Mbps | 9.4 | -5.5% | high |
| 25 Mbps | 24.5 | -2.2% | high |
| 60 Mbps | 57.2 | -4.7% | high |
| 100 Mbps | 94.5 | -5.5% | high |
| 200 Mbps | 182.4 | -8.8% | capped |

Readings run a few percent low and never high. The gap is packet, TLS and HTTP framing
overhead, which counts against the link but is never exposed to a script. Above ~150 Mbps
the stream count hits its ceiling and the app reports `capped` rather than pretending.

Reproduce with `scratchpad/verify.js` against the threaded gzip test server in
`scratchpad/server.py`.

### What it costs

Measuring bandwidth consumes bandwidth: confirming a 60 Mbps link really does 60 Mbps means
actually moving 60 Mbps of data. Each burst is ~1.3 s of saturated download, so at 60 Mbps a
test costs about 10 MB. Testing every 5 seconds is roughly 7 GB/hour; every 60 seconds is
roughly 0.6 GB/hour. The *Projected per hour* row shows the live figure. Use a slower
interval for long unattended runs or on a metered connection.

### Background limitation

iPadOS suspends web pages that are not on screen, so recording pauses when you switch apps or
lock the screen and resumes when you return. A gap in the chart marks where that happened.
Continuous background measurement is not possible without a native app.

## Files

`index.html` is the whole app - no build step, no dependencies. It is written as an HTML
*fragment* (no `<!doctype>`, `<html>`, `<head>` or `<body>` tags) because it is published as a
Claude Artifact, which supplies that skeleton at publish time. Browsers render it fine when
opened directly.

The trailing `<script type="text/ballast">` block is the incompressible padding described
above. It is inert, and the app reports its size in the *Ballast* row so a stripped or
minified copy is immediately visible.

```sh
python3 scratchpad/server.py     # threaded, gzip, HEAD - mimics a real static host
# then open http://127.0.0.1:8099/index.html
```

Against a local server the numbers describe the loopback interface, not Wi-Fi.
