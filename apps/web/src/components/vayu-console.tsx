"use client";

import React, { useEffect, useState } from "react";
import {
  type CycloneMetadata,
  type InfrastructureNode,
  type VayuRakshaState,
  runVayuRakshaSimulation,
} from "@/lib/vayu-engine";
import { AgentBrainHud } from "@/components/agent-brain-hud";
import { CascadeTopologyCanvas } from "@/components/cascade-topology-canvas";
import { CounterfactualSandbox } from "@/components/counterfactual-sandbox";
import { MultilingualAdvisoryHub } from "@/components/multilingual-advisory-hub";
import { ParametricSmartTrigger } from "@/components/parametric-smart-trigger";
import {
  Activity,
  AlertTriangle,
  Compass,
  Cpu,
  Gauge,
  Globe,
  Layers,
  MapPin,
  MessageSquare,
  Network,
  RefreshCw,
  Send,
  Shield,
  ShieldAlert,
  Sparkles,
  Waves,
  Wind,
  Zap,
} from "lucide-react";

interface VayuConsoleProps {
  initialScenario?: "fani" | "dana";
}

export function VayuConsole({ initialScenario = "fani" }: VayuConsoleProps) {
  const [scenario, setScenario] = useState<"fani" | "dana">(initialScenario);
  const [activeTab, setActiveTab] = useState<
    "overview" | "cascade" | "counterfactual" | "advisories" | "insurance"
  >("overview");
  const [hardenedNodeIds, setHardenedNodeIds] = useState<string[]>([
    "S_PURI_220KV",
    "H_PURI_DISTRICT",
  ]);
  const [state, setState] = useState<VayuRakshaState>(() =>
    runVayuRakshaSimulation(initialScenario, hardenedNodeIds)
  );
  const [dutyPrompt, setDutyPrompt] = useState("");
  const [dutyChat, setDutyChat] = useState<Array<{ role: "user" | "analyst"; text: string }>>([
    {
      role: "analyst",
      text: "VAYU-RAKSHA Duty Analyst (Gemini 3.8 Flash) standing by. 5 specialized agents have mapped Cyclone Fani's cascade footprint across coastal Odisha. Ask me why an asset is at risk, or command a pre-landfall counterfactual simulation.",
    },
  ]);

  // Recalculate state when scenario or hardening toggles change
  const handleToggleHardening = (actionId: string, approved: boolean) => {
    let newHardened = [...hardenedNodeIds];
    if (actionId === "ACT_DE_ENERGIZE_COASTAL_SUBSTATIONS") {
      const ids = ["S_PURI_220KV", "S_BALIKUDA_132KV", "S_PARADIP_220KV"];
      newHardened = approved
        ? Array.from(new Set([...newHardened, ...ids]))
        : newHardened.filter((id) => !ids.includes(id));
    } else if (actionId === "ACT_PREPOSITION_HOSPITAL_FUEL") {
      const ids = ["H_PURI_DISTRICT", "H_JAGATSINGHPUR_TRAUMA"];
      newHardened = approved
        ? Array.from(new Set([...newHardened, ...ids]))
        : newHardened.filter((id) => !ids.includes(id));
    } else if (actionId === "ACT_CLOSE_COASTAL_BRIDGE_RB22") {
      const ids = ["RB_BALIKUDA_BRIDGE"];
      newHardened = approved
        ? Array.from(new Set([...newHardened, ...ids]))
        : newHardened.filter((id) => !ids.includes(id));
    }
    setHardenedNodeIds(newHardened);
    setState(runVayuRakshaSimulation(scenario, newHardened));
  };

  const handleScenarioChange = (newScenario: "fani" | "dana") => {
    setScenario(newScenario);
    setState(runVayuRakshaSimulation(newScenario, hardenedNodeIds));
  };

  const handleSendPrompt = (textToSend?: string) => {
    const q = textToSend || dutyPrompt;
    if (!q.trim()) return;

    const userMsg = { role: "user" as const, text: q };
    let reply = "";

    if (q.toLowerCase().includes("hospital") || q.toLowerCase().includes("icu")) {
      reply = `NIRNAY + SETU Analysis: Puri District Hospital (DHH) has 450 beds and 32 ICUs. It directly depends on Substation S_PURI_220KV. When coastal storm surge (2.2m) inundates the substation at T-18h, mains power trips. Hospital diesel backup lasts only 8 hours. By pre-positioning a 15,000L tanker, we buy 72 hours of uninterrupted ICU oxygen and neonatal support.`;
    } else if (q.toLowerCase().includes("substation") || q.toLowerCase().includes("s-7")) {
      reply = `VAYU Atmospheric Model: Peak winds will hit 115 kt with a 2.3m surge crest. If 220kV substations are kept live during saltwater inundation, arc-fault explosions permanently destroy multi-crore transformers. Controlled pre-isolation at T-36h prevents equipment destruction and preserves 14 downstream transmission corridors.`;
    } else if (q.toLowerCase().includes("insurance") || q.toLowerCase().includes("payout")) {
      reply = `SANCHAR Smart Trigger: Policy PARAMETRIC_POL_ODISHA_2026 criteria met! Sustained wind observed at 215 km/h (threshold 89 km/h) and ISRO RISAT-1A SAR confirms 44.8% flood extent. Cryptographic hash 0x7F9B1E4D... has authorized instant ₹75.0 Crore liquidity to OSDMA.`;
    } else {
      reply = `NIRNAY Supervisor Directive: Based on real-time Holland wind field and ISRO C-band SAR pass, all 3 coastal districts (Puri, Jagatsinghpur, Kendrapara) are under ESCS advisory. Priority action #1 is de-energizing coastal high-voltage substations before gale onset at T-24h.`;
    }

    setDutyChat((prev) => [...prev, userMsg, { role: "analyst", text: reply }]);
    setDutyPrompt("");
  };

  const failedCount = state.infrastructureNodes.filter((n) => n.status === "FAILED").length;
  const atRiskCount = state.infrastructureNodes.filter((n) => n.status === "AT_RISK").length;
  const hardenedCount = state.infrastructureNodes.filter((n) => n.status === "HARDENED").length;

  return (
    <div className="min-h-screen bg-[#06090E] text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-black">
      {/* 1. Tactical Command Header */}
      <header className="glass-tactical border-b border-cyan-500/20 px-6 py-3 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          {/* Logo & Platform Title */}
          <div className="flex items-center gap-3">
            <div className="relative p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <Wind className="w-6 h-6 animate-spin" style={{ animationDuration: "12s" }} />
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
              </span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-black tracking-widest font-mono text-slate-100">
                  VAYU-RAKSHA <span className="text-cyan-400 font-sans font-light">वायु रक्षा</span>
                </h1>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                  TRACK 5 · BUILD WITH AI
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-sans">
                Anticipatory Cyclone & Infrastructure Cascade Intelligence · Team SYNTRIX
              </p>
            </div>
          </div>

          {/* Scenario Selector & Telemetry Readouts */}
          <div className="flex items-center gap-4 flex-wrap">
            {/* Storm Switcher */}
            <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-xl border border-white/10">
              <button
                onClick={() => handleScenarioChange("fani")}
                className={`px-3 py-1 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                  scenario === "fani"
                    ? "bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/30"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Cyclone Fani (2019)
              </button>
              <button
                onClick={() => handleScenarioChange("dana")}
                className={`px-3 py-1 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                  scenario === "dana"
                    ? "bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/30"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Cyclone Dana (2024)
              </button>
            </div>

            {/* Telemetry Chips */}
            <div className="flex items-center gap-2">
              <div className="px-3 py-1.5 rounded-xl bg-slate-900/80 border border-white/10 text-center font-mono">
                <div className="text-[9px] uppercase text-slate-400">Peak Core Wind</div>
                <div className="text-xs font-bold text-rose-400">
                  {state.cycloneMetadata.maxSustainedWindKmh} km/h
                </div>
              </div>

              <div className="px-3 py-1.5 rounded-xl bg-slate-900/80 border border-white/10 text-center font-mono">
                <div className="text-[9px] uppercase text-slate-400">Storm Surge</div>
                <div className="text-xs font-bold text-cyan-300">
                  +{state.atmosphericData.stormSurgeCrestM} m
                </div>
              </div>

              <div className="px-3 py-1.5 rounded-xl bg-slate-900/80 border border-white/10 text-center font-mono">
                <div className="text-[9px] uppercase text-slate-400">Landfall Window</div>
                <div className="text-xs font-bold text-amber-400">
                  T-{state.cycloneMetadata.leadTimeHours}h
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* 2. Primary Navigation Bar */}
      <div className="bg-[#0A0F18] border-b border-white/5 px-6 py-2.5">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4 overflow-x-auto">
          <div className="flex items-center gap-2">
            {[
              { id: "overview", label: "Overview & Mission HUD", icon: Activity },
              { id: "cascade", label: "Cascade Failure Topology", icon: Network },
              { id: "counterfactual", label: "What-If Simulator", icon: Sparkles },
              { id: "advisories", label: "6-Lang Advisories & IVR", icon: Globe },
              { id: "insurance", label: "Parametric Smart Trigger", icon: Zap },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-mono font-semibold flex items-center gap-2 transition-all cursor-pointer whitespace-nowrap ${
                    isActive
                      ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/20"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          <div className="flex items-center gap-3 shrink-0 text-xs font-mono text-slate-400 hidden lg:flex">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              ISRO RISAT-1A SAR Ground Truth: Active
            </span>
            <span className="text-slate-600">|</span>
            <span>Ensemble: 51 Members</span>
          </div>
        </div>
      </div>

      {/* 3. Main Dashboard Workspace */}
      <main className="max-w-7xl mx-auto p-6 flex-1 flex flex-col gap-6 w-full">
        {/* 5-Agent Live Brain Activity Monitor */}
        <AgentBrainHud telemetry={state.agentTelemetry} />

        {/* Tab 1: Overview Matrix */}
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left 2 Cols: Situation Report & Key Instruments */}
            <div className="lg:col-span-2 space-y-6">
              {/* Situation Banner */}
              <div className="glass-tactical p-5 rounded-2xl border border-cyan-500/30">
                <div className="flex items-center gap-2 mb-2 text-xs font-mono text-cyan-400 font-bold">
                  <ShieldAlert className="w-4 h-4" />
                  EXECUTIVE SITUATION DIRECTIVE · NIRNAY SUPERVISOR
                </div>
                <p className="text-sm text-slate-200 leading-relaxed font-sans">
                  {state.finalSituationSummary}
                </p>

                <div className="mt-4 pt-3 border-t border-white/10 flex flex-wrap items-center justify-between gap-3 text-xs font-mono text-slate-400">
                  <div className="flex items-center gap-4">
                    <span>
                      Failed Nodes: <strong className="text-rose-400">{failedCount}</strong>
                    </span>
                    <span>
                      At Risk: <strong className="text-amber-400">{atRiskCount}</strong>
                    </span>
                    <span>
                      Hardened: <strong className="text-cyan-400">{hardenedCount}</strong>
                    </span>
                  </div>
                  <span className="text-slate-500">
                    Modeled with Holland (1980) + ISRO RISAT-1A SAR
                  </span>
                </div>
              </div>

              {/* Embedded Cascade Network Canvas */}
              <CascadeTopologyCanvas
                nodes={state.infrastructureNodes}
                edges={state.dependencyEdges}
              />
            </div>

            {/* Right Col: Duty Analyst Co-Pilot with Gemini 3.8 Flash */}
            <div className="space-y-6">
              <div className="glass-tactical p-5 rounded-2xl border border-cyan-500/30 flex flex-col h-[600px]">
                {/* Analyst Header */}
                <div className="flex items-center justify-between pb-3 border-b border-white/10">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400">
                      <Cpu className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="text-xs font-bold font-mono tracking-wider text-cyan-300">
                        DUTY ANALYST CO-PILOT
                      </h3>
                      <div className="text-[10px] text-slate-400">Gemini 3.8 Flash Extended Thinking</div>
                    </div>
                  </div>
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                </div>

                {/* Chat Log Stream */}
                <div className="flex-1 overflow-y-auto space-y-3 py-3 pr-1 text-xs">
                  {dutyChat.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`p-3 rounded-xl ${
                        msg.role === "analyst"
                          ? "bg-slate-900/90 border border-cyan-500/20 text-slate-200"
                          : "bg-cyan-500/15 border border-cyan-500/30 text-cyan-100 ml-4"
                      }`}
                    >
                      <div className="font-mono text-[10px] text-slate-400 mb-1">
                        {msg.role === "analyst" ? "🤖 NIRNAY DUTY ANALYST" : "👤 DUTY OFFICER"}
                      </div>
                      <p className="leading-relaxed">{msg.text}</p>
                    </div>
                  ))}
                </div>

                {/* Quick situational prompt chips */}
                <div className="pt-2 border-t border-white/5 space-y-2">
                  <div className="text-[10px] font-mono text-slate-400">Quick Directives:</div>
                  <div className="flex flex-wrap gap-1.5">
                    {[
                      "Why is Puri Hospital ICU at risk?",
                      "Simulate de-energizing Substation S-7",
                      "Check parametric insurance trigger status",
                    ].map((chip) => (
                      <button
                        key={chip}
                        onClick={() => handleSendPrompt(chip)}
                        className="text-[10px] font-mono px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-white/10 truncate max-w-full cursor-pointer text-left"
                      >
                        {chip}
                      </button>
                    ))}
                  </div>

                  {/* Input Box */}
                  <div className="flex items-center gap-2 pt-2">
                    <input
                      type="text"
                      value={dutyPrompt}
                      onChange={(e) => setDutyPrompt(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleSendPrompt()}
                      placeholder="Ask the duty analyst or command pre-landfall action..."
                      className="flex-1 bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-400"
                    />
                    <button
                      onClick={() => handleSendPrompt()}
                      className="p-2 rounded-xl bg-cyan-500 text-slate-950 hover:bg-cyan-400 cursor-pointer transition-all"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Full Interactive Cascade Failure Topology */}
        {activeTab === "cascade" && (
          <div className="space-y-6">
            <CascadeTopologyCanvas
              nodes={state.infrastructureNodes}
              edges={state.dependencyEdges}
            />
          </div>
        )}

        {/* Tab 3: Counterfactual "What-If" Sandbox */}
        {activeTab === "counterfactual" && (
          <div className="space-y-6">
            <CounterfactualSandbox
              actions={state.rankedActionQueue}
              onToggleAction={handleToggleHardening}
            />
          </div>
        )}

        {/* Tab 4: 6-Language Advisories & IVR Voice Hub */}
        {activeTab === "advisories" && (
          <div className="space-y-6">
            <MultilingualAdvisoryHub advisories={state.advisories} />
          </div>
        )}

        {/* Tab 5: Automated Parametric Insurance Smart Trigger */}
        {activeTab === "insurance" && (
          <div className="space-y-6">
            <ParametricSmartTrigger insurance={state.parametricInsurance} />
          </div>
        )}
      </main>

      {/* 4. Tactical Status Footer */}
      <footer className="border-t border-white/10 px-6 py-3 bg-[#06090E] text-xs font-mono text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
            <span>VAYU-RAKSHA v2.0 · Anticipatory Cyclone & Infrastructure Cascade Platform</span>
          </div>

          <div className="flex items-center gap-4">
            <span>ISRO MOSDAC + RISAT-1A SAR Native</span>
            <span className="text-slate-700">|</span>
            <span>Google Earth Engine</span>
            <span className="text-slate-700">|</span>
            <a
              href="https://github.com/Niss54/gdg"
              target="_blank"
              rel="noreferrer"
              className="text-cyan-400 hover:underline"
            >
              github.com/Niss54/gdg
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
