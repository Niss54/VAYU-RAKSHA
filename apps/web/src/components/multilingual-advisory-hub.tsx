"use client";

import React, { useState } from "react";
import { type AdvisoryNotice } from "@/lib/vayu-engine";
import { AlertCircle, Download, FileText, Globe2, Pause, Play, Volume2, Waves } from "lucide-react";

interface MultilingualAdvisoryHubProps {
  advisories: AdvisoryNotice[];
}

export function MultilingualAdvisoryHub({ advisories }: MultilingualAdvisoryHubProps) {
  const [activeLang, setActiveLang] = useState<string>("or"); // Default to Odia for coastal Odisha
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  const currentAdvisory = advisories.find((a) => a.languageCode === activeLang) || advisories[0];

  const handleToggleVoice = () => {
    setIsPlayingAudio((prev) => !prev);
    // Real browser speech synthesis if available
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      if (!isPlayingAudio) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(currentAdvisory.ivrSpeechScript);
        utterance.rate = 0.95;
        utterance.onend = () => setIsPlayingAudio(false);
        utterance.onerror = () => setIsPlayingAudio(false);
        window.speechSynthesis.speak(utterance);
      } else {
        window.speechSynthesis.cancel();
      }
    }
  };

  const handleDownloadCAP = () => {
    const xml = `<alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
  <identifier>VAYU-RAKSHA-${Date.now()}</identifier>
  <sender>OSDMA-DISASTER-HQ</sender>
  <sent>${new Date().toISOString()}</sent>
  <status>Actual</status>
  <msgType>Alert</msgType>
  <info>
    <category>Met</category>
    <event>${currentAdvisory.headline}</event>
    <urgency>${currentAdvisory.urgency}</urgency>
    <severity>Extreme</severity>
    <certainty>Observed</certainty>
    <area><areaDesc>${currentAdvisory.district}</areaDesc></area>
    <description>${currentAdvisory.plainBody}</description>
  </info>
</alert>`;
    const blob = new Blob([xml], { type: "application/xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `CAP-1.2-ADVISORY-${activeLang.toUpperCase()}.xml`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="glass-tactical rounded-2xl p-5 border border-cyan-500/25 flex flex-col gap-4">
      {/* Header & Language Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Globe2 className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold tracking-wider font-mono text-cyan-300">
                MULTILINGUAL ADVISORY & IVR BROADCAST HUB
              </h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                6 LANGUAGES
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Context-aware native advisories with automated IVR audio broadcast scripts
            </p>
          </div>
        </div>

        {/* Language Switcher Buttons */}
        <div className="flex items-center gap-1.5 bg-slate-950/80 p-1 rounded-xl border border-white/10 overflow-x-auto">
          {advisories.map((adv) => {
            const isActive = adv.languageCode === activeLang;
            return (
              <button
                key={adv.languageCode}
                onClick={() => {
                  setActiveLang(adv.languageCode);
                  if (isPlayingAudio) {
                    setIsPlayingAudio(false);
                    if (typeof window !== "undefined") window.speechSynthesis?.cancel();
                  }
                }}
                className={`px-3 py-1 rounded-lg text-xs font-mono font-semibold transition-all cursor-pointer ${
                  isActive
                    ? "bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                }`}
              >
                {adv.languageName.split(" ")[0]}
              </button>
            );
          })}
        </div>
      </div>

      {/* Advisory Content Card */}
      <div className="p-4 rounded-xl bg-slate-950/70 border border-white/10 space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 text-[11px] font-mono mb-1">
              <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-bold border border-rose-500/30">
                URGENCY: {currentAdvisory.urgency}
              </span>
              <span className="text-slate-400">Target Area:</span>
              <span className="text-slate-200 font-semibold">{currentAdvisory.district}</span>
            </div>
            <h4 className="text-base font-bold text-slate-100">{currentAdvisory.headline}</h4>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={handleDownloadCAP}
              className="px-3 py-1.5 rounded-lg text-xs font-mono bg-slate-900 hover:bg-slate-800 text-slate-300 border border-white/10 flex items-center gap-1.5 transition-all cursor-pointer"
            >
              <FileText className="w-3.5 h-3.5 text-cyan-400" />
              CAP 1.2 XML
            </button>
          </div>
        </div>

        <p className="text-sm text-slate-200 leading-relaxed pl-3 border-l-2 border-cyan-400/60 font-sans">
          {currentAdvisory.plainBody}
        </p>

        {/* Action Bulletins */}
        {currentAdvisory.actionBulletins.length > 0 && (
          <div className="space-y-1.5 pt-2 border-t border-white/5">
            <div className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-wide">
              Mandatory Field Actions:
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {currentAdvisory.actionBulletins.map((b, i) => (
                <div
                  key={i}
                  className="p-2.5 rounded-lg bg-slate-900/60 border border-white/5 text-xs text-slate-300 flex items-start gap-2"
                >
                  <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <span>{b}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* IVR Voice Audio Broadcast Simulator Bar */}
        <div className="p-3 rounded-xl bg-slate-900/90 border border-cyan-500/20 flex flex-col sm:flex-row items-center justify-between gap-3 mt-3">
          <div className="flex items-center gap-2.5 text-xs">
            <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400">
              <Volume2 className="w-4 h-4" />
            </div>
            <div>
              <div className="font-mono font-bold text-slate-200">
                Automated IVR Community Voice Broadcast
              </div>
              <div className="text-[11px] text-slate-400">
                Simulate broadcast audio stream over rural mobile networks
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
            {isPlayingAudio && (
              <div className="flex items-center gap-1 text-cyan-400">
                <span className="w-1 h-3 bg-cyan-400 animate-bounce"></span>
                <span className="w-1 h-5 bg-cyan-400 animate-bounce delay-75"></span>
                <span className="w-1 h-2 bg-cyan-400 animate-bounce delay-150"></span>
                <span className="w-1 h-4 bg-cyan-400 animate-bounce delay-100"></span>
              </div>
            )}

            <button
              onClick={handleToggleVoice}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold flex items-center gap-1.5 cursor-pointer transition-all ${
                isPlayingAudio
                  ? "bg-rose-500 text-white hover:bg-rose-600"
                  : "bg-cyan-500 text-slate-950 hover:bg-cyan-400 shadow-md shadow-cyan-500/30"
              }`}
            >
              {isPlayingAudio ? (
                <>
                  <Pause className="w-3.5 h-3.5" /> Stop Broadcast
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" /> Play IVR Audio
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
