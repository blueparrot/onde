import os
import yaml

ABSOLUTE_PATH = os.path.dirname(__file__)
YAML_FILE = os.path.join(ABSOLUTE_PATH, "geodata.yaml")

with open(YAML_FILE, "r") as stream:
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
