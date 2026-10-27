"""Firestore client and tools for Leafs Nation Concierge."""

from typing import Any, Dict, List, Optional
from google.cloud import firestore

# Hardcoded project ID as required to avoid runtime project-number mismatch on Agent Platform
PROJECT_ID = "qwiklabs-gcp-04-c873db07994b"

_db: Optional[firestore.Client] = None


def get_db() -> firestore.Client:
    """Returns a singleton Firestore client instance with the explicit project ID."""
    global _db
    if _db is None:
        _db = firestore.Client(project=PROJECT_ID)
    return _db


def get_player(player_name_or_id: str) -> Dict[str, Any]:
    """Look up a Toronto Maple Leafs player by name or ID.

    Args:
        player_name_or_id: The player's name (e.g. 'Auston Matthews', 'Marner') or doc id ('auston-matthews').

    Returns:
        A dictionary containing player details, bio, career stats, and contract info, or an error status if not found.
    """
    db = get_db()
    norm = player_name_or_id.strip().lower()

    # Try direct document ID lookup first
    doc_id = norm.replace(" ", "-")
    doc = db.collection("leafs_players").document(doc_id).get()
    if doc.exists:
        return doc.to_dict()

    # Query all players and match by name
    players = db.collection("leafs_players").stream()
    for p in players:
        data = p.to_dict()
        name = data.get("name", "").lower()
        if norm in name or name in norm or norm in str(data.get("number")):
            return data

    return {"status": "not_found", "message": f"Player '{player_name_or_id}' was not found in the roster database."}


def list_players(position: Optional[str] = None) -> List[Dict[str, Any]]:
    """List Toronto Maple Leafs players on the roster, optionally filtered by position.

    Args:
        position: Optional position filter (e.g. 'Center', 'Right Wing', 'Defenseman', 'Goaltender').

    Returns:
        A list of player summaries.
    """
    db = get_db()
    players_ref = db.collection("leafs_players")
    results = []

    for doc in players_ref.stream():
        data = doc.to_dict()
        if position:
            if data.get("position", "").lower() != position.strip().lower():
                continue
        results.append({
            "name": data.get("name"),
            "number": data.get("number"),
            "position": data.get("position"),
            "captain": data.get("captain", False),
            "status": data.get("season_2026_2027_status"),
        })

    return results


def save_or_update_player(
    player_id: str,
    name: str,
    number: int,
    position: str,
    bio: str,
    status: str,
) -> Dict[str, Any]:
    """Save or update a Toronto Maple Leafs player entry in Firestore.

    Args:
        player_id: A unique identifier (e.g., 'matthew-knies').
        name: Full name of the player.
        number: Jersey number.
        position: Player position (e.g. 'Left Wing').
        bio: Short biography or notes on the player.
        status: 2026/2027 season status (e.g. 'Active Roster - 2nd Line LW').

    Returns:
        A status dictionary confirming the write.
    """
    db = get_db()
    doc_ref = db.collection("leafs_players").document(player_id.strip().lower().replace(" ", "-"))
    data = {
        "id": player_id,
        "name": name,
        "number": number,
        "position": position,
        "bio": bio,
        "season_2026_2027_status": status,
    }
    doc_ref.set(data, merge=True)
    return {"status": "success", "message": f"Player {name} (#{number}) saved successfully."}


def get_schedule(opponent: Optional[str] = None, home_away: Optional[str] = None) -> List[Dict[str, Any]]:
    """Query the Toronto Maple Leafs 2026/2027 season schedule.

    Args:
        opponent: Optional opponent team name to filter by (e.g. 'Montreal', 'Boston').
        home_away: Optional filter for 'Home' or 'Away' games.

    Returns:
        A list of scheduled games matching the criteria.
    """
    db = get_db()
    games_ref = db.collection("leafs_schedule_2026_2027")
    games = []

    for doc in games_ref.stream():
        data = doc.to_dict()
        if opponent and opponent.lower() not in data.get("opponent", "").lower():
            continue
        if home_away and data.get("home_away", "").lower() != home_away.lower():
            continue
        games.append(data)

    # Sort games chronologically
    games.sort(key=lambda g: g.get("date", ""))
    return games


def add_schedule_game(
    game_id: str,
    date: str,
    time_et: str,
    opponent: str,
    venue: str,
    home_away: str,
    broadcast: str,
    notes: str = "",
) -> Dict[str, Any]:
    """Add a new game to the Toronto Maple Leafs 2026/2027 schedule.

    Args:
        game_id: Unique game id (e.g. 'game-2026-11-12-det').
        date: Game date in YYYY-MM-DD format.
        time_et: Start time in ET (e.g. '19:00').
        opponent: Opponent team name.
        venue: Venue name (e.g. 'Scotiabank Arena, Toronto').
        home_away: Either 'Home' or 'Away'.
        broadcast: TV/broadcast network (e.g. 'Sportsnet', 'TSN4').
        notes: Special notes about the matchup.

    Returns:
        A confirmation status dictionary.
    """
    db = get_db()
    doc_ref = db.collection("leafs_schedule_2026_2027").document(game_id)
    game_data = {
        "id": game_id,
        "date": date,
        "time_et": time_et,
        "opponent": opponent,
        "venue": venue,
        "home_away": home_away,
        "broadcast": broadcast,
        "notes": notes,
    }
    doc_ref.set(game_data, merge=True)
    return {"status": "success", "message": f"Game vs {opponent} on {date} recorded successfully."}
