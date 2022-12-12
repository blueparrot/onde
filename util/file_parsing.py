import os
import csv
from typing import Union

import pandas as pd
from dbfread import DBF

import util.config

ABSOLUTE_PATH = os.path.dirname(__file__)
INPUT_FOLDER = os.path.join(ABSOLUTE_PATH, "..", "entrada")


def get_csv_dialect(file: Union[str, os.PathLike]) -> str:
    with open(file, "r") as csvfile:
        return csv.Sniffer().sniff(csvfile.readline())


def get_csv_columns(file: Union[str, os.PathLike]) -> list[str]:
    dialect = get_csv_dialect(file)
    separator = dialect.delimiter
    df = pd.read_csv(file, sep=separator, encoding_errors="ignore", nrows=1)
    return df.columns.to_list()


def get_dbf_columns(file: Union[str, os.PathLike]) -> list[str]:
    with DBF(file) as table:
        return table.field_names


def get_columns(file: Union[str, os.PathLike]) -> list[str]:
    _, file_extension = os.path.splitext(file)
    if file_extension.upper() == ".CSV":
        file_cols = get_csv_columns(file)
    if file_extension.upper() == ".DBF":
        file_cols = get_dbf_columns(file)
    return file_cols


def contains_output_cols(file: Union[str, os.PathLike]) -> bool:
    file_cols = get_columns(file)
    for col in file_cols:
        if col in ["REGIONAL", "AA", "QT", "BAIRRO", "X", "Y", "LOG_LGRD", "LOG_NUMR"]:
            return True
    return False


def contains_default_cols(file: Union[str, os.PathLike]) -> bool:
    file_cols = get_columns(file)
    for col in util.config.default_input_cols():
        if col not in file_cols:
            return False
    return True


def csv_streamer(file: Union[str, os.PathLike]):
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile, dialect=get_csv_dialect(file))
        for row in reader:
            yield (row)


def dbf_streamer(file: Union[str, os.PathLike]):
    with DBF(file) as table:
        for record in table:
            yield (dict(record))


def file_streamer(file: Union[str, os.PathLike]):
    _, file_extension = os.path.splitext(file)
    if file_extension.upper() == ".CSV":
        streamer = csv_streamer
    if file_extension.upper() == ".DBF":
        streamer = dbf_streamer
    return streamer(file)
