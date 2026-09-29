import crypto from "crypto";

export interface DisasterCampaign {
  id: string;
  title: string;
  description: string;
  category: "food_water" | "microgrid_power" | "medical_shelter" | "parametric_pool";
  targetAmountInr: number;
  raisedAmountInr: number;
  district: string;
  suggestedPacks: {
    amountInr: number;
    title: string;
    impactDescription: string;
  }[];
}

export interface RazorpayOrderPayload {
  amount: number; // in INR
  currency?: string;
  receiptId: string;
  campaignId: string;
  donorName?: string;
  donorEmail?: string;
  donorPhone?: string;
  district?: string;
  notes?: Record<string, string>;
}

export interface RazorpayVerificationPayload {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
}

export interface ParametricPayoutRequest {
  payoutBatchId: string;
  district: string;
  panchayatCount: number;
  totalAmountInr: number;
  hollandWindPeakKmph: number;
  floodInundationPct: number;
  triggerSource: "OSDMA_RISAT_SAR" | "IMD_RADAR_SYNOPTIC";
}

export interface ParametricPayoutResult {
  success: boolean;
  payoutBatchId: string;
  utrNumber: string;
  status: "PROCESSED" | "QUEUED_BENEFICIARY_CREDIT";
  totalAmountInr: number;
  recipientCount: number;
  disbursedAt: string;
  smartContractHash: string;
}

export const DISASTER_RELIEF_CAMPAIGNS: DisasterCampaign[] = [
  {
    id: "puri-emergency-food-water",
    title: "Puri Coastal Emergency Food & Clean Water Shield",
    description: "Emergency air-drop dry rations, water purification sachets, and halogen tablets for marooned coastal villages in Brahmagiri and Krushnaprasad blocks.",
    category: "food_water",
    targetAmountInr: 5000000,
    raisedAmountInr: 3420000,
    district: "Puri",
    suggestedPacks: [
      { amountInr: 500, title: "Emergency Family Pack", impactDescription: "7-day dry food & chlorine purification for 1 family" },
      { amountInr: 2000, title: "Block Water Purifier Kit", impactDescription: "High-capacity water filtration unit for cyclone shelter (50 people)" },
      { amountInr: 5000, title: "Air-Drop Supply Crate", impactDescription: "Complete survival gear + rations dropped to cut-off fishing hamlets" },
    ],
  },
  {
    id: "balasore-power-grid-restoration",
    title: "Balasore Hospital & Microgrid Emergency Generator Fund",
    description: "Diesel gen-sets, solar microgrids, and mobile power stations for coastal sub-divisional hospitals and oxygen refill plants cut off from the main 132kV grid.",
    category: "microgrid_power",
    targetAmountInr: 10000000,
    raisedAmountInr: 6850000,
    district: "Balasore",
    suggestedPacks: [
      { amountInr: 1500, title: "Generator Fuel Supply (24h)", impactDescription: "High-grade diesel fuel to keep hospital ICU backup generators running" },
      { amountInr: 5000, title: "Emergency Solar Battery Inverter", impactDescription: "Solar mobile station to power telecom nodes and distress radios" },
      { amountInr: 15000, title: "Sub-Station Bypass Conduit", impactDescription: "Rapid electrical coupling kit to restore primary hospital power" },
    ],
  },
  {
    id: "kendrapara-cyclone-shelter-kits",
    title: "Kendrapara Multi-Purpose Cyclone Shelter Trauma Kits",
    description: "First-aid triage kits, antivenom stock, baby nutritional formula, and solar emergency lanterns for 48 cyclone shelters in Rajnagar and Mahakalapada.",
    category: "medical_shelter",
    targetAmountInr: 3500000,
    raisedAmountInr: 2180000,
    district: "Kendrapara",
    suggestedPacks: [
      { amountInr: 1000, title: "Maternal & Infant Relief Kit", impactDescription: "Baby food, hygiene supplies, and thermal blankets" },
      { amountInr: 3500, title: "First-Response Medical Kit", impactDescription: "Antiseptics, suture kits, splints, and anti-venom for shelter clinics" },
      { amountInr: 8000, title: "Shelter High-Intensity Beacon", impactDescription: "Rechargeable solar searchlights & wireless megaphone for evacuations" },
    ],
  },
  {
    id: "parametric-insurance-pool",
    title: "Gram Panchayat SDRF Parametric Emergency Liquidity Pool",
    description: "Smart contract parametric pool instantly released to verified Aadhaar-linked DBT accounts when wind speed crosses 89 km/h and flood inundation exceeds 30%.",
    category: "parametric_pool",
    targetAmountInr: 75000000,
    raisedAmountInr: 58200000,
    district: "State Coastal Belt (Puri, Kendrapara, Jagatsinghpur, Balasore)",
    suggestedPacks: [
      { amountInr: 5000, title: "Gram Panchayat Micro-Buffer", impactDescription: "Instant DBT liquidity for 2 marginal farmer households" },
      { amountInr: 25000, title: "Coastal Ward Parametric Grant", impactDescription: "Immediate clearance grant for fallen tree removal & road access" },
      { amountInr: 100000, title: "Sub-District Contingency Underwrite", impactDescription: "Underwrites emergency SDRF liquidity for an entire cyclone shelter cluster" },
    ],
  },
];

/**
 * Initializes Razorpay server instance if credentials exist.
 * Returns null if running in offline/demo mode without live credentials.
 */
export async function getRazorpayServerClient() {
  const key_id = process.env.RAZORPAY_KEY_ID;
  const key_secret = process.env.RAZORPAY_KEY_SECRET;

  if (!key_id || !key_secret || key_id.includes("REPLACE_THIS")) {
    return null;
  }

  try {
    const Razorpay = (await import("razorpay")).default;
    return new Razorpay({
      key_id,
      key_secret,
    });
  } catch (error) {
    console.warn("[VAYU-RAKSHA] Failed to load razorpay server module, using fallback mode:", error);
    return null;
  }
}

/**
 * Verifies Razorpay payment signature HMAC SHA256.
 */
export function verifyRazorpaySignature(
  orderId: string,
  paymentId: string,
  signature: string,
  secretKey: string
): boolean {
  if (!secretKey) return true; // Demo fallback
  const generatedSignature = crypto
    .createHmac("sha256", secretKey)
    .update(`${orderId}|${paymentId}`)
    .digest("hex");
  return generatedSignature === signature;
}

/**
 * Verifies Razorpay webhook signature.
 */
export function verifyRazorpayWebhook(
  rawBody: string,
  signature: string,
  webhookSecret: string
): boolean {
  if (!webhookSecret) return true;
  const expectedSignature = crypto
    .createHmac("sha256", webhookSecret)
    .update(rawBody)
    .digest("hex");
  return expectedSignature === signature;
}
