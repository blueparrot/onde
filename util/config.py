import os
import yaml

ABSOLUTE_PATH = os.path.dirname(__file__)
GEODATA_CONFIG = os.path.join(ABSOLUTE_PATH, "geodata.yaml")
INPUT_CONFIG = os.path.join(ABSOLUTE_PATH, "config_entrada.yaml")

with open(GEODATA_CONFIG, "r") as stream:
    generator = yaml.safe_load_all(stream)
    server_configuration = generator.__next__()
    layer_configuration = generator.__next__()

unpacked_layers = sorted(
    [
        (c["ordem"], c["nome_original"], c["renomear_para"], c["datatype"])
        for col in [layer["colunas"] for layer in layer_configuration.values()]
        for c in col
    ]
)

with open(INPUT_CONFIG, "r") as stream:
    input_configuration = yaml.safe_load(stream)


def server():
    return server_configuration


def layers():
    return layer_configuration


def old_col_names():
    return [e[1] for e in unpacked_layers] + ["geometry"]


def new_col_names():
    return [e[2] for e in unpacked_layers] + ["geometry"]


def datatypes_list():
    return [e[3] for e in unpacked_layers]


def datatypes_dict():
    return {e[2]: e[3] for e in unpacked_layers}


def default_input_dict():
    return input_configuration


def default_input_cols():
    return list(input_configuration.values())


def default_input_cols_as_text():
    cols = default_input_cols()
    result = ""
    for index, col in enumerate(cols):
        separator = ", " if index < len(cols) else " e "
        if index == 0:
            result = col
        else:
            result = result + separator + col
    return "\n  - " + "\n  - ".join(default_input_cols()) + "\n"
