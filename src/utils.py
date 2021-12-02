import os
import string

from mido import MidiFile

from convert import convert_score


def rename(path: str):
    """Rename `.mxl` files in the given path, cancelling out unwanted characters"""
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


def get_midi_messages(file: str):
    """Get message strings in midi file as `mido` object"""
    mid = MidiFile(file)
    result = []
    for msg in mid:
        result.append(str(msg))
    return result


def convert_batch(files: list, new_dir: str, debug=False, skip_existing=True):
    """Convert all `.mxl` files in the given list into `.mid` files to new directory"""
    failed_files = []
    for i, file in enumerate(files):
        dest_path = get_dest_midi_path(file, new_dir)
        if skip_existing and os.path.exists(dest_path):
            continue
        print(f"[{i+1}/{len(files)}] Converting {file}")
        try:
            convert_score(file, dest_path)
        except Exception as error:
            failed_files.append(file)
            if os.path.exists(dest_path):
                os.remove(dest_path)
            print(f"[{i+1}/{len(files)}] Failed to convert {file}")
            if debug:
                raise error
            else:
                print(error)
    return failed_files
