import gc
import os
import requests
import yaml
from datetime import datetime
from typing import Union

# import pygeos
import geopandas as gpd
import colorama as color
from owslib.wfs import WebFeatureService

import util.cli as cli
from util.logradouro import padronizar_logradouro

# gpd.options.use_pygeos = True
ABSOLUTE_PATH = os.path.dirname(__file__)
GEODATA_FOLDER = os.path.join(ABSOLUTE_PATH, "..", "geodata")
YAML_FILE = os.path.join(ABSOLUTE_PATH, "geodata.yaml")
SPINNER_STOP_SYMBOL = color.Fore.GREEN + "  v" + color.Fore.RESET


def update_shapefiles(output_folder: Union[str, os.PathLike], config) -> None:
    """
    Downloads shapefiles from a WFS server
    """

    wfs = WebFeatureService(
        url="http://bhmap.pbh.gov.br/v2/api/idebhgeo/wfs", version="1.1.0", timeout=300
    )

    def save_file(
        filename: str, wfs_layer: str, output_folder: Union[str, os.PathLike]
    ) -> None:
        output_file = os.path.join(output_folder, filename)
        if os.path.isfile(output_file):
            mod_date = datetime.utcfromtimestamp(
                os.path.getmtime(output_file)
            ).strftime("%d/%m/%Y")
            print(
                "A camada "
                + color.Fore.GREEN
                + color.Style.BRIGHT
                + f"{filename[:-4]}"
                + color.Fore.RESET
                + f" foi atualizada em {mod_date}. Atualizar novamente? "
            )
            if cli.options("SIM", "NÃO") == "NÃO":
                print(
                    color.Fore.GREEN
                    + "Atualização dispensada para a camada "
                    + color.Fore.GREEN
                    + color.Style.BRIGHT
                    + f"{filename[:-4]}\n"
                )
                return

        sp = cli.spinner(f"Baixando camada {filename[:-4]}")
        sp.start()
        response = wfs.getfeature(typename=wfs_layer, outputFormat="shape-zip")
        with open(output_file, "wb") as w:
            w.write(bytes(response.read()))
        sp.stop_and_persist(symbol=SPINNER_STOP_SYMBOL)
        print(
            color.Fore.GREEN
            + "Camada "
            + color.Fore.GREEN
            + color.Style.BRIGHT
            + f"{filename[:-4]}"
            + color.Fore.GREEN
            + color.Style.NORMAL
            + " atualizada com sucesso\n"
        )

    for layer in config.values():
        save_file(layer["arquivo"], layer["camada_wfs"], output_folder)


def gdf_loader(file, cols_dict):
    """
    Presets for the "read_file" method in the GeoPandas module,
    with the option to specify the columns to be INCLUDED
    """
    include_cols = [c["nome_original"] for c in cols_dict]
    sp = cli.spinner(
        f"Carregando camada {os.path.basename(file)[:-4]} do disco para a memória"
    )
    sp.start()
    gdf_sample = gpd.read_file(file, rows=1)
    all_cols = list(gdf_sample.columns)
    include_cols.append("geometry")
    for col in include_cols:
        if col not in all_cols:
            raise KeyError(
                f"Coluna *{col}* não encontrada em {os.path.basename(file)}. Checar possível mudança de nomenclatura."
            )
    exclude_cols = [c for c in all_cols if c not in include_cols]
    gdf = gpd.read_file(file, ignore_fields=exclude_cols)
    sp.stop_and_persist(symbol=SPINNER_STOP_SYMBOL)
    return gdf


def spatial_join(gdf_points, gdf_polygons, text=""):
    """
    Presets for the "sjoin" method in the GeoPandas module
    """
    sp = cli.spinner(text)
    sp.start()
    gdf = gpd.sjoin(
        gdf_points,
        gdf_polygons,
        how="inner",
    )
    gdf.dropna(how="any", inplace=True)
    sp.stop_and_persist(symbol=SPINNER_STOP_SYMBOL)
    return gdf


