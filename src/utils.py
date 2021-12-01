import os
import string

from mido import MidiFile


def rename(path: str):
    allowed_chars = string.ascii_letters + string.digits + ".-_()"
    files = os.listdir(path)
    for file in files:
        new_name = "".join(filter(lambda c: c in allowed_chars, file))
        extension_index = new_name.rindex(".mxl")
        new_name = new_name[:extension_index] + ".mxl"
        os.rename(os.path.join(path, file), os.path.join(path, new_name))


def write_list(strings: list, path: str):
    with open(path, "w") as file:
        for str in strings:
            file.write(str + "\n")


def get_dest_midi_path(file: str, new_dir: str):
    return os.path.join(new_dir, os.path.basename(file).replace(".mxl", ".mid"))


def show_midi(file: str):
    mid = MidiFile(file)
    for msg in mid:
        print(msg)
