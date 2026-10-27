"""TheSportsDB public sports API tool for Leafs Nation Concierge.

Listed under Sports & Fitness in github.com/public-apis/public-apis.
Uses THESPORTSDB_API_KEY if configured in the environment, falling back to '123' (TheSportsDB free tier key).
"""

import os
from typing import Any, Dict, List, Optional
import httpx

API_BASE_URL = "https://www.thesportsdb.com/api/v1/json"


def get_api_key() -> str:
    """Read API key from environment variable, falling back to free community test key '123'."""
    return os.environ.get("THESPORTSDB_API_KEY", "123").strip()


def search_hockey_player_profile(player_name: str) -> Dict[str, Any]:
    """Search for an NHL player's media profile, images, and bio via TheSportsDB public API.

    Args:
        player_name: Name of the player to search (e.g. 'Auston Matthews', 'Mitch Marner', 'William Nylander').

    Returns:
        A dictionary containing verified media thumbnails, nationality, team, position, and cutout images.
    """
    key = get_api_key()
    url = f"{API_BASE_URL}/{key}/searchplayers.php"
    params = {"p": player_name}

    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            resp = client.get(url, params=params)
            if resp.status_code != 200:
                return {
                    "status": "error",
                    "message": f"TheSportsDB returned HTTP {resp.status_code}",
                }
            data = resp.json()

        players: Optional[List[Dict[str, Any]]] = data.get("player")
        if not players:
            return {
                "status": "not_found",
                "message": f"No player profile found for '{player_name}' on TheSportsDB.",
            }

        # Filter for ice hockey if multiple sports match
        matched = None
        for p in players:
            if p.get("strSport") == "Ice Hockey":
                matched = p
                break
        if not matched:
            matched = players[0]

        return {
            "status": "success",
            "player_id": matched.get("idPlayer"),
            "name": matched.get("strPlayer"),
            "team": matched.get("strTeam"),
            "sport": matched.get("strSport"),
            "position": matched.get("strPosition"),
            "nationality": matched.get("strNationality"),
            "birth_date": matched.get("dateBorn"),
            "thumbnail_url": matched.get("strThumb"),
            "cutout_url": matched.get("strCutout"),
            "description": matched.get("strDescriptionEN", "")[:300] if matched.get("strDescriptionEN") else "",
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to query TheSportsDB: {str(e)}"}
