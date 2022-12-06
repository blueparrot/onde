import os
import colorama as color

import submenu
import util.cli as cli
from util.update_geodata import update_all

VERSION = "1.0"
DISCLAIMER = (
    color.Fore.YELLOW
    + """O script Onde@BH não tem fins comerciais e pode ser livremente utilizado,
alterado e distribuído. Ele é disponibilizado com a expectativa de que seja
útil, mas sem NENHUMA GARANTIA.

Adicionalmente, vale ressaltar que este programa realiza o processamento de
dados geográficos disponibilizados publicamente no servidor WFS mantido pela
Empresa de Informática e Informação do Município de Belo Horizonte (PRODABEL),
mas nem a Prefeitura Municipal de Belo Horizonte nem a PRODABEL tem qualquer
responsabilidade pelo software em si. Trata-se de um projeto pessoal,
desenvolvido individualmente pelo autor em seu tempo livre (com eventuais
contribuições voluntárias que possam vir a ser propostas por outros
programadores, em se tratando de um projeto de código aberto sob a licença
"GNU General Public License v3.0").

Alertas sobre "bugs", sugestões e contribuições são muito bem vindos, mas o
autor reitera que o desenvolvimento, suporte e manutenção deste projeto não
fazem parte de suas atribuições profissionais.

O código-fonte está disponível em: https://github.com/blueparrot/onde

================================================================================
Autor: João Pedro Costa da Fonseca
Médico Veterinário, servidor da Secretaria Municipal de Saúde de Belo Horizonte
no cargo de Técnico Superior de Saúde (BM 88183-3)
Contato: joao.pfonseca@pbh.gov.br
"""
)
ABSOLUTE_PATH = os.path.dirname(__file__)


def action_menu() -> str:
    os.system("cls" if os.name == "nt" else "clear")
    cli.print_title(
        f"Onde@BH v{VERSION} - Geocodificador de endereços em Belo Horizonte",
        color_back=color.Back.GREEN,
    )
    print("Selecione a ação:\n")
    return cli.options(
        "Geocodificar arquivo CSV ou DBF",
        "Consultar endereço individual",
        "Atualizar dados geográficos",
        "Exibir aviso legal",
        "Sair",
    )


def wfs_alert() -> str:
    print(
        (
            color.Fore.YELLOW
            + "Alerta: "
            + color.Fore.RESET
            + """Este processo pode ser demorado, mas só precisa ser feito se esta for
uma instalação nova do script ou se houver mudanças significativas na base
geográfica da cidade.

Se a conexão com a internet ou o servidor de geosserviços estiverem instáveis,
o script pode ser interrompido com mensagens de erro. Neste caso, tente
novamente em outra ocasião (de preferência em horários de menor tráfego).

Prosseguir?\n"""
        )
    )
    return cli.options("SIM", "NÃO")


def datafile_exists() -> bool:
    if os.path.isfile(os.path.join(ABSOLUTE_PATH, "geodata", "base_enderecos.csv")):
        return True
    else:
        return False


def datafile_alert() -> None:
    print(
        color.Fore.YELLOW
        + "Alerta: "
        + color.Fore.RESET
        + "A base de endereços não foi detectada neste computador. \n"
        + "É necessário executar a ação "
        + color.Fore.GREEN
        + "*Atualizar dados geográficos* "
        + color.Fore.RESET
        + "ao menos uma vez \npara preparar o ambiente deste programa. \n"
    )
    input("Pressione <ENTER> para continuar...")


def start() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    os.system("mode con: cols=80 lines=30")
    color.init(autoreset=True)
    DEFAULT_FOLDERS = [
        os.path.join(ABSOLUTE_PATH, "entrada"),
        os.path.join(ABSOLUTE_PATH, "geodata"),
        os.path.join(ABSOLUTE_PATH, "resultado"),
    ]

    for folder in DEFAULT_FOLDERS:
        if not os.path.exists(folder):
            os.makedirs(folder)

    while True:
        action_choice = action_menu()
        if action_choice == "Geocodificar arquivo CSV ou DBF":
            if datafile_exists():
                print("Arquivo")
                submenu.file()
            else:
                datafile_alert()
        if action_choice == "Consultar endereço individual":
            if datafile_exists():
                print("Individual")
                submenu.single_address()
            else:
                datafile_alert()
        if action_choice == "Atualizar dados geográficos":
            update_geodata = wfs_alert()
            if update_geodata == "SIM":
                update_all()
        if action_choice == "Exibir aviso legal":
            os.system("cls" if os.name == "nt" else "clear")
            cli.print_title("AVISO LEGAL", color_back=color.Back.YELLOW)
            print(DISCLAIMER)
            input("Pressione <ENTER> para retornar ao menu inicial...")
        if action_choice == "Sair":
            quit()
    color.deinit()


if __name__ == "__main__":
    start()
