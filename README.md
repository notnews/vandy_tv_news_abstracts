# Vanderbilt TV News Abstracts

[![CI](https://github.com/notnews/vandy_tv_news_abstracts/actions/workflows/ci.yml/badge.svg)](https://github.com/notnews/vandy_tv_news_abstracts/actions/workflows/ci.yml)
[![Data](https://img.shields.io/badge/data-Dataverse-blue)](https://doi.org/10.7910/DVN/BP2JXU)
[![Code license](https://img.shields.io/badge/code-MIT-green)](LICENSE)

Segment abstracts from the Vanderbilt Television News Archive, with tools to convert the historical CSV and collect public metadata using Scrapy. The site migrated to a JavaScript application; the old URLs now return an app shell.

## Data

| Files | Coverage | Rows | DOI |
|---|---|---:|---|
| `vandy.csv`, `html-vandy.tar.bz2.parta*`, `httpcach-vandy.tar.bz2` | 1968–2025-05-08 | See Dataverse | [BP2JXU](https://doi.org/10.7910/DVN/BP2JXU) |
| `vandy_2020_2025_data.tar.gz` | 2020–2025 | 226,594, historical documentation | Same DOI |
| `vandy_2020_2025_html.tar.gz` | 2020–2025 | Raw subset HTML | Same DOI |

Counts describe the releases or local files identified above. Dataverse metadata requests returned HTTP 403 on 2026-09-10, so historical release counts could not all be reverified.

## Column dictionary

| Columns | Type | Description |
|---|---|---|
| `broadcast_id` | string | Historical segment page ID; null for API rows without a legacy mapping |
| `segment_id`, `program_id` | string | New API segment and broadcast identifiers; not interchangeable with historical page IDs |
| `date`, `network` | date, string | Broadcast date and network where available |
| `program_title`, `broadcast_title` | string | Program and segment labels |
| `program_duration`, `broadcast_duration` | int32 | Seconds; “about” durations remain approximate |
| `broadcast_time` | string | Historical printed time range; current API start time is seconds since midnight as supplied |
| `broadcast_order` | int32 | Historical listing position when parsed from a program page; null in old CSV conversion and current API |
| `broadcast_abstract` | string | Historical abstract or current API segment description; API transcript text is not substituted |
| `reporters` | string | Historical Reporter(s)/Reporters metadata; current API role mapping is left null |
| `url`, `source_kind` | string | Source URL and `historical_html`, `historical_csv`, or `api` |

## Coverage and known gaps

Historical coverage includes ABC, CBS, NBC, CNN, and FNC. The new API includes additional networks; collection keeps these five for consistency. Calendar queries use individual days and reject responses reaching the requested cap rather than assuming completeness.

The old CSV stored page IDs in `broadcast_order`. Conversion moves that value to `broadcast_id`; actual listing positions cannot be recovered from that column. New API IDs are alphanumeric, and observed legacy mappings are null.

Known archive defects from the original notes: one malformed metadata block, six missing durations, two missing broadcasts, and 45 missing-program references. The exact URLs remain in [historical NOTES.md](https://github.com/notnews/vandy_tv_news_abstracts/blob/901bd99/NOTES.md). These are observed examples, not corpus-wide defect rates.

No historical live HTML was available during cleanup. Historical selector tests use explicitly labeled synthetic fixtures; current API tests use captured responses.

## Collection methods

| Era | Method |
|---|---|
| Historical corpus | Site index → month indexes → program listings → segment pages, using Scrapy |
| Current website | Public calendar API → broadcast segment API; Scrapy retains raw JSON and appends one record per segment |

The current endpoint is discovered from the site's published application bundle. Raw JSON lives beside the checkpoint under `raw/`; Scrapy's HTTP cache is stored under `.scrapy/data/httpcache`. Historical HTML parsers remain available for offline use. The original cache export belongs to the old routes and is not a current API checkpoint.

The pre-cleanup implementation is preserved at [901bd99](https://github.com/notnews/vandy_tv_news_abstracts/tree/901bd99). New fetches write checkpoints under `data/`; reruns skip successful records and retry failures. Pure parsers read saved responses without accessing the network. Fixture provenance is in [tests/fixtures/SOURCES.md](tests/fixtures/SOURCES.md).

An interrupted, unterminated final JSONL record is removed before resuming; complete records are preserved. A valid final record missing only its newline is retained. Malformed complete lines remain errors.

## Usage

Python 3.12 or later and [uv](https://docs.astral.sh/uv/) are required. Run these commands from the repository root. Keep downloaded inputs and generated files under ignored `data/`.

### Install

```sh
uv sync --frozen --group dev
```

### Collect

```sh
uv run vandy-tv-news scrape --start 2025-05 --end 2025-05 --limit 20
uv run scrapy crawl broadcasts -a start=2025-05 -a end=2025-05 -a limit=20
```

### Convert

```sh
uv run vandy-tv-news to-parquet data/abstracts.jsonl --out data/abstracts.parquet
uv run vandy-tv-news to-parquet data/vandy.csv --start 2020 --end 2025 --out data/vandy_2020_2025.parquet
```

### Upload

The `upload` command reads `DATAVERSE_API_TOKEN` from the environment and adds the specified file to Dataverse. It does not publish a dataset version.

```sh
uv run vandy-tv-news upload data/abstracts.parquet
```

## Development

Run the local checks:

```sh
make check
```

This runs Ruff, formatting, pytest, and pre-commit. Run `make ci-docker` to check lint and tests in standard Python 3.12 and 3.14 Docker images. CI uses the same lockfile and checks. Install the Git hooks with `uv run pre-commit install`.

## Citation

Use [CITATION.cff](CITATION.cff) and cite the relevant [Dataverse release](https://doi.org/10.7910/DVN/BP2JXU), including its version and DOI.

## License

Code is [MIT licensed](LICENSE). News text, abstracts, and archived pages retain their owners' rights; a code license does not grant rights to those materials. Consult the terms of the linked data release.
