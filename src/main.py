import os

from utils import convert_batch, write_list

raw_path = "data/wikifonia"
output_path = "data/output"
failed_txt_path = "data/failed.txt"
all_txt_path = "data/all.txt"
succeed_txt_path = "data/succeed.txt"


def main():
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


if __name__ == "__main__":
    main()
