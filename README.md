# Wi-Fi Strip Chart

A continuous Wi-Fi throughput and latency recorder that runs in the browser, built to be
opened on an iPad and added to the Home Screen.

![](https://img.shields.io/badge/runs-in%20the%20browser-blue)

## What it does

- **Line graph of speed over the last 10 s / 30 s / 60 s**, or the full session, on a real
  time axis that scrolls live.
- **Average speed for all three windows at once**, so a dip is visible immediately.
- **Every measurable variable listed**: peak / floor / median / standard deviation of
  throughput; time-to-first-byte, median, best-worst range, jitter and probe loss for
  latency; DNS, TCP, TLS, transfer time, total request, protocol, connection reuse,
  payload size, compression ratio and parallel stream count for the connection; plus
  whatever the browser reports about the connection itself and running session totals.
- History persists in `localStorage`, so the chart survives a reload.
- Light and dark themes; no network dependency beyond the font stylesheet.

## How it measures

The page is sandboxed and cannot reach any outside server, so it cannot run a conventional
speed test against a distant test node. Instead it repeatedly re-downloads **itself** from
the origin it was served from and times the transfer, reading the phase breakdown out of the
[Resource Timing API](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming).

Each cycle issues one solo request (for an uncontended latency reading) followed by a burst
of four parallel requests (to push enough bytes to time a transfer). Throughput is total
bytes divided by the transfer window across the burst.

### Accuracy

| Metric | Trust it? |
| --- | --- |
| Latency (TTFB) | Yes. A true round trip across your Wi-Fi, router, and out to the host. |
| Jitter | Yes. Mean absolute change between consecutive round trips. |
| Probe loss | Yes, as a reachability signal. |
| Throughput | As a **floor, not a ceiling**, and as a relative trend. |

The probe payload is small, so on a fast link the transfer completes before TCP reaches full
speed — a 400 Mbps connection can read far lower. That makes it reliable for watching
*change* over time and finding where in a home the connection degrades, but not for an
absolute Mbps figure. Use a dedicated speed test for that.

Sampling every second costs bandwidth of its own. The app reports its own consumption in the
*Data rate* row; slow the interval down before leaving it running.

### Background limitation

iPadOS suspends web pages that are not on screen, so recording pauses when you switch apps or
lock the screen and resumes when you return. A gap in the chart marks where that happened.
Continuous background measurement is not possible without a native app.

## Files

`index.html` is the whole app — no build step, no dependencies. It is written as an HTML
*fragment* (no `<!doctype>`, `<html>`, `<head>` or `<body>` tags) because it is published as a
Claude Artifact, which supplies that skeleton at publish time. Browsers render it fine when
opened directly.

To run it locally:

```sh
python3 -m http.server 8099
# then open http://127.0.0.1:8099/index.html
```

Note that against a local server the numbers describe the loopback interface, not Wi-Fi.
