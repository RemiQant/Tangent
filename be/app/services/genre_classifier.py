"""Maps raw Spotify artist genre tags to broad genre families.

Spotify genre tags are extremely granular (e.g. "electro house", "melodic
dubstep", "nu metal") and rarely match each other as exact strings even when
they describe the same broad style. This module groups raw tags into a small
set of families so that, e.g., an "edm" seed can match an "electro house"
candidate.

Some tags are ambiguous bridges between unrelated families (e.g. bare
"industrial" appears on both EDM-adjacent and Metal-adjacent artists). To
avoid those bridges causing cross-family matches (the original EDM+Metal
mixing bug), more specific compound phrases are matched before generic
single-word ones, and a generic rule is skipped if a more specific rule
already matched a superstring of it.
"""

from typing import Iterable

# Ordered most-specific-first: multi-word/compound phrases before the generic
# single-word keywords they contain. A single genre tag may contribute to
# multiple families (e.g. "electronic rock" -> EDM + Rock).
GENRE_FAMILY_RULES: tuple[tuple[str, frozenset[str]], ...] = (
    # --- Industrial bridging cases (must precede bare "industrial") ---
    ("industrial metal", frozenset({"Metal"})),
    ("industrial rock", frozenset({"Rock"})),
    ("industrial techno", frozenset({"EDM"})),
    ("industrial house", frozenset({"EDM"})),
    ("industrial hardcore", frozenset({"EDM"})),

    # --- EDM (specific subgenres before generic) ---
    ("electro house", frozenset({"EDM"})),
    ("melodic dubstep", frozenset({"EDM"})),
    ("future bass", frozenset({"EDM"})),
    ("drum and bass", frozenset({"EDM"})),
    ("drum & bass", frozenset({"EDM"})),
    ("electronic rock", frozenset({"EDM", "Rock"})),
    ("electropop", frozenset({"EDM", "Pop"})),
    ("synthwave", frozenset({"EDM"})),
    ("dubstep", frozenset({"EDM"})),
    ("techno", frozenset({"EDM"})),
    ("house", frozenset({"EDM"})),
    ("trance", frozenset({"EDM"})),
    ("edm", frozenset({"EDM"})),
    ("electronic", frozenset({"EDM"})),
    ("electro", frozenset({"EDM"})),

    # --- Metal ---
    ("death metal", frozenset({"Metal"})),
    ("black metal", frozenset({"Metal"})),
    ("thrash metal", frozenset({"Metal"})),
    ("doom metal", frozenset({"Metal"})),
    ("nu metal", frozenset({"Metal"})),
    ("metalcore", frozenset({"Metal", "Punk"})),
    ("heavy metal", frozenset({"Metal"})),
    ("metal", frozenset({"Metal"})),

    # --- Punk ---
    ("post-punk", frozenset({"Punk", "Rock"})),
    ("pop punk", frozenset({"Punk", "Pop"})),
    ("punk rock", frozenset({"Punk", "Rock"})),
    ("punk", frozenset({"Punk"})),

    # --- Rock ---
    ("classic rock", frozenset({"Rock"})),
    ("indie rock", frozenset({"Rock"})),
    ("alternative rock", frozenset({"Rock"})),
    ("alt rock", frozenset({"Rock"})),
    ("hard rock", frozenset({"Rock"})),
    ("rock", frozenset({"Rock"})),
    ("alternative", frozenset({"Rock"})),
    ("indie", frozenset({"Rock"})),

    # --- Hip-Hop ---
    ("hip hop", frozenset({"Hip-Hop"})),
    ("hip-hop", frozenset({"Hip-Hop"})),
    ("rap", frozenset({"Hip-Hop"})),
    ("trap", frozenset({"Hip-Hop"})),

    # --- Pop ---
    ("k-pop", frozenset({"Pop"})),
    ("pop", frozenset({"Pop"})),

    # --- R&B / Soul ---
    ("r&b", frozenset({"R&B/Soul"})),
    ("rnb", frozenset({"R&B/Soul"})),
    ("soul", frozenset({"R&B/Soul"})),
    ("funk", frozenset({"R&B/Soul"})),

    # --- Country / Folk / Acoustic ---
    ("bluegrass", frozenset({"Country", "Folk/Acoustic"})),
    ("country", frozenset({"Country"})),
    ("singer-songwriter", frozenset({"Folk/Acoustic"})),
    ("acoustic", frozenset({"Folk/Acoustic"})),
    ("folk", frozenset({"Folk/Acoustic"})),

    # --- Jazz / Classical ---
    ("jazz", frozenset({"Jazz"})),
    ("classical", frozenset({"Classical"})),
    ("orchestra", frozenset({"Classical"})),
    ("opera", frozenset({"Classical"})),

    # --- Latin / Reggae ---
    ("reggaeton", frozenset({"Latin"})),
    ("latin", frozenset({"Latin"})),
    ("salsa", frozenset({"Latin"})),
    ("ska", frozenset({"Reggae", "Punk"})),
    ("reggae", frozenset({"Reggae"})),
    ("dancehall", frozenset({"Reggae"})),

    # --- Ambient / Chill / Lo-fi ---
    ("chillwave", frozenset({"Ambient/Chill"})),
    ("lo-fi", frozenset({"Ambient/Chill"})),
    ("lofi", frozenset({"Ambient/Chill"})),
    ("chill", frozenset({"Ambient/Chill"})),
    ("ambient", frozenset({"Ambient/Chill"})),

    # --- Neutral bucket for bare "industrial" ---
    # Deliberately does not overlap with EDM or Metal so an artist tagged
    # only "industrial" doesn't bridge those two families.
    ("industrial", frozenset({"Industrial"})),
)


def classify_single_genre(genre: str) -> frozenset[str]:
    """Classify one raw Spotify genre tag into its genre family/families.

    Rules are scanned most-specific-first. Once a keyword matches, any later
    keyword that is itself a substring of an already-matched keyword is
    skipped, so e.g. "industrial metal" claims {"Metal"} without the bare
    "industrial" rule also contributing {"Industrial"}.

    Returns an empty frozenset if no rule matches.
    """
    normalized = genre.lower().strip()
    families: set[str] = set()
    matched_keywords: list[str] = []

    for keyword, family_set in GENRE_FAMILY_RULES:
        if keyword not in normalized:
            continue
        if any(keyword in matched for matched in matched_keywords):
            continue
        families.update(family_set)
        matched_keywords.append(keyword)

    return frozenset(families)


def classify_genres(genres: Iterable[str]) -> frozenset[str]:
    """Classify a collection of raw Spotify genre tags into the union of
    all genre families they belong to."""
    families: set[str] = set()
    for genre in genres:
        families.update(classify_single_genre(genre))
    return frozenset(families)
