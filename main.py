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
from google.adk.runners import InMemoryRunner
from google.genai import types
from app.agent import app

async def main():
    print("Initializing InMemoryRunner...")
    runner = InMemoryRunner(app=app)
    
    session = await runner.session_service.create_session(
        app_name="diatax-web", user_id="test_user"
    )
    
    import json
    sample_input = json.dumps({
        "repo_url": "https://github.com/google/adk-samples",
        "guide_type": "tutorial",
        "description": "Sample description"
    })
    print("Starting session run...")
    
    async for event in runner.run_async(
        user_id="test_user",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part.from_text(text=sample_input)]),
    ):
        if event.output is not None:
            print(f"[Node Output]: {event.output}")
        if event.actions and event.actions.state_delta:
            print(f"[State Delta]: {event.actions.state_delta}")

if __name__ == "__main__":
    asyncio.run(main())
