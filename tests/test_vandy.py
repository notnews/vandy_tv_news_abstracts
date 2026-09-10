import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from vandy_tv_news import cli, convert, parsers
from vandy_tv_news.spiders.broadcasts import BroadcastsSpider

FIXTURES = Path(__file__).parent / "fixtures"


def test_historical_program_and_broadcast():
    html = (FIXTURES / "historical.html").read_text()
    row = parsers.parse_program(html)[0]
    assert row["broadcast_order"] == 16
    assert row["program_duration"] == 1800
    for label in ["Reporter(s):", "Reporters:"]:
        detail = parsers.parse_broadcast(
            html.replace("Reporter(s):", label),
            "https://tvnews.vanderbilt.edu/broadcasts/100",
        )
        assert detail["broadcast_id"] == "100"
        assert detail["broadcast_order"] is None
        assert detail["broadcast_duration"] == 120
        assert detail["reporters"] == "Reporter, Example"


def test_api_ids_are_not_legacy_page_ids():
    rows = parsers.parse_api_segments(
        json.loads((FIXTURES / "segments.json").read_text())
    )
    assert rows[0]["segment_id"] == "H2crtJVGDd"
    assert rows[0]["broadcast_id"] is None
    assert rows[0]["date"] == "2025-05-01"
    assert rows[1]["broadcast_abstract"]


def test_shell_is_not_success():
    with pytest.raises(ValueError, match="index"):
        parsers.parse_site_index((FIXTURES / "app_shell.html").read_text())


def test_legacy_conversion_filter_and_order(tmp_path):
    source = tmp_path / "legacy.csv"
    source.write_text(
        "date,broadcast_order,broadcast_duration,broadcast_reporter(s)\n"
        "May 1 2025,100,00:02:00,Example\nMay 1 2019,200,00:00:10,Other\n"
    )
    out = tmp_path / "out.parquet"
    assert (
        cli.main(
            [
                "to-parquet",
                str(source),
                "--out",
                str(out),
                "--start",
                "2020",
                "--end",
                "2025",
            ]
        )
        == 0
    )
    table = pq.read_table(out)
    assert table.schema == convert.SCHEMA
    assert table.num_rows == 1
    assert table.to_pylist()[0]["broadcast_order"] is None
    assert table.to_pylist()[0]["broadcast_id"] == "100"


def test_spider_resume(tmp_path):
    out = tmp_path / "records.jsonl"
    out.write_text('{"segment_id":"abc"}\n')
    spider = BroadcastsSpider(start="2025-05", end="2025-05", out=str(out))
    assert "abc" in spider.seen
    with pytest.raises(ValueError, match="start"):
        BroadcastsSpider(start="2025-06", end="2025-05")
