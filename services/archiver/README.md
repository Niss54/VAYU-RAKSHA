# ShadowCast feed archiver

A Cloud Run Job that snapshots the cyclone feeds that have **no public history** every 6 hours. Any storm, including one forming during judging, can then be replayed later with the forecasts and warnings *as they were issued*, not with hindsight.

| Source | What is archived | Why |
|---|---|---|
| `gdacs` | North Indian Ocean tropical-cyclone events: listing, event details, GeoJSON geometry (track, forecast points, wind buffers, cone) | As-issued forecast cones |
| `sachet` | NDMA SACHET CAP 1.2 RSS for India and 12 coastal states/UTs, plus every linked CAP alert document | Official multilingual warnings and alert polygons |
| `ibtracs` | IBTrACS provisional file of active storms | Near-real-time best track |
| `weathernext2` | Google WeatherNext 2, 64-member ensemble (wind, gusts, rain, MSLP) at 18 coastal district HQs via Open-Meteo | Open-Meteo serves only the latest run |

ECMWF ensemble track files are **not** archived here: ECMWF's Google Cloud mirror (`gs://ecmwf-open-data`) already keeps their full history.

## Layout

```
{source}/{YYYY}/{MM}/{DD}/{HHMM}Z/...        raw artifacts, byte-for-byte as served
manifests/{YYYY}/{MM}/{DD}/{HHMM}Z.json      per-run status: files, bytes or error per source
```

A failing source is recorded in the manifest and never blocks the others. The job exits non-zero only if every source fails.

## Develop

```bash
uv sync
uv run ruff check . && uv run ruff format --check . && uv run pyright && uv run pytest
uv run python -m shadowcast_archiver          # writes to ./archive when ARCHIVE_BUCKET is unset
```

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `ARCHIVE_BUCKET` | `argmax-cyclone-2026-archive` | GCS bucket the archive is written to (the only store) |
| `ARCHIVE_GDACS_LOOKBACK_DAYS` | `10` | GDACS event window |
| `ARCHIVE_FORECAST_DAYS` | `10` | WeatherNext 2 horizon |
| `ARCHIVE_HTTP_TIMEOUT_S` | `60` | Per-request timeout |
| `ARCHIVE_MAX_CONCURRENCY` | `8` | Concurrent upstream requests |
| `ARCHIVE_MAX_ATTEMPTS` | `3` | Attempts per request (retries 429/5xx and transport errors) |
| `ARCHIVE_RETRY_BACKOFF_S` | `2` | Exponential backoff base |

Deploy with [`infra/archiver.sh`](../../infra/archiver.sh).
