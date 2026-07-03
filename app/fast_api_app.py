# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import contextlib
import os
from collections.abc import AsyncIterator

import google.auth
from a2a.server.tasks import InMemoryTaskStore
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.runners import Runner
from google.cloud import logging as google_cloud_logging

from app.app_utils import services
from app.app_utils.a2a import attach_a2a_routes
from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uuid
import json
from pathlib import Path
from google.genai import types

load_dotenv()
setup_telemetry()

import logging

class FallbackLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        logging.basicConfig(level=logging.INFO)
        
    def log_struct(self, info, severity="INFO"):
        self.logger.info(f"[{severity}] {json.dumps(info)}")

try:
    _, project_id = google.auth.default()
    logging_client = google_cloud_logging.Client()
    logger = logging_client.logger(__name__)
except Exception:
    logger = FallbackLogger(__name__)

allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    from app.agent import app as adk_app
    from app.agent import root_agent

    runner = Runner(
        app=adk_app,
        session_service=services.get_session_service(),
        artifact_service=services.get_artifact_service(),
        auto_create_session=True,
    )
    app.state.runner = runner
    app.state.agent_app_name = adk_app.name
    await attach_a2a_routes(
        app,
        agent=root_agent,
        runner=runner,
        task_store=InMemoryTaskStore(),
        rpc_path=f"/a2a/{adk_app.name}",
    )
    yield


app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=services.ARTIFACT_SERVICE_URI,
    allow_origins=allow_origins,
    session_service_uri=services.SESSION_SERVICE_URI,
    otel_to_cloud=False,
    lifespan=lifespan,
)
app.title = "diatax-web"
app.description = "API for interacting with the Agent diatax-web"

# Schema for generation request
class GenerateRequest(BaseModel):
    repo_url: str
    guide_type: str
    description: str

@app.post("/generate")
async def generate(req: GenerateRequest):
    runner = app.state.runner
    
    # Create the ADK runner session
    session = await runner.session_service.create_session(
        app_name=app.state.agent_app_name, user_id="web_user"
    )
    
    # Build payload to send as user input
    payload = {
        "repo_url": req.repo_url,
        "guide_type": req.guide_type,
        "description": req.description
    }
    
    # Run the workflow
    session_id = None
    async for event in runner.run_async(
        user_id="web_user",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part.from_text(text=json.dumps(payload))]),
    ):
        if event.actions and event.actions.state_delta:
            state_delta = event.actions.state_delta
            if "session_id" in state_delta:
                session_id = state_delta["session_id"]
                
    if not session_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="The agent workflow failed to initialize the workspace.")
        
    return {
        "status": "success",
        "session_id": session_id
    }

# Mount static directories and index endpoint
app.mount("/workspace_tmp", StaticFiles(directory="workspace_tmp"), name="workspaces")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/download/{session_id}")
async def download_session_zip(session_id: str, background_tasks: BackgroundTasks):
    from app.agent import rmtree_force
    zip_path = Path("workspace_tmp") / session_id / "documentation.zip"
    
    if not zip_path.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="The file does not exist or has already been deleted.")
        
    def cleanup():
        import time
        time.sleep(2)  # Delay to ensure response is fully sent
        rmtree_force(Path("workspace_tmp") / session_id)
        
    background_tasks.add_task(cleanup)
    
    return FileResponse(
        path=zip_path,
        filename="documentation.zip",
        media_type="application/zip"
    )


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
