import os
import csv
from typing import Union

import pandas as pd
from dbfread import DBF

import util.config

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


def get_dbf_columns(file: Union[str, os.PathLike]) -> list[str]:
    with DBF(file) as table:
        return table.field_names


def contains_default_cols(file: Union[str, os.PathLike]) -> bool:
    _, file_extension = os.path.splitext(file)
    if file_extension.upper() == ".CSV":
        file_cols = get_csv_columns(file)
    if file_extension.upper() == ".DBF":
        file_cols = get_dbf_columns(file)
    for col in util.config.input_cols():
        if col not in file_cols:
            return False
    return True
