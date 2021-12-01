from copy import deepcopy

from music21.converter import parse
from music21.harmony import ChordSymbol
from music21.midi.translate import prepareStreamForMidi
from music21.stream import Score

from chord import add_chord_markers


def extract_chords_music21(score: Score):
    score_processed_flat = prepareStreamForMidi(score).flatten()
    chord_elements = score_processed_flat.getElementsByClass(ChordSymbol)
    chords = [(element.figure, element.offset) for element in chord_elements]

    new_score = deepcopy(score)
    for chord_symbol in new_score.recurse(classFilter=(ChordSymbol)):
        new_score.remove(chord_symbol, recurse=True)

    return new_score, chords


def convert_music21(src_path: str, dest_path: str):
    score: Score = parse(src_path, format="musicxml")
    score_flat, chords = extract_chords_music21(score)
    score_flat.write("midi", dest_path)

    add_chord_markers(dest_path, chords)
