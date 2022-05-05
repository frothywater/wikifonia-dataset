from typing import Dict, List

from mido import MetaMessage, MidiFile, MidiTrack


def accumulate_time(messages: list):
    if len(messages) == 0:
        return
    current = 0
    result = []
    for msg, delta_time in messages:
        current += delta_time
        result.append((msg, current))
    return result


def decumulate_time(messages: list):
    if len(messages) == 0:
        return
    result = []
    for i in range(len(messages)):
        if i == 0:
            result.append(messages[0])
        else:
            msg, abs_time = messages[i]
            _, prev_time = messages[i - 1]
            result.append((msg, abs_time - prev_time))
    return result


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


def add_markers(file: str, chords: list, key: str = None):
    """Add chord markers in given MIDI file, chord list and key notation.
    
    Chords are a list of tuple in form of (name, quarter offset).
    Key notation is tonic pitch name, uppercased if major, lowercased if minor.

    In the resulting MIDI file, there will be two types of markers:
    1) Key marker at the beginning, with text `Key_{key}`,
    2) Chord markers, with text `{root}_{quality}`.
    """
    mid = MidiFile(file)
    track: MidiTrack = mid.tracks[1]
    messages = [(msg, msg.time) for msg in track]

    # Calculate absolute time of each message
    messages = accumulate_time(messages)

    # Append key marker
    if key is not None:
        key = change_flat_notation(key)
        key_message = MetaMessage("marker", text=key)
        messages.append((key_message, 0))

    # Append chord markers into the track
    for name, offset in chords:
        chord = convert_chord(name)
        if chord is None:
            continue
        root, quality = convert_chord(name)
        marker_message = MetaMessage("marker", text=f"{root}_{quality}")
        abs_time = int(offset * mid.ticks_per_beat)
        messages.append((marker_message, abs_time))

    # Sort all the messages, and decumulate to relative time
    messages.sort(key=lambda x: x[1])
    messages = decumulate_time(messages)

    # Clear the track and add the processed messages
    track.clear()
    for msg, delta_time in messages:
        msg.time = delta_time
        track.append(msg)
    mid.save(file)
