"""Builds the static site in docs/ from a TagStats checkout.

    python build.py <path to TagStats>

TagStats writes the page (reports/dashboard/dashboard_doc.json, made by
`python -m tagstats dashboard ...`) and each game's data
(reports/<report>/leaderboard.json and pairs_rows.json). This copies them into
docs/, points the page's stored files (/_blob/... links: game logos and site
icons) at local copies, and wraps the page in docs/index.html with the theme
and dash-lite.js, which runs it without the dashboard runtime.
"""

import datetime
import html
import json
import pathlib
import re
import shutil
import sys

import yaml

HERE = pathlib.Path(__file__).parent
DOCS = HERE / "docs"
D3 = "https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"
# the network draws with PixiJS (WebGL) where it is loaded
PIXI = "https://cdn.jsdelivr.net/npm/pixi.js@8.22.0/dist/pixi.min.js"

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Character Art Leaderboard</title>
<meta name="description" content="How much fan art each character of Zenless Zone Zero, Genshin Impact, Honkai: Star Rail and Wuthering Waves has on Danbooru, Rule34 and pixiv, the R-18 share, and who is drawn together.">
<!-- the card a shared link shows (Discord, Telegram, Reddit, X): docs/preview.png -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://rehnidergje.github.io/character-art-leaderboard/">
<meta property="og:title" content="Character Art Leaderboard">
<meta property="og:description" content="How much fan art each Zenless Zone Zero, Genshin Impact, Honkai: Star Rail and Wuthering Waves character has, the R-18 share, and who gets drawn together.">
<meta property="og:image" content="https://rehnidergje.github.io/character-art-leaderboard/preview.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<!-- the theme before anything is drawn: the one picked with the page's button, else the system's -->
<script>
var saved = null;
try { saved = localStorage.getItem('tagstats-theme'); } catch (e) {}
document.documentElement.dataset.theme = saved === 'light' || saved === 'dark' ? saved
  : matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
</script>
<style>
:root {
  color-scheme: light;
  --color-bg: #faf9f5; --color-panel: #ffffff; --color-fg: #141413; --color-fg-muted: #6b6a65;
  --color-border-line: rgb(20 20 19 / .13); --color-warn: #a86a00;
  --cds-border: rgb(20 20 19 / .1); --cds-chart-grid: rgb(20 20 19 / .08);
  --cds-surface-popover: #ffffff; --cds-shadow-popover: 0 8px 24px #0000001f, 0 2px 6px #00000014;
  --cds-text-secondary: #6b6a65;
  --cds-dur-slow: .45s;
  --cds-font-size-body: .8125rem; --cds-font-size-caption: .6875rem; --cds-font-size-heading: .875rem; --cds-font-size-title: 1.25rem;
  --cds-font-weight-medium: 500;
  --cds-gap-xs: .375rem; --cds-gap-sm: .5rem; --cds-gap-md: .75rem; --cds-gap-xl: 2rem;
  --cds-pad-xs: .25rem; --cds-pad-sm: .375rem; --cds-pad-md: .5rem; --cds-pad-lg: .75rem;
  --cds-radius: .375rem;
  --font-anthropic-sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-anthropic-serif: ui-serif, Georgia, "Times New Roman", serif;
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --color-bg: #262624; --color-panel: #30302e; --color-fg: #f5f4ef; --color-fg-muted: #a6a39a;
  --color-border-line: rgb(255 255 255 / .14); --color-warn: #e0a440;
  --cds-border: rgb(255 255 255 / .12); --cds-chart-grid: rgb(255 255 255 / .08);
  --cds-surface-popover: #30302e; --cds-shadow-popover: 0 8px 24px #00000052, 0 2px 6px #0003;
  --cds-text-secondary: #a6a39a;
}
[hidden] { display: none !important; }
.dash-loading body::after { content: ''; position: fixed; top: 14px; right: 18px; z-index: 10; width: 20px; height: 20px; border: 2.5px solid var(--color-border-line); border-top-color: var(--color-fg); border-radius: 50%; animation: dash-spin .7s linear infinite; }
@keyframes dash-spin { to { transform: rotate(1turn); } }
body { margin: 0; background: var(--color-bg); color: var(--color-fg); font-family: var(--font-anthropic-sans); font-size: var(--cds-font-size-body); line-height: 1.45; }
#dash-root { max-width: 1240px; margin: 0 auto; padding: 24px 16px 32px; }
.site-foot { max-width: 1240px; margin: 0 auto; padding: 0 16px 32px; color: var(--color-fg-muted); font-size: var(--cds-font-size-caption); }
</style>
<script>window.DASH_DATASETS = __DATASETS__;</script>
<script src="__D3__"></script>
<script src="__PIXI__"></script>
<script src="dash-lite.js"></script>
</head>
<body>
<div id="dash-root">
__PAGE__
</div>
<footer class="site-foot">Counts of tag searches on Danbooru, Rule34 and pixiv, collected __DATE__. Only numbers are shown, no pictures from those sites. Character icons from the games' fandom wikis, © their publishers.</footer>
</body>
</html>
"""


DATA = HERE / "data"
SITES = ("danbooru", "rule34", "pixiv")
DATA_README = """# Data

