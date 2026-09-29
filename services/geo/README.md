# ShadowCast geo service

It turns a cyclone track into a **ranked, explained list of the assets that are about to lose power**, and it proves the model against satellite ground truth.

- **Offline build** (`python -m shadowcast_geo.build`): track → hazard per asset → Earth Engine enrichment → night-light truth → calibrated outage model → ranking → JSON artifacts in Cloud Storage.
- **API** (FastAPI on Cloud Run): serves the built scenarios and computes hazard on demand, e.g. wind at every asset at any moment, for the console's timeline scrubber.

## Method

| Step | How |
|---|---|
| Track | IBTrACS best track (JTWC intensity, radius of maximum wind, quadrant wind radii) for replays and backtests; **as-issued ECMWF ensemble tracks** for forecast replays (below) |
| Hazard | Holland (1980) parametric wind profile per asset. The track is densified to 15-minute steps, because 3-hourly fixes let the eyewall pass *between* fixes at near-track assets |
| Exposure | 3,325 assets on the Odisha coast: 765 official OSDMA cyclone shelters plus 2,560 from OSM (264 substations, 38 power plants, 671 hospitals, 796 health centres, 358 clinics, 247 schools, 105 water works, 65 police and 16 fire stations). Each has WorldPop population within 2 km and Copernicus DEM elevation |
| Truth | VIIRS VNP46A2 raw radiance, masked to high-quality retrievals, before vs after landfall within 1.5 km of each substation. The gap-filled band is avoided because it carries pre-storm values into cloudy post-storm nights |
| Model | `P(outage) = logistic(a + b · peak wind)`, fitted on Fani. An asset "lost power" when its light fell by at least 50 % |
| Priority | `score = P(outage) × criticality / 5`, where criticality is hospitals and shelters 5, substations 4, …, schools 2. Every rank carries plain-language reasons |
| Surge (`surge.py`) | Coast-normal transects from every open-coast cell of ETOPO1 to the 100 m shelf edge; the steady 1D wind-setup equation integrated shoreward with the Holland onshore stress (Garratt drag capped at 2.5e-3) plus the inverse barometer from Holland's wind-pressure relation; the crest carried inland at 1 m per 14.5 km against bare-earth DeltaDTM ground. Compared with IMD's reported surge per storm |
| Rain (`hazard.py`) | R-CLIPER rain rate (Tuleya et al. 2007) summed over the densified track, per member in forecasts; scored against NASA GPM IMERG V07 storm totals at every asset |
| Parametric cover (`insurance.py`) | District index = wind reached at 25 % of a district's sites (geoBoundaries ADM2); payouts 25/50/100 % at 64/83/96 kt. Best track: trigger time and a basis-risk check against satellite outages. Forecast: probability of a payout from every member |
| Evidence and live (`earth.py`, `live.py`) | Before/after VIIRS night-light PNGs per region on one scale, for Gemini to read; `/live` digests the feed archiver's newest GDACS and NDMA SACHET run |

## As-issued ensemble replay

Best-track replays are hindsight. The forecast replay uses what forecasters actually had.

1. ECMWF's IFS ensemble tropical-cyclone track file for each issue time is fetched from ECMWF open data on Google Cloud (`gs://ecmwf-open-data`, history from 2024) and decoded with ecCodes: 52 members, 6-hourly centre, MSLP and maximum 10 m wind.
2. The right storm is picked from the worldwide file by **member agreement**: the storm with the most members passing within 150 km of the observed landfall. Early runs can split genesis between neighbouring vortices; for Dana on 22 Oct 00Z, 36 members tracked 70B and 17 tracked 71B.
3. Each member's hazard is run through the same wind model. The radius of maximum wind comes from Willoughby, Darling & Rahn (2006), because the ensemble does not report it.
4. Results are aggregated per asset:
   - `P(outage)`, the mean over members of the calibrated model;
   - `p34` and `p64`, the share of members bringing gale-force and hurricane-force wind;
   - the 10/50/90 % peak wind;
   - the median **gale arrival**.
5. Ranking is by `P(outage) × criticality`; when outage risk is negligible, gale exposure × criticality decides.

**Cyclone Dana (2024):**

| Issued | Lead to landfall | Members on Dana | Assets where ≥ half the members bring gales |
|---|---|---|---|
| 22 Oct 00Z | 68 h | 36 (70B) | 685 |
| 22 Oct 12Z | 56 h | 51 | 216 |
| 23 Oct 00Z | 44 h | 52 | 1,895 |
| 23 Oct 12Z | 32 h | 52 (03B) | 1,979 |
| 24 Oct 00Z | 20 h | 52 | 1,925 |

