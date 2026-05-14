"""
Prometheus V7 - Analytics Engine
Correlations, predictions, and match analysis for Dota 2.
"""

import json
import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# =============================================================================
# DATA LOADING
# =============================================================================

DATABASE_PATH = Path(__file__).parent.parent / "Database" / "Json"


def _load_json(filepath: Path) -> dict:
    """Load JSON file safely."""
    try:
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def load_pro_teams() -> List[Dict[str, Any]]:
    """Load pro teams data."""
    data = _load_json(DATABASE_PATH / "teams" / "pro_teams.json")
    return data.get("teams", [])


def load_pro_players() -> List[Dict[str, Any]]:
    """Load pro players data."""
    data = _load_json(DATABASE_PATH / "players" / "pro_players.json")
    return data.get("players", [])


def load_dreamleague() -> Dict[str, Any]:
    """Load DreamLeague S27 data."""
    return _load_json(DATABASE_PATH / "leagues" / "dreamleague_s27.json")


def load_heroes_meta() -> List[Dict[str, Any]]:
    """Load heroes meta data."""
    data = _load_json(DATABASE_PATH / "heroes" / "heroes_meta.json")
    return data.get("heroes", [])


# =============================================================================
# TEAM ANALYTICS
# =============================================================================


def get_team_by_id(team_id: int) -> Optional[Dict[str, Any]]:
    """Get team data by team_id."""
    teams = load_pro_teams()
    for team in teams:
        if team.get("team_id") == team_id:
            return team
    return None


def get_team_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get team data by name (case-insensitive)."""
    teams = load_pro_teams()
    name_lower = name.lower()
    for team in teams:
        if team.get("name", "").lower() == name_lower or team.get("tag", "").lower() == name_lower:
            return team
    return None


def calculate_team_form(team: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate team's current form based on recent stats."""
    recent = team.get("recent_stats", {})

    winrate = recent.get("winrate", 0)
    matches = recent.get("matches", 0)

    # Form rating: scale from 0-100
    form_score = winrate

    # Adjust based on match volume
    if matches < 50:
        form_score *= 0.9  # Penalty for small sample

    # Determine form tier
    if form_score >= 65:
        form_tier = "🔥 Hot"
    elif form_score >= 55:
        form_tier = "✅ Good"
    elif form_score >= 45:
        form_tier = "😐 Average"
    else:
        form_tier = "❄️ Cold"

    return {
        "form_score": round(form_score, 1),
        "form_tier": form_tier,
        "recent_winrate": winrate,
        "recent_matches": matches,
        "avg_duration_min": recent.get("avg_duration_min", 0),
    }


