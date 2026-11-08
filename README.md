# Character Art Leaderboard

How much fan art each character of **Zenless Zone Zero**, **Genshin Impact**, **Honkai: Star Rail** and **Wuthering Waves** has on Danbooru, Rule34 and pixiv, how much of it is R-18, what it shows, and which characters get drawn together.

Site: https://rehnidergje.github.io/character-art-leaderboard/

The site shows only numbers from tag searches on those sites: no pictures from them. Character icons come from the games' fandom wikis.

## What the page shows

- **Leaderboard**: posts per character on the chosen sites, all time or the first 3 months after release, all art, R-18 only or without R-18.
- **Alone**: how much of a character's art shows them alone.
- **Categories**: how much of a character's art has a theme, in groups: people, body, pairing, power, type, habits.
- **Crossovers**: a network of the characters drawn together most; categories can join it too.
- **Popularity and share**: posts against a share (R-18, alone or a category) for every character.
- **Settings** (the gear): animations, light or dark theme, and AI art counted or left out.

## What is here

- `docs/` is the site that GitHub Pages serves: `index.html`, `dash-lite.js` (the small runtime the page runs on) and `data/<game>/` (each game's numbers as JSON: `board.json` and `pairs.json` with AI art, `board_noai.json` and `pairs_noai.json` without).
- `data/` has the same numbers as CSV for reading and analysis; see [data/README.md](data/README.md).
- `build.py` rebuilds `docs/` and `data/` from the collection tool's output. The collection tool is not public.

  ```
  python build.py <path to the collection tool>
  ```

## How the numbers are counted

- Each character is searched by its own tags on each site; tags inside one site are joined with OR, so a picture counts once there.
- Totals add the chosen sites together, so a picture posted on two sites counts twice.
- R-18 is Danbooru `rating:explicit`, Rule34 `rating:explicit`, and pixiv's R-18 search (with R-18G).
- The first 3 months: art uploaded up to 3 months after the character's first banner, art from before release included. Rule34 has no date search, so there it is by post id.
- A crossover is a picture that has both characters, through any of their tags on the site (pixiv: main tags first, then works found through the other tags).
- Alone and categories come from the posts' own tags, read from Rule34 and pixiv. Alone means no other character, no tag for several people or a partner. pixiv works carry fewer such tags, so alone is an upper bound there.
- Without AI art: Rule34 posts with an AI tag are taken out; pixiv numbers come from its own search without AI. Danbooru does not take AI art, so its numbers stay.
- Danbooru was down while the tags were read, so it has totals only. Its alone and category numbers on the page follow the shares on Rule34 and pixiv.

## License

[MIT](LICENSE)