At 44 h the top priorities are Mahakalapada shelters and Paradip hospitals: 94-96 % of members bring gales, arriving around 24 Oct 05:00 UTC, about 15 h before landfall. No member brings hurricane-force wind, so outage probabilities stay near zero, which matches the observed lack of widespread blackouts. The ensemble's peak winds are well below observed intensity (about 43 kt median vs Dana's 65 kt), a known limitation of global-model tracker winds. Gale probability and arrival time are the robust outputs.

## Results

**Cyclone Fani (2019), in-sample:**
- 200 lit substations, ROC AUC **0.97**, Brier **0.049**, Spearman(peak wind, light loss) **0.65**.
- The model crosses 50 % outage probability at **~107 kt**.
- Assets modelled above 100 kt lost a median **77 %** of their lights; at or below 80 kt, about **0 %**.

**Cyclone Dana (2024), held out:**
- The strongest modelled wind at any substation was 61 kt, and the model raised **no high-probability outage flags** (mean P 0.2 %).
- 2 % of substations crossed the 50 % loss threshold, which is consistent with night-to-night noise (this storm's low-wind band shows a median 21 % light variation).
- Dana tests false-alarm behaviour, not detection. **A strong held-out storm, Amphan (2020), is the next validation.**

## Assumptions and limitations

- Holland B = 1.5 and no over-land decay or asymmetry from forward motion. Peak winds over land are therefore upper bounds.
- The outage model has one feature (wind). Grid topology, pole age and pre-emptive shutdowns are not modelled. It was calibrated on one storm and one state.
- Night-light loss is a proxy for grid outage. Clouds, the moon and festivals add noise, which is handled by medians, the quality mask and the 50 % threshold.
- Best-track replays are hindsight, so lead times are short; the ensemble replay removes this. Ensemble intensity is biased low and is not corrected; it feeds `P(outage)` unchanged.
- Surge is a screening model (no tide, waves, rivers or alongshore flow) and runs high on narrow shelves; rain is a symmetric climatology-persistence profile. Neither changes the outage score.

## API

| Endpoint | Returns |
|---|---|
| `GET /health` | Liveness and loaded scenarios |
| `GET /scenarios` | Built scenarios |
| `GET /scenarios/{id}` | Metadata, outage model, backtest skill, loss by wind band |
| `GET /scenarios/{id}/track` | GeoJSON track (path and fixes) |
| `GET /scenarios/{id}/assets?kind=&min_score=&limit=&offset=` | Ranked assets with hazard, probability and reasons |
| `GET /scenarios/{id}/assets/{asset_id}` | One asset with its 15-minute wind timeline |
| `GET /scenarios/{id}/hazard?at=` | Wind at every asset, plus the storm position, at one moment |
| `GET /scenarios/{id}/backtest` | Predicted vs observed per substation, with skill |
| `GET /scenarios/{id}/surge` | Peak modelled surge per open-coast point (wind setup and inverse barometer) |
| `GET /scenarios/{id}/evidence/{night-lights-pre,night-lights-post}.png` | Before/after VIIRS night-light images of the region |
| `GET /live` | GDACS cyclones and NDMA SACHET warnings from the feed archiver's newest run (cached 15 min) |
| `GET /scenarios/{id}/forecasts` | As-issued ensemble forecasts replayed (issue time, lead, members) |
| `GET /scenarios/{id}/forecasts/{key}/tracks` | Ensemble member tracks as GeoJSON (the "spaghetti plot") |
| `GET /scenarios/{id}/forecasts/{key}/assets?kind=&min_score=&limit=&offset=` | Assets ranked under that forecast: `p34`, `p64`, wind percentiles, gale arrival and reasons |

Interactive docs are at `/docs`.

## Develop

```bash
uv sync --all-extras
uv run ruff check . && uv run ruff format --check . && uv run pyright && uv run pytest
uv run python -m shadowcast_geo.build                  # writes to gs://$GEO_BUCKET (gcloud ADC with Earth Engine)
uv run uvicorn shadowcast_geo.api:create_app --factory --reload   # serves from the same bucket
```

Artifacts live only in Cloud Storage (`GEO_BUCKET`, default `argmax-cyclone-2026-scenarios`): the build writes there and the API loads from there. Deploy with [`infra/geo.sh`](../../infra/geo.sh).
