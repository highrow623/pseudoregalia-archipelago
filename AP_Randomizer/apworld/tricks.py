from typing import Dict, List, Set
from BaseClasses import CollectionState

class Loadout:
    dream_breaker: bool = False
    strikebreak: bool = False
    soul_cutter: bool = False
    sunsetter: bool = False
    slide: bool = False
    solar_wind: bool = False
    ascendant_light: bool = False
    cling_gem: bool = False
    kicks: int = 0
    small_keys: bool = False

    def __init__(self, state: CollectionState, player: int, required_small_keys: int):
        self.dream_breaker = state.has_any({"Dream Breaker", "Progressive Dream Breaker"}, player)
        self.strikebreak = state.has("Strikebreak", player) or state.count("Progressive Dream Breaker", player) >= 2
        self.soul_cutter = state.has("Soul Cutter", player) or state.count("Progressive Dream Breaker", player) >= 3
        self.sunsetter = state.has("Sunsetter", player)
        self.slide = state.has_any({"Slide", "Progressive Slide"}, player)
        self.solar_wind = state.has("Solar Wind", player) or state.count("Progressive Slide", player) >= 2
        self.ascendant_light = state.has("Ascendant Light", player)
        self.cling_gem = state.has("Cling Gem", player)
        self.kicks += 3 if state.has("Sun Greaves", player) else 0
        self.kicks += state.count("Heliacal Power", player)
        self.kicks += state.count("Air Kick", player)
        self.small_keys = state.count("Small Key") >= required_small_keys
    
    def to_bit_rep(self) -> int:
        bit_rep = 0
        mask = 1

        def mark_if_true(condition: bool):
            nonlocal bit_rep, mask
            if condition:
                bit_rep = bit_rep | mask
            mask = mask << 1

        mark_if_true(self.dream_breaker)
        mark_if_true(self.strikebreak)
        mark_if_true(self.soul_cutter)
        mark_if_true(self.sunsetter)
        mark_if_true(self.slide)
        mark_if_true(self.solar_wind)
        mark_if_true(self.ascendant_light)
        mark_if_true(self.cling_gem)
        for i in range(1, 5):
            mark_if_true(self.kicks >= i)
        mark_if_true(self.small_keys)

        return bit_rep

class Trick:
    id: str
    loadout: Loadout
    tags: Set[str]

class LogicTricks:
    region_tricks: Dict[str, List[Trick]]
    location_tricks: Dict[str, List[Trick]]
    tag_hierarchy: Dict[str, List[str]]
