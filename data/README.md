# Data

The numbers behind https://rehnidergje.github.io/character-art-leaderboard/,
as plain CSV for reading and analysis (the site itself reads `docs/data/`,
which also has the character icons in it). Exported 2026-11-08; when each
game's counts were collected is in its `collected_at.txt`.

One folder per game (`zzz`, `genshin`, `hsr`, `wuwa`), two files each.
`naruto` is here too, but not on the site yet: its numbers are still being checked.

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
- `<site>_pair_tag`: the tag or OR group that stands for the character in pair
  searches
- `window_until`, `window_<site>_total`, `window_<site>_r18`: the same search
  limited to art uploaded up to 3 months after release (art from before release
  included). Danbooru and pixiv by date; Rule34 has no date search, so by post
  id (the last id uploaded on that day). `window_incomplete` is 1 when those
  3 months are not over yet. Characters with no release date have their
  all-time numbers here
- `<site>_lead_pov_total`, `<site>_lead_pov_r18` and the same with `window_` in
  front (Danbooru and Rule34, the game's male lead only): his posts that also
  have `pov`, `male_pov`, `faceless_male` or `disembodied_penis`. They mark art
  where he is only the camera or a faceless partner. The site does not use them yet. pixiv has no such tags

Sites are separate columns; on the site, the chosen sites are added together,
so a picture posted on two sites counts twice there.

## pairs.csv

One row per pair and site: posts that have both characters.

- `a`, `a_name`, `b`, `b_name`, `site`, `total`, `r18`
- A character with several tags on a site is searched as an OR group, so a pair
  is `(a or b) (c or d)` on Danbooru and `( a ~ b ) ( c ~ d )` on Rule34. pixiv
  cannot join AND with OR: its pairs start from both main tags, then add works
  that show both characters through any of their other tags
- `r18` is only counted for a pair with at least 20 posts on that site; empty
  below that
- `window_total`, `window_r18`: up to 3 months after the newer character's
  release. A pair with a character with no release date has its all-time
  numbers here
- `lead_pov_total`, `lead_pov_r18`, `window_lead_pov_total`,
  `window_lead_pov_r18`: pairs of the male lead only, the same posts as in
  characters.csv
- Pairs with 0 posts are kept, so a 0 is a counted zero. A pair is missing for a
  site only when one of its characters has no usable tag there

## Notes

- Some characters are merged from several forms: e.g. Wanderer includes
  Scaramouche (on Danbooru the wanderer tag implies the scaramouche tag), Herta
  includes The Herta, Firefly includes Sam. The query columns show what was
  searched.
- The counts include AI art. The same numbers without it are in
  `docs/data/<game>/board_noai.json` and `pairs_noai.json`: Rule34 less its
  posts with an AI tag, pixiv from its own search without AI. Danbooru does not
  take AI art.
- Alone and category numbers are not in the CSV; they are in
  `docs/data/<game>/board.json` (and `board_noai.json`).
- No images from these sites are included, only numbers.
