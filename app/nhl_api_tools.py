"""NHL Official API Integration Tool for Leafs Nation Concierge."""

from typing import Any, Dict, List, Optional
import httpx

NHL_API_SCHEDULE_URL = "https://api-web.nhle.com/v1/club-schedule-season/TOR/now"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LeafsNationConcierge/1.0"


def get_nhl_live_game_feed(opponent: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
    """Fetch official schedule and game feed data from the live NHL API for the Toronto Maple Leafs.

    Args:
        opponent: Optional opponent team name or abbreviation to filter by (e.g. 'Bruins', 'MTL', 'Oilers').
        limit: Maximum number of games to return (defaults to 5).

    Returns:
        A dictionary containing upcoming official NHL games with broadcast channels, venues, and team matchups.
    """
    headers = {"User-Agent": USER_AGENT}
    try:
        with httpx.Client(timeout=10.0, headers=headers, follow_redirects=True) as client:
            resp = client.get(NHL_API_SCHEDULE_URL)
            if resp.status_code != 200:
                return {
                    "status": "error",
                    "message": f"NHL API returned HTTP status {resp.status_code}",
                }
            data = resp.json()

        raw_games: List[Dict[str, Any]] = data.get("games", [])
        matched_games = []

        for g in raw_games:
            home_team = g.get("homeTeam", {})
            away_team = g.get("awayTeam", {})
            home_name = home_team.get("commonName", {}).get("default", "")
            away_name = away_team.get("commonName", {}).get("default", "")
            home_place = home_team.get("placeName", {}).get("default", "")
            away_place = away_team.get("placeName", {}).get("default", "")

            opponent_team = away_name if home_team.get("abbrev") == "TOR" else home_name
            opponent_place = away_place if home_team.get("abbrev") == "TOR" else home_place

            if opponent:
                opp_lower = opponent.lower().strip()
                if (
                    opp_lower not in opponent_team.lower()
                    and opp_lower not in opponent_place.lower()
                    and opp_lower not in home_team.get("abbrev", "").lower()
                    and opp_lower not in away_team.get("abbrev", "").lower()
                ):
                    continue

            broadcasts = [
                b.get("network") for b in g.get("tvBroadcasts", []) if b.get("network")
            ]

            matched_games.append({
                "game_id": g.get("id"),
                "game_date": g.get("gameDate"),
                "start_time_utc": g.get("startTimeUTC"),
                "matchup": f"{away_place} {away_name} @ {home_place} {home_name}",
                "opponent": f"{opponent_place} {opponent_team}",
                "venue": g.get("venue", {}).get("default", "Scotiabank Arena"),
                "game_state": g.get("gameState"),
                "broadcasts": broadcasts or ["Sportsnet / TSN"],
                "tickets_link": g.get("ticketsLink", ""),
            })

            if len(matched_games) >= limit:
                break

        return {
            "status": "success",
            "team": "Toronto Maple Leafs",
            "total_matched": len(matched_games),
            "games": matched_games,
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch NHL live feed: {str(e)}"}
