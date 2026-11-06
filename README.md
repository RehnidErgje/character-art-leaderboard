# Character Art Leaderboard

How much fan art each character of **Zenless Zone Zero**, **Genshin Impact**, **Honkai: Star Rail** and **Wuthering Waves** has on Danbooru, Rule34 and pixiv, how much of it is R-18, and which characters get drawn together.

The site shows only numbers from tag searches on those sites: no pictures from them. Character icons come from the games' fandom wikis.

## What is here

- `docs/` is the site that GitHub Pages serves: `index.html`, `dash-lite.js` (the small runtime the page runs on) and `data/<game>/` (each game's counts and crossovers as JSON).
- `build.py` rebuilds `docs/` from the collection tool's output:

  ```
  python build.py <path to the collection tool>
  ```

## How the numbers are counted

- Each character is searched by its own tags on each site; tags inside one site are joined with OR, so a picture counts once there.
- Totals add the chosen sites together, so a picture posted on two sites counts twice.
- R-18 is Danbooru `rating:explicit`, Rule34 `rating:explicit`, and pixiv's R-18 search (with R-18G).
- A crossover is a picture that has both characters, through any of their tags on the site (pixiv: main tags first, then works found through the other tags).
