import os
import glob
from typing import Union

import colorama as color
import inquirer
from inquirer.themes import Default
from blessed import Terminal
from halo import Halo

term = Terminal()


class CustomTheme(Default):
    """
    Custom inquirer theme compatible with Windows Command Prompt
    """

    def __init__(self):
        super().__init__()
        self.Question.mark_color = term.green
        self.Question.brackets_color = term.green
        self.Checkbox.selection_color = term.black_on_green
        self.Checkbox.selection_icon = ">"
        self.Checkbox.selected_icon = "◉"
        self.Checkbox.selected_color = term.green
        self.Checkbox.unselected_icon = "◯"
        self.List.selection_color = term.black_on_green
        self.List.selection_cursor = ">"


def print_title(
    title: str, width=80, color_fore=color.Fore.BLACK, color_back=color.Back.WHITE
) -> None:
    """
    Prints title centered in a bar of the given width
    """
    left_space = (width - len(title)) // 2
    print(
        color_back
        + color_fore
        + " " * left_space
        + title
        + " " * (width - left_space - len(title))
        + color.Style.RESET_ALL
        + "\n"
    )


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
    resposta = inquirer.prompt(q, theme=CustomTheme())
    return os.path.join(folder, resposta["arquivo"])


def options(*option_list: str) -> str:
    q = [inquirer.List("opt", choices=option_list)]
    return inquirer.prompt(q, theme=CustomTheme())["opt"]


def text_question(question: str) -> str:
    q = [inquirer.Text("answer", message=question)]
    return inquirer.prompt(q, theme=CustomTheme())["answer"]


def spinner(text: str):
    """
    Presets the spinner in the Halo package
    """
    return Halo(
        text=text,
        spinner={
            "interval": 200,
            "frames": [".  ", ".. ", "...", " ..", "  .", "   "],
        },
        color="green",
    )
