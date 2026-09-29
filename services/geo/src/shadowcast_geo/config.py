"""Scenarios, regions, datasets and runtime settings for the ShadowCast geo service."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

USER_AGENT = "shadowcast-geo/0.1 (+https://github.com/tsathya98/shadowcast)"

IBTRACS_NI_CSV = (
    "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs"
    "/v04r01/access/csv/ibtracs.NI.list.v04r01.csv"
)
OVERPASS_URLS = ("https://overpass.kumi.systems/api/interpreter", "https://overpass-api.de/api/interpreter")
OSDMA_SHELTERS_URL = "https://www.osdma.org/preparedness/multi-purpose-cyclone-flood-shelters/"
# ECMWF open data mirrored on Google Cloud Storage; keeps full history from 2024 onwards.
ECMWF_OPEN_DATA = "https://storage.googleapis.com/ecmwf-open-data"
ECMWF_TRACK_STEPS = (360, 240)  # tropical-cyclone track files are named -360h- since 2026 and -240h- before
IMD_REPORTS = "https://rsmcnewdelhi.imd.gov.in/uploads/report/26"  # RSMC New Delhi cyclone reports

# Earth Engine datasets.
NIGHT_LIGHTS = "NASA/VIIRS/002/VNP46A2"
NIGHT_LIGHTS_BAND = "DNB_BRDF_Corrected_NTL"  # raw radiance; the gap-filled band hides post-storm blackouts
NIGHT_LIGHTS_QUALITY_BAND = "Mandatory_Quality_Flag"  # 0/1 = high-quality retrieval
NIGHT_LIGHTS_DISPLAY_MAX = 30.0  # nW/cm2/sr at full brightness in the evidence images
NIGHT_LIGHTS_PALETTE = ["0e1012", "f28a2e", "ffe2b0"]  # the console's void to amber
NIGHT_LIGHTS_IMAGE_PX = 900
EVIDENCE_IMAGES = ("night-lights-pre", "night-lights-post")
POPULATION = "WorldPop/GP/100m/pop"
POPULATION_YEAR = 2020
RAINFALL = "NASA/GPM_L3/IMERG_V07"  # half-hourly satellite precipitation (mm/h), the rainfall truth
RAINFALL_BAND = "precipitation"
RAINFALL_SCALE_M = 11132  # IMERG's native 0.1 degree
RAINFALL_WINDOW_DAYS = 3  # storm totals are taken from this many days before landfall to as many after
DISTRICTS = "projects/sat-io/open-datasets/geoboundaries/CGAZ_ADM2"  # geoBoundaries ADM2, CC BY 4.0
ELEVATION = "COPERNICUS/DEM/GLO30_2024_1"  # a surface model: reads roofs and canopy, used only inland
# Bare-earth coastal terrain (Pronk et al. 2024, CC BY 4.0), so surge is compared with the ground, not the rooftops.
COASTAL_DTM = "projects/sat-io/open-datasets/DELTARES/deltadtm_v1"
BATHYMETRY = "NOAA/NGDC/ETOPO1"  # 1 arc-minute bedrock relief: negative below sea level
BATHYMETRY_BAND = "bedrock"

# Physical and modelling constants.
EARTH_RADIUS_KM = 6371.0
NM_TO_KM = 1.852
KT_PER_MS = 1.943844
HOLLAND_B = 1.5  # Holland (1980) profile shape parameter; 1.5 is the conventional mid-range value
DENSIFY_STEP_MINUTES = 15  # hazard time step; 3-hourly best tracks miss the eyewall at near-track assets
WIND_BANDS_KT = (34, 50, 64)
GALE_KT = 34.0
ENSEMBLE_MATCH_KM = 150.0  # a member "hits" the target when its track passes within this distance
POPULATION_RADIUS_M = 2000
NIGHT_LIGHTS_RADIUS_M = 1500
LIT_RADIANCE = 1.0  # nW/cm2/sr; below this, percentage loss is dominated by noise
OUTAGE_LOSS_PCT = 50.0  # an asset "lost power" when its night-light radiance fell by at least this much
HOLDOUT_FOLDS = 5  # spatial cross-validation blocks along the reference coast
LOW_LYING_M = 5.0
LOSS_BANDS_KT = (0, 60, 80, 100, 130)

# R-CLIPER parametric rain rate (Tuleya et al. 2007, the NHC defaults as bias-adjusted): each parameter is a + b * U
# with U = 1 + (Vmax - 35 kt) / 33; rates in inches/day, radii in km.
RCLIPER = {"t0": (-1.10, 3.96), "tm": (-1.60, 4.80), "rm": (64.5, -13.0), "re": (150.0, -16.0)}
MM_PER_H_PER_IN_PER_DAY = 25.4 / 24
EXTREME_RAIN_MM = 204.5  # IMD's "extremely heavy" rainfall threshold (24 h); used here for storm totals

# Illustrative parametric cover (see insurance.py): the index is the wind reached at this share of a district's sites,
# and payouts step up at the Saffir-Simpson category 1-3 thresholds.
TRIGGER_SHARE = 0.25
PAYOUT_TIERS_KT = ((64.0, 0.25), (83.0, 0.5), (96.0, 1.0))

# Arterial roads (see roads.py): OSM classes kept, sampling step, and the winds that cut a road or put it at risk.
ROAD_HIGHWAYS = ("motorway", "trunk", "primary")
ROAD_SAMPLE_KM = 1.0
# IMD's damage classes: an extremely severe cyclonic storm (90 kt and above) brings "disruption of rail/road link at
# several places"; from very severe (64 kt) roads take damage and travel becomes unsafe.
ROAD_CUT_KT = 90.0
ROAD_RISK_KT = 64.0
ACCESS_RADIUS_KM = 10.0  # a site further than this from an arterial road has no arterial access listed

# Storm surge screening model (see surge.py).
RHO_AIR = 1.15  # kg/m3, near-surface air in a tropical cyclone
RHO_SEA = 1025.0  # kg/m3
GRAVITY = 9.81  # m/s2
INFLOW_DEG = 20.0  # surface inflow angle toward the storm centre
TEN_MINUTE_FACTOR = 0.93  # 1-minute sustained to 10-minute mean wind at sea (Harper, Kepert & Ginger 2010)
DRAG_MAX = 2.5e-3  # sea-surface drag saturates in hurricane winds (Powell, Vickery & Reinhold 2003)
SHELF_DEPTH_M = 100.0  # transects end here; wind setup over deeper water is negligible
MIN_WATER_DEPTH_M = 2.0  # floor on total depth at the shoreline, where 1D setup is singular
TRANSECT_STEP_KM = 1.0
TRANSECT_MAX_KM = 300.0
BATHYMETRY_MARGIN_DEG = 2.5  # seaward extent fetched around a region so its transects reach the shelf edge
COAST_NORMAL_CELLS = 9  # smoothing window (grid cells) for the coast orientation
SURGE_DECAY_M_PER_KM = 1.0 / 14.5  # inland attenuation: the classic 1 m per 14.5 km (US Army Corps of Engineers 1963)
SURGE_REACH_KM = 600.0  # storm positions farther than this from every coast point are skipped
SURGE_TIME_CHUNK = 16
FLOOD_DEPTH_M = 0.3  # "flooded" in summaries: ankle-deep water, enough to stop vehicles and wet equipment

# Relative consequence of losing an asset (1-5), used to turn outage probability into a priority score.
CRITICALITY: dict[str, int] = {
    "hospital": 5,
    "cyclone_shelter": 5,
    "health_centre": 4,
    "substation": 4,
    "power_plant": 4,
    "clinic": 3,
    "water_works": 3,
    "fire_station": 3,
    "police": 2,
    "school": 2,
}

# OSM (key, value) -> asset kind.
OSM_KINDS: dict[tuple[str, str], str] = {
    ("power", "substation"): "substation",
    ("power", "plant"): "power_plant",
    ("amenity", "hospital"): "hospital",
    ("amenity", "clinic"): "clinic",
    ("healthcare", "centre"): "health_centre",
    ("amenity", "school"): "school",
    ("amenity", "fire_station"): "fire_station",
    ("amenity", "police"): "police",
    ("man_made", "water_works"): "water_works",
    ("man_made", "water_tower"): "water_works",
}


@dataclass(frozen=True)
class Region:
    """A study area.

    Attributes:
        id: Stable identifier.
        name: Human-readable name.
        bbox: ``(south, west, north, east)`` in degrees.
        osdma_districts: OSDMA districts whose cyclone shelters fall inside the region (empty outside Odisha).
    """

    id: str
    name: str
    bbox: tuple[float, float, float, float]
    osdma_districts: tuple[str, ...] = ()


@dataclass(frozen=True)
class SurgeReport:
    """IMD's account of a storm's surge, the benchmark for the modelled crest.

    Attributes:
        place: Where it was reported.
        bbox: ``(south, west, north, east)`` of that stretch of coast; the modelled peak inside it is compared.
        low_m: Lower end of the reported height above astronomical tide (metres).
        high_m: Upper end (equal to ``low_m`` for a single value).
        kind: How it was measured: a tide gauge, a post-storm survey or an IMD estimate.
        source: URL of the IMD report.
    """

    place: str
    bbox: tuple[float, float, float, float]
    low_m: float
    high_m: float
    kind: str
    source: str


@dataclass(frozen=True)
class Scenario:
    """A historical cyclone replayed over a region.

    Attributes:
        id: Stable identifier used in URLs and artifact paths.
        storm: IBTrACS storm name.
        season: IBTrACS season (year).
        region: Study area.
        landfall: Official landfall time (UTC), used for lead-time reporting.
        truth_pre: Inclusive start / exclusive end dates of the pre-storm night-light window.
        truth_post: Inclusive start / exclusive end dates of the post-landfall night-light window.
        reference: Whether the outage model is fitted on this scenario (exactly one scenario should be).
        forecasts: ECMWF ensemble issue times (UTC) to replay as-issued; ECMWF open data exists from 2024 onwards.
        surge_report: IMD's reported surge, when there is one.
    """

    id: str
    storm: str
    season: int
    region: Region
    landfall: datetime
    truth_pre: tuple[date, date]
    truth_post: tuple[date, date]
    reference: bool = False
    forecasts: tuple[datetime, ...] = ()
    surge_report: SurgeReport | None = None


ODISHA_COAST = Region(
    id="odisha-coast",
    name="Odisha coast (Ganjam to Balasore)",
    bbox=(19.0, 84.4, 21.7, 87.6),
    osdma_districts=(
        "BALASORE",
        "BHADRAK",
        "CUTTACK",
        "GANJAM",
        "JAGATSINGHPUR",
        "JAJPUR",
        "KENDRAPARA",
        "KHURDA",
        "MAYURBHANJ",
        "NAYAGARH",
        "PURI",
    ),
)

WEST_BENGAL_COAST = Region(
    id="west-bengal-coast",
    name="West Bengal coast (Digha to Kolkata and the Sundarbans)",
    bbox=(21.5, 87.4, 23.0, 89.0),
)

NORTH_ANDHRA_COAST = Region(
    id="north-andhra-coast",
    name="North Andhra coast (Visakhapatnam to Srikakulam)",
    bbox=(17.2, 82.4, 18.8, 84.3),
)

# Night-light windows follow one rule for every storm: about two weeks ending just before the storm's approach, and
# the seven nights after landfall.
SCENARIOS: dict[str, Scenario] = {
    scenario.id: scenario
    for scenario in (
        Scenario(
            id="fani-2019",
            storm="FANI",
            season=2019,
            region=ODISHA_COAST,
            landfall=datetime(2019, 5, 3, 3, 30, tzinfo=UTC),  # IMD: crossed near Puri 08:00-10:00 IST
            truth_pre=(date(2019, 4, 20), date(2019, 5, 2)),
            truth_post=(date(2019, 5, 4), date(2019, 5, 11)),
            reference=True,
            surge_report=SurgeReport(
                place="Puri coast",
                bbox=(19.6, 85.4, 20.0, 86.3),
                low_m=1.5,
                high_m=1.5,
                kind="IMD estimate at landfall",
                source=f"{IMD_REPORTS}/26_7122ae_Preliminary%20Report%20on%20ESCS%20FANI_15082020.pdf",
            ),
        ),
        Scenario(
            id="dana-2024",
            storm="DANA",
            season=2024,
            region=ODISHA_COAST,
            landfall=datetime(2024, 10, 24, 20, 0, tzinfo=UTC),  # IMD: crossed near Bhitarkanika-Dhamra overnight
            truth_pre=(date(2024, 10, 10), date(2024, 10, 22)),
            truth_post=(date(2024, 10, 25), date(2024, 11, 1)),
            forecasts=tuple(
                datetime(2024, 10, day, hour, tzinfo=UTC)
                for day, hour in ((22, 0), (22, 12), (23, 0), (23, 12), (24, 0))
            ),
            surge_report=SurgeReport(
                place="Kendrapara, Bhadrak and Balasore coast",
                bbox=(20.4, 86.5, 21.6, 87.2),
                low_m=1.0,
                high_m=2.0,
                kind="IMD estimate",
                source=f"{IMD_REPORTS}/26_5d5a67_Preliminary%20Report_SCS%20Dana_Approved.pdf",
            ),
        ),
        # Held-out strong storm in a different state and grid; it predates ECMWF open data, so there is no as-issued
        # forecast replay. Both night-light windows fall inside India's COVID-19 lockdown.
        # Untouched test storm, scored once with the Fani-fitted model.
        Scenario(
            id="hudhud-2014",
            storm="HUDHUD",
            season=2014,
            region=NORTH_ANDHRA_COAST,
            landfall=datetime(2014, 10, 12, 7, 0, tzinfo=UTC),  # IMD: crossed near Visakhapatnam 12:00-13:00 IST
            truth_pre=(date(2014, 9, 26), date(2014, 10, 10)),
            truth_post=(date(2014, 10, 13), date(2014, 10, 20)),
            surge_report=SurgeReport(
                place="Visakhapatnam port",
                bbox=(17.6, 83.2, 17.8, 83.4),
                low_m=1.4,
                high_m=1.4,
                kind="tide gauge",
                source=f"{IMD_REPORTS}/26_fac6af_hud.pdf",
            ),
        ),
        Scenario(
            id="amphan-2020",
            storm="AMPHAN",
            season=2020,
            region=WEST_BENGAL_COAST,
            landfall=datetime(2020, 5, 20, 11, 0, tzinfo=UTC),  # IMD: crossed near the Sundarbans 15:30-17:30 IST
            truth_pre=(date(2020, 5, 5), date(2020, 5, 19)),
            truth_post=(date(2020, 5, 21), date(2020, 5, 28)),
            surge_report=SurgeReport(
                place="South and North 24 Parganas",
                bbox=(21.5, 88.0, 22.3, 89.0),
                low_m=4.6,
                high_m=4.6,
                kind="post-storm survey (ACWC Kolkata)",
                source=f"{IMD_REPORTS}/26_3c837f_amphan%20with%20damage.pdf",
            ),
        ),
    )
}


@dataclass(frozen=True)
class Settings:
    """Geo service settings resolved from the environment.

    Attributes:
        bucket: GCS bucket holding built scenario artifacts (the build writes there, the API reads from there).
        cache_dir: Local cache for downloaded build inputs (IBTrACS, Overpass, OSDMA).
        ee_project: Google Cloud project used to initialise Earth Engine during builds.
        http_timeout_s: Per-request timeout for build-time downloads.
        max_attempts: Attempts per download before giving up.
        retry_backoff_s: Base delay for exponential backoff between attempts.
        allowed_origins: CORS origins allowed to call the API.
        archive_bucket: GCS bucket the feed archiver writes to (read for the live picture).
        live_ttl_s: How long the live digest is served before the archive is read again.
    """

    bucket: str = "argmax-cyclone-2026-scenarios"
    cache_dir: Path = Path(".cache")
    ee_project: str = "argmax-cyclone-2026"
    http_timeout_s: float = 300.0
    max_attempts: int = 3
    retry_backoff_s: float = 5.0
    allowed_origins: tuple[str, ...] = ("*",)
    archive_bucket: str = "argmax-cyclone-2026-archive"
    live_ttl_s: float = 900.0

    @classmethod
    def from_env(cls) -> Settings:
        """Build settings from ``GEO_*`` environment variables, falling back to defaults.

        Returns:
            Settings: The resolved configuration.

        Raises:
            ValueError: If a numeric variable cannot be parsed.
        """
        env = os.environ
        origins = env.get("GEO_ALLOWED_ORIGINS")
        return cls(
            bucket=env.get("GEO_BUCKET") or cls.bucket,
            cache_dir=Path(env.get("GEO_CACHE_DIR", cls.cache_dir)),
            ee_project=env.get("GEO_EE_PROJECT", cls.ee_project),
            http_timeout_s=float(env.get("GEO_HTTP_TIMEOUT_S", cls.http_timeout_s)),
            max_attempts=int(env.get("GEO_MAX_ATTEMPTS", cls.max_attempts)),
            retry_backoff_s=float(env.get("GEO_RETRY_BACKOFF_S", cls.retry_backoff_s)),
            allowed_origins=tuple(o.strip() for o in origins.split(",")) if origins else cls.allowed_origins,
            archive_bucket=env.get("GEO_ARCHIVE_BUCKET") or cls.archive_bucket,
        )