def get_team_hero_pool(team: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get team's hero pool with statistics."""
    from hero_mapper import get_hero_image_url, get_hero_name

    top_heroes = team.get("top_heroes", [])

    hero_pool = []
    for hero in top_heroes:
        hero_id = hero.get("hero_id")
        hero_pool.append(
            {
                "hero_id": hero_id,
                "hero_name": get_hero_name(hero_id),
                "image_url": get_hero_image_url(hero_id, "icon"),
                "games": hero.get("games", 0),
                "wins": hero.get("wins", 0),
                "winrate": hero.get("winrate", 0),
            }
        )

    return hero_pool


def compare_hero_pools(team_a: Dict[str, Any], team_b: Dict[str, Any]) -> Dict[str, Any]:
    """Compare hero pools of two teams to find overlaps and advantages."""
    from hero_mapper import get_hero_name

    pool_a = {h.get("hero_id"): h for h in team_a.get("top_heroes", [])}
    pool_b = {h.get("hero_id"): h for h in team_b.get("top_heroes", [])}

    # Find contested heroes (both teams play)
    contested = set(pool_a.keys()) & set(pool_b.keys())

    contested_heroes = []
    for hero_id in contested:
        hero_a = pool_a[hero_id]
        hero_b = pool_b[hero_id]

        contested_heroes.append(
            {
                "hero_id": hero_id,
                "hero_name": get_hero_name(hero_id),
                "team_a_games": hero_a.get("games", 0),
                "team_a_winrate": hero_a.get("winrate", 0),
                "team_b_games": hero_b.get("games", 0),
                "team_b_winrate": hero_b.get("winrate", 0),
                "advantage": "A" if hero_a.get("winrate", 0) > hero_b.get("winrate", 0) else "B",
            }
        )

    # Unique heroes for each team
    unique_a = [get_hero_name(h) for h in pool_a.keys() if h not in contested]
    unique_b = [get_hero_name(h) for h in pool_b.keys() if h not in contested]

    return {
        "contested_heroes": contested_heroes,
        "unique_to_team_a": unique_a,
        "unique_to_team_b": unique_b,
        "total_overlap": len(contested),
    }


# =============================================================================
# HEAD-TO-HEAD ANALYSIS
# =============================================================================


def calculate_h2h(team_a_name: str, team_b_name: str) -> Dict[str, Any]:
    """
    Calculate head-to-head statistics between two teams.
    Note: This is a placeholder - actual H2H requires match history data.
    """
    team_a = get_team_by_name(team_a_name)
    team_b = get_team_by_name(team_b_name)

    if not team_a or not team_b:
        return {"error": "Team not found"}

    # Basic comparison based on available stats
    a_rating = team_a.get("rating", 0)
    b_rating = team_b.get("rating", 0)

    a_recent = team_a.get("recent_stats", {})
    b_recent = team_b.get("recent_stats", {})

    # Calculate strength comparison
    rating_diff = a_rating - b_rating
    winrate_diff = a_recent.get("winrate", 50) - b_recent.get("winrate", 50)

    # Predicted advantage
    if rating_diff > 100:
        predicted_winner = team_a_name
        confidence = min(85, 60 + (rating_diff - 100) / 10)
    elif rating_diff < -100:
        predicted_winner = team_b_name
        confidence = min(85, 60 + (abs(rating_diff) - 100) / 10)
    else:
        # Close match - use winrate
        if winrate_diff > 10:
            predicted_winner = team_a_name
            confidence = 55 + winrate_diff / 4
        elif winrate_diff < -10:
            predicted_winner = team_b_name
            confidence = 55 + abs(winrate_diff) / 4
        else:
            predicted_winner = team_a_name if rating_diff >= 0 else team_b_name
            confidence = 50 + abs(rating_diff) / 20

    return {
        "team_a": {
            "name": team_a_name,
            "rating": a_rating,
            "recent_winrate": a_recent.get("winrate", 0),
            "avg_duration": a_recent.get("avg_duration_min", 0),
            "form": calculate_team_form(team_a),
        },
        "team_b": {
            "name": team_b_name,
            "rating": b_rating,
            "recent_winrate": b_recent.get("winrate", 0),
            "avg_duration": b_recent.get("avg_duration_min", 0),
            "form": calculate_team_form(team_b),
        },
        "comparison": {
            "rating_advantage": team_a_name if rating_diff > 0 else team_b_name,
            "rating_diff": abs(rating_diff),
            "winrate_advantage": team_a_name if winrate_diff > 0 else team_b_name,
            "winrate_diff": abs(winrate_diff),
        },
        "prediction": {
            "winner": predicted_winner,
            "confidence": round(confidence, 1),
        },
        "hero_pools": compare_hero_pools(team_a, team_b),
    }


# =============================================================================
# PLAYER ANALYTICS
# =============================================================================


def get_player_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get player data by name."""
    players = load_pro_players()
    name_lower = name.lower()
    for player in players:
        if player.get("name", "").lower() == name_lower:
            return player
    return None


def get_team_roster_analysis(team_name: str) -> Dict[str, Any]:
    """Analyze a team's roster performance."""
    team = get_team_by_name(team_name)
    if not team:
        return {"error": "Team not found"}

    roster = team.get("current_roster", [])

    roster_analysis = []
    total_winrate = 0
    total_games = 0

    for player in roster:
        games = player.get("games_played", 0)
        winrate = player.get("winrate", 0)

        roster_analysis.append(
            {
                "name": player.get("name", "Unknown"),
                "account_id": player.get("account_id"),
                "games_played": games,
                "wins": player.get("wins", 0),
                "winrate": winrate,
                "performance_tier": "⭐" if winrate >= 60 else "✅" if winrate >= 55 else "😐",
            }
        )

        total_winrate += winrate * games
        total_games += games

    # Sort by winrate
    roster_analysis.sort(key=lambda x: x["winrate"], reverse=True)

    return {
        "team_name": team_name,
        "roster": roster_analysis,
        "roster_size": len(roster),
        "avg_winrate": round(total_winrate / total_games, 1) if total_games > 0 else 0,
        "star_player": roster_analysis[0]["name"] if roster_analysis else None,
    }


# =============================================================================
# MATCH PREVIEW GENERATOR
# =============================================================================


def generate_match_preview(team_a_name: str, team_b_name: str, match_format: str = "Bo3") -> Dict[str, Any]:
    """Generate comprehensive match preview for betting analysis."""
    from hero_mapper import get_hero_name

    h2h = calculate_h2h(team_a_name, team_b_name)

    if "error" in h2h:
        return h2h

    team_a = get_team_by_name(team_a_name)
    team_b = get_team_by_name(team_b_name)

    # Key factors
    key_factors = []

    # Rating advantage
    rating_diff = h2h["comparison"]["rating_diff"]
    if rating_diff > 150:
        key_factors.append(
            f"🏆 {h2h['comparison']['rating_advantage']} has significant rating advantage (+{rating_diff:.0f})"
        )
    elif rating_diff > 50:
        key_factors.append(f"📊 {h2h['comparison']['rating_advantage']} has rating advantage (+{rating_diff:.0f})")

    # Form advantage
    form_a = h2h["team_a"]["form"]["form_tier"]
    form_b = h2h["team_b"]["form"]["form_tier"]
    if "Hot" in form_a and "Hot" not in form_b:
        key_factors.append(f"🔥 {team_a_name} is in hot form ({h2h['team_a']['recent_winrate']}% WR)")
    elif "Hot" in form_b and "Hot" not in form_a:
        key_factors.append(f"🔥 {team_b_name} is in hot form ({h2h['team_b']['recent_winrate']}% WR)")

    # Hero pool overlap
    overlap = h2h["hero_pools"]["total_overlap"]
    if overlap >= 3:
        key_factors.append(f"⚔️ High hero pool overlap ({overlap} contested heroes)")

    # Game duration tendency
    dur_a = h2h["team_a"]["avg_duration"]
    dur_b = h2h["team_b"]["avg_duration"]
    if abs(dur_a - dur_b) > 3:
        faster = team_a_name if dur_a < dur_b else team_b_name
        key_factors.append(f"⏱️ {faster} plays faster games (~{min(dur_a, dur_b):.0f} min avg)")

    # Contested heroes detail
    contested_detail = []
    for ch in h2h["hero_pools"]["contested_heroes"][:3]:
        contested_detail.append(
            {
                "hero": ch["hero_name"],
                "advantage": team_a_name if ch["advantage"] == "A" else team_b_name,
                "winrate_diff": abs(ch["team_a_winrate"] - ch["team_b_winrate"]),
            }
        )

    # Betting recommendation
    confidence = h2h["prediction"]["confidence"]
    if confidence >= 70:
        bet_recommendation = f"Strong lean towards {h2h['prediction']['winner']}"
    elif confidence >= 60:
        bet_recommendation = f"Moderate lean towards {h2h['prediction']['winner']}"
    elif confidence >= 55:
        bet_recommendation = f"Slight edge to {h2h['prediction']['winner']}"
    else:
        bet_recommendation = "Coin flip - consider underdog value"

    return {
        "match": {
            "team_a": team_a_name,
            "team_b": team_b_name,
            "format": match_format,
        },
        "prediction": h2h["prediction"],
        "key_factors": key_factors,
        "team_comparison": {
            "team_a": {
                "name": team_a_name,
                "rating": h2h["team_a"]["rating"],
                "form": h2h["team_a"]["form"],
                "top_heroes": [get_hero_name(h.get("hero_id")) for h in team_a.get("top_heroes", [])[:3]],
            },
            "team_b": {
                "name": team_b_name,
                "rating": h2h["team_b"]["rating"],
                "form": h2h["team_b"]["form"],
                "top_heroes": [get_hero_name(h.get("hero_id")) for h in team_b.get("top_heroes", [])[:3]],
            },
        },
        "contested_heroes": contested_detail,
        "betting_analysis": {
            "recommendation": bet_recommendation,
            "confidence": confidence,
            "predicted_winner": h2h["prediction"]["winner"],
        },
        "generated_at": datetime.now().isoformat(),
    }


# =============================================================================
# HERO META ANALYTICS
# =============================================================================


def get_meta_tier_list() -> Dict[str, List[Dict[str, Any]]]:
    """Get current hero meta tier list."""
    heroes = load_heroes_meta()

    tiers = {"S": [], "A": [], "B": [], "C": []}

    for hero in heroes:
        tier = hero.get("tier", "C")
        tiers[tier].append(
            {
                "hero_id": hero.get("hero_id"),
                "hero_name": hero.get("hero_name"),
                "picks": hero.get("stats", {}).get("picks", 0),
                "bans": hero.get("stats", {}).get("bans", 0),
                "winrate": hero.get("stats", {}).get("winrate", 0),
                "presence_rate": hero.get("stats", {}).get("presence_rate", 0),
            }
        )

    # Sort each tier by presence
    for tier in tiers:
        tiers[tier].sort(key=lambda x: x["presence_rate"], reverse=True)

    return tiers


def get_hero_recommendation(team_name: str) -> List[Dict[str, Any]]:
    """Recommend heroes for a team based on their pool and meta."""
    team = get_team_by_name(team_name)
    if not team:
        return []

    meta_heroes = {h.get("hero_id"): h for h in load_heroes_meta()}
    team_heroes = {h.get("hero_id"): h for h in team.get("top_heroes", [])}

    recommendations = []

    # Find high-meta heroes the team plays well
    for hero_id, team_hero in team_heroes.items():
        meta = meta_heroes.get(hero_id, {})

        team_wr = team_hero.get("winrate", 0)
        meta_tier = meta.get("tier", "C")
        meta_presence = meta.get("stats", {}).get("presence_rate", 0)

        # High-value picks: team has good WR + hero is meta
        if team_wr >= 55 and meta_tier in ["S", "A"]:
            recommendations.append(
                {
                    "hero_id": hero_id,
                    "hero_name": meta.get("hero_name", f"Hero {hero_id}"),
                    "team_winrate": team_wr,
                    "meta_tier": meta_tier,
                    "meta_presence": meta_presence,
                    "recommendation": "🌟 Priority Pick" if team_wr >= 60 else "✅ Strong Pick",
                }
            )

    recommendations.sort(key=lambda x: x["team_winrate"], reverse=True)
    return recommendations[:5]


# =============================================================================
# DREAMLEAGUE ANALYTICS
# =============================================================================


def get_dreamleague_teams_analysis() -> List[Dict[str, Any]]:
    """Analyze all DreamLeague S27 teams."""
    dl = load_dreamleague()
    pro_teams = load_pro_teams()

    # Create lookup
    pro_map = {t.get("team_id"): t for t in pro_teams}

    teams_analysis = []

    for team in dl.get("teams", []):
        team_id = team.get("team_id")
        pro_data = pro_map.get(team_id, {})

        if pro_data:
            form = calculate_team_form(pro_data)
            teams_analysis.append(
                {
                    "name": team.get("name"),
                    "tier": team.get("tier", "C"),
                    "region": team.get("region"),
                    "rating": pro_data.get("rating", 0),
                    "recent_winrate": pro_data.get("recent_stats", {}).get("winrate", 0),
                    "form": form,
                    "top_heroes": [h.get("hero_id") for h in pro_data.get("top_heroes", [])[:3]],
                }
            )
        else:
            teams_analysis.append(
                {
                    "name": team.get("name"),
                    "tier": team.get("tier", "C"),
                    "region": team.get("region"),
                    "rating": 0,
                    "recent_winrate": 0,
                    "form": {"form_tier": "❓ Unknown"},
                }
            )

    # Sort by rating
    teams_analysis.sort(key=lambda x: x["rating"], reverse=True)

    return teams_analysis


def get_dreamleague_schedule() -> List[Dict[str, Any]]:
    """Get DreamLeague S27 schedule with team analysis."""
    dl = load_dreamleague()
    schedule = dl.get("schedule", {})

    matches = []

    for round_key, round_data in schedule.items():
        for match in round_data.get("matches", []):
            team_a = match.get("team_a")
            team_b = match.get("team_b")

            # Quick H2H preview
            h2h = calculate_h2h(team_a, team_b)

            matches.append(
                {
                    "round": round_key,
                    "date": round_data.get("date"),
                    "time_brt": match.get("time_brt"),
                    "time_cet": match.get("time_cet"),
                    "team_a": team_a,
                    "team_b": team_b,
                    "format": match.get("format", "Bo3"),
                    "status": match.get("status", "scheduled"),
                    "prediction": h2h.get("prediction", {}) if "error" not in h2h else None,
                    "stream": match.get("stream"),
                }
            )

    return matches


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("📊 Testing Analytics Engine...")

    # Test team lookup
    print("\n--- Team Analysis ---")
    falcons = get_team_by_name("Team Falcons")
    if falcons:
        form = calculate_team_form(falcons)
        print(f"Team Falcons: {form['form_tier']} ({form['form_score']})")

    # Test H2H
    print("\n--- H2H Analysis ---")
    h2h = calculate_h2h("Team Falcons", "Team Spirit")
    print(f"Prediction: {h2h['prediction']['winner']} ({h2h['prediction']['confidence']}% confidence)")

    # Test match preview
    print("\n--- Match Preview ---")
    preview = generate_match_preview("Team Liquid", "OG", "Bo3")
    print(f"Key factors: {len(preview.get('key_factors', []))}")
    for factor in preview.get("key_factors", []):
        print(f"  - {factor}")

    # Test meta tier list
    print("\n--- Meta Tiers ---")
    tiers = get_meta_tier_list()
    print(f"S-tier: {len(tiers['S'])} heroes")
    print(f"A-tier: {len(tiers['A'])} heroes")

    # Test DreamLeague analysis
    print("\n--- DreamLeague Teams ---")
    teams = get_dreamleague_teams_analysis()
    print(f"Analyzed {len(teams)} teams")
    for team in teams[:5]:
        print(f"  {team['name']}: {team['rating']:.0f} rating, {team['form']['form_tier']}")

    print("\n✅ Analytics Engine test complete!")
