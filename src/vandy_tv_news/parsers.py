"""Pure parsers for historical HTML and the current public metadata API."""

import re

from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_date

BASE = "https://tvnews.vanderbilt.edu"


def duration_seconds(value: str | int | None) -> int | None:
    """Convert HH:MM:SS or minute/hour descriptions to seconds."""
    if value is None or value == "":
        return None
    if isinstance(value, int):
        return value
    value = value.strip()
    if re.fullmatch(r"\d+:\d{2}:\d{2}", value):
        hours, minutes, seconds = map(int, value.split(":"))
        return hours * 3600 + minutes * 60 + seconds
    units = {"hour": 3600, "minute": 60, "second": 1}
    matches = re.findall(r"(\d+)\s*(hour|minute|second)s?", value)
    return sum(int(n) * units[unit] for n, unit in matches) if matches else None


def iso_date(value: str | None) -> str | None:
    """Parse a complete historical date, leaving missing dates null."""
    if not value or not re.search(r"\b(?:19|20)\d{2}\b", value):
        return None
    try:
        return parse_date(value, fuzzy=True).date().isoformat()
    except (ValueError, OverflowError):
        return None


def parse_month_index(html: str) -> list[str]:
    """Extract program/broadcast links from a historical month page."""
    soup = BeautifulSoup(html, "html.parser")
    links = [
        a["href"]
        for a in soup.select("li.elist_segment a[href], li.slist_segment a[href]")
    ]
    if not links:
        raise ValueError("unrecognized or empty historical month index")
    return list(dict.fromkeys(links))


def parse_site_index(html: str) -> list[str]:
    """Extract historical month index links; reject an app shell."""
    soup = BeautifulSoup(html, "html.parser")
    links = [
        a["href"]
        for a in soup.select("a[href]")
        if re.search(r"/siteindex/\d{4}-\d{2}", a["href"])
    ]
    if not links:
        raise ValueError("unrecognized historical site index; use the current API")
    return list(dict.fromkeys(links))


def parse_program(html: str) -> list[dict]:
    """Extract each historical listing as one unit, avoiding positional zip joins."""
    soup = BeautifulSoup(html, "html.parser")
    title = soup.select_one("h4.program-headline")
    duration = soup.select_one("p.program-duration")
    rows = []
    for listing in soup.select("li.listing"):
        link = listing.select_one("a[href]")
        order = listing.select_one("p.id em")
        stamp = listing.select_one("p.timestamp")
        if link is None:
            continue
        rows.append(
            {
                "url": BASE + link["href"],
                "broadcast_order": int(order.get_text(strip=True).lstrip("#"))
                if order
                else None,
                "broadcast_time": stamp.get_text(" ", strip=True) if stamp else None,
                "program_title": title.get_text(" ", strip=True).split(" for ")[0]
                if title
                else None,
                "program_duration": duration_seconds(duration.get_text())
                if duration
                else None,
            }
        )
    if not rows:
        raise ValueError("unrecognized or empty historical program")
    return rows


def parse_broadcast(html: str, url: str) -> dict:
    """Parse historical segment details; page ID is distinct from listing order."""
    soup = BeautifulSoup(html, "html.parser")
    title = soup.select_one("h4.video-title")
    if title is None:
        raise ValueError("unrecognized historical broadcast")
    info = soup.select_one("p.broadcast-info")
    description = soup.select_one("div.video-description")
    metadata = {}
    for term in soup.select("dl.video-meta dt"):
        value = term.find_next_sibling("dd")
        if value:
            metadata[term.get_text(strip=True)] = value.get_text(";", strip=True)
    reporters = next(
        (v for k, v in metadata.items() if re.fullmatch(r"Reporter(?:s|\(s\))?:", k)),
        None,
    )
    info = info.get_text(" ", strip=True) if info else ""
    return {
        "broadcast_id": url.rstrip("/").rsplit("/", 1)[-1],
        "broadcast_order": None,
        "date": iso_date(info.rsplit(" for ", 1)[-1]),
        "program_title": info.split(" for ")[0] or None,
        "broadcast_title": title.get_text(" ", strip=True),
        "broadcast_duration": duration_seconds(metadata.get("Duration:")),
        "broadcast_abstract": description.get_text(" ", strip=True)
        if description
        else None,
        "reporters": reporters,
        "url": url,
        "source_kind": "historical_html",
    }


def parse_api_segments(payload: dict) -> list[dict]:
    """Map API segment descriptions to abstracts; keep new IDs separate."""
    if not isinstance(payload.get("data"), list) or not payload["data"]:
        raise ValueError("missing API segments")
    rows = []
    for item in payload["data"]:
        segment = str(item["segment_id"])
        rows.append(
            {
                "segment_id": segment,
                "program_id": str(item["broadcast_id"]),
                "broadcast_id": str(item["legacy_segment_id"])
                if item.get("legacy_segment_id")
                else None,
                "broadcast_order": None,
                "date": iso_date(item.get("broadcast_date")),
                "program_title": item.get("broadcast_title"),
                "program_duration": duration_seconds(item.get("broadcast_duration")),
                "broadcast_title": item.get("segment_title"),
                "broadcast_duration": duration_seconds(item.get("segment_duration")),
                "broadcast_time": item.get("segment_start_time"),
                "broadcast_abstract": item.get("segment_description"),
                "reporters": None,
                "network": item.get("network_name"),
                "url": f"{BASE}/broadcasts/{item['broadcast_id']}",
                "source_kind": "api",
            }
        )
    return rows
