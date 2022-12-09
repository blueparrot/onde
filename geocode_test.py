import os
import pandas as pd

from geocode import geocode, SearchMode
import util.cli as cli
from util.config import datatypes_dict

ABSOLUTE_PATH = os.path.dirname(__file__)
ADDRESS_DATA = os.path.join(ABSOLUTE_PATH, "geodata", "base_enderecos.csv")

if os.path.isfile(ADDRESS_DATA):
    sp = cli.spinner("Carregando base de endereços")
    sp.start()
    END = pd.read_csv(ADDRESS_DATA, sep=";", dtype=datatypes_dict())
    unique_streets = list(END["NOMELOGR"].sort_values().unique())
    sp.stop()

response = geocode(END, "95", "", SearchMode.BY_CODE)
print(response.head())
