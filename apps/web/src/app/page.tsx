import { Console } from "@/components/console";
import type { ScenarioSummary } from "@/lib/types";
import { geoFetch } from "@/server/geo";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "VAYU-RAKSHA | Anticipatory Cyclone & Infrastructure Cascade Intelligence Platform",
  description:
    "Track 5: Track-Based Cyclone Impact & Infrastructure Vulnerability Forecaster · Build with AI: Code for Communities (2nd Edition) · Team SYNTRIX",
  icons: {
    icon: "/logo.png",
    shortcut: "/logo.png",
    apple: "/logo.png",
  },
};

const BUNDLED_SCENARIOS: ScenarioSummary[] = [
  {
    id: "fani-2019",
    storm: "Fani",
    season: 2019,
    region: { id: "odisha", name: "Odisha coast (Ganjam to Balasore)", bbox: [19.0, 84.5, 21.8, 87.5] },
    landfall: "2019-05-03T03:30:00Z",
    peak_vmax_kt: 115,
  },
  {
    id: "dana-2024",
    storm: "Dana",
    season: 2024,
    region: { id: "odisha", name: "Odisha coast (Puri to Dhamra)", bbox: [19.5, 85.5, 21.5, 87.5] },
    landfall: "2024-10-24T18:00:00Z",
    peak_vmax_kt: 65,
  },
  {
    id: "amphan-2020",
    storm: "Amphan",
    season: 2020,
    region: { id: "west-bengal", name: "West Bengal coast & Sundarbans", bbox: [21.0, 87.5, 22.8, 89.5] },
    landfall: "2020-05-20T09:00:00Z",
    peak_vmax_kt: 85,
  },
  {
    id: "hudhud-2014",
    storm: "Hudhud",
    season: 2014,
    region: { id: "andhra-pradesh", name: "Andhra Pradesh (Visakhapatnam)", bbox: [17.2, 82.8, 18.5, 84.2] },
    landfall: "2014-10-12T06:00:00Z",
    peak_vmax_kt: 100,
  },
];

async function loadScenarios(): Promise<ScenarioSummary[]> {
  try {
    const data = await geoFetch<ScenarioSummary[]>("/scenarios");
    if (Array.isArray(data) && data.length > 0) return data;
  } catch (error) {
    console.warn("[VAYU-RAKSHA] Geo fetch error, falling back to bundled scenarios:", error);
  }
  return BUNDLED_SCENARIOS;
}

export default async function Home() {
  const scenarios = await loadScenarios();
  const mapsApiKey =
    process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ||
    "AIzaSyDi8-cAA-OjsfqyVqo0j27cba89_VZZXfw";

  return <Console scenarios={scenarios} mapsApiKey={mapsApiKey} />;
}
