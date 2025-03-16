from dataclasses import dataclass
from typing import Dict, Set, List
import re

from BaseClasses import CollectionState

@dataclass
class Loadout:
    dream_breaker: bool = False
    strikebreak: bool = False
    soul_cutter: bool = False
    sunsetter: bool = False
    slide: bool = False
    solar_wind: bool = False
    ascendant_light: bool = False
    clings: int = 0
    kicks: int = 0
    small_keys: bool = False

@dataclass
class Trick:
    id: str
    loadout: Loadout
    tags: Set[str]

@dataclass
class LogicTricks:
    entrance_tricks: Dict[str, List[Trick]]
    location_tricks: Dict[str, List[Trick]]
    tag_hierarchy: Dict[str, Set[str]]

def json_to_trick(trick_json) -> Trick:
    # the trick_json comes from tricks.json
    # it should have the same structure as Trick, which is assumed here
    return Trick(
        id = trick_json["id"],
        loadout = Loadout(**(trick_json["loadout"])),
        tags = set(trick_json["tags"]) if "tags" in trick_json else set(),
    )

def json_to_trick_list_dict(trick_list_dict_json) -> Dict[str, List[Trick]]:
    return {name: [json_to_trick(trick_json) for trick_json in trick_list_json] for name, trick_list_json in trick_list_dict_json.items()}

def json_to_str_set_dict(str_list_dict_json) -> Dict[str, Set[str]]:
    return {name: set(json_list) for name, json_list in str_list_dict_json.items()}

def json_to_logic_tricks(logic_tricks_json) -> LogicTricks:
    # the logic_tricks_json comes from tricks.json
    # it should have the same structure as LogicTricks, which is assumed here
    return LogicTricks(
        entrance_tricks=json_to_trick_list_dict(logic_tricks_json["entrance_tricks"]),
        location_tricks=json_to_trick_list_dict(logic_tricks_json["location_tricks"]),
        tag_hierarchy=json_to_str_set_dict(logic_tricks_json["tag_hierarchy"]))

def state_to_loadout(state: CollectionState, player: int, required_small_keys: int) -> Loadout:
    clings = 6 if state.has("Cling Gem", player) else 0

    kicks = 3 if state.has("Sun Greaves", player) else 0
    kicks += state.count("Heliacal Power", player)
    kicks += state.count("Air Kick", player)

    return Loadout(
        dream_breaker = state.has_any({"Dream Breaker", "Progressive Dream Breaker"}, player),
        strikebreak = state.has("Strikebreak", player) or state.count("Progressive Dream Breaker", player) >= 2,
        soul_cutter = state.has("Soul Cutter", player) or state.count("Progressive Dream Breaker", player) >= 3,
        sunsetter = state.has("Sunsetter", player),
        slide = state.has_any({"Slide", "Progressive Slide"}, player),
        solar_wind = state.has("Solar Wind", player) or state.count("Progressive Slide", player) >= 2,
        ascendant_light = state.has("Ascendant Light", player),
        clings = clings,
        kicks = kicks,
        small_keys = state.count("Small Key") >= required_small_keys,
    )

def loadout_to_bit_rep(loadout: Loadout) -> int:
    bit_rep = 0
    mask = 1

    def mark_if_true(condition: bool):
        nonlocal bit_rep, mask
        if condition:
            bit_rep = bit_rep | mask
        mask = mask << 1

    mark_if_true(loadout.dream_breaker)
    mark_if_true(loadout.strikebreak)
    mark_if_true(loadout.soul_cutter)
    mark_if_true(loadout.sunsetter)
    mark_if_true(loadout.slide)
    mark_if_true(loadout.solar_wind)
    mark_if_true(loadout.ascendant_light)
    for i in range(1, 7):
        mark_if_true(loadout.clings >= i)
    for i in range(1, 5):
        mark_if_true(loadout.kicks >= i)
    mark_if_true(loadout.small_keys)

    return bit_rep

def add_to_mutually_incomparable_set(bit_reps: Set[int], bit_rep: int) -> Set[int]:
    new_minimal_set: Set[int] = {bit_rep}
    for known_bit_rep in bit_reps:
        if known_bit_rep & bit_rep == known_bit_rep:
            # known_bit_rep is strictly more permissive than bit_rep
            # so we can ignore bit_rep
            return bit_reps
        if known_bit_rep & bit_rep == bit_rep:
            # bit_rep is strictly more permissive than known_bit_rep
            # so we can ignore known_bit_rep
            continue
        # otherwise, the bit_reps are incomparable, so we keep both
        new_minimal_set.add(known_bit_rep)
    return new_minimal_set

def bit_rep_to_summary(bit_rep: int) -> str:
    summary = ""
    mask = 1

    def add_to_summary_if_next(item: str):
        nonlocal summary, mask
        if bit_rep & mask != 0:
            summary += f"{item}, "
        mask = mask << 1
    
    def has_next() -> bool:
        nonlocal mask
        has = bit_rep & mask != 0
        mask = mask << 1
        return has
    
    add_to_summary_if_next("dream breaker")
    add_to_summary_if_next("strikebreak")
    add_to_summary_if_next("soul cutter")
    add_to_summary_if_next("sunsetter")
    add_to_summary_if_next("slide")
    add_to_summary_if_next("solar wind")
    add_to_summary_if_next("ascendant light")

    clings = 0
    for _ in range(6):
        clings += 1 if has_next() else 0
    if clings == 1:
        summary += "1 cling, "
    elif clings > 1:
        summary += f"{clings} clings, "

    kicks = 0
    for _ in range(4):
        kicks += 1 if has_next() else 0
    if kicks == 1:
        summary += "1 kick, "
    elif kicks > 1:
        summary += f"{kicks} kicks, "

    add_to_summary_if_next("small keys")

    summary = re.sub(", $", "", summary)

    return f"[{summary}]"
