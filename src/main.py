import os
from glob import glob
from multiprocessing import Pool

from tqdm import tqdm

from convert import convert_score
from utils import get_dest_midi_path

raw_path = "data/raw"
output_path = "data/midi"


def convert_job(src_path: str, dest_path: str):
    try:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
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

    with Pool() as pool:
        futures = [pool.apply_async(convert_job, args=pair) for pair in file_pairs]
        results = [future.get() for future in tqdm(futures)]


def main():
    """Convert the whole dataset"""
    files = glob(raw_path + "/*.mxl")
    convert_batch(files, output_path)


if __name__ == "__main__":
    main()
