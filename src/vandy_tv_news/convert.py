"""Stream historical CSV or current JSONL to an explicit Parquet schema."""

import csv
import gzip
import json
import sys
from datetime import date
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from vandy_tv_news.parsers import duration_seconds, iso_date

SCHEMA = pa.schema(
    [
        ("broadcast_id", pa.string()),
        ("segment_id", pa.string()),
        ("program_id", pa.string()),
        ("date", pa.date32()),
        ("network", pa.string()),
        ("program_title", pa.string()),
        ("program_duration", pa.int32()),
        ("broadcast_title", pa.string()),
        ("broadcast_duration", pa.int32()),
        ("broadcast_time", pa.string()),
        ("broadcast_order", pa.int32()),
        ("broadcast_abstract", pa.string()),
        ("reporters", pa.string()),
        ("url", pa.string()),
        ("source_kind", pa.string()),
    ]
)
csv.field_size_limit(sys.maxsize)


def rows(path: Path):
    """Read compressed CSV or new JSONL without loading the full corpus."""
    with (
        gzip.open(path, "rt", encoding="utf-8")
        if path.suffix == ".gz"
        else path.open(encoding="utf-8")
    ) as handle:
        legacy = not path.name.removesuffix(".gz").endswith(".jsonl")
        source = (
            csv.DictReader(handle)
            if legacy
            else (json.loads(line) for line in handle if line.strip())
        )
        for record in source:
            if legacy:
                record["broadcast_id"] = record.pop("broadcast_order", None)
                record["broadcast_order"] = None
                record["reporters"] = record.pop(
                    "broadcast_reporter(s)", None
                ) or record.get("reporter(s)")
                record["source_kind"] = "historical_csv"
            when = iso_date(record.get("date"))
            record["date"] = date.fromisoformat(when) if when else None
            for column in ("program_duration", "broadcast_duration"):
                record[column] = duration_seconds(record.get(column))
            yield {field.name: record.get(field.name) for field in SCHEMA}


def convert(
    paths: list[Path], out: Path, start: int | None = None, end: int | None = None
) -> int:
    """Write batches, filtering inclusively by calendar year when requested."""
    if start and end and start > end:
        raise ValueError("start year must not follow end year")
    out.parent.mkdir(parents=True, exist_ok=True)
    part = out.with_suffix(".parquet.part")
    count = 0
    with pq.ParquetWriter(part, SCHEMA, compression="zstd") as writer:
        batch = []
        for path in paths:
            for row in rows(path):
                when = row["date"]
                if (start or end) and (
                    when is None
                    or (start and when.year < start)
                    or (end and when.year > end)
                ):
                    continue
                batch.append(row)
                count += 1
                if len(batch) == 20_000:
                    writer.write_table(pa.Table.from_pylist(batch, schema=SCHEMA))
                    batch.clear()
        if batch:
            writer.write_table(pa.Table.from_pylist(batch, schema=SCHEMA))
    part.replace(out)
    return count
