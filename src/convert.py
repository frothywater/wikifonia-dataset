from copy import deepcopy

from music21.converter import parse
from music21.duration import GraceDuration
from music21.expressions import Expression
from music21.harmony import ChordSymbol
from music21.interval import Interval
from music21.key import Key, KeySignature
from music21.note import Note
from music21.pitch import Pitch
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

    return list(score.flatten().getElementsByClass(Key))


def unify_key(score: Score):
    """Return a new score transposed to C Major or a minor according its beginning key, and its mode."""
    score_local = deepcopy(score).flatten()
    keys = list(score_local.getElementsByClass(Key))
    mode = "major"
    if len(keys) > 0 and keys[0] is not None:
        tonic: Pitch = keys[0].tonic
        mode = keys[0].mode
        # Calculate pitch shift
        interval = Interval(tonic, Pitch("C")) if mode != "minor" else Interval(tonic, Pitch("A"))
        score_local = score_local.transpose(interval)

    return score_local, mode


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

    # Unify key
    score_unified, mode = unify_key(score)
    key_str = "keymode_C_major" if mode != "minor" else "keymode_A_minor"

    score_flat, chords = extract_chords_music21(score_unified)

    score_flat.write("midi", dest_path)
    add_markers(dest_path, chords, key_str)
