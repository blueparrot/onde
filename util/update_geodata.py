import gc
import os
import requests
from datetime import datetime
from typing import Union

import geopandas as gpd
import colorama as color
from owslib.wfs import WebFeatureService

import util.config
import util.cli as cli
from util.street_names import standardize_street_names

ABSOLUTE_PATH = os.path.dirname(__file__)
GEODATA_FOLDER = os.path.join(ABSOLUTE_PATH, "..", "geodata")
SPINNER_STOP_SYMBOL = color.Fore.GREEN + "  v" + color.Fore.RESET

server_configuration = util.config.server()
layer_configuration = util.config.layers()


def update_shapefiles(
    output_folder: Union[str, os.PathLike], layer_configuration
) -> None:
    """
    Downloads shapefiles from a WFS server
    """

    wfs = WebFeatureService(
        url=server_configuration["wfs_server"],
        version=server_configuration["wfs_version"],
        timeout=300,
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
                + f" foi atualizada em {mod_date}.\nAtualizar novamente? "
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

    for layer in layer_configuration.values():
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
    cli.print_title("DOWNLOAD DE CAMADAS DO SERVIDOR WFS")

    try:
        update_shapefiles(GEODATA_FOLDER, layer_configuration)
    except requests.exceptions.Timeout:
        print(
            color.Fore.RED
            + "Falha de conexão com o servidor WFS. Tente novamente mais tarde."
        )

    cli.print_title("PROCESSAMENTO DOS DADOS GEOGRÁFICOS")

    # Links addresses to areas
    aa = gdf_loader(
        file=os.path.join(GEODATA_FOLDER, layer_configuration["AA"]["arquivo"]),
        cols_dict=layer_configuration["AA"]["colunas"],
    )
    end_raw = gdf_loader(
        file=os.path.join(GEODATA_FOLDER, layer_configuration["END"]["arquivo"]),
        cols_dict=layer_configuration["END"]["colunas"],
    )
    end_aa = spatial_join(end_raw, aa, f"Associando endereços a áreas de abrangência")
    del [[end_raw, aa]]
    gc.collect()
    end_aa.drop(["index_right"], axis=1, inplace=True)

    # Links addresses to city blocks
    qt = gdf_loader(
        file=os.path.join(GEODATA_FOLDER, layer_configuration["QT"]["arquivo"]),
        cols_dict=layer_configuration["QT"]["colunas"],
    )
    end = spatial_join(end_aa, qt, f"Associando endereços a quarteirões")
    del [[end_aa, qt]]
    gc.collect()
    end.drop(["index_right"], axis=1, inplace=True)

    # Rearrange data
    end = end.loc[:, util.config.old_col_names()]
    end.columns = util.config.new_col_names()

    # Drop empty values or duplicates
    end.dropna(how="any", inplace=True)
    end.drop_duplicates(subset=["COD_LOGR", "NUM_IMOV"], inplace=True)

    # Convert datatypes
    sp = cli.spinner("Convertendo dados")
    sp.start()
    for col, datatype in zip(util.config.new_col_names(), util.config.datatypes_list()):
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
        lambda row: standardize_street_names(row["NOMELOGR"]), axis=1
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
