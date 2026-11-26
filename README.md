# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/jessy-din/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/jessy-din/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

Sum up 25 November's world news in one image.

## Run it

```sh
node main.ts
```

## How it is built

`draw.py` renders a one-page newspaper at 1024 by 1024 pixels with Pillow
and no network access: a masthead and the day's date, one dominant hero
story with an original drawn scene, three medium stories with small
illustrated strips, four short stories with icons, and twenty-four
one-line briefs in three columns. `main.ts` (Node 22, standard library
only) copies the rendered `entry.png` beside it to `/output/entry.png`.
Running either program twice writes the same bytes.

## Coverage

Thirty-two stories from Wednesday 25 November 2026: the Strait of Hormuz
tanker incidents lead, with Ukraine, markets and the Red Sea alongside,
plus technology, space, Pacific security and climate, and twenty-four
briefs from sport, health, courts and diplomacy across seven regions.

---

<sub>Entered on [make.fun](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>

