"""A set of classes used to represent Mods in memory."""

# Disable warnings about 'too few class methods'
# pylint: disable=R0903

from typing import List, NamedTuple, Union


def yaml_serializable(cls):
    """Make a NamedTuple serializable by PyYAML."""
    class Wrapper(object):
        """Provides the __dict__ property for annotated objects."""

        def __init__(self, *args):
            self.__wrapped = cls(*args)
            self.__dict__ = dict(self.__wrapped._asdict())

    return Wrapper


@yaml_serializable
class Media(NamedTuple):
    """Container for media URLs."""

    images: List[str]  # Screenshots of the mod
    videos: List[str]  # Videos of the mod


@yaml_serializable
class Webpages(NamedTuple):
    """Container for the mod's homepages."""

    steam: Union[str, None]  # The URL of the mod's workshop page, or None
    nexus: Union[str, None]  # The URL of the mod's nexus page, or None
    bethesda: Union[str, None]  # The URL of the mod's bethesda page, or None
    others: List[str]   # The URLs for the mod's other pages (GH, AFKM, etc)


@yaml_serializable
class Requirement(NamedTuple):
    """Pointer to another mod needed by this mod."""

    modid: Union[int, None]  # The modid of the required mod, or None if N/A
    name: str  # The name of the required mod
    optional: bool  # If true, the mod will work without the requirement


@yaml_serializable
class Oldrim(NamedTuple):
    """Container for oldrim-specific data."""

    is_oldrim: bool  # If true, the mod has an oldrim version
    webpages: Webpages
    requirements: List[Requirement]


@yaml_serializable
class Sse(NamedTuple):
    """Container for SSE-specific data."""

    is_sse: bool  # If true, the mod has an SSE version
    webpages: Webpages
    requirements: List[Requirement]


@yaml_serializable
class Mod(NamedTuple):
    """A collection of useful info about a mod."""

    modid: int  # The id of this mod (order it was added)
    name: str  # The name of this mod
    description: str  # A description of what this mod does
    notes: List[str]  # Installation notes and warnings
    gems_category: Union[str, None]  # This mod's category in GEMS, if any
    media: Media
    oldrim: Oldrim
    sse: Sse
    tags: List[str] = []  # A list of strings
    deprecated: bool = False  # Whether this mod has been replaced
    entry_verified: bool = False  # Whether this entry was checked by a human
