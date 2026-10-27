"""Hockey analytics and statistical projection tools for Leafs Nation Concierge."""

from typing import Any, Dict
from app.firestore_tools import get_player


def calculate_player_pace(
    player_name: str,
    games_played: int = 15,
    goals: int = 10,
    assists: int = 12,
    target_season_games: int = 82,
) -> Dict[str, Any]:
    """Calculate and project a player's full-season scoring pace.

    If games_played, goals, and assists are provided (or defaulted), calculates the pace
    over an 82-game regular season schedule. Also looks up historical benchmarks from Firestore.

    Args:
        player_name: Name of the Maple Leafs player (e.g. 'Auston Matthews', 'Mitch Marner').
        games_played: Number of games played so far in the current stretch/season.
        goals: Goals scored in that stretch.
        assists: Assists tallied in that stretch.
        target_season_games: Full season games to project across (standard is 82).

    Returns:
        A dictionary with games, goals pace, assists pace, points pace, and historical comparison.
    """
    if games_played <= 0:
        return {"error": "games_played must be greater than 0 to calculate pace."}

    points = goals + assists
    goals_per_game = goals / games_played
    assists_per_game = assists / games_played
    points_per_game = points / games_played

    projected_goals = round(goals_per_game * target_season_games)
    projected_assists = round(assists_per_game * target_season_games)
    projected_points = projected_goals + projected_assists

    # Fetch Firestore player record if available
    firestore_info = get_player(player_name)
    career_stats = firestore_info.get("career_stats", {}) if isinstance(firestore_info, dict) else {}

    return {
        "player": player_name,
        "sample_size": {
            "games_played": games_played,
            "goals": goals,
            "assists": assists,
            "points": points,
        },
        "per_game_rates": {
            "goals_per_game": round(goals_per_game, 2),
            "assists_per_game": round(assists_per_game, 2),
            "points_per_game": round(points_per_game, 2),
        },
        "82_game_projection": {
            "target_games": target_season_games,
            "projected_goals": projected_goals,
            "projected_assists": projected_assists,
            "projected_points": projected_points,
            "pace_milestone": (
                "50+ Goal Pace!" if projected_goals >= 50
                else "100+ Point Pace!" if projected_points >= 100
                else "Strong Top-6 Pace"
            ),
        },
        "historical_context": {
            "career_goals": career_stats.get("goals", "N/A"),
            "career_points": career_stats.get("points", "N/A"),
            "contract_aav": firestore_info.get("contract", {}).get("aav", "N/A"),
        },
    }
