"""
Prometheus V7 - Steam Web API Client
Live match tracking for DreamLeague S27 and other tournaments.
"""

import os
import time
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional

import requests

# =============================================================================
# CONFIGURATION
# =============================================================================

STEAM_API_BASE = "https://api.steampowered.com"
DOTA2_API_BASE = f"{STEAM_API_BASE}/IDOTA2Match_570"

# DreamLeague S27 League ID (update if needed)
DREAMLEAGUE_S27_LEAGUE_ID = 17225

# Rate limiting
RATE_LIMIT_DELAY = 1.0  # 1 second between requests


def _get_api_key() -> Optional[str]:
    """Get Steam API key from environment."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    return os.getenv("STEAM_API_KEY")


def _make_request(endpoint: str, params: dict) -> Optional[dict]:
    """Make a request to Steam API with rate limiting."""
    api_key = _get_api_key()
    if not api_key:
        print("⚠️ STEAM_API_KEY not found in environment")
        return None

    params["key"] = api_key

    try:
        response = requests.get(endpoint, params=params, timeout=30)
        response.raise_for_status()
        time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Steam API error: {e}")
        return None


# =============================================================================
# LIVE MATCH TRACKING
# =============================================================================


def get_live_league_games(league_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get all live Dota 2 league games.

    Args:
        league_id: Filter by specific league (e.g., DreamLeague S27)

    Returns:
        List of live matches with game details
    """
    endpoint = f"{DOTA2_API_BASE}/GetLiveLeagueGames/v1"
    params = {}

    if league_id:
        params["league_id"] = league_id

    result = _make_request(endpoint, params)

    if not result:
        return []

    games = result.get("result", {}).get("games", [])

    # Process and enrich game data
    processed_games = []
    for game in games:
        processed_game = {
            "match_id": game.get("match_id"),
            "league_id": game.get("league_id"),
            "league_name": game.get("league_tier"),
            "series_id": game.get("series_id"),
            "game_number": game.get("game_number"),
            "stream_delay_s": game.get("stream_delay_s", 0),
            # Teams
            "radiant_team": {
                "team_id": game.get("radiant_team", {}).get("team_id"),
                "name": game.get("radiant_team", {}).get("team_name", "Radiant"),
                "logo": game.get("radiant_team", {}).get("team_logo"),
                "score": game.get("radiant_series_wins", 0),
            },
            "dire_team": {
                "team_id": game.get("dire_team", {}).get("team_id"),
                "name": game.get("dire_team", {}).get("team_name", "Dire"),
                "logo": game.get("dire_team", {}).get("team_logo"),
                "score": game.get("dire_series_wins", 0),
            },
            # Game state
            "game_time": game.get("game_time", 0),
            "game_time_formatted": _format_game_time(game.get("game_time", 0)),
            "radiant_score": game.get("scoreboard", {}).get("radiant", {}).get("score", 0),
            "dire_score": game.get("scoreboard", {}).get("dire", {}).get("score", 0),
            # Gold/XP advantage
            "radiant_gold_adv": _calculate_gold_advantage(game),
            "radiant_xp_adv": _calculate_xp_advantage(game),
            # Players
            "radiant_players": _extract_players(game, "radiant"),
            "dire_players": _extract_players(game, "dire"),
            # Draft
            "radiant_picks": _extract_picks(game, "radiant"),
            "dire_picks": _extract_picks(game, "dire"),
            "radiant_bans": _extract_bans(game, "radiant"),
            "dire_bans": _extract_bans(game, "dire"),
            # Metadata
            "spectators": game.get("spectators", 0),
            "last_update": datetime.now().isoformat(),
        }
        processed_games.append(processed_game)

    return processed_games


def get_dreamleague_live() -> List[Dict[str, Any]]:
    """Get live DreamLeague S27 matches."""
    return get_live_league_games(DREAMLEAGUE_S27_LEAGUE_ID)


def get_all_live_pro_matches() -> List[Dict[str, Any]]:
    """Get all live pro Dota 2 matches (no league filter)."""
    return get_live_league_games()


# =============================================================================
# MATCH DETAILS
# =============================================================================


