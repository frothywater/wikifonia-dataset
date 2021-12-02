import os

from convert import convert_music21
from utils import get_dest_midi_path, show_midi, write_list

raw_path = "data/wikifonia"
output_path = "data/output"

all_txt_path = "data/all.txt"
failed_txt_path = "data/failed.txt"
succeed_txt_path = "data/succeed.txt"
failed_output_path = "data/failed_output"
data_path = "data"
test_file = "data/wikifonia/BryanWellsRonaldN.Miller-SomedayatChristmas.mxl"


def convert_batch(files: list, new_dir: str, debug=False, skip_existing=True):
    """Convert all `.mxl` files in the given list into `.mid` files to new directory"""
    failed_files = []
    for i, file in enumerate(files):
        dest_path = get_dest_midi_path(file, new_dir)
        if skip_existing and os.path.exists(dest_path):
            continue

        print(f"[{i+1}/{len(files)}] Converting {file}")
        try:
            convert_music21(file, dest_path, ignore_repeat=True)
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


def do_batch():
    """Convert the whole dataset"""
    files = [os.path.join(raw_path, file) for file in os.listdir(raw_path)]
    os.makedirs(output_path, exist_ok=True)

    failed_files = convert_batch(files, output_path)

    # Record failed and suceeded files as text file
    failed_set = set(failed_files)
    all_set = set(files)
    succeed_set = all_set - failed_set
    write_list(files, all_txt_path)
    write_list(failed_files, failed_txt_path)
    write_list(list(succeed_set), succeed_txt_path)


def redo_failed():
    """Redo the files failed last time"""
    failed_files = [file.replace("\n", "") for file in open(failed_txt_path).readlines()]
    os.makedirs(failed_output_path, exist_ok=True)
    convert_batch(failed_files, failed_output_path, skip_existing=False)


def do_test():
    """Test a single file with debugging"""
    convert_batch([test_file], data_path, debug=True, skip_existing=False)
    show_midi(get_dest_midi_path(test_file, data_path))


def main():
    # do_batch()
    # redo_failed()
    do_test()


if __name__ == "__main__":
    main()
