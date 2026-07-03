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

import asyncio
import json
from google.adk.runners import InMemoryRunner
from google.genai import types
from app.agent import app

# =========================================================================
# Local CLI Verification Script (main.py)
# =========================================================================
# This script enables developers to run the multi-agent graph workflow
# directly in the terminal to inspect state changes and outputs in real-time.
# =========================================================================
async def main():
    print("Initializing InMemoryRunner...")
    # Binds our ADK Workflow App definition to a local InMemoryRunner instance
    runner = InMemoryRunner(app=app)
    
    # Initialize a new session thread for local tracking
    session = await runner.session_service.create_session(
        app_name="diatax-web", user_id="test_user"
    )
    
    # Setup mock input payload representing client inputs
    sample_input = json.dumps({
        "repo_url": "https://github.com/google/adk-samples",
        "guide_type": "tutorial",
        "description": "Sample description"
    })
    print("Starting session run...")
    
    # Run graph node execution asynchronously and print trace logs of state modifications
    async for event in runner.run_async(
        user_id="test_user",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part.from_text(text=sample_input)]),
    ):
        if event.output is not None:
            # Prints outputs returned specifically by the active Node function
            print(f"[Node Output]: {event.output}")
        if event.actions and event.actions.state_delta:
            # Prints details of global state updates in the shared workflow context
            print(f"[State Delta]: {event.actions.state_delta}")

if __name__ == "__main__":
    # Execute the event loop locally
    asyncio.run(main())