def get_match_details(match_id: int) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a completed match.

    Args:
        match_id: The match ID to retrieve

    Returns:
        Match details including players, items, abilities
    """
    endpoint = f"{DOTA2_API_BASE}/GetMatchDetails/v1"
    params = {"match_id": match_id}

    result = _make_request(endpoint, params)

    if not result:
        return None

    match = result.get("result", {})

    return {
        "match_id": match.get("match_id"),
        "match_seq_num": match.get("match_seq_num"),
        "start_time": match.get("start_time"),
        "start_time_formatted": datetime.fromtimestamp(match.get("start_time", 0)).strftime("%Y-%m-%d %H:%M"),
        "lobby_type": match.get("lobby_type"),
        "duration": match.get("duration"),
        "duration_formatted": _format_game_time(match.get("duration", 0)),
        "radiant_win": match.get("radiant_win"),
        "winner": "Radiant" if match.get("radiant_win") else "Dire",
        # Teams
        "radiant_team_id": match.get("radiant_team_id"),
        "dire_team_id": match.get("dire_team_id"),
        "radiant_score": match.get("radiant_score"),
        "dire_score": match.get("dire_score"),
        # League
        "leagueid": match.get("leagueid"),
        "series_id": match.get("series_id"),
        "series_type": match.get("series_type"),
        "game_mode": match.get("game_mode"),
        # First blood
        "first_blood_time": match.get("first_blood_time"),
        # Tower status (bitmasks)
        "tower_status_radiant": match.get("tower_status_radiant"),
        "tower_status_dire": match.get("tower_status_dire"),
        "barracks_status_radiant": match.get("barracks_status_radiant"),
        "barracks_status_dire": match.get("barracks_status_dire"),
        # Players
        "players": [_process_player(p) for p in match.get("players", [])],
        # Picks/Bans
        "picks_bans": match.get("picks_bans", []),
    }


def get_match_history(
    account_id: Optional[int] = None,
    hero_id: Optional[int] = None,
    league_id: Optional[int] = None,
    matches_requested: int = 25,
) -> List[Dict[str, Any]]:
    """
    Get match history with optional filters.

    Args:
        account_id: Filter by player
        hero_id: Filter by hero
        league_id: Filter by league
        matches_requested: Number of matches to retrieve (max 100)

    Returns:
        List of match summaries
    """
    endpoint = f"{DOTA2_API_BASE}/GetMatchHistory/v1"
    params = {"matches_requested": min(matches_requested, 100)}

    if account_id:
        params["account_id"] = account_id
    if hero_id:
        params["hero_id"] = hero_id
    if league_id:
        params["league_id"] = league_id

    result = _make_request(endpoint, params)

    if not result:
        return []

    matches = result.get("result", {}).get("matches", [])

    return [
        {
            "match_id": m.get("match_id"),
            "match_seq_num": m.get("match_seq_num"),
            "start_time": m.get("start_time"),
            "start_time_formatted": datetime.fromtimestamp(m.get("start_time", 0)).strftime("%Y-%m-%d %H:%M"),
            "lobby_type": m.get("lobby_type"),
            "players": m.get("players", []),
        }
        for m in matches
    ]


def get_league_listing() -> List[Dict[str, Any]]:
    """Get list of available leagues."""
    endpoint = f"{DOTA2_API_BASE}/GetLeagueListing/v1"

    result = _make_request(endpoint, {})

    if not result:
        return []

    leagues = result.get("result", {}).get("leagues", [])

    return [
        {
            "leagueid": l.get("leagueid"),
            "name": l.get("name"),
            "description": l.get("description"),
            "tournament_url": l.get("tournament_url"),
            "itemdef": l.get("itemdef"),
        }
        for l in leagues
    ]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _format_game_time(seconds: int) -> str:
    """Format game time as MM:SS."""
    if seconds < 0:
        return f"-{abs(seconds) // 60}:{abs(seconds) % 60:02d}"
    return f"{seconds // 60}:{seconds % 60:02d}"


def _calculate_gold_advantage(game: dict) -> int:
    """Calculate radiant gold advantage from scoreboard."""
    scoreboard = game.get("scoreboard", {})
    radiant = scoreboard.get("radiant", {})
    dire = scoreboard.get("dire", {})

    radiant_gold = sum(p.get("gold", 0) for p in radiant.get("players", []))
    dire_gold = sum(p.get("gold", 0) for p in dire.get("players", []))

    return radiant_gold - dire_gold


def _calculate_xp_advantage(game: dict) -> int:
    """Calculate radiant XP advantage from scoreboard."""
    scoreboard = game.get("scoreboard", {})
    radiant = scoreboard.get("radiant", {})
    dire = scoreboard.get("dire", {})

    radiant_xp = sum(p.get("xp", 0) for p in radiant.get("players", []))
    dire_xp = sum(p.get("xp", 0) for p in dire.get("players", []))

    return radiant_xp - dire_xp


def _extract_players(game: dict, team: str) -> List[Dict[str, Any]]:
    """Extract player information from scoreboard."""
    scoreboard = game.get("scoreboard", {})
    team_data = scoreboard.get(team, {})

    players = []
    for p in team_data.get("players", []):
        players.append(
            {
                "account_id": p.get("account_id"),
                "hero_id": p.get("hero_id"),
                "kills": p.get("kills", 0),
                "deaths": p.get("death", 0),
                "assists": p.get("assists", 0),
                "last_hits": p.get("last_hits", 0),
                "denies": p.get("denies", 0),
                "gold": p.get("gold", 0),
                "level": p.get("level", 1),
                "gold_per_min": p.get("gold_per_min", 0),
                "xp_per_min": p.get("xp_per_min", 0),
                "net_worth": p.get("net_worth", 0),
                "items": [p.get(f"item{i}", 0) for i in range(6)],
                "position_x": p.get("position_x"),
                "position_y": p.get("position_y"),
            }
        )

    return players


def _extract_picks(game: dict, team: str) -> List[int]:
    """Extract hero picks for a team."""
    picks = game.get("scoreboard", {}).get(team, {}).get("picks", [])
    return [p.get("hero_id") for p in picks]


def _extract_bans(game: dict, team: str) -> List[int]:
    """Extract hero bans for a team."""
    bans = game.get("scoreboard", {}).get(team, {}).get("bans", [])
    return [b.get("hero_id") for b in bans]


def _process_player(player: dict) -> Dict[str, Any]:
    """Process player data from match details."""
    return {
        "account_id": player.get("account_id"),
        "player_slot": player.get("player_slot"),
        "team": "radiant" if player.get("player_slot", 0) < 128 else "dire",
        "hero_id": player.get("hero_id"),
        "kills": player.get("kills", 0),
        "deaths": player.get("deaths", 0),
        "assists": player.get("assists", 0),
        "kda": f"{player.get('kills', 0)}/{player.get('deaths', 0)}/{player.get('assists', 0)}",
        "last_hits": player.get("last_hits", 0),
        "denies": player.get("denies", 0),
        "gold_per_min": player.get("gold_per_min", 0),
        "xp_per_min": player.get("xp_per_min", 0),
        "level": player.get("level", 1),
        "hero_damage": player.get("hero_damage", 0),
        "tower_damage": player.get("tower_damage", 0),
        "hero_healing": player.get("hero_healing", 0),
        "gold_spent": player.get("gold_spent", 0),
        "net_worth": player.get("net_worth", player.get("gold", 0)),
        "items": [player.get(f"item_{i}", 0) for i in range(6)],
        "backpack": [player.get(f"backpack_{i}", 0) for i in range(3)],
        "item_neutral": player.get("item_neutral", 0),
    }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def is_dreamleague_live() -> bool:
    """Check if there's a live DreamLeague match."""
    games = get_dreamleague_live()
    return len(games) > 0


def get_live_match_summary() -> Dict[str, Any]:
    """Get a quick summary of all live pro matches."""
    games = get_all_live_pro_matches()

    return {
        "total_live_matches": len(games),
        "dreamleague_matches": len([g for g in games if g.get("league_id") == DREAMLEAGUE_S27_LEAGUE_ID]),
        "matches": [
            {
                "match_id": g.get("match_id"),
                "teams": f"{g['radiant_team']['name']} vs {g['dire_team']['name']}",
                "score": f"{g['radiant_team']['score']}-{g['dire_team']['score']}",
                "game_time": g.get("game_time_formatted"),
                "kills": f"{g.get('radiant_score', 0)}-{g.get('dire_score', 0)}",
            }
            for g in games
        ],
        "last_check": datetime.now().isoformat(),
    }


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("🎮 Testing Steam API...")

    # Test live games
    print("\n📺 Checking live matches...")
    live = get_live_match_summary()
    print(f"   Total live: {live['total_live_matches']}")
    print(f"   DreamLeague: {live['dreamleague_matches']}")

    for match in live.get("matches", [])[:3]:
        print(f"   • {match['teams']} ({match['score']}) - {match['game_time']} - Kills: {match['kills']}")

    print("\n✅ Steam API test complete!")
