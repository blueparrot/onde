import os
import glob
from typing import Union

import inquirer
from inquirer.themes import GreenPassion
from halo import Halo


def file_selector(
    folder: Union[str, os.PathLike], *filetypes: str
) -> Union[str, os.PathLike]:
    """
    Apresenta um menu de seleção de arquivos e retorna o caminho do arquivo escolhido
    """
    file_choices = []
    for ft in filetypes:
        file_choices.extend(
            os.path.basename(f) for f in glob.glob(os.path.join(folder, f"*.{ft}"))
        )
    if len(file_choices) == 0:
        raise FileNotFoundError(
            f"Não foram encontrados arquivos dos tipos: {filetypes}"
        )
    if len(file_choices) == 1:
        return os.path.join(folder, file_choices[0])
    q = [
        inquirer.List(
            "arquivo", message="Escolha o arquivo", choices=sorted(file_choices)
        ),
    ]
    resposta = inquirer.prompt(q, theme=GreenPassion())
    return os.path.join(folder, resposta["arquivo"])


def options(*option_list: str) -> str:
    q = [inquirer.List("opt", choices=option_list)]
    return inquirer.prompt(q, theme=GreenPassion())["opt"]


def spinner(text: str):
    """
    Presets the spinner in the Halo package
    """
    return Halo(
        text=text,
        spinner={
            "interval": 80,
            "frames": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        },
        color="green",
    )
