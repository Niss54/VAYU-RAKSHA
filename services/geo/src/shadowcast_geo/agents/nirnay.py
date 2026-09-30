"""NIRNAY — Supervisor Agent.

Orchestrates sub-agents and synthesizes outputs into a ranked
pre-landfall action queue and executive district brief.
Uses Gemini Flash (with template fallback) for structured reasoning.
"""
from __future__ import annotations

import logging
import os
from shadowcast_geo.agents.state import CycloneState

logger = logging.getLogger("shadowcast_geo.agents.nirnay")
_iteration_limit = 2


def run(state: CycloneState) -> CycloneState:
    """NIRNAY synthesis step — runs at start (routing) and end (final brief)."""
    state = dict(state)
    state["iteration_count"] = state.get("iteration_count", 0) + 1

    if state["iteration_count"] >= _iteration_limit:
        state["final_brief"] = _synthesize_brief(state)
        state["action_queue"] = state.get("hardening_actions", [])
        logger.info("NIRNAY: final brief generated, %d actions queued", len(state["action_queue"]))
    return state


def route(state: CycloneState) -> str:
    """Route: first call starts parallel sub-agents, second call finalizes."""
    if state.get("iteration_count", 0) >= _iteration_limit:
        return "finalize"
    return "start_parallel"


def _synthesize_brief(state: CycloneState) -> str:
    """Generate final district brief using Gemini or template fallback."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = f"""
You are NIRNAY, the supervisor AI for cyclone disaster management in India.
Synthesize the following multi-agent analysis into a concise District Collector brief.

Storm: {state.get('storm_name')}
Wind intensity: {state.get('intensity_kt', 'unknown')} kt
ISRO MOSDAC intensity: {state.get('mosdac_intensity_kt', 'not available')} kt
Rapid intensification risk: {state.get('ri_risk', False)}
Surge peak: {state.get('surge_peak_m', 'unknown')} m
Extreme rain sites: {state.get('rain_extreme_sites', 0)}
Infrastructure nodes in cascade graph: {state.get('infrastructure_nodes', 0)}
Cascade failure chains identified: {state.get('cascade_chains_count', 0)}
Population at cascade risk: {state.get('population_at_cascade_risk', 0):,.0f}

Top pre-landfall action: {state.get('top_action', 'none identified')}

Write a 3-paragraph brief:
1. Situation summary (storm status, ISRO validation)
2. Critical cascade risks (which assets, what chain)
3. Immediate actions for District Collector (ranked, with timing)

Be specific. Use real numbers. Write for a District Collector who has 30 seconds.
"""
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as exc:
            logger.warning("Gemini brief generation failed: %s — using template", exc)

    return _template_brief(state)


def _template_brief(state: CycloneState) -> str:
    return (
        f"VAYU-RAKSHA SITUATION BRIEF — {state.get('storm_name', 'CYCLONE')}\n\n"
        f"STORM: Intensity {state.get('intensity_kt', 'N/A')} kt | "
        f"Surge peak {state.get('surge_peak_m', 'N/A')} m | "
        f"RI risk: {'YES' if state.get('ri_risk') else 'NO'} (ISRO MOSDAC)\n\n"
        f"CASCADE RISK: {state.get('cascade_chains_count', 0)} failure chains identified. "
        f"~{state.get('population_at_cascade_risk', 0):,.0f} people at cascade risk.\n\n"
        f"TOP ACTION: {state.get('top_action', 'See action queue.')}\n"
        f"Total actions queued: {len(state.get('hardening_actions', []))}"
    )
