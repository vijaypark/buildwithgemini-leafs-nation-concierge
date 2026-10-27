# ruff: noqa
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

import datetime
import os
import sys
from zoneinfo import ZoneInfo

_VENDOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor")
if _VENDOR_DIR not in sys.path:
    sys.path.insert(0, _VENDOR_DIR)

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback

MODEL = "gemini-3.8-flash"
SANDBOX_RESOURCE_NAME = (
    "projects/124744075477/locations/us-east1/reasoningEngines/8617240963275816960"
    "/sandboxEnvironments/7406261946187513856"
)


from app.analytics_tools import calculate_player_pace
from app.firestore_tools import (
    add_schedule_game,
    get_player,
    get_schedule,
    list_players,
    save_or_update_player,
)
from app.nhl_api_tools import get_nhl_live_game_feed
from app.poster_tools import generate_vintage_game_poster
from app.sportsdb_tools import search_hockey_player_profile


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: after each turn, send the session events to Memory Bank for extraction."""
    await callback_context.add_session_to_memory()
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

ROLE_DESCRIPTION = (
    "You are the LeafsNation Concierge, an expert sports assistant dedicated to the Toronto Maple Leafs "
    "and their 2026/2027 NHL season. You have access to:\n"
    "1. A live Firestore database for local player roster details, bios, contracts, and custom 2026/2027 game notes.\n"
    "2. The live official NHL schedule and game feed (via get_nhl_live_game_feed) for real-time broadcast and fixture data.\n"
    "3. An analytics engine (calculate_player_pace) for projecting 82-game goals and points paces based on current scoring streaks.\n"
    "4. A poster generator (generate_vintage_game_poster) that creates collectible 1940s-style retro match posters and stores them in Cloud Storage.\n"
    "5. TheSportsDB public sports API (search_hockey_player_profile) for official player media, headshots, and profile cutouts.\n"
    "6. A secure Agent Platform Python sandbox (AgentEngineSandboxCodeExecutor) to write and run Python calculations, data simulations, or hockey statistics scripts when needed.\n"
    "7. A persistent Memory Bank to remember everything the user mentions about players (favorite players, opinions on roster/lines, player stats, trade thoughts) and games (games attended or watched, favorite matchups, schedule preferences, poster designs, rivalries). Actively incorporate these remembered facts in future sessions.\n"
    "Always be engaging, accurate, and cater directly to Leafs fans."
)

instruction = schema_manager.generate_system_prompt(
    role_description=ROLE_DESCRIPTION,
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name=SANDBOX_RESOURCE_NAME
    ),
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        get_player,
        list_players,
        save_or_update_player,
        get_schedule,
        add_schedule_game,
        get_nhl_live_game_feed,
        calculate_player_pace,
        generate_vintage_game_poster,
        search_hockey_player_profile,
        get_weather,
        get_current_time,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
