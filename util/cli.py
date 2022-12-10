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
    Custom inquirer theme compatible with Windows Command Prompt (few colors)
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


def print_result(
    legend: str,
    result: str,
    indent_spacing=5,
    color_fore=color.Fore.BLUE,
    color_style=color.Style.BRIGHT,
) -> None:
    """
    Prints indented colored text
    """
    print(" " * indent_spacing + legend + ": " + color_fore + color_style + result)


def file_selector(
    folder: Union[str, os.PathLike], *filetypes: str
) -> Union[str, os.PathLike]:
    """
    File selection menu
    """
    options = []
    options.extend(["*** Atualizar lista de arquivos"])
    for ft in filetypes:
        options.extend(
            os.path.basename(f) for f in glob.glob(os.path.join(folder, f"*.{ft}"))
        )
    options.extend(["<<< Retornar ao menu inicial"])
    q = [
        inquirer.List("option", message="", choices=options, carousel=True),
    ]
    return inquirer.prompt(q, theme=CustomTheme())["option"]


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
