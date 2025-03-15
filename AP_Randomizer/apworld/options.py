from dataclasses import dataclass
from Options import Toggle, DefaultOnToggle, DeathLink, PerGameCommonOptions, OptionSet


class TrickTags(OptionSet):
    """
    These tags define which tricks to include in the logic.
    A default set of tricks is always included, so this can be empty.

    TODO finish this comment
    """
    display_name = "Trick Tags"


class IncludeTrickIDs(OptionSet):
    """
    This list of trick ids bypasses the trick_tags to include tricks that would otherwise be excluded.

    TODO finish this comment
    """
    display_name = "Include Trick IDs"


class ExcludeTrickIDs(OptionSet):
    """
    This list of trick ids bypasses the trick_tags to exclude tricks that would otherwise be included.
    A default trick (i.e. a trick with no tags) cannot be excluded. (Or else the logic might become impossible!)

    TODO finish this comment
    """
    display_name = "Exclude Trick IDs"


class ProgressiveBreaker(DefaultOnToggle):
    """
    Replaces Dream Breaker, Strikebreak, and Soul Cutter with three Progressive Dream Breaker items.
    """
    display_name = "Progressive Dream Breaker"


class ProgressiveSlide(DefaultOnToggle):
    """
    Replaces Slide and Solar Wind with two Progressive Slide items.
    """
    display_name = "Progressive Slide"


class SplitSunGreaves(Toggle):
    """
    Replaces Sun Greaves and Heliacal Power with four individual Air Kicks.
    """
    display_name = "Split Sun Greaves"


@dataclass
class PseudoregaliaOptions(PerGameCommonOptions):
    trick_tags: TrickTags
    include_trick_ids: IncludeTrickIDs
    exclude_trick_ids: ExcludeTrickIDs
    progressive_breaker: ProgressiveBreaker
    progressive_slide: ProgressiveSlide
    split_sun_greaves: SplitSunGreaves
    death_link: DeathLink

