# 🚀 VAYU-RAKSHA — Production Deployment Guide
### Complete Zero-Downtime Deployment on Railway (Backend) & Vercel (Frontend)

This guide walks you through deploying the **VAYU-RAKSHA** platform in less than 5 minutes.

---

## 🏗️ Architecture Overview

- **Backend (Python FastAPI Geo & Cascade Engine):** Deployed on **Railway** via Docker (`services/geo/Dockerfile`).
- **Frontend (Next.js 16 Tactical Command Center HUD):** Deployed on **Vercel** (`apps/web`).
- **Database:** **Neon Serverless PostgreSQL** (already configured with connection pooling).
- **Payments:** **Razorpay Live Gateway** (active credentials configured).
- **Indian Languages Voice:** **Sarvam AI (Bulbul:v1)** for Odia, Hindi, Bengali, Tamil, Telugu, English.

---

## Part 1: Deploy Backend to Railway (Python FastAPI)

1. Open [Railway.app](https://railway.app) and click **"New Project"**.
2. Select **"Deploy from GitHub repo"** and choose your repository: `Niss54/VAYU-RAKSHA` (or `Niss54/gdg`).
3. Click on the newly created service and go to **Settings**:
   - **Root Directory:** Set to `services/geo` (or leave default if using root `railway.json`).
   - Railway will automatically detect the `Dockerfile` and build it with `uv`.
4. Go to the **"Variables"** tab and add:
   ```env
   PYTHONUNBUFFERED=1
   PORT=8080
   ```
5. In **Settings** ➔ **Networking**, click **"Generate Domain"**.
   - Your backend public URL will look like: `https://vayu-raksha-production.up.railway.app`
   - Test it by visiting: `https://vayu-raksha-production.up.railway.app/health` (should return `{"status":"ok"}`).
   - Copy this URL for Part 2!

---

## Part 2: Deploy Frontend to Vercel (Next.js 16)

1. Open [Vercel.com](https://vercel.com) and click **"Add New..." ➔ "Project"**.
2. Import your GitHub repository: `Niss54/VAYU-RAKSHA` (or `Niss54/gdg`).
3. In the project configuration:
   - **Framework Preset:** `Next.js`
   - **Root Directory:** Click `Edit` and select `apps/web`.
4. In **"Environment Variables"**, paste the following keys:

| Variable Name | Value / Source | Required? |
|---|---|:---:|
| `GEO_API_URL` | Your Railway backend URL from Part 1 | **Yes** |
| `NEXT_PUBLIC_RAZORPAY_KEY_ID` | `rzp_live_TiDzKorTN30dVk` (or from `.env.local`) | **Yes (Live)** |
| `RAZORPAY_KEY_ID` | `rzp_live_TiDzKorTN30dVk` (or from `.env.local`) | **Yes (Live)** |
| `RAZORPAY_KEY_SECRET` | Copy from `RAZORPAY_KEY_SECRET` in `.env.local` | **Yes (Live)** |
| `RAZORPAY_WEBHOOK_SECRET` | Copy from `RAZORPAY_WEBHOOK_SECRET` in `.env.local` | **Yes** |
| `SARVAM_API_KEY` | Your Sarvam AI Key from dashboard.sarvam.ai | **Recommended** |
| `DATABASE_URL` | Copy from `DATABASE_URL` in `.env.local` (Neon Postgres) | **Yes** |
| `RESEND_API_KEY` | Copy from `RESEND_API_KEY` in `.env.local` | **Yes** |
| `CLOUDINARY_CLOUD_NAME` | Copy from `CLOUDINARY_CLOUD_NAME` in `.env.local` | **Yes** |
| `CLOUDINARY_API_KEY` | Copy from `CLOUDINARY_API_KEY` in `.env.local` | **Yes** |
| `CLOUDINARY_API_SECRET` | Copy from `CLOUDINARY_API_SECRET` in `.env.local` | **Yes** |
| `CLOUDINARY_URL` | Copy from `CLOUDINARY_URL` in `.env.local` | **Yes** |
| `JWT_SECRET` | Copy from `JWT_SECRET` in `.env.local` | **Yes** |
| `JWT_REFRESH_SECRET` | Copy from `JWT_REFRESH_SECRET` in `.env.local` | **Yes** |

5. Click **"Deploy"**. Vercel will build and assign you a global CDN URL (e.g. `https://vayu-raksha.vercel.app`).

---

## Part 3: Verification & Post-Deployment Checklist

1. **Open your Vercel URL:** Verify that the Tactical Command HUD loads with Cyclone Dana, Biparjoy, Michaung, and Amphan.
2. **Test Cascade & ISRO Tabs:** Click on the new **"CASCADE"** tab to view the NetworkX graph and **"ISRO"** tab to view MOSDAC & RISAT-1A SAR ground truth.
3. **Test Multilingual IVR Voice:** Switch languages (Odia, Hindi, Bengali, Tamil, Telugu, English) and click **"Play IVR Audio"** to hear Sarvam AI native speech.
4. **Test Live Razorpay:** Click **"₹ RELIEF DISASTER FUND"** at the top right, pick a campaign, and click **"CONTRIBUTE VIA RAZORPAY"**. The real-time Razorpay India checkout modal will open with live UPI / QR / NetBanking options!

---
*VAYU-RAKSHA — Build with AI: Code for Communities (Track 5)*
