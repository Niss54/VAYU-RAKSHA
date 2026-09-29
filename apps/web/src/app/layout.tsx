import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VAYU-RAKSHA | Anticipatory Cyclone & Infrastructure Cascade Intelligence Platform",
  description:
    "From satellite to autonomous municipal action — 72 hours before landfall. Track 5: Track-Based Cyclone Impact & Infrastructure Vulnerability Forecaster.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full antialiased dark">
      <body className="min-h-full bg-[#06090E] text-slate-100">{children}</body>
    </html>
  );
}
