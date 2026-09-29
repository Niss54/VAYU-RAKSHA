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
