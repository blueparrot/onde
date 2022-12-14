import os
import csv
from typing import Union, Iterator

import pandas as pd
import chardet
from dbfread import DBF

import util.config

ABSOLUTE_PATH = os.path.dirname(__file__)
INPUT_FOLDER = os.path.join(ABSOLUTE_PATH, "..", "entrada")


def get_csv_separator(file: Union[str, os.PathLike]) -> str:
    with open(file, "r") as csvfile:
        return csv.Sniffer().sniff(csvfile.readline()).delimiter


def get_csv_encoding(file: Union[str, os.PathLike]) -> str:
    with open(file, "rb") as rawdata:
        result = chardet.detect(rawdata.read(100000))
        return result["encoding"]


def get_csv_columns(file: Union[str, os.PathLike]) -> list[str]:
    column_names = []
    with open(file, encoding=get_csv_encoding(file)) as csvfile:
        reader = csv.reader(csvfile, delimiter=get_csv_separator(file))
        for row in reader:
            column_names.append(row)
            break
        return column_names[0]


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


def csv_streamer(file: Union[str, os.PathLike]) -> Iterator[dict[str, str]]:
    with open(file, encoding=get_csv_encoding(file)) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=get_csv_separator(file))
        for row in reader:
            yield (row)


def dbf_streamer(file: Union[str, os.PathLike]) -> Iterator[dict[str, str]]:
    with DBF(file, encoding="iso-8859-1") as table:
        for record in table:
            yield (dict(record))


def file_streamer(file: Union[str, os.PathLike]) -> Iterator[dict[str, str]]:
    _, file_extension = os.path.splitext(file)
    if file_extension.upper() == ".CSV":
        streamer = csv_streamer
    if file_extension.upper() == ".DBF":
        streamer = dbf_streamer
    return streamer(file)