The numbers behind https://rehnidergje.github.io/character-art-leaderboard/,
as plain CSV for reading and analysis (the site itself reads `docs/data/`,
which also has the character icons in it). Exported __DATE__; when each
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
"""


def export_data(tagstats, config, game):
    """Readable copies of a game's data in data/<game>/: characters.csv (counts,
    the queries searched, release window) and pairs.csv."""
    import csv
    sys.path.insert(0, str(tagstats))
    from tagstats import collect, pairs

    report = tagstats / "reports" / config["report"]
    leaderboard = json.loads((report / "leaderboard.json").read_text(encoding="utf-8"))
    board = leaderboard["rows"]
    run = json.loads(collect.latest_run(config).read_text(encoding="utf-8"))["results"]
    pair_tags = {site: pairs.main_tags(config, site) for site in SITES}
    names = {r["id"]: r["name"] for r in board}
    out = DATA / game
    out.mkdir(parents=True, exist_ok=True)
    (out / "collected_at.txt").write_text(str(leaderboard.get("collected_at", "")) + "\n", encoding="utf-8")

    fields = ["id", "name", "release_date"]
    fields += [f"{s}_{k}" for s in SITES for k in ("query", "total", "r18", "pair_tag")]
    fields += ["window_until", "window_incomplete"] + [f"window_{s}_{k}" for s in SITES for k in ("total", "r18")]
    fields += [f"{w}{s}_lead_pov_{k}" for w in ("", "window_") for s in ("danbooru", "rule34") for k in ("total", "r18")]
    with open(out / "characters.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        for r in board:
            row = {"id": r["id"], "name": r["name"], "release_date": r.get("release") or "",
                   "window_until": r.get("w_until") or "", "window_incomplete": int(bool(r.get("w_incomplete")))}
            for s in SITES:
                row[f"{s}_query"] = (run.get(r["id"], {}).get(s) or {}).get("query", "")
                row[f"{s}_total"] = r.get(f"{s}_total")
                row[f"{s}_r18"] = r.get(f"{s}_r18")
                row[f"{s}_pair_tag"] = pair_tags[s].get(r["id"], "")
                row[f"window_{s}_total"] = r.get(f"w_{s}_total")
                row[f"window_{s}_r18"] = r.get(f"w_{s}_r18")
            for s in ("danbooru", "rule34"):
                row[f"{s}_lead_pov_total"] = r.get(f"{s}_si_total")
                row[f"{s}_lead_pov_r18"] = r.get(f"{s}_si_r18")
                row[f"window_{s}_lead_pov_total"] = r.get(f"w_{s}_si_total")
                row[f"window_{s}_lead_pov_r18"] = r.get(f"w_{s}_si_r18")
            w.writerow(row)

    rows = json.loads((report / "pairs_rows.json").read_text(encoding="utf-8"))["rows"]
    with open(out / "pairs.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["a", "a_name", "b", "b_name", "site", "total", "r18", "window_total", "window_r18",
                    "lead_pov_total", "lead_pov_r18", "window_lead_pov_total", "window_lead_pov_r18"])
        for p in sorted(rows, key=lambda p: (p["site"], -(p["total"] or 0))):
            w.writerow([p["a"], names.get(p["a"], p["a"]), p["b"], names.get(p["b"], p["b"]), p["site"], p["total"], p["r18"],
                        p.get("w_total"), p.get("w_r18"), p.get("si_total"), p.get("si_r18"), p.get("w_si_total"), p.get("w_si_r18")])


def main(tagstats):
    tagstats = pathlib.Path(tagstats)
    page = json.loads((tagstats / "reports/dashboard/dashboard_doc.json").read_text(encoding="utf-8"))["text"]
    page = page.replace('<meta name="dash-one-writer">', "").strip()

    # the page's stored files -> local copies
    links = {}
    source = (tagstats / "tagstats/dashboard.py").read_text(encoding="utf-8")
    block = re.search(r"SITE_ICON = \{(.*?)\}", source, re.S).group(1)
    for site, blob in re.findall(r'"(\w+)":\s*"(/_blob/[0-9a-f]+)"', block):
        file = next((tagstats / "assets/sites").glob(f"{site}.*"))
        links[blob] = ("assets/sites", file)
    datasets = {}
    for path in sorted((tagstats / "configs").glob("*.yaml")):
        config = yaml.safe_load(path.read_text(encoding="utf-8"))
        game = config.get("game")
        if not game or config.get("logo_url") not in page:
            continue
        links[config["logo_url"]] = ("assets/logos", tagstats / config["logo"])
        report = tagstats / "reports" / config["report"]
        target = DOCS / "data" / game
        target.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(report / "leaderboard.json", target / "board.json")
        shutil.copyfile(report / "pairs_rows.json", target / "pairs.json")
        datasets[f"board_{game}"] = f"data/{game}/board.json"
        datasets[f"pairs_{game}"] = f"data/{game}/pairs.json"
        # the same without AI art (python -m tagstats no-ai), for the page's AI switch
        for name, file in (("board", "leaderboard_noai.json"), ("pairs", "pairs_rows_noai.json")):
            if (report / file).exists():
                shutil.copyfile(report / file, target / f"{name}_noai.json")
                datasets[f"{name}_noai_{game}"] = f"data/{game}/{name}_noai.json"
        export_data(tagstats, config, game)
    for blob, (folder, file) in links.items():
        (DOCS / folder).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, DOCS / folder / file.name)
        page = page.replace(blob, f"{folder}/{file.name}")
    left = re.findall(r"/_blob/[0-9a-f]+", page)
    if left:
        sys.exit(f"stored files with no local copy: {sorted(set(left))}")

    out = (TEMPLATE.replace("__DATASETS__", json.dumps(datasets))
           .replace("__D3__", D3)
           .replace("__PIXI__", PIXI)
           .replace("__DATE__", html.escape(datetime.date.today().isoformat()))
           .replace("__PAGE__", page))
    (DOCS / "index.html").write_text(out, encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (DATA / "README.md").write_text(DATA_README.replace("__DATE__", datetime.date.today().isoformat()), encoding="utf-8")
    games = len([k for k in datasets if k.startswith("board_") and "_noai_" not in k])
    print(f"Built {DOCS / 'index.html'}: {games} games, {len(links)} local files")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
