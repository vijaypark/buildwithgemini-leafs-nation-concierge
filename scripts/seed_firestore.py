#!/usr/bin/env python3
"""Seed script for Leafs Nation Concierge Firestore database."""

from google.cloud import firestore

# Hardcoded project ID as required to avoid runtime project-number mismatch
PROJECT_ID = "qwiklabs-gcp-04-c873db07994b"

PLAYERS = [
    {
        "id": "auston-matthews",
        "name": "Auston Matthews",
        "number": 34,
        "position": "Center",
        "captain": True,
        "birth_date": "1997-09-17",
        "shoots": "Left",
        "bio": "Elite goal-scoring center and franchise captain for the Toronto Maple Leafs.",
        "career_stats": {"games_played": 562, "goals": 368, "assists": 281, "points": 649},
        "contract": {"aav": 13250000, "expiry_year": 2028},
        "season_2026_2027_status": "Active Roster - 1st Line Center",
    },
    {
        "id": "mitch-marner",
        "name": "Mitch Marner",
        "number": 16,
        "position": "Right Wing",
        "captain": False,
        "birth_date": "1997-05-05",
        "shoots": "Right",
        "bio": "Playmaking winger renowned for vision, play-creation, and penalty killing excellence.",
        "career_stats": {"games_played": 576, "goals": 194, "assists": 445, "points": 639},
        "contract": {"aav": 10900000, "expiry_year": 2028},
        "season_2026_2027_status": "Active Roster - 1st Line Wing",
    },
    {
        "id": "william-nylander",
        "name": "William Nylander",
        "number": 88,
        "position": "Right Wing",
        "captain": False,
        "birth_date": "1996-05-01",
        "shoots": "Right",
        "bio": "Dynamic offensive threat with elite zone-entry and puck-possession skills.",
        "career_stats": {"games_played": 603, "goals": 217, "assists": 311, "points": 528},
        "contract": {"aav": 11500000, "expiry_year": 2032},
        "season_2026_2027_status": "Active Roster - 2nd Line Wing",
    },
    {
        "id": "morgan-rielly",
        "name": "Morgan Rielly",
        "number": 44,
        "position": "Defenseman",
        "captain": False,
        "birth_date": "1994-03-09",
        "shoots": "Left",
        "bio": "Top-pairing offensive defenseman and longest-tenured active Maple Leaf.",
        "career_stats": {"games_played": 791, "goals": 80, "assists": 392, "points": 472},
        "contract": {"aav": 7500000, "expiry_year": 2030},
        "season_2026_2027_status": "Active Roster - Top Pairing D",
    },
    {
        "id": "anthony-stolarz",
        "name": "Anthony Stolarz",
        "number": 41,
        "position": "Goaltender",
        "captain": False,
        "birth_date": "1994-01-20",
        "shoots": "Left",
        "bio": "Solid veteran goaltender providing dependable netminding tandem presence.",
        "career_stats": {"games_played": 108, "save_pct": 0.915, "gaa": 2.69, "wins": 43},
        "contract": {"aav": 2500000, "expiry_year": 2027},
        "season_2026_2027_status": "Active Roster - Goaltender Tandem",
    },
]

GAMES_2026_2027 = [
    {
        "id": "game-2026-10-10-mtl",
        "date": "2026-10-10",
        "time_et": "19:00",
        "opponent": "Montreal Canadiens",
        "venue": "Scotiabank Arena, Toronto",
        "home_away": "Home",
        "broadcast": "CBC / Sportsnet",
        "notes": "2026-2027 Season Home Opener rivalry match",
    },
    {
        "id": "game-2026-10-15-bos",
        "date": "2026-10-15",
        "time_et": "19:00",
        "opponent": "Boston Bruins",
        "venue": "TD Garden, Boston",
        "home_away": "Away",
        "broadcast": "TSN4 / NESN",
        "notes": "Original Six showdown in Boston",
    },
    {
        "id": "game-2026-10-22-edm",
        "date": "2026-10-22",
        "time_et": "19:30",
        "opponent": "Edmonton Oilers",
        "venue": "Scotiabank Arena, Toronto",
        "home_away": "Home",
        "broadcast": "Sportsnet / TNT",
        "notes": "Auston Matthews vs Connor McDavid marquee game",
    },
    {
        "id": "game-2026-11-05-ott",
        "date": "2026-11-05",
        "time_et": "19:00",
        "opponent": "Ottawa Senators",
        "venue": "Canadian Tire Centre, Ottawa",
        "home_away": "Away",
        "broadcast": "TSN4 / RDS",
        "notes": "Battle of Ontario road game",
    },
]


def seed():
    print(f"Connecting to Firestore using project ID: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)

    print("Seeding 'leafs_players' collection...")
    for player in PLAYERS:
        doc_ref = db.collection("leafs_players").document(player["id"])
        doc_ref.set(player)
        print(f"  - Added player: {player['name']} (#{player['number']})")

    print("Seeding 'leafs_schedule_2026_2027' collection...")
    for game in GAMES_2026_2027:
        doc_ref = db.collection("leafs_schedule_2026_2027").document(game["id"])
        doc_ref.set(game)
        print(f"  - Added game: {game['date']} vs {game['opponent']}")

    print("✅ Firestore seed complete!")


if __name__ == "__main__":
    seed()
