import pandas as pd
from enum import Enum, auto

from thefuzz import fuzz, process
from util.street_names import standardize_street_names

LIMITE_NUMERO = 50  # Diferença máxima de numeração no imóvel a ser interpolado
FUZZ_CUTOFF = 90  # Diferença máxima no match pelo fuzzywuzzy
fuzz_cache = {}


class SearchMode(Enum):
    BY_CODE = auto()
    BY_CEP = auto()
    BY_NAME = auto()


def clean_number(text: str) -> int:
    clean_text = [char for char in text if char.isdigit()]
    if len(clean_text) == 0:
        return 0
    return int("".join(clean_text))


def geocode(
    address_data: pd.DataFrame,
    street_list: list[str],
    street: str,
    address_number: str,
    search_mode: SearchMode,
) -> dict[str, str]:
    log_street = "Não localizado"
    log_address = "Não localizado"

    def select_street_by_code(
        street_code: str, df: pd.DataFrame = address_data
    ) -> pd.DataFrame:
        log_street = "Loc. pelo código"
        return df[df["COD_LOGR"] == int(street_code)]

    def select_street_by_cep(
        street_cep: str, df: pd.DataFrame = address_data
    ) -> pd.DataFrame:
        log_street = "Loc. pelo CEP"
        return df[df["CEP"] == int(street_cep)]

    def select_street_by_name(
        street_name: str, df: pd.DataFrame = address_data
    ) -> pd.DataFrame:
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
                return pd.DataFrame(columns=df.columns)
            street_match = street_match[0]
        fuzz_cache[street_name] = street_match
        log_street = "Loc. pelo nome"
        return df[df["NOMELOGR"] == street_match]

    def get_closest_neighbours(
        address_number: int, street_selection: pd.DataFrame
    ) -> pd.DataFrame:
        odd_even = 0 if address_number % 2 == 0 else 1
        same_side_of_street = street_selection.loc[
            street_selection["NUM_IMOV"].mod(2).eq(odd_even), :
        ]
        return same_side_of_street.iloc[
            (same_side_of_street["NUM_IMOV"] - address_number).abs().argsort()[:2]
        ]

    def interpolate_position():
        pass

    if search_mode == SearchMode.BY_CODE:
        street_selection = select_street_by_code(street, address_data)
        if len(street_selection) > 0:
            log_street = "Loc. pelo código"
    if search_mode == SearchMode.BY_CEP:
        street_selection = select_street_by_cep(street, address_data)
        if len(street_selection) > 0:
            log_street = "Loc. pelo CEP"
    if search_mode == SearchMode.BY_NAME:
        street_selection = select_street_by_name(street, address_data)
        if len(street_selection) > 0:
            log_street = "Loc. pelo nome"

    address_number = clean_number(address_number)
    located_address = street_selection[street_selection["NUM_IMOV"] == address_number]
    if len(located_address) > 0:
        log_address = "End. oficial"
        result = located_address.to_dict(orient="list")
        result["GEO_LOGR"] = log_street
        result["GEO_END"] = log_address
        return result
    else:
        closest_neighbours = get_closest_neighbours(address_number, street_selection)
        if len(closest_neighbours) < 2:
            return "Poucos vizinhos"
        return closest_neighbours.to_dict(orient="list")


