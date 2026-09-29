"""Runtime configuration and upstream feed constants for the ShadowCast feed archiver."""

from __future__ import annotations

import os
from dataclasses import dataclass

USER_AGENT = "shadowcast-archiver/0.1 (+https://github.com/tsathya98/shadowcast)"

GDACS_API = "https://www.gdacs.org/gdacsapi/api"
SACHET_RSS = "https://sachet.ndma.gov.in/cap_public_website/rss/rss_{slug}.xml"
IBTRACS_ACTIVE_CSV = (
    "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs"
    "/v04r01/access/csv/ibtracs.ACTIVE.list.v04r01.csv"
)
OPEN_METEO_ENSEMBLE = "https://ensemble-api.open-meteo.com/v1/ensemble"
WEATHERNEXT2_MODEL = "google_weathernext2_ensemble"
WEATHERNEXT2_VARIABLES = ("wind_speed_10m", "wind_gusts_10m", "precipitation", "pressure_msl")

# North Indian Ocean basin (Bay of Bengal + Arabian Sea): lon_min, lat_min, lon_max, lat_max.
NORTH_INDIAN_BASIN = (30.0, -5.0, 100.0, 35.0)

# NDMA SACHET feed slugs for India and its coastal states / UTs (verified 26 Sep 2026).
# The "india" feed is archived as RSS only; CAP documents are fetched from the coastal feeds.
SACHET_NATIONAL_SLUG = "india"
SACHET_COASTAL_SLUGS = (
    "odisha",
    "andhra",
    "tamil",
    "west",
    "puducherry",
    "andaman",
    "gujarat",
    "maharashtra",
    "goa",
    "karnataka",
    "kerala",
    "lakshadweep",
)

# Coastal district headquarters sampled for WeatherNext 2 ensemble snapshots: (name, lat, lon).
COASTAL_POINTS = (
    ("balasore", 21.49, 86.93),
    ("bhadrak", 21.06, 86.50),
    ("kendrapara", 20.50, 86.42),
    ("jagatsinghpur", 20.26, 86.17),
    ("puri", 19.81, 85.83),
    ("berhampur", 19.31, 84.79),
    ("visakhapatnam", 17.69, 83.22),
    ("kakinada", 16.99, 82.25),
    ("machilipatnam", 16.19, 81.14),
    ("nellore", 14.44, 79.99),
    ("chennai", 13.08, 80.27),
    ("cuddalore", 11.75, 79.77),
    ("nagapattinam", 10.77, 79.84),
    ("digha", 21.63, 87.51),
    ("port_blair", 11.62, 92.73),
    ("porbandar", 21.64, 69.61),
    ("mumbai", 19.08, 72.88),
    ("kochi", 9.93, 76.27),
)


@dataclass(frozen=True)
class Settings:
    """Archiver settings resolved from the environment.

    Attributes:
        bucket: GCS bucket the archive is written to.
        gdacs_lookback_days: How many days of GDACS cyclone events to include per run.
        forecast_days: WeatherNext 2 forecast horizon requested from Open-Meteo.
        http_timeout_s: Per-request timeout in seconds.
        max_concurrency: Upper bound on simultaneous upstream requests.
        max_attempts: Attempts per request before giving up (retries on 429/5xx and transport errors).
        retry_backoff_s: Base delay for exponential backoff between attempts.
    """

    bucket: str = "argmax-cyclone-2026-archive"
    gdacs_lookback_days: int = 10
    forecast_days: int = 10
    http_timeout_s: float = 60.0
    max_concurrency: int = 8
    max_attempts: int = 3
    retry_backoff_s: float = 2.0

    @classmethod
    def from_env(cls) -> Settings:
        """Build settings from ``ARCHIVE_*`` environment variables, falling back to defaults.

        Returns:
            Settings: The resolved configuration.

        Raises:
            ValueError: If a numeric variable cannot be parsed.
        """
        env = os.environ
        return cls(
            bucket=env.get("ARCHIVE_BUCKET") or cls.bucket,
            gdacs_lookback_days=int(env.get("ARCHIVE_GDACS_LOOKBACK_DAYS", cls.gdacs_lookback_days)),
            forecast_days=int(env.get("ARCHIVE_FORECAST_DAYS", cls.forecast_days)),
            http_timeout_s=float(env.get("ARCHIVE_HTTP_TIMEOUT_S", cls.http_timeout_s)),
            max_concurrency=int(env.get("ARCHIVE_MAX_CONCURRENCY", cls.max_concurrency)),
            max_attempts=int(env.get("ARCHIVE_MAX_ATTEMPTS", cls.max_attempts)),
            retry_backoff_s=float(env.get("ARCHIVE_RETRY_BACKOFF_S", cls.retry_backoff_s)),
        )
