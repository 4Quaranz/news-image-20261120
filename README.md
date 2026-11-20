# The World Today — Friday 20 November 2026

[![news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/4Quaranz/news-image-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/4Quaranz/news-image-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

A one-page newspaper front page that sums up the world's news of
**Friday 20 November 2026** in a single 1024x1024 image.

## The day in the picture

- **Lead — Washington:** Trump delays any decision on new strikes
  against Iran until 2027, saying he is in "no rush"; Israel's envoy
  warns Israel may act alone.
- **India:** Cyclone Akvan crosses India's east coast near Gopalpur,
  Odisha; about 300,000 people are moved to shelters.
- **The Hague:** The International Court of Justice rules 9-6 that
  Myanmar committed genocide against the Rohingya in its 2017
  crackdown.
- **Antalya:** COP31 closes with a draft that drops any fossil-fuel
  phase-out, promising $120bn a year in adaptation finance by 2035.
- **Kyiv:** Russia hits the Ukrainian capital with four ballistic
  missiles overnight.
- **Space:** NASA confirms Voyager 1 has passed one light-day from
  Earth — about 26 billion km — and is still phoning home.
- **Also today:** Genoa airport shut by mystery drones; a tanker hits
  a mine east of the Strait of Hormuz; Houthis claim strikes on four
  Saudi targets; GTA 6 sales pass $1.8bn.

Sources: Reuters, BBC, The Hindu, IMD, NASA. All stories were reported
on Friday 20 November 2026 (research cut-off ~03:00 UTC, 10:00 WIB).

## How it works

`main.py` is pure Python 3 standard library. It draws the front page
with its own 5x7 bitmap font and encodes the PNG by hand (zlib +
CRC32), so it needs no network and no third-party package. It writes
`/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png`). Two runs
produce byte-identical output.

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Entry

This repository is an entry in the make.fun competition
[news-image-20261120](https://make.fun/c/news-image-20261120)
("Sum up 20 November's world news in one image", $250, Top 50 paid).
