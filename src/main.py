import os
from glob import glob

from utils import convert_batch

raw_path = "data/wikifonia"
output_path = "data/output"


def main():
    """Convert the whole dataset"""
    files = glob(raw_path + "/*.mxl")
    os.makedirs(output_path, exist_ok=True)

    convert_batch(files, output_path)


if __name__ == "__main__":
    main()
