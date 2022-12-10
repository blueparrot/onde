from enum import Enum, auto

import numpy as np
import pandas as pd
from thefuzz import fuzz, process

from util.street_names import standardize_street_names

MAX_ADDRESS_DELTA = 50  # Diferença máxima de numeração no imóvel a ser interpolado
FUZZ_CUTOFF = 90  # Diferença máxima no match pelo fuzzywuzzy
fuzz_cache = {}
empty_result = {
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


class SearchMode(Enum):
    BY_CODE = auto()
    BY_CEP = auto()
    BY_NAME = auto()


def clean_number(text: str) -> int:
    clean_text = [char for char in text if char.isdigit()]
    if len(clean_text) == 0:
        return 0
    return int("".join(clean_text))


# # Identifica os pontos de referência com maior e menor numeração
# p_max = pontos[pontos.NUM_IMOV == pontos.NUM_IMOV.max()]
# p_min = pontos[pontos.NUM_IMOV == pontos.NUM_IMOV.min()]
# # Calcula a diferença de numeração ente os pontos de referência
# delta_n = p_max.iloc[0]["NUM_IMOV"] - p_min.iloc[0]["NUM_IMOV"]
# # Se p_max é igual a p_min, retorna em branco
# if delta_n == 0:
#     return {"X": "", "Y": ""}
# # Converte as coordenadas para float e calcula as inclinações em que X e Y variam  de acordo com a variação
# # dos números dos imóveis. Em outras palavras, considera-se que a numeração dos imóveis seria o eixo horizontal
# # e as coordenadas de longitude ou latitude UTM seriam os eixos verticais em uma linha
# delta_x = float(p_max.iloc[0]["X"].replace(",", ".")) - float(
#     p_min.iloc[0]["X"].replace(",", ".")
# )
# delta_y = float(p_max.iloc[0]["Y"].replace(",", ".")) - float(
#     p_min.iloc[0]["Y"].replace(",", ".")
# )
# inc_x = delta_x / delta_n
# inc_y = delta_y / delta_n
# # Determina as coordenadas do imóvel procurado a partir do ponto de referência com menor numeração
# dist_n = num - p_min.iloc[0]["NUM_IMOV"]
# x = float(p_min.iloc[0]["X"].replace(",", ".")) + (dist_n * inc_x)
# y = float(p_min.iloc[0]["Y"].replace(",", ".")) + (dist_n * inc_y)
# # Converte as coordenadas novamente para formato string
# x_str = "{:.3f}".format(x).replace(".", ",")
# y_str = "{:.3f}".format(y).replace(".", ",")
# return {"X": x_str, "Y": y_str}


def geocode(
    address_data: pd.DataFrame,
    street_list: list[str],
    street: str,
    address_number: str,
    search_mode: SearchMode,
) -> dict[str, str]:
    result = empty_result

    def select_street_by_code(street_code: str) -> pd.DataFrame:
        log_street = "Loc. pelo código"
        return address_data[address_data["COD_LOGR"] == int(street_code)]

    def select_street_by_cep(street_cep: str) -> pd.DataFrame:
        log_street = "Loc. pelo CEP"
        return address_data[address_data["CEP"] == int(street_cep)]

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
        log_street = "Loc. pelo nome"
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
        result = empty_result
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
        print(
            ">>>>>>>>>>>>>>>>>",
            coordinates["X"],
            type(coordinates["X"]),
            coordinates["Y"],
            type(coordinates["Y"]),
        )
        result["X"], result["Y"] = [coordinates["X"]], [coordinates["Y"]]
        result["LOG_NUMR"] = ["End. aproximado"]
        return result

    if search_mode == SearchMode.BY_CODE:
        street_selection = select_street_by_code(street)
        if len(street_selection) > 0:
            log_street = ["Loc. pelo código"]
    if search_mode == SearchMode.BY_CEP:
        street_selection = select_street_by_cep(street)
        if len(street_selection) > 0:
            log_street = ["Loc. pelo CEP"]
    if search_mode == SearchMode.BY_NAME:
        street_selection = select_street_by_name(street)
        if len(street_selection) > 0:
            log_street = ["Loc. pelo nome"]
    if len(street_selection) == 0:
        return {key: str(value[0]) for key, value in empty_result.items()}

    address_number = clean_number(address_number)
    located_address = street_selection[street_selection["NUM_IMOV"] == address_number]
    if len(located_address) > 0:
        result = located_address.to_dict(orient="list")
        result["LOG_LGRD"] = log_street
        result["LOG_NUMR"] = ["End. oficial"]
    else:
        result = interpolate_position()
        result["LOG_LGRD"] = log_street
    return {key: str(value[0]) for key, value in result.items()}
