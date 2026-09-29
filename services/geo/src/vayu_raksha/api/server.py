"""VAYU-RAKSHA FastAPI Application Server.

Exposes REST and real-time streaming endpoints for the 5-agent LangGraph platform,
ISRO/GEE satellite telemetry, and counterfactual simulation sandbox.
"""

from typing import Any, Dict, List, Optional
import time

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
except ImportError:
    # If fastapi is not installed in the local environment, create mock stubs
    FastAPI = None
    BaseModel = object
    Field = lambda **kwargs: None

from vayu_raksha.data.mosdac_client import IsroMosdacClient
from vayu_raksha.data.risat_client import IsroRisatClient
from vayu_raksha.engine.cascade_graph import CascadeGraphEngine
from vayu_raksha.engine.counterfactual import CounterfactualOptimizer
from vayu_raksha.graph.workflow import VayuRakshaWorkflow


class AssessRequest(BaseModel):
    scenario: str = Field(default="fani", description="Cyclone scenario ('fani' or 'dana')")
    hardened_node_ids: List[str] = Field(default_factory=list, description="IDs of pre-isolated/hardened assets")


class CounterfactualRequest(BaseModel):
    scenario: str = Field(default="fani")
    toggle_node_id: str = Field(..., description="ID of node to isolate/reinforce")
    currently_hardened_ids: List[str] = Field(default_factory=list)


def create_app():
    """Initializes the FastAPI application."""
    if FastAPI is None:
        return None

    app = FastAPI(
        title="VAYU-RAKSHA API",
        version="2.0.0",
        description="Anticipatory Cyclone & Infrastructure Cascade Intelligence Platform (Team SYNTRIX)",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    workflow = VayuRakshaWorkflow()
    mosdac_client = IsroMosdacClient()
    risat_client = IsroRisatClient()

    @app.get("/health")
    def health_check() -> Dict[str, str]:
        return {
            "status": "healthy",
            "platform": "VAYU-RAKSHA",
            "version": "2.0.0",
            "agents_registered": "5 (NIRNAY, BHUMI, VAYU, SETU, SANCHAR)",
        }

    @app.post("/api/pipeline/assess")
    def run_assessment(req: AssessRequest) -> Dict[str, Any]:
        """Runs the 5-agent LangGraph pipeline."""
        state = workflow.create_initial_state(req.scenario)
        result = workflow.execute_pipeline(state)
        return {"success": True, "data": result}

    @app.get("/api/satellite/telemetry")
    def get_satellite_telemetry(storm_id: str = Query(default="FANI_2019")) -> Dict[str, Any]:
        """Returns live/benchmark ISRO MOSDAC and RISAT-1A SAR radar telemetry."""
        insat = mosdac_client.fetch_insat3ds_cyclone_telemetry(storm_id)
        risat = risat_client.fetch_disaster_pass_flood_mask("OD_PURI")
        return {
            "success": True,
            "insat_3ds": insat,
            "risat_1a_sar": risat,
        }

    return app


app = create_app()
