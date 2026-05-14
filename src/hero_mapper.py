"""
Prometheus V7 - Hero Mapper
Maps hero_id to hero name, image, and metadata.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

# =============================================================================
# HERO DATABASE
# Complete Dota 2 hero mapping (as of December 2025)
# =============================================================================

HERO_DATA = {
    1: {
        "name": "Anti-Mage",
        "localized_name": "Anti-Mage",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Escape", "Nuker"],
    },
    2: {
        "name": "Axe",
        "localized_name": "Axe",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Initiator", "Durable", "Disabler"],
    },
    3: {
        "name": "Bane",
        "localized_name": "Bane",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Disabler", "Nuker"],
    },
    4: {
        "name": "Bloodseeker",
        "localized_name": "Bloodseeker",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Disabler", "Initiator"],
    },
    5: {
        "name": "Crystal Maiden",
        "localized_name": "Crystal Maiden",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Disabler", "Nuker"],
    },
    6: {
        "name": "Drow Ranger",
        "localized_name": "Drow Ranger",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Carry", "Disabler", "Pusher"],
    },
    7: {
        "name": "Earthshaker",
        "localized_name": "Earthshaker",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Support", "Initiator", "Disabler"],
    },
    8: {
        "name": "Juggernaut",
        "localized_name": "Juggernaut",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Pusher", "Escape"],
    },
    9: {
        "name": "Mirana",
        "localized_name": "Mirana",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Carry", "Support", "Escape"],
    },
    10: {
        "name": "Morphling",
        "localized_name": "Morphling",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Carry", "Escape", "Durable"],
    },
    11: {
        "name": "Shadow Fiend",
        "localized_name": "Shadow Fiend",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Carry", "Nuker"],
    },
    12: {
        "name": "Phantom Lancer",
        "localized_name": "Phantom Lancer",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Escape", "Pusher"],
    },
    13: {
        "name": "Puck",
        "localized_name": "Puck",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Initiator", "Disabler", "Escape"],
    },
    14: {
        "name": "Pudge",
        "localized_name": "Pudge",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Disabler", "Initiator", "Durable"],
    },
    15: {
        "name": "Razor",
        "localized_name": "Razor",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Carry", "Durable", "Nuker"],
    },
    16: {
        "name": "Sand King",
        "localized_name": "Sand King",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Initiator", "Disabler", "Nuker"],
    },
    17: {
        "name": "Storm Spirit",
        "localized_name": "Storm Spirit",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Carry", "Escape", "Nuker"],
    },
    18: {
        "name": "Sven",
        "localized_name": "Sven",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Disabler", "Initiator"],
    },
    19: {
        "name": "Tiny",
        "localized_name": "Tiny",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Nuker", "Pusher"],
    },
    20: {
        "name": "Vengeful Spirit",
        "localized_name": "Vengeful Spirit",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Support", "Initiator", "Disabler"],
    },
    21: {
        "name": "Windranger",
        "localized_name": "Windranger",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Carry", "Support", "Disabler"],
    },
    22: {"name": "Zeus", "localized_name": "Zeus", "primary_attr": "int", "attack_type": "Ranged", "roles": ["Nuker"]},
    23: {
        "name": "Kunkka",
        "localized_name": "Kunkka",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Disabler", "Initiator"],
    },
    25: {
        "name": "Lina",
        "localized_name": "Lina",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Carry", "Support", "Nuker"],
    },
    26: {
        "name": "Lion",
        "localized_name": "Lion",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Disabler", "Nuker"],
    },
    27: {
        "name": "Shadow Shaman",
        "localized_name": "Shadow Shaman",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Pusher", "Disabler"],
    },
    28: {
        "name": "Slardar",
        "localized_name": "Slardar",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Initiator", "Disabler"],
    },
    29: {
        "name": "Tidehunter",
        "localized_name": "Tidehunter",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Initiator", "Durable", "Disabler"],
    },
    30: {
        "name": "Witch Doctor",
        "localized_name": "Witch Doctor",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Nuker", "Disabler"],
    },
    31: {
        "name": "Lich",
        "localized_name": "Lich",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Nuker"],
    },
    32: {
        "name": "Riki",
        "localized_name": "Riki",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Escape", "Disabler"],
    },
    33: {
        "name": "Enigma",
        "localized_name": "Enigma",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Initiator", "Disabler", "Pusher"],
    },
    34: {
        "name": "Tinker",
        "localized_name": "Tinker",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Nuker", "Pusher"],
    },
    35: {
        "name": "Sniper",
        "localized_name": "Sniper",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Carry", "Nuker"],
    },
    36: {
        "name": "Necrophos",
        "localized_name": "Necrophos",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Carry", "Nuker", "Durable"],
    },
    37: {
        "name": "Warlock",
        "localized_name": "Warlock",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Initiator", "Disabler"],
    },
    38: {
        "name": "Beastmaster",
        "localized_name": "Beastmaster",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Initiator", "Disabler", "Durable"],
    },
    39: {
        "name": "Queen of Pain",
        "localized_name": "Queen of Pain",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Carry", "Nuker", "Escape"],
    },
    40: {
        "name": "Venomancer",
        "localized_name": "Venomancer",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Support", "Nuker", "Pusher"],
    },
    41: {
        "name": "Faceless Void",
        "localized_name": "Faceless Void",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Initiator", "Disabler"],
    },
    42: {
        "name": "Wraith King",
        "localized_name": "Wraith King",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Durable", "Initiator"],
    },
    43: {
        "name": "Death Prophet",
        "localized_name": "Death Prophet",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Carry", "Pusher", "Nuker"],
    },
    44: {
        "name": "Phantom Assassin",
        "localized_name": "Phantom Assassin",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Escape"],
    },
    45: {
        "name": "Pugna",
        "localized_name": "Pugna",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Nuker", "Pusher"],
    },
    46: {
        "name": "Templar Assassin",
        "localized_name": "Templar Assassin",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Carry", "Escape"],
    },
    47: {
        "name": "Viper",
        "localized_name": "Viper",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Carry", "Durable", "Initiator"],
    },
    48: {
        "name": "Luna",
        "localized_name": "Luna",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Carry", "Nuker", "Pusher"],
    },
    49: {
        "name": "Dragon Knight",
        "localized_name": "Dragon Knight",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Pusher", "Durable"],
    },
    50: {
        "name": "Dazzle",
        "localized_name": "Dazzle",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Nuker", "Disabler"],
    },
    51: {
        "name": "Clockwerk",
        "localized_name": "Clockwerk",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Initiator", "Durable", "Disabler"],
    },
    52: {
        "name": "Leshrac",
        "localized_name": "Leshrac",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Carry", "Nuker", "Pusher"],
    },
    53: {
        "name": "Nature's Prophet",
        "localized_name": "Nature's Prophet",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Carry", "Pusher", "Escape"],
    },
    54: {
        "name": "Lifestealer",
        "localized_name": "Lifestealer",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Durable", "Escape"],
    },
    55: {
        "name": "Dark Seer",
        "localized_name": "Dark Seer",
        "primary_attr": "int",
        "attack_type": "Melee",
        "roles": ["Initiator", "Escape"],
    },
    56: {
        "name": "Clinkz",
        "localized_name": "Clinkz",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Carry", "Escape", "Pusher"],
    },
    57: {
        "name": "Omniknight",
        "localized_name": "Omniknight",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Support", "Durable", "Nuker"],
    },
    58: {
        "name": "Enchantress",
        "localized_name": "Enchantress",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Pusher", "Durable"],
    },
    59: {
        "name": "Huskar",
        "localized_name": "Huskar",
        "primary_attr": "str",
        "attack_type": "Ranged",
        "roles": ["Carry", "Initiator", "Durable"],
    },
    60: {
        "name": "Night Stalker",
        "localized_name": "Night Stalker",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Initiator", "Durable"],
    },
    61: {
        "name": "Broodmother",
        "localized_name": "Broodmother",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Pusher", "Escape"],
    },
    62: {
        "name": "Bounty Hunter",
        "localized_name": "Bounty Hunter",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Escape", "Nuker"],
    },
    63: {
        "name": "Weaver",
        "localized_name": "Weaver",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Carry", "Escape"],
    },
    64: {
        "name": "Jakiro",
        "localized_name": "Jakiro",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Nuker", "Pusher"],
    },
    65: {
        "name": "Batrider",
        "localized_name": "Batrider",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Initiator", "Disabler", "Escape"],
    },
    66: {
        "name": "Chen",
        "localized_name": "Chen",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Pusher"],
    },
    67: {
        "name": "Spectre",
        "localized_name": "Spectre",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Durable", "Escape"],
    },
    68: {
        "name": "Ancient Apparition",
        "localized_name": "Ancient Apparition",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Disabler"],
    },
    69: {
        "name": "Doom",
        "localized_name": "Doom",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Initiator", "Durable"],
    },
    70: {
        "name": "Ursa",
        "localized_name": "Ursa",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Durable"],
    },
    71: {
        "name": "Spirit Breaker",
        "localized_name": "Spirit Breaker",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Initiator", "Disabler"],
    },
    72: {
        "name": "Gyrocopter",
        "localized_name": "Gyrocopter",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Carry", "Nuker", "Disabler"],
    },
    73: {
        "name": "Alchemist",
        "localized_name": "Alchemist",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Durable", "Disabler"],
    },
    74: {
        "name": "Invoker",
        "localized_name": "Invoker",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Carry", "Nuker", "Disabler"],
    },
    75: {
        "name": "Silencer",
        "localized_name": "Silencer",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Carry", "Support", "Disabler"],
    },
    76: {
        "name": "Outworld Destroyer",
        "localized_name": "Outworld Destroyer",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Carry", "Nuker", "Disabler"],
    },
    77: {
        "name": "Lycan",
        "localized_name": "Lycan",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Pusher", "Durable"],
    },
    78: {
        "name": "Brewmaster",
        "localized_name": "Brewmaster",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Initiator", "Disabler"],
    },
    79: {
        "name": "Shadow Demon",
        "localized_name": "Shadow Demon",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Disabler", "Initiator"],
    },
    80: {
        "name": "Lone Druid",
        "localized_name": "Lone Druid",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Carry", "Pusher", "Durable"],
    },
    81: {
        "name": "Chaos Knight",
        "localized_name": "Chaos Knight",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Disabler", "Durable"],
    },
    82: {
        "name": "Meepo",
        "localized_name": "Meepo",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Escape", "Nuker"],
    },
    83: {
        "name": "Treant Protector",
        "localized_name": "Treant Protector",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Support", "Initiator", "Durable"],
    },
    84: {
        "name": "Ogre Magi",
        "localized_name": "Ogre Magi",
        "primary_attr": "int",
        "attack_type": "Melee",
        "roles": ["Support", "Nuker", "Durable"],
    },
    85: {
        "name": "Undying",
        "localized_name": "Undying",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Support", "Durable", "Disabler"],
    },
    86: {
        "name": "Rubick",
        "localized_name": "Rubick",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Disabler", "Nuker"],
    },
    87: {
        "name": "Disruptor",
        "localized_name": "Disruptor",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Disabler", "Initiator"],
    },
    88: {
        "name": "Nyx Assassin",
        "localized_name": "Nyx Assassin",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Initiator", "Disabler", "Nuker"],
    },
    89: {
        "name": "Naga Siren",
        "localized_name": "Naga Siren",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Support", "Pusher"],
    },
    90: {
        "name": "Keeper of the Light",
        "localized_name": "Keeper of the Light",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Nuker"],
    },
    91: {
        "name": "Io",
        "localized_name": "Io",
        "primary_attr": "str",
        "attack_type": "Ranged",
        "roles": ["Support", "Escape", "Nuker"],
    },
    92: {
        "name": "Visage",
        "localized_name": "Visage",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Nuker", "Durable"],
    },
    93: {
        "name": "Slark",
        "localized_name": "Slark",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Escape", "Disabler"],
    },
    94: {
        "name": "Medusa",
        "localized_name": "Medusa",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Carry", "Disabler", "Durable"],
    },
    95: {
        "name": "Troll Warlord",
        "localized_name": "Troll Warlord",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Carry", "Pusher", "Disabler"],
    },
    96: {
        "name": "Centaur Warrunner",
        "localized_name": "Centaur Warrunner",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Initiator", "Durable", "Disabler"],
    },
    97: {
        "name": "Magnus",
        "localized_name": "Magnus",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Initiator", "Disabler", "Escape"],
    },
    98: {
        "name": "Timbersaw",
        "localized_name": "Timbersaw",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Nuker", "Durable", "Escape"],
    },
    99: {
        "name": "Bristleback",
        "localized_name": "Bristleback",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Durable", "Initiator"],
    },
    100: {
        "name": "Tusk",
        "localized_name": "Tusk",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Initiator", "Disabler", "Nuker"],
    },
    101: {
        "name": "Skywrath Mage",
        "localized_name": "Skywrath Mage",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Nuker", "Disabler"],
    },
    102: {
        "name": "Abaddon",
        "localized_name": "Abaddon",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Support", "Carry", "Durable"],
    },
    103: {
        "name": "Elder Titan",
        "localized_name": "Elder Titan",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Initiator", "Disabler", "Nuker"],
    },
    104: {
        "name": "Legion Commander",
        "localized_name": "Legion Commander",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Disabler", "Durable"],
    },
    105: {
        "name": "Techies",
        "localized_name": "Techies",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Nuker", "Disabler"],
    },
    106: {
        "name": "Ember Spirit",
        "localized_name": "Ember Spirit",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Escape", "Nuker"],
    },
    107: {
        "name": "Earth Spirit",
        "localized_name": "Earth Spirit",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Initiator", "Disabler", "Escape"],
    },
    108: {
        "name": "Underlord",
        "localized_name": "Underlord",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Durable", "Nuker", "Disabler"],
    },
    109: {
        "name": "Terrorblade",
        "localized_name": "Terrorblade",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Pusher", "Nuker"],
    },
    110: {
        "name": "Phoenix",
        "localized_name": "Phoenix",
        "primary_attr": "str",
        "attack_type": "Ranged",
        "roles": ["Support", "Nuker", "Initiator"],
    },
    111: {
        "name": "Oracle",
        "localized_name": "Oracle",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Nuker", "Escape"],
    },
    112: {
        "name": "Winter Wyvern",
        "localized_name": "Winter Wyvern",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Disabler", "Nuker"],
    },
    113: {
        "name": "Arc Warden",
        "localized_name": "Arc Warden",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Carry", "Escape", "Nuker"],
    },
    114: {
        "name": "Monkey King",
        "localized_name": "Monkey King",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Escape", "Disabler"],
    },
    119: {
        "name": "Dark Willow",
        "localized_name": "Dark Willow",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Nuker", "Disabler"],
    },
    120: {
        "name": "Pangolier",
        "localized_name": "Pangolier",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Initiator", "Disabler"],
    },
    121: {
        "name": "Grimstroke",
        "localized_name": "Grimstroke",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Nuker", "Disabler"],
    },
    123: {
        "name": "Hoodwink",
        "localized_name": "Hoodwink",
        "primary_attr": "agi",
        "attack_type": "Ranged",
        "roles": ["Nuker", "Escape", "Disabler"],
    },
    126: {
        "name": "Void Spirit",
        "localized_name": "Void Spirit",
        "primary_attr": "int",
        "attack_type": "Melee",
        "roles": ["Carry", "Escape", "Nuker"],
    },
    128: {
        "name": "Snapfire",
        "localized_name": "Snapfire",
        "primary_attr": "str",
        "attack_type": "Ranged",
        "roles": ["Support", "Nuker", "Disabler"],
    },
    129: {
        "name": "Mars",
        "localized_name": "Mars",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Initiator", "Disabler"],
    },
    131: {
        "name": "Ringmaster",
        "localized_name": "Ringmaster",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Support", "Disabler", "Nuker"],
    },
    135: {
        "name": "Dawnbreaker",
        "localized_name": "Dawnbreaker",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Durable", "Nuker"],
    },
    136: {
        "name": "Marci",
        "localized_name": "Marci",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Carry", "Support", "Disabler"],
    },
    137: {
        "name": "Primal Beast",
        "localized_name": "Primal Beast",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Initiator", "Durable", "Disabler"],
    },
    138: {
        "name": "Muerta",
        "localized_name": "Muerta",
        "primary_attr": "int",
        "attack_type": "Ranged",
        "roles": ["Carry", "Nuker", "Disabler"],
    },
}

# =============================================================================
# HERO IMAGE URLS
# =============================================================================

HERO_IMAGE_BASE = "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes"


def get_hero_image_url(hero_id: int, size: str = "full") -> str:
    """
    Get hero portrait image URL.

    Args:
        hero_id: The hero ID
        size: 'full', 'icon', 'vert' (full portrait, mini icon, vertical portrait)

    Returns:
        CDN URL for hero image
    """
    hero = HERO_DATA.get(hero_id)
    if not hero:
        return ""

    # Convert name to URL-safe format
    name_slug = hero["name"].lower().replace(" ", "_").replace("'", "")

    if size == "icon":
        return f"{HERO_IMAGE_BASE}/icons/{name_slug}.png"
    elif size == "vert":
        return f"{HERO_IMAGE_BASE}/{name_slug}.png"
    else:
        return f"{HERO_IMAGE_BASE}/{name_slug}.png"


# =============================================================================
# LOOKUP FUNCTIONS
# =============================================================================


@lru_cache(maxsize=256)
def get_hero_name(hero_id: int) -> str:
    """Get hero name from ID."""
    hero = HERO_DATA.get(hero_id)
    return hero["localized_name"] if hero else f"Unknown ({hero_id})"


@lru_cache(maxsize=256)
def get_hero_id(hero_name: str) -> Optional[int]:
    """Get hero ID from name (case-insensitive)."""
    hero_name_lower = hero_name.lower()
    for hid, hero in HERO_DATA.items():
        if hero["name"].lower() == hero_name_lower or hero["localized_name"].lower() == hero_name_lower:
            return hid
    return None


def get_hero_data(hero_id: int) -> Optional[Dict[str, Any]]:
    """Get full hero data from ID."""
    hero = HERO_DATA.get(hero_id)
    if hero:
        return {
            "hero_id": hero_id,
            **hero,
            "image_url": get_hero_image_url(hero_id),
            "icon_url": get_hero_image_url(hero_id, "icon"),
        }
    return None


def get_all_heroes() -> List[Dict[str, Any]]:
    """Get all heroes with their data."""
    return [get_hero_data(hid) for hid in sorted(HERO_DATA.keys())]


def get_heroes_by_attribute(attr: str) -> List[Dict[str, Any]]:
    """Get heroes filtered by primary attribute (str, agi, int)."""
    return [get_hero_data(hid) for hid, hero in HERO_DATA.items() if hero["primary_attr"] == attr]


def get_heroes_by_role(role: str) -> List[Dict[str, Any]]:
    """Get heroes that have a specific role."""
    role_lower = role.lower()
    return [
        get_hero_data(hid)
        for hid, hero in HERO_DATA.items()
        if any(r.lower() == role_lower for r in hero.get("roles", []))
    ]


# =============================================================================
# PRO META INTEGRATION
# =============================================================================


def load_pro_meta() -> Dict[int, Dict[str, Any]]:
    """Load pro meta statistics from heroes_meta.json."""
    meta_path = Path(__file__).parent.parent / "Database" / "Json" / "heroes" / "heroes_meta.json"

    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        heroes_meta = {}
        for hero in data.get("heroes", []):
            hero_id = hero.get("hero_id")
            if hero_id:
                heroes_meta[hero_id] = {
                    "hero_name": hero.get("hero_name"),
                    "picks": hero.get("stats", {}).get("picks", 0),
                    "bans": hero.get("stats", {}).get("bans", 0),
                    "presence_rate": hero.get("stats", {}).get("presence_rate", 0),
                    "winrate": hero.get("stats", {}).get("winrate", 0),
                    "tier": hero.get("tier", "C"),
                    "roles": hero.get("roles", []),
                }

        return heroes_meta
    except Exception as e:
        print(f"⚠️ Could not load pro meta: {e}")
        return {}


def get_hero_with_meta(hero_id: int) -> Optional[Dict[str, Any]]:
    """Get hero data enriched with pro meta statistics."""
    hero = get_hero_data(hero_id)
    if not hero:
        return None

    meta = load_pro_meta()
    hero_meta = meta.get(hero_id, {})

    return {
        **hero,
        "pro_meta": {
            "picks": hero_meta.get("picks", 0),
            "bans": hero_meta.get("bans", 0),
            "presence_rate": hero_meta.get("presence_rate", 0),
            "winrate": hero_meta.get("winrate", 0),
            "tier": hero_meta.get("tier", "C"),
            "pro_roles": hero_meta.get("roles", []),
        },
    }


# =============================================================================
# BATCH CONVERSION
# =============================================================================


def convert_hero_ids_to_names(hero_ids: List[int]) -> List[str]:
    """Convert list of hero IDs to names."""
    return [get_hero_name(hid) for hid in hero_ids]


def format_picks_bans(picks: List[int], bans: List[int]) -> Dict[str, List[str]]:
    """Format picks and bans with hero names."""
    return {
        "picks": convert_hero_ids_to_names(picks),
        "bans": convert_hero_ids_to_names(bans),
    }


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("🦸 Testing Hero Mapper...")

    # Test basic lookup
    print(f"\nHero 19: {get_hero_name(19)}")  # Tiny
    print(f"Hero 120: {get_hero_name(120)}")  # Pangolier
    print(f"Hero 86: {get_hero_name(86)}")  # Rubick

    # Test reverse lookup
    print(f"\nTiny ID: {get_hero_id('Tiny')}")
    print(f"Pangolier ID: {get_hero_id('Pangolier')}")

    # Test hero data
    hero = get_hero_data(19)
    print(f"\nTiny data: {hero}")

    # Test image URL
    print(f"\nTiny image: {get_hero_image_url(19)}")

    # Test pro meta
    meta = load_pro_meta()
    print(f"\nLoaded {len(meta)} heroes with pro meta")

    # Test hero with meta
    tiny_meta = get_hero_with_meta(19)
    print(f"\nTiny with meta: Tier {tiny_meta['pro_meta']['tier']}, WR {tiny_meta['pro_meta']['winrate']}%")

    print("\n✅ Hero Mapper test complete!")
