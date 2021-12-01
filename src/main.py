import os

from music21.environment import get

from convert import convert_music21
from utils import get_dest_midi_path, show_midi, write_list

raw_path = "data/wikifonia"
output_path = "data/output"
test_file = "data/wikifonia/BryanWellsRonaldN.Miller-SomedayatChristmas.mxl"


def convert_batch(files: list, new_dir: str, debug=False, skip_existing=True):
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


def main():
    files = [os.path.join(raw_path, file) for file in os.listdir(raw_path)]
    os.makedirs(output_path, exist_ok=True)
    failed_files = convert_batch(files, output_path)

    failed_set = set(failed_files)
    all_set = set(files)
    succeed_set = all_set - failed_set
    write_list(files, "data/all.txt")
    write_list(failed_files, "data/failed.txt")
    write_list(list(succeed_set), "data/succeed.txt")

    # convert_batch([test_file], "data", debug=True, skip_existing=False)
    # show_midi(get_dest_midi_path(test_file, "data"))


if __name__ == "__main__":
    main()
