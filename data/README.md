# Data

The numbers behind https://rehnidergje.github.io/character-art-leaderboard/,
as plain CSV for reading and analysis (the site itself reads `docs/data/`,
which also has the character icons in it). Exported 2026-11-04; when each
game's counts were collected is in its `collected_at.txt`.

One folder per game (`zzz`, `genshin`, `hsr`), two files each.

## characters.csv

One row per character.

- `id`, `name`
- `release_date`: the date the character's first banner started; empty for
  characters that are not playable (NPCs) or not out yet
- `<site>_query`: the exact search used on that site. Several tags joined with
  OR (Danbooru `~a ~b`, Rule34 `( a ~ b )`, pixiv `a OR b`) count a picture once
  even when it has several of them; `-tag` excludes a tag
- `<site>_total`, `<site>_r18`: posts the search finds, and the R-18 part
  (Danbooru and Rule34 `rating:explicit`, pixiv's R-18 search including R-18G)
- `<site>_pair_tag`: the tag (or query) that stands for the character in pair
  searches
- `window_until`, `window_<site>_total`, `window_<site>_r18`: the same search
  limited to art uploaded up to 3 months after release (art from before release
  included). Danbooru and pixiv by date; Rule34 has no date search, so by post
  id (the last id uploaded on that day). `window_incomplete` is 1 when those
  3 months are not over yet. Characters with no release date have their
  all-time numbers here

Sites are separate columns; on the site, the chosen sites are added together,
so a picture posted on two sites counts twice there.

## pairs.csv

One row per pair and site: posts tagged with both characters' pair tags at once.

- `a`, `a_name`, `b`, `b_name`, `site`, `total`, `r18`
- `r18` is only counted for a pair with at least 20 posts on that site; empty
  below that
- Pairs with 0 posts are kept, so a 0 is a counted zero; a pair missing for a
  site was not counted there (on pixiv, Genshin pairs are only partly counted)

## Notes

- Some characters are merged from several forms: e.g. Wanderer includes
  Scaramouche (on Danbooru the wanderer tag implies the scaramouche tag), Herta
  includes The Herta, Firefly includes Sam. The query columns show what was
  searched.
- No images from these sites are included, only numbers.
