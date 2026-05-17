#!/usr/bin/env python3
"""Extract 2020-2025 data and HTML files into clean archives."""

import json
import re
import shutil
import subprocess
import tarfile
from pathlib import Path


def load_jsonl(filepath: Path) -> list[dict]:
    """Load JSONL file."""
    records = []
    with open(filepath, "r") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def save_jsonl(records: list[dict], filepath: Path) -> None:
    """Save records to JSONL file."""
    with open(filepath, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")


def extract_year(date_str: str) -> int | None:
    """Extract year from date string like 'Thursday, Aug 29, 1968'."""
    if not date_str:
        return None
    match = re.search(r"\b(19\d{2}|20\d{2})\b", date_str)
    return int(match.group(1)) if match else None


def filter_2020_2025(records: list[dict]) -> list[dict]:
    """Filter records to only those from 2020-2025."""
    filtered = []
    for record in records:
        date_str = record.get("date", "")
        year = extract_year(date_str)
        if year and 2020 <= year <= 2025:
            record["year"] = year
            filtered.append(record)
    return filtered


def copy_html_files(
    records: list[dict], src_dir: Path, dest_dir: Path
) -> tuple[int, int]:
    """Copy HTML files for the given records (handles .html.gz)."""
    dest_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    missing = 0

    for record in records:
        broadcast_order = record.get("broadcast_order")
        if not broadcast_order:
            continue

        src_file = src_dir / f"{broadcast_order}.html.gz"
        if src_file.exists():
            shutil.copy2(src_file, dest_dir / f"{broadcast_order}.html.gz")
            copied += 1
        else:
            missing += 1

    return copied, missing


def create_tar_gz(source_path: Path, archive_path: Path) -> None:
    """Create a tar.gz archive."""
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(source_path, arcname=source_path.name)


def main():
    base_dir = Path(__file__).parent
    broadcasts_clean = base_dir / "broadcasts_clean.jsonl"
    html_dir = base_dir / "html" / "broadcasts"

    print("Loading broadcasts_clean.jsonl...")
    records = load_jsonl(broadcasts_clean)
    print(f"  Total records: {len(records)}")

    print("\nFiltering to 2020-2025...")
    filtered = filter_2020_2025(records)
    print(f"  2020-2025 records: {len(filtered)}")

    year_counts = {}
    for r in filtered:
        y = r.get("year")
        year_counts[y] = year_counts.get(y, 0) + 1
    print("  By year:")
    for y in sorted(year_counts.keys()):
        print(f"    {y}: {year_counts[y]}")

    jsonl_output = base_dir / "vandy_2020_2025.jsonl"
    print(f"\nSaving filtered data to {jsonl_output.name}...")
    save_jsonl(filtered, jsonl_output)

    html_dest = base_dir / "html_2020_2025" / "broadcasts"
    print(f"\nCopying HTML files to {html_dest.parent.name}/...")
    copied, missing = copy_html_files(filtered, html_dir, html_dest)
    print(f"  Copied: {copied}")
    print(f"  Missing: {missing}")

    data_archive = base_dir / "vandy_2020_2025_data.tar.gz"
    print(f"\nCreating {data_archive.name}...")
    with tarfile.open(data_archive, "w:gz") as tar:
        tar.add(jsonl_output, arcname="vandy_2020_2025.jsonl")
    data_size = data_archive.stat().st_size / (1024 * 1024)
    print(f"  Size: {data_size:.1f} MB")

    html_archive = base_dir / "vandy_2020_2025_html.tar.gz"
    print(f"\nCreating {html_archive.name}...")
    create_tar_gz(html_dest.parent, html_archive)
    html_size = html_archive.stat().st_size / (1024 * 1024)
    print(f"  Size: {html_size:.1f} MB")

    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  JSONL records: {len(filtered)}")
    print(f"  HTML files: {copied}")
    print(f"  Data archive: {data_archive.name} ({data_size:.1f} MB)")
    print(f"  HTML archive: {html_archive.name} ({html_size:.1f} MB)")

    print("\nVerification:")
    with tarfile.open(data_archive, "r:gz") as tar:
        members = tar.getnames()
        print(f"  Data archive contents: {members}")

    result = subprocess.run(
        ["tar", "-tzf", str(html_archive)],
        capture_output=True,
        text=True,
    )
    html_count = len([l for l in result.stdout.strip().split("\n") if ".html" in l])
    print(f"  HTML archive file count: {html_count}")

    if html_count == len(filtered):
        print("\n✓ Verification passed: HTML count matches record count")
    else:
        print(f"\n⚠ Warning: HTML count ({html_count}) != record count ({len(filtered)})")


if __name__ == "__main__":
    main()
