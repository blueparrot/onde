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

# response = geocode(END, unique_streets, "125733", "142", SearchMode.BY_CODE)
# response = geocode(END, unique_streets, "30575060", "142", SearchMode.BY_CEP)
# response = geocode(END, unique_streets, "iracy manata", "142", SearchMode.BY_NAME)
# print(response)

# csv_generator = fp.csv_streamer(os.path.join(INPUT_FOLDER, "dengue.csv"))
# print(csv_generator.__next__())

# dbf_generator = fp.dbf_streamer(os.path.join(INPUT_FOLDER, "dengue.dbf"))
# print(dbf_generator.__next__())

# flexible_generator = fp.file_streamer(os.path.join(INPUT_FOLDER, "dengue.csv"))
# print(flexible_generator.__next__())

input_file = os.path.join(ABSOLUTE_PATH, ".", "entrada", "dengue.csv")
geocode_file(
    END,
    unique_streets,
    file=input_file,
    # col_street_code="codigolograd",
    col_street_code="--- AUSENTE NESTE ARQUIVO ---",
    # col_street_cep="cep",
    col_street_cep="--- AUSENTE NESTE ARQUIVO ---",
    col_street_name="nomelograd",
    # col_street_name="--- AUSENTE NESTE ARQUIVO ---",
    col_address_number="numnu",
)
