from copy import deepcopy

from music21.converter import parse
from music21.duration import GraceDuration
from music21.expressions import Expression
from music21.harmony import ChordSymbol
from music21.key import Key
from music21.note import Note
from music21.repeat import RepeatMark
from music21.stream import Score

from chord import add_markers


def extract_chords_music21(score: Score):
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


def extract_keys(score: Score):
    """Extract keys or key signatures from a `music21` score."""

    score_local = deepcopy(score)
    return list(score_local.flatten().getElementsByClass(Key))


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

    score_flat, chords = extract_chords_music21(score)

    # Get first key in the score
    keys = extract_keys(score)
    if len(keys) == 0:
        # Assume C Major if the score doesn't have a key
        key_str = "C"    
    else:
        key_str = keys[0].tonicPitchNameWithCase

    score_flat.write("midi", dest_path)
    add_markers(dest_path, chords, key_str)
