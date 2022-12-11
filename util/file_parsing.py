import os
import csv
import yaml
from typing import Union

import pandas as pd

ABSOLUTE_PATH = os.path.dirname(__file__)
INPUT_FOLDER = os.path.join(ABSOLUTE_PATH, "..", "entrada")


def get_csv_separator(file: Union[str, os.PathLike]) -> str:
    with open(file, "r") as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.readline())
        return dialect.delimiter


def get_csv_columns(file: Union[str, os.PathLike]) -> list[str]:
    separator = get_csv_separator(file)
    df = pd.read_csv(file, sep=separator, encoding_errors="ignore", nrows=1)
    return df.columns.to_list()


def contains_defaut_cols(file: Union[str, os.PathLike]) -> bool:
    file_cols = get_csv_columns(file)
    pass


if __name__ == "__main__":
    print(get_csv_columns(os.path.join(INPUT_FOLDER, "ansi.csv")))
