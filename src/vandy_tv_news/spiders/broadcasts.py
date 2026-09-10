"""Collect segment metadata through Vanderbilt's public calendar API."""

import json
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlencode

import scrapy

from vandy_tv_news.checkpoint import prepare_checkpoint
from vandy_tv_news.parsers import parse_api_segments

API = "https://7itm2l2dz8.execute-api.us-east-1.amazonaws.com/prod"


class BroadcastsSpider(scrapy.Spider):
    """Append parsed segments and retain raw calendar/broadcast responses."""

    name = "broadcasts"

    def __init__(
        self, start=None, end=None, out="data/abstracts.jsonl", limit=None, **kwargs
    ):
        """Require a bounded month range and resume by API segment ID."""
        super().__init__(**kwargs)
        if not start or not end:
            raise ValueError("start and end are required in YYYY-MM format")
        self.first = date.fromisoformat(start + "-01")
        last = date.fromisoformat(end + "-01")
        self.stop = (last.replace(day=28) + timedelta(days=4)).replace(day=1)
        if self.first >= self.stop:
            raise ValueError("start must not follow end")
        self.out = Path(out)
        self.limit = int(limit) if limit is not None else None
        if self.limit is not None and self.limit < 1:
            raise ValueError("limit must be positive")
        self.written = 0
        self.failed = False
        prepare_checkpoint(self.out)
        self.seen = (
            {
                json.loads(line).get("segment_id")
                for line in self.out.read_text().splitlines()
                if line
            }
            if self.out.exists()
            else set()
        )

    async def start(self):
        """Schedule one calendar day at a time to avoid the API's size cap."""
        yield self.calendar_request(self.first)

    def calendar_request(self, day):
        """Build a request whose callback schedules the next day."""
        params = urlencode(
            {"startDate": day.isoformat(), "endDate": day.isoformat(), "size": 1000}
        )
        return scrapy.Request(
            f"{API}/broadcasts/calendar?{params}",
            callback=self.parse,
            cb_kwargs={"day": day},
            errback=self.failure,
        )

    def save_raw(self, name, response):
        """Save raw JSON atomically outside the tracked source tree."""
        path = self.out.parent / "raw" / (name + ".json")
        path.parent.mkdir(parents=True, exist_ok=True)
        part = path.with_suffix(".part")
        part.write_bytes(response.body)
        part.replace(path)

    def parse(self, response, day):
        """Read the day's broadcasts, rejecting malformed or truncated calendars."""
        payload = response.json()
        rows = payload.get("data")
        if not isinstance(rows, list) or len(rows) >= 1000:
            self.failed = True
            raise ValueError("invalid or possibly truncated calendar")
        self.save_raw(day.isoformat(), response)
        for item in rows:
            if item.get("net_dist_value") not in {"ABC", "CBS", "NBC", "CNN", "FNC"}:
                continue
            identifier = str(item["broadcast_id"])
            yield scrapy.Request(
                f"{API}/broadcasts/{identifier}?sort=ASC",
                callback=self.parse_segments,
                errback=self.failure,
            )
        next_day = day + timedelta(days=1)
        if next_day < self.stop and (self.limit is None or self.written < self.limit):
            yield self.calendar_request(next_day)

    def parse_segments(self, response):
        """Flush each segment before yielding it; stop at the exact requested limit."""
        try:
            rows = parse_api_segments(response.json())
        except (ValueError, KeyError):
            self.failed = True
            raise
        self.save_raw(rows[0]["program_id"], response)
        self.out.parent.mkdir(parents=True, exist_ok=True)
        with self.out.open("a", encoding="utf-8") as handle:
            for row in rows:
                if row["segment_id"] in self.seen:
                    continue
                if self.limit is not None and self.written >= self.limit:
                    return
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()
                self.seen.add(row["segment_id"])
                self.written += 1
                yield row

    def failure(self, failure):
        """Record failed requests so an interrupted run can be diagnosed."""
        self.failed = True
        self.out.parent.mkdir(parents=True, exist_ok=True)
        with (self.out.parent / "failures.jsonl").open("a") as handle:
            handle.write(
                json.dumps({"url": failure.request.url, "error": str(failure.value)})
                + "\n"
            )
        self.logger.error("request failed: %s", failure.value)
