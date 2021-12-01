import os
import string
from copy import deepcopy

from mido import MetaMessage, MidiFile, MidiTrack
from music21.converter import parse
from music21.harmony import ChordSymbol
from music21.midi.translate import prepareStreamForMidi
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
    score_processed_flat = prepareStreamForMidi(score).flatten()
    chord_elements = score_processed_flat.getElementsByClass(ChordSymbol)
    chords = [(element.figure, element.offset) for element in chord_elements]

    new_score = deepcopy(score)
    for chord_symbol in new_score.recurse(classFilter=(ChordSymbol)):
        new_score.remove(chord_symbol, recurse=True)

    return new_score, chords


def accumulate_time(messages: list):
    if len(messages) == 0:
        return
    current = 0
    result = []
    for msg, delta_time in messages:
        current += delta_time
        result.append((msg, current))
    return result


def deaccumulate_time(messages: list):
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


def add_chord_markers(file: str, chords: list):
    mid = MidiFile(file)
    track: MidiTrack = mid.tracks[1]
    messages = [(msg, msg.time) for msg in track]

    messages = accumulate_time(messages)
    for name, offset in chords:
        marker_message = MetaMessage("marker")
        marker_message.text = name.replace("-", "b")
        abs_time = int(offset * mid.ticks_per_beat)
        messages.append((marker_message, abs_time))
    messages.sort(key=lambda x: x[1])
    messages = deaccumulate_time(messages)

    track.clear()
    for msg, delta_time in messages:
        msg.time = delta_time
        track.append(msg)
    mid.save(file)


def show_midi(file: str):
    mid = MidiFile(file)
    for msg in mid:
        print(msg)


def convert_music21(src_path: str, dest_path: str):
    score: Score = parse(src_path, format="musicxml")
    score_flat, chords = extract_chords_music21(score)
    score_flat.write("midi", dest_path)

    add_chord_markers(dest_path, chords)


def convert_batch(files: list, new_dir: str):
    failed_files = []
    for i, file in enumerate(files):
        print(f"[{i+1}/{len(files)}] Converting {file}", flush=True)
        dest_path = get_dest_midi_path(file, new_dir)
        try:
            convert_music21(file, dest_path)
        except:
            failed_files.append(file)
            if os.path.exists(dest_path):
                os.remove(dest_path)
            print(f"[{i+1}/{len(files)}] Failed to convert {file}", flush=True)
    return failed_files


def main():
    files = [os.path.join(raw_path, file) for file in os.listdir(raw_path)]
    os.makedirs(output_path, exist_ok=True)
    failed_files = convert_batch(files, output_path)

    print(f"Succeed {len(files) - len(failed_files)} files.")
    print(f"There're {len(failed_files)} failed files:")
    for file in failed_files:
        print(file)


if __name__ == "__main__":
    main()