def geocode_old(df, logradouro, num, area=None, modo="nome"):
    """
    Localiza as coordenadas geográficas de um dado endereço

    Parâmetros:

    - df : DataFrame Pandas contendo todos os endereços
    - logradouro : Nome do logradouro do endereço a ser localizado
    - num : Número do endereço a ser localizado
    - area (opcional) : Se informado, este parâmetro restringe a busca a uma determinada área
        Deve ser um "tuple" no formato: ('COLUNA DO BANCO A SER USADA COMO FILTRO','VALOR A SER SELECIONADO')
        Caso este parâmetro não seja informado, a busca é realizada em todo o banco
    - modo: método pelo qual os logradouros serão identificados, com as opções abaixo
        > nome (padrão): pesquisa pelo nome do logradouro, buscando o nome mais próximo se não houver correspondência exata
        > codigo : busca o código de logradouro, aceitando apenas correspondência exata
        > cep : busca o CEP, aceitando apenas correspondência exata

    ID_LOGRADO
    NOMELOGR
    CEP

    """

    def interpolar(num, pontos):
        """
        Interpola as coordenadas geográficas de um endereço a partir dos imóveis mais próximos a ele.
        A função toma partido do fato de que as coordenadas do pontos de referência estão em formato UTM
        e faz o cálculo através de geometria básica.

        Parâmetros:

        - num : Número do endereço a ser localizado
        - pontos : Endereços, no mesmo logradouro e de mesma paridade, que estejam mais próximos da numeração buscada
        """
        # Identifica os pontos de referência com maior e menor numeração
        p_max = pontos[pontos.NUM_IMOV == pontos.NUM_IMOV.max()]
        p_min = pontos[pontos.NUM_IMOV == pontos.NUM_IMOV.min()]
        # Calcula a diferença de numeração ente os pontos de referência
        delta_n = p_max.iloc[0]["NUM_IMOV"] - p_min.iloc[0]["NUM_IMOV"]
        # Se p_max é igual a p_min, retorna em branco
        if delta_n == 0:
            return {"X": "", "Y": ""}
        # Converte as coordenadas para float e calcula as inclinações em que X e Y variam  de acordo com a variação
        # dos números dos imóveis. Em outras palavras, considera-se que a numeração dos imóveis seria o eixo horizontal
        # e as coordenadas de longitude ou latitude UTM seriam os eixos verticais em uma linha
        delta_x = float(p_max.iloc[0]["X"].replace(",", ".")) - float(
            p_min.iloc[0]["X"].replace(",", ".")
        )
        delta_y = float(p_max.iloc[0]["Y"].replace(",", ".")) - float(
            p_min.iloc[0]["Y"].replace(",", ".")
        )
        inc_x = delta_x / delta_n
        inc_y = delta_y / delta_n
        # Determina as coordenadas do imóvel procurado a partir do ponto de referência com menor numeração
        dist_n = num - p_min.iloc[0]["NUM_IMOV"]
        x = float(p_min.iloc[0]["X"].replace(",", ".")) + (dist_n * inc_x)
        y = float(p_min.iloc[0]["Y"].replace(",", ".")) + (dist_n * inc_y)
        # Converte as coordenadas novamente para formato string
        x_str = "{:.3f}".format(x).replace(".", ",")
        y_str = "{:.3f}".format(y).replace(".", ",")
        return {"X": x_str, "Y": y_str}

    # Retorna coordenadas em branco se o número não for inteiro
    try:
        num = int(num)
    except:
        return {"X": "", "Y": "", "GEOLOG": "NUMERO INEXISTENTE"}

    # Restringe busca a uma área, que pode ser qualquer coluna do banco de dados
    if area != None:
        area_selecionada = df[(df[area[0]] == area[1])]
    else:
        area_selecionada = df

    # Determina o modo de busca de logradouros
    if modo == "nome":
        logradouro = standardize_street_names(logradouro)
        logradouro_selecionado = area_selecionada[
            (area_selecionada["NOMELOGR"] == logradouro)
        ]
    else:
        try:
            logradouro = int(logradouro)
        except:
            return {"X": "", "Y": "", "GEOLOG": "LOGRADOURO NAO ENCONTRADO"}
    if modo == "codigo":
        logradouro_selecionado = area_selecionada[
            (area_selecionada["ID_LOGRADO"] == logradouro)
        ]
    if modo == "cep":
        logradouro_selecionado = area_selecionada[
            (area_selecionada["CEP"] == logradouro)
        ]

    texto_log = "LOGRADOURO EXATO / "  # Valor padrão, pode ser alterado abaixo

    # Determina o que retornar quanto não há correspondência exata para o logradouro
    if len(logradouro_selecionado) == 0:
        # Se modo de busca for por CEP ou código de logradouro, retorna em branco
        if modo != "nome":
            return {"X": "", "Y": "", "GEOLOG": "LOGRADOURO NAO ENCONTRADO"}
        # Quando a busca é pelo nome do logradouro, tenta fazer aproximação
        lista_logradouros = area_selecionada["NOMELOGR"].tolist()
        logradouro_aproximado = process.extractOne(
            logradouro, choices=lista_logradouros, score_cutoff=FUZZ_CUTOFF
        )
        if logradouro_aproximado == None:
            return {"X": "", "Y": "", "GEOLOG": "LOGRADOURO NAO ENCONTRADO"}
        else:
            logradouro_selecionado = area_selecionada[
                (area_selecionada["NOMELOGR"] == logradouro_aproximado[0])
            ]
            texto_log = "LOGRADOURO APROXIMADO / "

    # Busca o número do imóvel
    selecao_imoveis = logradouro_selecionado[logradouro_selecionado["NUM_IMOV"] == num]
    if (
        len(selecao_imoveis) > 0
    ):  # Correspondência exata encontrada para o número do imóvel
        return {
            "REGIONAL": selecao_imoveis.iloc[0]["REGIONAL"],
            "AA": selecao_imoveis.iloc[0]["AA"],
            "X": selecao_imoveis.iloc[0]["X"],
            "Y": selecao_imoveis.iloc[0]["Y"],
            "GEOLOG": texto_log + "NUMERO EXATO",
        }
    else:
        # Não houve correspondência exata, tenta interpolar
        # Encontra os dois números de mesma paridade mais próximos
        num_par = True if (num % 2) == 0 else False
        selecao_imoveis = logradouro_selecionado[
            logradouro_selecionado["PAR"] == num_par
        ]
        proximos = selecao_imoveis.iloc[
            (selecao_imoveis["NUM_IMOV"] - num).abs().argsort()[:2]
        ]
        if len(proximos) < 2:
            # Retorna coordenadas em branco se não houver ao menos 2 imóveis para interpolar
            return {
                "REGIONAL": "",
                "AA": "",
                "X": "",
                "Y": "",
                "GEOLOG": texto_log + "POUCOS PARAMETROS PARA INTERPOLACAO",
            }
        elif (abs(proximos.iloc[0]["NUM_IMOV"] - num) > LIMITE_NUMERO) or (
            abs(proximos.iloc[1]["NUM_IMOV"] - num) > LIMITE_NUMERO
        ):
            # Retorna coordenadas em branco se a numeração for muito distante dos mais próximos
            return {"X": "", "Y": "", "GEOLOG": texto_log + "NUMERO MUITO DISTANTE"}
        else:
            # Interpola coordenadas do imóvel com base em sua numeração e imóveis de mesma paridade mais próximos
            val = interpolar(num, proximos)
            if (val["X"] == "") or (val["Y"] == ""):
                return {"X": "", "Y": "", "GEOLOG": texto_log + "NUMERO NAO ENCONTRADO"}
            else:
                return {
                    "X": val["X"],
                    "Y": val["Y"],
                    "GEOLOG": texto_log + "NUMERO INTERPOLADO",
                }
