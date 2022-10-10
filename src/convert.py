from copy import deepcopy

from mido import MetaMessage, MidiFile, MidiTrack
from music21.converter import parse
from music21.duration import GraceDuration
from music21.expressions import Expression
from music21.harmony import ChordSymbol
from music21.note import Note
from music21.repeat import RepeatMark
from music21.stream import Score

from chord import convert_chord


def extract_chords(score: Score):
    """Extract chords from a `music21` score. Return a tuple of (new score without chords, chords).

    Chords are a list of tuple in form of (name, quarter offset).
    """
    score_local = deepcopy(score)

    # Collect all chords
    # (in flattened score to get right offset)
    chords = []
    for chord_symbol in score_local.flatten().getElementsByClass(ChordSymbol):
        chords.append((chord_symbol.figure, chord_symbol.offset))

    # Remove all chords from the score
    # (otherwise, `music21` will render chords to notes in final midi file)
    for chord_symbol in score_local.recurse(classFilter=ChordSymbol):
        score_local.remove(chord_symbol, recurse=True)

    return score_local, chords


def convert_score(src_path: str, dest_path: str, expand_repeat=False, realize_expression=False):
    """Convert a `.mxl` file into a `.mid` file.

    Jobs: (1) extract chords from score; (2) add chord markers into result MIDI file.

    Parameter:
    - `expand_repeat`: If true, repeat signs in the score will be expanded, which could cause problems.
    - `realize_expression`: If true, expressions in the score will be realized, which could cause problems.
    """

    score: Score = parse(src_path, format="musicxml")

    if expand_repeat:
        # Expand repeats in the score (return a new copy)
        score = score.expandRepeats()
    else:
        # Remove all repeat signs
        for repeat in score.recurse(classFilter=RepeatMark):
            score.remove(repeat, recurse=True)

    if not realize_expression:
        # Remove all expressions
        for expression in score.recurse(classFilter=Expression):
            score.remove(expression, recurse=True)
        # Remove all notes with *grace duration*
        for note in score.recurse(classFilter=Note):
            if isinstance(note.duration, GraceDuration):
                score.remove(note, recurse=True)

    score_flat, chords = extract_chords(score)

    score_flat.write("midi", dest_path)
    add_markers(dest_path, chords)


def add_markers(file: str, chords: list):
    """Add chord markers in given MIDI file, chord list and key notation.

    Chords are a list of tuple in form of (name, quarter offset).

    In the resulting MIDI file, there will be:
    1) Chord markers, with text `{root}_{quality}`.
    """
    mid = MidiFile(file)
    track: MidiTrack = mid.tracks[1]
    messages = [(msg, msg.time) for msg in track]

    # Calculate absolute time of each message
    messages = accumulate_time(messages)

    # Append chord markers into the track
    for name, offset in chords:
        chord = convert_chord(name)
        if chord is None:
            continue
        root, quality = convert_chord(name)
        marker_message = MetaMessage("marker", text=f"Chord_{root}_{quality}")
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
