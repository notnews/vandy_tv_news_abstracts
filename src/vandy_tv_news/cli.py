"""Scrape, convert, and upload Vanderbilt segment abstracts."""

import argparse
import sys
from pathlib import Path

from vandy_tv_news import convert, upload


def main(argv: list[str] | None = None) -> int:
    """Run the selected command."""
    parser = argparse.ArgumentParser(prog="vandy-tv-news")
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("scrape")
    command.add_argument("--start", required=True)
    command.add_argument("--end", required=True)
    command.add_argument("--limit", type=int)
    command.add_argument("--out", type=Path, default=Path("data/abstracts.jsonl"))
    command = sub.add_parser("to-parquet")
    command.add_argument("inputs", nargs="+", type=Path)
    command.add_argument("--out", required=True, type=Path)
    command.add_argument("--start", type=int)
    command.add_argument("--end", type=int)
    command = sub.add_parser("upload")
    command.add_argument("file", type=Path)
    args = parser.parse_args(argv)
    if args.command == "upload":
        sys.stdout.write(upload.upload(args.file) + "\n")
        return 0
    if args.command == "to-parquet":
        count = convert.convert(args.inputs, args.out, args.start, args.end)
        sys.stdout.write(f"rows: {count}\n")
        return 0
    from scrapy.crawler import CrawlerProcess
    from scrapy.settings import Settings

    from vandy_tv_news.spiders.broadcasts import BroadcastsSpider

    settings = Settings()
    settings.setmodule("vandy_tv_news.settings")
    process = CrawlerProcess(settings)
    crawler = process.create_crawler(BroadcastsSpider)
    errors = []
    process.crawl(
        crawler, start=args.start, end=args.end, limit=args.limit, out=str(args.out)
    ).addErrback(errors.append)
    process.start()
    return int(
        bool(errors)
        or crawler.spider is None
        or crawler.spider.failed
        or bool(crawler.stats.get_value("spider_exceptions/count", 0))
    )
