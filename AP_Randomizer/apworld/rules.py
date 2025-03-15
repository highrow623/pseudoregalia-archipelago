import os
import json
from BaseClasses import CollectionState
from typing import Dict, Callable, List, Set, TYPE_CHECKING
from worlds.generic.Rules import set_rule
from tricks import LogicTricks, Trick, Loadout
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

    def __init__(self, world: PseudoregaliaWorld) -> None:
        self.world = world
        self.player = world.player

        logic_tricks = self.load_logic_tricks()
        tags = self.get_tags(logic_tricks)

        if ONLY_REQUIRE_SIX_KEYS in tags:
            self.required_small_keys = 6

        entrance_trick_bit_reps = self.filter_tricks(logic_tricks.entrance_tricks, tags)
        location_trick_bit_reps = self.filter_tricks(logic_tricks.location_tricks, tags)

        self.entrance_rules = self.build_rules(entrance_trick_bit_reps)
        self.location_rules = self.build_rules(location_trick_bit_reps)

    def load_logic_tricks(self) -> LogicTricks:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        tricks_path = os.path.join(current_dir, "tricks.json")
        with open(tricks_path) as f:
            logic_tricks: LogicTricks = json.load(f)
            return logic_tricks

    def get_tags(self, tag_hierarchy: Dict[str, List[str]]) -> Set[str]:
        tags: Set[str] = set() # already evaluated
        tag_queue: Set[str] = set() # to add but not yet evaluated
        for tag in self.world.options.trick_tags.value:
            tag_queue.add(tag)
        
        while True:
            if len(tag_queue) == 0:
                return tags
            
            tag = tag_queue.pop()
            tags.add(tag)

            if tag not in tag_hierarchy:
                continue

            for child_tag in tag_hierarchy[tag]:
                if child_tag in tags:
                    continue
                tag_queue.add(child_tag)
    
    def filter_tricks(self, rules: Dict[str, List[Trick]], player_tags: Set[str]) -> Dict[str, Set[int]]:
        trick_bit_reps: Dict[str, Set[int]] = {}
        for name, tricks in rules.items():
            trick_bit_reps[name] = []
            for trick in tricks:
                is_default_trick = len(trick.tags) == 0
                is_included = trick.id in self.world.options.include_trick_ids.value
                is_excluded = trick.id in self.world.options.exclude_trick_ids.value
                player_has_tags = set(trick.tags) <= player_tags
                if is_default_trick or is_included or not is_excluded and player_has_tags:
                    trick_bit_reps[name].add(trick.loadout.to_bit_rep())
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

            state_bit_rep = Loadout(state, self.player, self.required_small_keys).to_bit_rep()
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
                    new_name = f"{name} {i}"
                    location = multiworld.get_location(new_name, self.player)
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
