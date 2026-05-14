"""
Prometheus V7 - Batch Migration Script for 2025 Match Data
Migrates JSON data from Database/2025 to Supabase PostgreSQL

Usage:
    python scripts/migrate_2025_data.py [--month YYYYMM] [--batch-size 1000]

Expected data volumes:
    - 25,672 matches
    - 283,120 player records
    - 604,599 picks/bans
    - 529,806 objectives
    - 210,446 teamfights
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

try:
    from supabase import Client, create_client
except ImportError:
    print("❌ Install supabase: pip install supabase")
    sys.exit(1)

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).parent.parent
DATA_2025_PATH = BASE_DIR / "Database" / "2025"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Months to process
MONTHS = [
    "202501",
    "202502",
    "202503",
    "202504",
    "202505",
    "202506",
    "202507",
    "202508",
    "202509",
    "202510",
    "202511",
    "202512",
]

# Batch sizes for different tables
BATCH_SIZES = {
    "matches": 500,
    "players": 1000,
    "picks_bans": 2000,
    "objectives": 2000,
    "teamfights": 1000,
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def load_json(filepath: Path) -> dict:
    """Load JSON file safely."""
    try:
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"  ⚠️ Error loading {filepath.name}: {e}")
    return {}


def get_supabase_client() -> Optional[Client]:
    """Create Supabase client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing SUPABASE_URL or SUPABASE_KEY")
        return None

    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return client
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return None


def batch_insert(client: Client, table: str, records: List[Dict], batch_size: int = 1000) -> int:
    """Insert records in batches."""
    total = 0
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        try:
            client.table(table).upsert(batch).execute()
            total += len(batch)
        except Exception as e:
            print(f"    ❌ Batch error at {i}: {e}")
    return total


def safe_int(value) -> Optional[int]:
    """Safely convert to int."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def safe_float(value) -> Optional[float]:
    """Safely convert to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


# =============================================================================
# MIGRATION FUNCTIONS
# =============================================================================


def migrate_matches(client: Client, month: str) -> int:
    """Migrate matches from main_metadata.json."""
    print(f"  📦 Migrating matches...")

    filepath = DATA_2025_PATH / month / "main_metadata.json"
    data = load_json(filepath)

    if not data or "by_match" not in data:
        print(f"    ⚠️ No match data found")
        return 0

    # Also load teams data for team names
    teams_filepath = DATA_2025_PATH / month / "teams.json"
    teams_data = load_json(teams_filepath)
    teams_by_match = teams_data.get("by_match", {}) if teams_data else {}

    records = []
    for match_id, match_list in data["by_match"].items():
        if not match_list:
            continue

        m = match_list[0]  # Get first (usually only) record

        # Get team names
        team_info = teams_by_match.get(match_id, [{}])[0] if teams_by_match else {}

        record = {
            "match_id": safe_int(match_id),
            "leagueid": safe_int(m.get("leagueid")),
            "start_date_time": m.get("start_date_time"),
            "duration": safe_int(m.get("duration")),
            "cluster": safe_int(m.get("cluster")),
            "radiant_win": m.get("radiant_win"),
            "radiant_score": safe_int(m.get("radiant_score")),
            "dire_score": safe_int(m.get("dire_score")),
            "radiant_team_id": safe_int(m.get("radiant_team_id")),
            "dire_team_id": safe_int(m.get("dire_team_id")),
            "radiant_team_name": team_info.get("radiant.name"),
            "dire_team_name": team_info.get("dire.name"),
            "game_mode": safe_int(m.get("game_mode")),
            "lobby_type": safe_int(m.get("lobby_type")),
            "patch": safe_int(m.get("patch")),
            "region": safe_int(m.get("region")),
            "tower_status_radiant": safe_int(m.get("tower_status_radiant")),
            "tower_status_dire": safe_int(m.get("tower_status_dire")),
            "barracks_status_radiant": safe_int(m.get("barracks_status_radiant")),
            "barracks_status_dire": safe_int(m.get("barracks_status_dire")),
            "first_blood_time": safe_int(m.get("first_blood_time")),
            "series_id": safe_int(m.get("series_id")),
            "series_type": safe_int(m.get("series_type")),
            "stomp": safe_float(m.get("stomp")),
            "comeback": safe_float(m.get("comeback")),
            "replay_url": m.get("replay_url"),
            "replay_salt": safe_int(m.get("replay_salt")),
            "month": month,
        }
        records.append(record)

    if records:
        count = batch_insert(client, "matches_2025", records, BATCH_SIZES["matches"])
        print(f"    ✅ {count} matches migrated")
        return count
    return 0


def migrate_picks_bans(client: Client, month: str) -> int:
    """Migrate picks and bans."""
    print(f"  📦 Migrating picks/bans...")

    filepath = DATA_2025_PATH / month / "picks_bans.json"
    data = load_json(filepath)

    if not data or "by_match" not in data:
        print(f"    ⚠️ No picks/bans data found")
        return 0

    records = []
    for match_id, pb_list in data["by_match"].items():
        for pb in pb_list:
            record = {
                "match_id": safe_int(match_id),
                "leagueid": safe_int(pb.get("leagueid")),
                "is_pick": pb.get("is_pick"),
                "hero_id": safe_int(pb.get("hero_id")),
                "team": safe_int(pb.get("team")),
                "order": safe_int(pb.get("order")),
                "month": month,
            }
            records.append(record)

    if records:
        count = batch_insert(client, "picks_bans_2025", records, BATCH_SIZES["picks_bans"])
        print(f"    ✅ {count} picks/bans migrated")
        return count
    return 0


