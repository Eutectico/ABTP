from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List

import feedparser
from jinja2 import Environment, FileSystemLoader, Template

DEFAULT_TEMPLATE = """# Weekly Digest ({{ generated.strftime('%Y-%m-%d') }})

{% for item in items -%}
## {{ item.title }}
*Source:* [{{ item.feed_title }}]({{ item.link }})  
*Published:* {{ item.published }}

{{ item.summary }}

{% endfor -%}
"""


def load_template(path: Path | None) -> Template:
    if path and path.exists():
        env = Environment(loader=FileSystemLoader(str(path.parent)))
        return env.get_template(path.name)
    env = Environment()
    return env.from_string(DEFAULT_TEMPLATE)


def fetch_feed_items(urls: Iterable[str], since: datetime | None) -> List[dict]:
    items: List[dict] = []
    for url in urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            if since and published:
                published_dt = datetime(*published[:6])
                if published_dt < since:
                    continue
            items.append(
                {
                    "title": entry.get("title", "Untitled"),
                    "link": entry.get("link"),
                    "summary": entry.get("summary", ""),
                    "published": entry.get("published", ""),
                    "feed_title": feed.feed.get("title", url),
                }
            )
    items.sort(key=lambda item: item.get("published", ""), reverse=True)
    return items


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Markdown digest from RSS or Atom feeds.")
    parser.add_argument("feeds", nargs="+", help="Feed URLs.")
    parser.add_argument("--template", type=Path, help="Optional Jinja2 template file.")
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Only include entries from the last N days. Set to 0 to disable.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("digest.md"),
        help="Destination Markdown file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    since = datetime.utcnow() - timedelta(days=args.days) if args.days else None
    template = load_template(args.template)
    items = fetch_feed_items(args.feeds, since)
    output = template.render(items=items, generated=datetime.utcnow())
    args.output.write_text(output, encoding="utf-8")
    print(f"[OK] Digest written to {args.output}")


if __name__ == "__main__":
    main()
