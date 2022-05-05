import os
import string
from multiprocessing import Pool

from mido import MidiFile
from tqdm import tqdm

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


def convert_job(src_path: str, dest_path: str):
    try:
        convert_score(src_path, dest_path)
    except Exception as error:
        if os.path.exists(dest_path):
            os.remove(dest_path)
        print(f"Failed to convert {src_path}")
        print(error)
        # if not str(error).startswith("Degree"):
        #     raise Exception


def convert_batch(files: list, new_dir: str, skip_existing=True):
    """Convert all `.mxl` files in the given list into `.mid` files to new directory"""

    file_pairs = []
    for file in files:
        dest_path = get_dest_midi_path(file, new_dir)
        if skip_existing and os.path.exists(dest_path):
            continue
        file_pairs.append((file, dest_path))

    with Pool(processes=32) as pool:
        futures = [pool.apply_async(convert_job, args=pair) for pair in file_pairs] 
        results = [future.get() for future in tqdm(futures)]
