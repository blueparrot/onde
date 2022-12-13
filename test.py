import csv
import os
import pandas as pd

from geocode import geocode, geocode_file, SearchMode
import util.cli as cli
import util.file_parsing as fp
from util.config import datatypes_dict

ABSOLUTE_PATH = os.path.dirname(__file__)
ADDRESS_DATA = os.path.join(ABSOLUTE_PATH, "geodata", "base_enderecos.csv")
INPUT_FOLDER = os.path.join(ABSOLUTE_PATH, ".", "entrada")

if os.path.isfile(ADDRESS_DATA):
    sp = cli.spinner("Carregando base de endereços")
    sp.start()
    END = pd.read_csv(ADDRESS_DATA, sep=";", dtype=datatypes_dict())
    unique_streets = list(END["NOMELOGR"].sort_values().unique())
    sp.stop()

input_file = os.path.join(ABSOLUTE_PATH, ".", "entrada", "dengue_csv.csv")
geocode_file(
    END,
    unique_streets,
    file=input_file,
    col_street_code="NM_REFEREN",
    # col_street_code="--- AUSENTE NESTE ARQUIVO ---",
    col_street_cep="NU_CEP",
    # col_street_cep="--- AUSENTE NESTE ARQUIVO ---",
    # col_street_name="NM_LOGRADO",
    col_street_name="--- AUSENTE NESTE ARQUIVO ---",
    col_address_number="NU_NUMERO",
)