def migrate_objectives(client: Client, month: str) -> int:
    """Migrate objectives (towers, rosh, etc)."""
    print(f"  📦 Migrating objectives...")

    filepath = DATA_2025_PATH / month / "objectives.json"
    data = load_json(filepath)

    if not data or "by_match" not in data:
        print(f"    ⚠️ No objectives data found")
        return 0

    records = []
    for match_id, obj_list in data["by_match"].items():
        for obj in obj_list:
            record = {
                "match_id": safe_int(match_id),
                "leagueid": safe_int(obj.get("leagueid")),
                "time": safe_int(obj.get("time")),
                "type": obj.get("type"),
                "team": safe_int(obj.get("team")),
                "slot": safe_int(obj.get("slot")),
                "player_slot": safe_int(obj.get("player_slot")),
                "key": obj.get("key"),
                "unit": obj.get("unit"),
                "value": safe_float(obj.get("value")),
                "killer": safe_int(obj.get("killer")),
                "month": month,
            }
            records.append(record)

    if records:
        count = batch_insert(client, "objectives_2025", records, BATCH_SIZES["objectives"])
        print(f"    ✅ {count} objectives migrated")
        return count
    return 0


def migrate_teamfights(client: Client, month: str) -> int:
    """Migrate teamfights."""
    print(f"  📦 Migrating teamfights...")

    filepath = DATA_2025_PATH / month / "teamfights.json"
    data = load_json(filepath)

    if not data or "by_match" not in data:
        print(f"    ⚠️ No teamfights data found")
        return 0

    records = []
    for match_id, tf_list in data["by_match"].items():
        for tf in tf_list:
            record = {
                "match_id": safe_int(match_id),
                "leagueid": safe_int(tf.get("leagueid")),
                "start_time": safe_int(tf.get("start")),
                "end_time": safe_int(tf.get("end")),
                "last_death": safe_int(tf.get("last_death")),
                "deaths": safe_int(tf.get("deaths")),
                "month": month,
            }
            records.append(record)

    if records:
        count = batch_insert(client, "teamfights_2025", records, BATCH_SIZES["teamfights"])
        print(f"    ✅ {count} teamfights migrated")
        return count
    return 0


def migrate_month(client: Client, month: str) -> Dict[str, int]:
    """Migrate all data for a specific month."""
    print(f"\n{'='*60}")
    print(f"📅 MIGRATING MONTH: {month}")
    print(f"{'='*60}")

    month_path = DATA_2025_PATH / month
    if not month_path.exists():
        print(f"  ⚠️ Month directory not found: {month_path}")
        return {}

    totals = {
        "matches": migrate_matches(client, month),
        "picks_bans": migrate_picks_bans(client, month),
        "objectives": migrate_objectives(client, month),
        "teamfights": migrate_teamfights(client, month),
    }

    print(f"\n  📊 Month {month} Summary:")
    for table, count in totals.items():
        print(f"     • {table}: {count:,}")

    return totals


def verify_migration(client: Client):
    """Verify migration results."""
    print(f"\n{'='*60}")
    print("📊 MIGRATION VERIFICATION")
    print(f"{'='*60}")

    tables = [
        ("matches_2025", "Matches"),
        ("picks_bans_2025", "Picks/Bans"),
        ("objectives_2025", "Objectives"),
        ("teamfights_2025", "Teamfights"),
    ]

    for table, name in tables:
        try:
            result = client.table(table).select("*", count="exact").limit(1).execute()
            count = len(result.data) if hasattr(result, "count") else "?"
            # Get actual count
            count_result = client.table(table).select("count", count="exact").execute()
            print(f"  {name}: {count_result.count:,} records")
        except Exception as e:
            print(f"  {name}: ❌ Error - {e}")


# =============================================================================
# MAIN
# =============================================================================


def main():
    parser = argparse.ArgumentParser(description="Migrate 2025 match data to Supabase")
    parser.add_argument("--month", type=str, help="Specific month to migrate (YYYYMM)")
    parser.add_argument("--all", action="store_true", help="Migrate all months")
    parser.add_argument("--verify", action="store_true", help="Only verify current data")
    args = parser.parse_args()

    print("=" * 60)
    print("🔥 PROMETHEUS V7 - 2025 DATA MIGRATION")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Data path: {DATA_2025_PATH}")

    # Connect to Supabase
    client = get_supabase_client()
    if not client:
        return

    print("✅ Connected to Supabase")

    if args.verify:
        verify_migration(client)
        return

    # Determine months to process
    if args.month:
        months_to_process = [args.month]
    elif args.all:
        months_to_process = MONTHS
    else:
        # Default: process latest month with data
        months_to_process = ["202512"]

    # Process months
    grand_totals = {
        "matches": 0,
        "picks_bans": 0,
        "objectives": 0,
        "teamfights": 0,
    }

    for month in months_to_process:
        totals = migrate_month(client, month)
        for key, value in totals.items():
            grand_totals[key] += value

    # Final summary
    print(f"\n{'='*60}")
    print("✅ MIGRATION COMPLETE")
    print(f"{'='*60}")
    print("📊 Grand Totals:")
    for table, count in grand_totals.items():
        print(f"   • {table}: {count:,}")

    # Verify
    verify_migration(client)


if __name__ == "__main__":
    main()
