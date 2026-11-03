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

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Character Art Leaderboard</title>
<meta name="description" content="How much fan art each character of Zenless Zone Zero, Genshin Impact and Honkai: Star Rail has on Danbooru, Rule34 and pixiv, the R-18 share, and who is drawn together.">
<style>
:root {
  color-scheme: light dark;
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
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #262624; --color-panel: #30302e; --color-fg: #f5f4ef; --color-fg-muted: #a6a39a;
    --color-border-line: rgb(255 255 255 / .14); --color-warn: #e0a440;
    --cds-border: rgb(255 255 255 / .12); --cds-chart-grid: rgb(255 255 255 / .08);
    --cds-surface-popover: #30302e; --cds-shadow-popover: 0 8px 24px #00000052, 0 2px 6px #0003;
    --cds-text-secondary: #a6a39a;
  }
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
    for blob, (folder, file) in links.items():
        (DOCS / folder).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, DOCS / folder / file.name)
        page = page.replace(blob, f"{folder}/{file.name}")
    left = re.findall(r"/_blob/[0-9a-f]+", page)
    if left:
        sys.exit(f"stored files with no local copy: {sorted(set(left))}")

    out = (TEMPLATE.replace("__DATASETS__", json.dumps(datasets))
           .replace("__D3__", D3)
           .replace("__DATE__", html.escape(datetime.date.today().isoformat()))
           .replace("__PAGE__", page))
    (DOCS / "index.html").write_text(out, encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {DOCS / 'index.html'}: {len(datasets) // 2} games, {len(links)} local files")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
