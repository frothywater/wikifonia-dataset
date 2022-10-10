from typing import Dict, List


def change_flat_notation(s: str):
    """Change flat notation from `-` to `b`"""
    return s.replace("-", "b")


def convert_chord(c: str):
    """Convert chord name to an unified representation. Return a tuple of (root_enharm_name, quality)."""
    notes = ["C", "D", "E", "F", "G", "A", "B"]
    accidentals = ["b", "#", "bb", "x", "##"]
    accidental_map = {"b": -1, "#": +1, "bb": -2, "x": +2, "##": +2, "": 0}
    name_to_num = {"C": 0, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}
    num_to_name = {num: name for name, num in name_to_num.items()}

    quality_aliases: Dict[str, List[str]] = {
        "M": ["", "6", "pedal", "power", "maj"],
        "m": ["min"],
        "o": ["dim"],
        "+": ["aug"],
        "sus": ["sus2", "sus4"],
        "MM7": ["maj7", "M7", "M9", "M13"],
        "Mm7": ["7", "7+", "9", "11", "13"],
        "mM7": [],
        "mm7": ["m7", "m9", "m6", "m11", "m13", "min7"],
        "o7": ["dim7"],
        "%7": ["ø7", "m7b5"],
        "+7": [],
        "M7": [],
    }

    # Make aliases include the original name
    for key in quality_aliases:
        quality_aliases[key].append(key)

    quality_map = {alias: quality for quality, aliases in quality_aliases.items() for alias in aliases}
    invalid_chords = ["Chord Symbol Cannot Be Identified", "N.C."]

    def partition_left(s: str, subs: list):
        subs = subs.copy()
        subs.sort(key=lambda s: -len(s))
        for sub in subs:
            _, middle, right = s.partition(sub)
            if middle == sub:
                return sub, right
        return "", s

    c = change_flat_notation(c)

    if len(c) == 0 or c[0] not in notes or c in invalid_chords:
        return None

    # Ignore any extension, alternation, add and omit
    if c.find(" ") != -1:
        c = c.split(" ")[0]
    # Ignore bass note
    if c.find("/") != -1:
        c = c.split("/")[0]

    # Lookup root and accidental
    root_note, remains = partition_left(c, notes)
    if root_note == "":
        return None
    root_accidental, kind = partition_left(remains, accidentals)

    # Convert to enharmonical root and simplified quality
    root_num = (name_to_num[root_note] + accidental_map[root_accidental]) % 12
    root_enharm_name = num_to_name[root_num]
    quality = quality_map[kind]

    return root_enharm_name, quality
