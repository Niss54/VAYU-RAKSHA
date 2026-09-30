# ShadowCast console

The operations console for district and state disaster teams. Pick a storm, then scrub from days before landfall to the week after:

- **Map (Google Maps with a deck.gl overlay):** every shelter, hospital, substation and school in the region, coloured and sized by grid-outage risk, by the chance of gales across ECMWF ensemble members, or by the modelled wind at the scrubber time. The storm track, or the 52 as-issued ensemble member tracks, sits on top, along with the storm's eye and radius of maximum wind.
- **Brief** (the opening tab): the situation in two sentences, exception tiles (sites at risk, how many gales have reached, the next site in line), recommended actions per agency (health, power utility, district administration, water supply, police and fire), each due before gales reach its first site, and the latest officer decisions from the audit log. It is computed from the ranked assets, not by Gemini, updates as the timeline moves, and every item opens the matching site or list.
- **Prioritise:** the ranked asset list with kind filters. Each asset opens to its outage probability, gale arrival, population served, elevation, its wind timeline and the plain-language reasons for its rank.
- **Replay modes:** the best track (hindsight, used for backtesting) or each ECMWF ensemble forecast _as issued_, 68 to 20 hours before landfall.
- **Prepare:** the Gemini duty analyst (Gemini 3.8 Flash on Vertex AI). It explains ranks using only numbers from the geo API, and drafts advisories: officer actions plus a CAP 1.2 message in English, Hindi and Odia. The officer approves or rejects each one on a card; decisions go to an append-only Firestore audit log; approved advisories download as CAP XML and play as Gemini-TTS audio.
- **Prove:** backtest skill (ROC AUC, Brier score, Spearman), median night-light loss by modelled wind band, and predicted vs observed loss for every substation.

## Architecture

Next.js 16 (App Router) with React 19 and Tailwind 4. The page server-renders the scenario list. Everything else is fetched client-side with SWR through the same-origin `/api/geo/*` rewrite to the [geo API](../../services/geo), so the API location is server configuration only. The map is loaded client-side only.

| Route                                    | What                                                                                                                                                                                                                                                |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST /api/agent`                        | AI SDK 7 `ToolLoopAgent` streamed to `useChat`. Tools: `searchAssets` (the geo API, scoped to the replay being viewed) and `issueAdvisory` (requires officer approval; builds CAP XML and writes the audit record). Rejections are audited here too |
| `GET /api/advisories?scenario=fani-2019` | The latest five officer decisions for a scenario from the audit log (never cached)                                                                                                                                                                  |
| `GET /api/advisories/{id}/audio?lang=or` | Gemini-TTS audio for one language of an _issued_ advisory, read back from the audit log; cached immutably                                                                                                                                           |

Server code lives in `src/server` (geo client, Google clients, agent); `src/lib/advisory.ts` holds the advisory schema and the CAP 1.2 builder shared with the UI.

## Develop

```bash
cp .env.example .env.local          # set NEXT_PUBLIC_GOOGLE_MAPS_API_KEY; GEO_API_URL defaults to the Cloud Run API
pnpm install
pnpm dev                            # http://localhost:3000
pnpm format:check && pnpm lint && pnpm typecheck && pnpm test && pnpm build
```

The agent and audio routes use Application Default Credentials (`gcloud auth application-default login` locally) for Vertex AI and Firestore in `GOOGLE_CLOUD_PROJECT`. Set `TOOL_APPROVAL_SECRET` so approvals are signed.

To use a local geo API instead, run `uv run uvicorn shadowcast_geo.api:create_app --factory --port 8000` in `services/geo` and set `GEO_API_URL=http://localhost:8000`.

The Maps key must be a browser key restricted to the Maps JavaScript API and to your origins (`localhost:3000`, `*.vercel.app`).

## Datadog Infrastructure & APM Monitoring

The web application integrates Datadog for production observability, APM tracing, and infrastructure telemetry.

### Configuration (`.env.local` / `.env`):
```env
DD_API_KEY=your_datadog_api_key
DD_APP_KEY=your_datadog_application_key
DD_SERVICE_NAME=VAYU-RAKSHA
DD_SITE=datadoghq.com
DD_ENV=development
```

### Features:
- **APM Tracing**: Powered by `dd-trace` initialized in `src/instrumentation.ts`.
- **Infrastructure Metrics**: Collects Node.js heap memory, CPU usage, process uptime, and system memory, shipped to Datadog V2 Series API.
- **Diagnostics**:
  - `GET /api/health/datadog`: Checks key presence and configuration safely without leaking secrets.
  - `POST /api/health/datadog`: Dispatches a live telemetry heartbeat and infrastructure metrics snapshot.
  - CLI Test: `node -r dotenv/config scripts/test-datadog.js dotenv_config_path=.env.local`
- **Fail-Safe**: Non-blocking and resilient — if Datadog is unreachable or credentials are missing, the application runs normally without interruption.

## Cloudinary File Storage

VAYU-RAKSHA uses Cloudinary for unified, server-side media and document asset storage, completely replacing legacy AWS S3 and Cloudflare R2 implementations.

### Configuration (`.env.local` / `.env`):
```env
STORAGE_PROVIDER=cloudinary
CLOUDINARY_CLOUD_NAME=x9sncqcz
CLOUDINARY_API_KEY=145764614276676
CLOUDINARY_API_SECRET=CLOUDINARY_URL=cloudinary://145764614276676:ey_K80B4FsA-4VGG_ICYCQl9hMY@x9sncqcz
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/webp,application/pdf,audio/wav,audio/webm,audio/mp3,audio/mpeg,audio/ogg
```

### Features:
- **Server-Side Security**: All credentials (`CLOUDINARY_API_SECRET`) are read strictly server-side and never exposed to client-side code.
- **Unified Upload Endpoint (`/api/upload`)**:
  - `POST /api/upload`: Accepts `multipart/form-data` or JSON base64 payloads; validates MIME type and file size; returns HTTPS `secure_url`.
  - `GET /api/upload?public_id=...`: Retrieves asset metadata securely from Cloudinary.
  - `DELETE /api/upload`: Deletes uploaded assets by public ID.
- **Client Helper**: `uploadAttachment(blob, filename)` from `@/lib/media`.
- **Supported Formats**: Images (JPEG, PNG, WebP, GIF, SVG), Documents (PDF), and Audio voice notes (WAV, WebM, MP3, OGG).
- **Diagnostics & Verification**:
  - CLI Test: `node -r dotenv/config scripts/test-cloudinary.js dotenv_config_path=.env.local`
  - Automated Vitest suite: `npm test`