def update_all() -> None:
    """
    Main function
    """
    if not os.path.exists(GEODATA_FOLDER):
        os.makedirs(GEODATA_FOLDER)

    os.system("cls" if os.name == "nt" else "clear")
    color.init(autoreset=True)

    with open(YAML_FILE, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    cli.print_title("DOWNLOAD DE CAMADAS DO SERVIDOR WFS")

    try:
        update_shapefiles(GEODATA_FOLDER, config)
    except requests.exceptions.Timeout:
        print(
            color.Fore.RED
            + "Falha de conexão com o servidor WFS. Tente novamente mais tarde."
        )

    cli.print_title("PROCESSAMENTO DOS DADOS GEOGRÁFICOS")

    # Links addresses to areas
    aa = gdf_loader(
        file=os.path.join(GEODATA_FOLDER, config["AA"]["arquivo"]),
        cols_dict=config["AA"]["colunas"],
    )
    end_raw = gdf_loader(
        file=os.path.join(GEODATA_FOLDER, config["END"]["arquivo"]),
        cols_dict=config["END"]["colunas"],
    )
    end_aa = spatial_join(end_raw, aa, f"Associando endereços a áreas de abrangência")
    del [[end_raw, aa]]
    gc.collect()
    end_aa.drop(["index_right"], axis=1, inplace=True)

    # Links addresses to city blocks
    qt = gdf_loader(
        file=os.path.join(GEODATA_FOLDER, config["QT"]["arquivo"]),
        cols_dict=config["QT"]["colunas"],
    )
    end = spatial_join(end_aa, qt, f"Associando endereços a quarteirões")
    del [[end_aa, qt]]
    gc.collect()
    end.drop(["index_right"], axis=1, inplace=True)

    # Rearrange data
    cols_tuples = sorted(
        [
            (c["ordem"], c["nome_original"], c["renomear_para"], c["datatype"])
            for col in [layer["colunas"] for layer in config.values()]
            for c in col
        ]
    )
    cols_old_names = [e[1] for e in cols_tuples] + ["geometry"]
    cols_new_names = [e[2] for e in cols_tuples] + ["geometry"]
    cols_datatypes = [e[3] for e in cols_tuples]
    end = end.loc[:, cols_old_names]
    end.columns = cols_new_names

    # Drop empty values or duplicates
    end.dropna(how="any", inplace=True)
    end.drop_duplicates(subset=["COD_LOGR", "NUM_IMOV"], inplace=True)

    # Convert datatypes
    sp = cli.spinner("Convertendo dados")
    sp.start()
    for col, datatype in zip(cols_new_names, cols_datatypes):
        if datatype != "str":
            end[col] = end[col].astype(datatype)
    sp.stop_and_persist(symbol=SPINNER_STOP_SYMBOL)

    # Cast coordinates to text columns
    sp = cli.spinner("Extraindo coordenadas X e Y da geometria")
    sp.start()
    end["X"] = end["geometry"].x.round(0).astype(int)
    end["Y"] = end["geometry"].y.round(0).astype(int)
    end.drop(["geometry"], axis=1, inplace=True)
    sp.stop_and_persist(symbol=SPINNER_STOP_SYMBOL)

    # Standardization of street names
    sp = cli.spinner("Padronizando nomes de logradouros")
    sp.start()
    end["NOMELOGR"] = end.apply(
        lambda row: padronizar_logradouro(row["NOMELOGR"]), axis=1
    )
    sp.stop_and_persist(symbol=SPINNER_STOP_SYMBOL)

    # Sort data and save to CSV
    sp = cli.spinner("Salvando base de endereços processada")
    sp.start()
    end.sort_values(by=["COD_LOGR", "NUM_IMOV"], inplace=True)
    end.reset_index(drop=True, inplace=True)
    end.to_csv(os.path.join(GEODATA_FOLDER, "base_enderecos.csv"), index=False, sep=";")
    sp.stop_and_persist(symbol=SPINNER_STOP_SYMBOL)

    # Try to clean memory
    del [[end]]
    gc.collect()

    print(
        color.Fore.GREEN
        + color.Style.BRIGHT
        + "Dados geográficos atualizados com sucesso!"
        + color.Fore.RESET
    )
    color.deinit()
    input("\nPressione <ENTER> para retornar ao menu inicial...")


if __name__ == "__main__":
    update_all()
