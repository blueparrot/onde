import os
import colorama as color
import util.cli as cli

VERSION = "1.0"


def main_menu() -> str:
    os.system("cls" if os.name == "nt" else "clear")
    cli.print_title(f"ONDE@BH v{VERSION}", color_back=color.Back.GREEN)
    print("Selecione a ação:\n")
    return cli.options(
        "Geocodificar arquivo CSV ou DBF",
        "Consultar endereço individual",
        "Atualizar dados geográficos",
        "Sair",
    )


def wfs_alert() -> None:
    print(
        color.Fore.YELLOW
        + "Alerta: "
        + color.Fore.RESET
        + "Se a conexão com a internet ou o servidor de geosserviços estiverem \n"
        "instáveis, este script pode ser interrompido com mensagens de erro. Caso isso \n"
        "aconteça, tente novamente em outra ocasião (de preferência em horários de \n"
        "menor tráfego).\n"
        "Prosseguir?\n"
    )
    option = cli.options("SIM", "NÃO")
    if option == "NÃO":
        main_menu()


if __name__ == "__main__":
    color.init(autoreset=True)
    action_choice = main_menu()
    if action_choice == "Geocodificar arquivo CSV ou DBF":
        print("Módulo não implementado")
    if action_choice == "Consultar endereço individual":
        print("Módulo não implementado")
    if action_choice == "Atualizar dados geográficos":
        wfs_alert()
    if action_choice == "Sair":
        quit()

    color.deinit()
