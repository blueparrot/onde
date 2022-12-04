import os
import colorama as color
import util.cli as cli


def main_menu() -> str:
    os.system("cls" if os.name == "nt" else "clear")
    cli.print_title("ONDE@BH", color_back=color.Back.GREEN)
    print("Selecione a ação:\n")
    return cli.options(
        "Geocodificar arquivo CSV ou DBF",
        "Consultar endereço individual",
        "Atualizar dados geográficos",
        "Sair",
    )


if __name__ == "__main__":
    color.init(autoreset=True)
    action_choice = main_menu()
    if action_choice == "Geocodificar arquivo CSV ou DBF":
        print("Módulo não implementado")
    if action_choice == "Consultar endereço individual":
        print("Módulo não implementado")
    if action_choice == "Atualizar dados geográficos":
        print("Bora")
    if action_choice == "Sair":
        quit()

    color.deinit()
