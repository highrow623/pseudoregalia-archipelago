from typing import Dict, List
from BaseClasses import CollectionState

class Items:
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
        if state.has_any({"Dream Breaker", "Progressive Dream Breaker"}, player):
            self.dream_breaker = True
        if state.has("Strikebreak", player) or state.count("Progressive Dream Breaker", player) >= 2:
            self.strikebreak = True
        if state.has("Soul Cutter", player) or state.count("Progressive Dream Breaker", player) >= 3:
            self.soul_cutter = True
        if state.has("Sunsetter", player):
            self.sunsetter = True
        if state.has_any({"Slide", "Progressive Slide"}, player):
            self.slide = True
        if state.has("Solar Wind", player) or state.count("Progressive Slide", player) >= 2:
            self.solar_wind = True
        if state.has("Ascendant Light", player):
            self.ascendant_light = True
        if state.has("Cling Gem", player):
            self.cling_gem = True
        if (state.has("Sun Greaves", player)):
            self.kicks += 3
        self.kicks += state.count("Heliacal Power", player)
        self.kicks += state.count("Air Kick", player)
        if state.count("Small Key") >= required_small_keys:
            self.small_keys = True
    
    def to_bit_rep(self) -> int:
        bits = 0
        mask = 1

        def mark_if_true(condition: bool):
            nonlocal bits, mask
            if condition:
                bits = bits | mask
            mask = mask << 1

        mark_if_true(self.dream_breaker)
        mark_if_true(self.strikebreak)
        mark_if_true(self.soul_cutter)
        mark_if_true(self.sunsetter)
        mark_if_true(self.slide)
        mark_if_true(self.solar_wind)
        mark_if_true(self.ascendant_light)
        mark_if_true(self.cling_gem)
        mark_if_true(self.kicks >= 1)
        mark_if_true(self.kicks >= 2)
        mark_if_true(self.kicks >= 3)
        mark_if_true(self.kicks >= 4)
        mark_if_true(self.small_keys)

        return bits

class Trick:
    id: str
    items: Items
    tags: List[str]

class LogicTricks:
    region_tricks: Dict[str, List[Trick]]
    location_tricks: Dict[str, List[Trick]]
    tag_hierarchy: Dict[str, List[str]]
