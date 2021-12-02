from copy import deepcopy

from music21.converter import parse
from music21.harmony import ChordSymbol
from music21.repeat import RepeatMark
from music21.stream import Score

from chord import add_chord_markers


def extract_chords_music21(score: Score, ignore_repeat):
    """Extract chords from a `music21` score. Return a tuple of (new score without chords, chords).

    Chords are a list of tuple in form of (name, quarter offset).
    
    Parameter:
    - `ignore_repeat`: If true, repeat marks in the score will be not expanded.
    """
    score_local = deepcopy(score)

    if ignore_repeat:
        # Remove all repeat expressions
        for repeat in score_local.recurse(classFilter=RepeatMark):
            score_local.remove(repeat, recurse=True)
    else:
        # Expand repeats in the score (return a new copy)
        score_local = score_local.expandRepeats()

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


def convert_music21(src_path: str, dest_path: str, ignore_repeat=False):
    """Convert a `.mxl` file into a `.mid` file.
    
    Jobs: (1) extract chords from score; (2) add chord markers into result MIDI file.
    """

    score: Score = parse(src_path, format="musicxml")
    score_flat, chords = extract_chords_music21(score, ignore_repeat)
    score_flat.write("midi", dest_path)

    add_chord_markers(dest_path, chords)
