import copy
import os
import string

import muspy
import pretty_midi
from music21.converter import parse
from music21.harmony import ChordSymbol
from music21.midi import MidiFile
from music21.midi.translate import prepareStreamForMidi, streamToMidiFile
from music21.stream import Score

raw_path = "data/wikifonia"
output_path = "data/output"
test_file = "data/wikifonia/AaronSchroederWallyGold-GoodLuckcharm.mxl"


def rename():
    allowed_chars = string.ascii_letters + string.digits + ".-_()"
    files = os.listdir(raw_path)
    for file in files:
        new_name = "".join(filter(lambda c: c in allowed_chars, file))
        extension_index = new_name.rindex(".mxl")
        new_name = new_name[:extension_index] + ".mxl"
        os.rename(os.path.join(raw_path, file), os.path.join(raw_path, new_name))


def get_dest_midi_path(file: str, new_dir: str):
    return os.path.join(new_dir, os.path.basename(file).replace(".mxl", ".mid"))


def extract_chords_music21(score: Score):
    score_midi: Score = prepareStreamForMidi(score)
    score_flattened: Score = score_midi.flatten()
    chords = copy.deepcopy(score_flattened.getElementsByClass(ChordSymbol))
    score_flattened.removeByClass(ChordSymbol)

    # for el in score_flattened.elements:
    #     print(el, el.offset)
    # for chord in chords:
    #     print(chord, chord.offset)

    return score_flattened


def convert_music21(src_path: str, dest_path: str):
    score: Score = parse(src_path, format="musicxml")
    extract_chords_music21(score)
    score.write("midi", dest_path)


def convert_muspy(src_path: str, dest_path: str):
    """Deprecated."""
    music = muspy.read_musicxml(src_path)
    midi = muspy.to_pretty_midi(music)
    midi.write(dest_path)


def convert_batch(files: list, new_dir: str):
    for file in files:
        print(f"Converting {file}")
        try:
            convert_music21(file, get_dest_midi_path(file, new_dir))
        except:
            print(f"[FAILED] Can't convert {file}!")


def main():
    # files = [os.path.join(raw_path, file) for file in os.listdir(raw_path)]
    # os.makedirs(output_path, exist_ok=True)
    # convert_batch(files, output_path)

    convert_music21(test_file, get_dest_midi_path(test_file, "data"))


if __name__ == "__main__":
    main()
