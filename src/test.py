import os

from main import failed_txt_path
from utils import convert_batch, get_dest_midi_path, get_midi_messages, write_list

failed_output_path = "data/failed_output"
data_path = "data"
output_txt_path = "data/output.txt"
test_file = "data/wikifonia/A.HumeP.Livingstone-AGuidNewYear.mxl"


def redo_failed():
    """Redo the files failed last time"""
    failed_files = [file.replace("\n", "") for file in open(failed_txt_path).readlines()]
    os.makedirs(failed_output_path, exist_ok=True)
    convert_batch(failed_files, failed_output_path, skip_existing=False)


def do_test():
    """Test a single file with debugging"""
    convert_batch([test_file], data_path, debug=True, skip_existing=False)
    messages = get_midi_messages(get_dest_midi_path(test_file, data_path))
    write_list(messages, output_txt_path)


if __name__ == "__main__":
    do_test()
