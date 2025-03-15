from BaseClasses import CollectionState
from typing import Dict, Callable, List, Set, TYPE_CHECKING
from worlds.generic.Rules import set_rule
from tricks import LogicTricks, Trick, Items
from .constants.tags import ONLY_REQUIRE_SIX_KEYS
from .constants.names import SUN_GREAVES

if TYPE_CHECKING:
    from . import PseudoregaliaWorld
else:
    PseudoregaliaWorld = object


class PseudoregaliaRules:
    world: PseudoregaliaWorld
    player: int
    region_trick_hashes: Dict[str, Set[int]]
    location_trick_hashes: Dict[str, Set[int]]
    required_small_keys: int = 7 # Set to 6 for only_require_6_keys tag

    def __init__(self, world: PseudoregaliaWorld) -> None:
        self.world = world
        self.player = world.player

        logic_tricks = self.load_logic_tricks()
        tags = self.get_tags(logic_tricks)

        self.region_trick_hashes = self.filter_tricks(logic_tricks.region_tricks, tags)
        self.location_trick_hashes = self.filter_tricks(logic_tricks.location_tricks, tags)

        if ONLY_REQUIRE_SIX_KEYS in tags:
            self.required_small_keys = 6

    def load_logic_tricks(self) -> LogicTricks:
        # TODO load logic tricks from tricks.json file
        pass

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
        trick_hashes: Dict[str, Set[int]] = {}
        for name, tricks in rules.items():
            trick_hashes[name] = []
            for trick in tricks:
                is_default_trick = len(trick.tags) == 0
                is_included = trick.id in self.world.options.include_trick_ids.value
                is_excluded = trick.id in self.world.options.exclude_trick_ids.value
                player_has_tags = trick.tags <= player_tags
                if is_default_trick or is_included or not is_excluded and player_has_tags:
                    trick_hashes[name].add(trick.items.build_hash())
        return trick_hashes

    def build_rule(self, trick_hashes: Set[int]) -> Callable[[CollectionState], bool]:
        def rule(state: CollectionState) -> bool:
            if len(trick_hashes) == 0:
                return True

            state_hash = Items(state, self.player, self.required_small_keys).build_hash()
            for trick_hash in trick_hashes:
                if trick_hash & state_hash == trick_hash:
                    return True
            return False
        return rule

    def set_pseudoregalia_rules(self) -> None:
        world = self.world
        multiworld = self.world.multiworld
        split_kicks = bool(world.options.split_sun_greaves)

        for name, trick_hashes in self.region_trick_hashes.items():
            rule = self.build_rule(trick_hashes)
            entrance = multiworld.get_entrance(name, self.player)
            set_rule(entrance, rule)
        for name, trick_hashes in self.location_trick_hashes.items():
            rule = self.build_rule(trick_hashes)
            if name == SUN_GREAVES and split_kicks:
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
