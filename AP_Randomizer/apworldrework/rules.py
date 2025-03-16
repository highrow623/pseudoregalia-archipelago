import os
import json
from BaseClasses import CollectionState
from typing import Dict, Callable, List, Set, TYPE_CHECKING
from worlds.generic.Rules import set_rule
from .tricks import LogicTricks, Trick, json_to_logic_tricks, state_to_loadout, loadout_to_bit_rep, remove_unnecessary_tricks
from .constants.tags import ONLY_REQUIRE_SIX_KEYS
from .constants.names import LOCATION_SUN_GREAVES

if TYPE_CHECKING:
    from . import PseudoregaliaWorld
else:
    PseudoregaliaWorld = object


class PseudoregaliaRules:
    world: PseudoregaliaWorld
    player: int
    entrance_rules: Dict[str, Callable[[CollectionState], bool]]
    location_rules: Dict[str, Callable[[CollectionState], bool]]
    required_small_keys: int = 7 # Set to 6 for only_require_6_keys tag

    logic_tricks: LogicTricks
    player_tags: Set[str]
    entrance_trick_bit_reps: Dict[str, Set[int]]
    location_trick_bit_reps: Dict[str, Set[int]]

    def __init__(self, world: PseudoregaliaWorld) -> None:
        self.world = world
        self.player = world.player

        self.logic_tricks = self.load_logic_tricks()
        self.player_tags = self.get_tags()

        if ONLY_REQUIRE_SIX_KEYS in self.player_tags:
            self.required_small_keys = 6

        self.entrance_trick_bit_reps = self.filter_tricks(self.logic_tricks.entrance_tricks)
        self.location_trick_bit_reps = self.filter_tricks(self.logic_tricks.location_tricks)

        self.entrance_rules = self.build_rules(self.entrance_trick_bit_reps)
        self.location_rules = self.build_rules(self.location_trick_bit_reps)

    def load_logic_tricks(self) -> LogicTricks:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        tricks_path = os.path.join(current_dir, "tricks.json")
        with open(tricks_path) as f:
            logic_tricks_json = json.load(f)
            return json_to_logic_tricks(logic_tricks_json)

    def get_tags(self) -> Set[str]:
        tags: Set[str] = set() # already evaluated
        tag_queue: Set[str] = set() # to add but not yet evaluated
        for tag in self.world.options.trick_tags.value:
            tag_queue.add(tag)
        
        while len(tag_queue) != 0:
            tag = tag_queue.pop()
            tags.add(tag)

            if tag not in self.logic_tricks.tag_hierarchy:
                continue

            for child_tag in self.logic_tricks.tag_hierarchy[tag]:
                if child_tag in tags:
                    continue
                tag_queue.add(child_tag)
        
        return tags
    
    def filter_tricks(self, rule_tricks: Dict[str, List[Trick]]) -> Dict[str, Set[int]]:
        trick_bit_reps: Dict[str, Set[int]] = {}
        for name, tricks_list in rule_tricks.items():
            trick_bit_rep_set: Set[int] = set()
            for trick in tricks_list:
                is_default_trick = len(trick.tags) == 0
                is_included = trick.id in self.world.options.include_trick_ids.value
                is_excluded = trick.id in self.world.options.exclude_trick_ids.value
                player_has_tags = trick.tags <= self.player_tags
                if is_default_trick or is_included or not is_excluded and player_has_tags:
                    trick_bit_rep_set.add(loadout_to_bit_rep(trick.loadout))
            trick_bit_rep_set = remove_unnecessary_tricks(trick_bit_rep_set)
            if next(iter(trick_bit_rep_set)) == 0:
                continue
            trick_bit_reps[name] = trick_bit_rep_set
        return trick_bit_reps

    def build_rules(self, rules_bit_reps: Dict[str, Set[int]]) -> Dict[str, Callable[[CollectionState], bool]]:
        rules: Dict[str, Callable[[CollectionState], bool]] = {}
        for name, trick_bit_reps in rules_bit_reps.items():
            rules[name] = self.build_rule(trick_bit_reps)
        return rules

    def build_rule(self, trick_bit_reps: Set[int]) -> Callable[[CollectionState], bool]:
        def rule(state: CollectionState) -> bool:
            if len(trick_bit_reps) == 0:
                return True

            state_loadout = state_to_loadout(state, self.player, self.required_small_keys)
            state_bit_rep = loadout_to_bit_rep(state_loadout)
            for trick_bit_rep in trick_bit_reps:
                if trick_bit_rep & state_bit_rep == trick_bit_rep:
                    return True
            return False
        return rule

    def set_pseudoregalia_rules(self) -> None:
        world = self.world
        multiworld = world.multiworld
        split_kicks = bool(world.options.split_sun_greaves)

        for name, rule in self.entrance_rules.items():
            entrance = multiworld.get_entrance(name, self.player)
            set_rule(entrance, rule)
        for name, rule in self.location_rules.items():
            if name == LOCATION_SUN_GREAVES and split_kicks:
                for i in range(1, 4):
                    location = multiworld.get_location(f"{name} {i}", self.player)
                    set_rule(location, rule)
                continue
            location = multiworld.get_location(name, self.player)
            set_rule(location, rule)

        set_rule(multiworld.get_location("D S T RT ED M M O   Y", self.player), lambda state:
                 state.has_all({
                     "Major Key - Empty Bailey",
                     "Major Key - The Underbelly",
                     "Major Key - Tower Remains",
                     "Major Key - Sansa Keep",
                     "Major Key - Twilight Theatre",
                 }, self.player))
        multiworld.completion_condition[self.player] = lambda state: state.has(
            "Something Worth Being Awake For", self.player)
