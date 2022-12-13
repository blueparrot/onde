import csv
import os
import time
from enum import Enum, auto
from typing import Union

import pandas as pd
import colorama as color
from thefuzz import fuzz, process

import util.cli as cli
import util.file_parsing as fp
from util.street_names import standardize_street_names


MAX_ADDRESS_DELTA = 50
FUZZ_CUTOFF = 90
fuzz_cache = {}
ABSOLUTE_PATH = os.path.dirname(__file__)
OUTPUT_FOLDER = os.path.join(ABSOLUTE_PATH, "resultado")
OUTPUT_ENCODING = "cp1252"
SPINNER_STOP_SYMBOL = color.Fore.GREEN + "  v" + color.Fore.RESET

output_columns = [
    "REGIONAL",
    "AA",
    "QT",
    "BAIRRO",
    "X",
    "Y",
    "LOG_LGRD",
    "LOG_NUMR",
]


class SearchMode(Enum):
    BY_CODE = auto()
    BY_CEP = auto()
    BY_NAME = auto()


def clean_number(text: str) -> int:
    clean_text = [char for char in text if char.isdigit()]
    if len(clean_text) == 0:
        return 0
    return int("".join(clean_text))


def join_result(row: dict[str, str], geocode_result: dict[str, str]) -> list[str]:
    left_side = {}
    right_side = {}
    for key, value in row.items():
        if key not in output_columns:
            left_side[key] = value
    for key, value in geocode_result.items():
        if key in output_columns:
            right_side[key] = value
    merge = left_side | right_side
    return list(merge.values())


def geocode(
    address_data: pd.DataFrame,
    street_list: list[str],
    street: str,
    address_number: str,
    search_mode: SearchMode,
) -> dict[str, str]:
    result = {
        "REGIONAL": [""],
        "AA": [""],
        "QT": [""],
        "CEP": [""],
        "COD_LOGR": [""],
        "TIPOLOGR": [""],
        "NOMELOGR": [""],
        "NUM_IMOV": [""],
        "BAIRRO": [""],
        "X": [""],
        "Y": [""],
        "LOG_LGRD": ["Não localizado"],
        "LOG_NUMR": ["Não localizado"],
    }

    def select_street_by_code(street_code: str) -> pd.DataFrame:
        return address_data[address_data["COD_LOGR"] == clean_number(street_code)]

    def select_street_by_cep(street_cep: str) -> pd.DataFrame:
        return address_data[address_data["CEP"] == clean_number(street_cep)]

    def select_street_by_name(street_name: str) -> pd.DataFrame:
        if street_name in fuzz_cache:
            street_match = fuzz_cache[street_name]
        else:
            street_match = process.extractOne(
                standardize_street_names(street_name),
                street_list,
                scorer=fuzz.token_sort_ratio,
                score_cutoff=FUZZ_CUTOFF,
            )
            if street_match is None:
                return pd.DataFrame(columns=address_data.columns)
            street_match = street_match[0]
        fuzz_cache[street_name] = street_match
        return address_data[address_data["NOMELOGR"] == street_match]

    def get_closest_neighbours(
        address_number: int, street_selection: pd.DataFrame
    ) -> pd.DataFrame:
        odd_even = 0 if address_number % 2 == 0 else 1
        same_side_of_street = street_selection.loc[
            street_selection["NUM_IMOV"].mod(2).eq(odd_even), :
        ]
        return same_side_of_street.iloc[
            (same_side_of_street["NUM_IMOV"] - address_number).abs().argsort().iloc[:2]
        ]

    def linear_regression(
        address_number: int, neighbours: pd.DataFrame
    ) -> dict[str, str]:
        # Assumes that the address data is sorted, which it is
        address_smaller = neighbours.iloc[0, :]
        address_bigger = neighbours.iloc[1, :]

        delta_neighbours = float(
            address_bigger["NUM_IMOV"] - address_smaller["NUM_IMOV"]
        )
        if delta_neighbours == 0.0:
            return {"X": "", "Y": ""}
        delta_x = float(address_bigger["X"] - address_smaller["X"])
        delta_y = float(address_bigger["Y"] - address_smaller["Y"])
        slope_x = delta_x / delta_neighbours
        slope_y = delta_y / delta_neighbours
        delta_address = float(address_number - address_smaller["NUM_IMOV"])
        x_float = float(address_smaller["X"]) + (delta_address * slope_x)
        y_float = float(address_smaller["Y"]) + (delta_address * slope_y)
        x_str = str(int(round(x_float, 0)))
        y_str = str(int(round(y_float, 0)))
        return {"X": x_str, "Y": y_str}

    def interpolate_position() -> dict[str, str]:
        closest_neighbours = get_closest_neighbours(address_number, street_selection)

        if any(
            abs(closest_neighbours["NUM_IMOV"] - address_number) > MAX_ADDRESS_DELTA
        ):
            return result

        if len(closest_neighbours) < 2:
            return result
        result["NUM_IMOV"] = [address_number]

        for col in [
            "REGIONAL",
            "AA",
            "QT",
            "CEP",
            "COD_LOGR",
            "TIPOLOGR",
            "NOMELOGR",
            "BAIRRO",
        ]:
            if closest_neighbours.iloc[0, :][col] == closest_neighbours.iloc[1, :][col]:
                result[col] = [closest_neighbours.iloc[0, :][col]]
            else:
                result[col] = ["Indeterminado"]

        coordinates = linear_regression(address_number, closest_neighbours)
        result["X"], result["Y"] = [coordinates["X"]], [coordinates["Y"]]
        result["LOG_NUMR"] = ["End. aproximado"]
        return result

    if search_mode == SearchMode.BY_CODE:
        street_selection = select_street_by_code(street)
        if len(street_selection) > 0:
            result["LOG_LGRD"] = ["Loc. pelo código"]
    if search_mode == SearchMode.BY_CEP:
        street_selection = select_street_by_cep(street)
        if len(street_selection) > 0:
            result["LOG_LGRD"] = ["Loc. pelo CEP"]
    if search_mode == SearchMode.BY_NAME:
        street_selection = select_street_by_name(street)
        if len(street_selection) > 0:
            result["LOG_LGRD"] = ["Loc. pelo nome"]
    if len(street_selection) == 0:
        return {key: str(value[0]) for key, value in result.items()}

    address_number = clean_number(address_number)
    located_address = street_selection[street_selection["NUM_IMOV"] == address_number]
    if len(located_address) > 0:
        for key, value in located_address.to_dict(orient="list").items():
            result[key] = value
        result["LOG_NUMR"] = ["End. oficial"]
    else:
        result = interpolate_position()
    return {key: str(value[0]) for key, value in result.items()}


def geocode_file(
    address_data: pd.DataFrame,
    street_list: list[str],
    file: Union[str, os.PathLike] = None,
    col_street_code: str = None,
    col_street_cep: str = None,
    col_street_name: str = None,
    col_address_number: str = None,
) -> dict[str, int]:
    start_time = time.perf_counter()
    not_found_pool = []

    # Determine geocoding order
    street_identifiers = {
        SearchMode.BY_CODE: (col_street_code, "código de logradouro"),
        SearchMode.BY_CEP: (col_street_cep, "CEP"),
        SearchMode.BY_NAME: (col_street_name, "nome de logradouro"),
    }
    search_order = [
        (mode, col)
        for mode, col in street_identifiers.items()
        if col[0] != "--- AUSENTE NESTE ARQUIVO ---"
    ]

    # Set output filename
    basename, _ = os.path.splitext(os.path.basename(file))
    output_file = os.path.join(OUTPUT_FOLDER, basename + ".csv")

    # Initiate csv output
    with open(output_file, "w", newline="", encoding=OUTPUT_ENCODING) as csvfile:
        stream = csv.writer(csvfile, delimiter=";")
        column_names = [
            name for name in fp.get_columns(file) if name not in output_columns
        ]
        column_names.extend(output_columns)
        stream.writerow(column_names)

        # Call geocoding steps
        first_round = True
        for step in search_order:
            step_mode, step_column = step
            if first_round:
                first_round = False
                file_streamer = fp.file_streamer(file)
                sp = cli.spinner(f"Pesquisando endereços por {step_column[1]}")
                sp.start()
                for row in file_streamer:
                    result = geocode(
                        address_data,
                        street_list,
                        row[step_column[0]],
                        row[col_address_number],
                        step_mode,
                    )
                    if result["LOG_LGRD"] != "Não localizado":
                        stream.writerow(join_result(row, result))
                    else:
                        not_found_pool.append(row)
                sp.stop_and_persist(symbol=SPINNER_STOP_SYMBOL)
            elif len(not_found_pool) > 0:
                sp = cli.spinner(
                    f"Pesquisando endereços remanescentes por {step_column[1]}"
                )
                sp.start()
                for row in not_found_pool:
                    result = geocode(
                        address_data,
                        street_list,
                        row[step_column[0]],
                        row[col_address_number],
                        step_mode,
                    )
                    if result["LOG_LGRD"] != "Não localizado":
                        stream.writerow(join_result(row, result))
                        not_found_pool.remove(row)
                sp.stop_and_persist(symbol=SPINNER_STOP_SYMBOL)
            else:
                break

        # Put the rows in "not_found_pool" back to the output
        result_not_found = {
            "REGIONAL": "",
            "AA": "",
            "QT": "",
            "BAIRRO": "",
            "X": "",
            "Y": "",
            "LOG_LGRD": "Não localizado",
            "LOG_NUMR": "Não localizado",
        }
        for row in not_found_pool:
            stream.writerow(join_result(row, result_not_found))
    end_time = time.perf_counter()
    elapsed_time = round(end_time - start_time, ndigits=1)

    # Get statistics about geocoding results
    result_df = pd.read_csv(
        output_file,
        encoding=OUTPUT_ENCODING,
        sep=";",
        usecols=["LOG_LGRD", "LOG_NUMR"],
        dtype="category",
    )
    streets_found = result_df["LOG_LGRD"].value_counts().to_dict()
    addresses_found = result_df["LOG_NUMR"].value_counts().to_dict()
    total_addresses = result_df["LOG_NUMR"].count()
    total_found = result_df[result_df["LOG_NUMR"] != "Não localizado"][
        "LOG_NUMR"
    ].count()
    stats = {
        "LOCALIZAÇÃO DOS LOGRADOUROS": streets_found,
        "LOCALIZAÇÃO DOS ENDEREÇOS": addresses_found,
        "ENDEREÇOS GEOCODIFICADOS": total_found,
        "TOTAL DE ENDEREÇOS": total_addresses,
        "TAXA DE SUCESSO": round(100 * total_found / total_addresses, ndigits=1),
        "TEMPO DE PROCESSAMENTO (segundos)": elapsed_time,
    }

    # Save statistics to text file
    stats_text = ""
    for key, value in stats.items():
        stats_text = (
            stats_text
            + key
            + ": "
            + str(value).replace("{", "\n  - ").replace(",", "\n  - ").replace("}", "")
            + "\n\n"
        )
    stats_file = os.path.join(OUTPUT_FOLDER, basename + "_log.txt")
    with open(stats_file, "w") as f:
        f.write(stats_text)

    return stats
