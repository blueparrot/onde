import os
import pandas as pd
import colorama as color

import util.cli as cli
import util.file_parsing as fp
from util.config import datatypes_dict, default_input_cols_as_text, default_input_dict
from util.update_geodata import update_all
from geocode import geocode, geocode_file, SearchMode

VERSION = "1.0"
DISCLAIMER = (
    color.Fore.YELLOW
    + color.Style.BRIGHT
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
LOGO = """


                      ____          __    _____  ___  __ __
                     / __ \___  ___/ /__ / ___ \/ _ )/ // /
                    / /_/ / _ \/ _  / -_) / _ `/ _  / _  / 
                    \____/_//_/\_,_/\__/\ \_,_/____/_//_/  
                                         \___/              




                                                          .
                                                        .:::.
                                                      .:::::::.           .
                                                       '::::::::.       .::
                                                         '::::::::.   .::::
                                                           ':::::::::::::::
                                                             ':::::::::::::
                                                               ':::::::::::
                                                              .::::::::::::
                                                            .::::::::::::::
                                                          .::::::::::::::::
                                                                            .-.
                                                                           (   )
                                                                            '-'
"""
ABSOLUTE_PATH = os.path.dirname(__file__)
DATA = os.path.join(ABSOLUTE_PATH, "geodata", "base_enderecos.csv")

cli.clear_screen()
print(color.Fore.GREEN + color.Style.BRIGHT + LOGO + color.Style.RESET_ALL)

if os.path.isfile(DATA):
    sp = cli.spinner("Carregando base de endereços")
    sp.start()
    END = pd.read_csv(DATA, sep=";", dtype=datatypes_dict())
    unique_streets = list(END["NOMELOGR"].sort_values().unique())
    sp.stop()


def main_menu() -> str:
    """
    Shows the main menu
    """
    cli.clear_screen()
    cli.print_title(
        f"Onde@BH v{VERSION} - Geocodificador de endereços em Belo Horizonte",
        color_back=color.Back.GREEN,
    )
    print("Navegue com as setas do teclado e pressione <ENTER> para executar a ação:\n")
    return cli.options(
        "Geocodificar arquivo CSV ou DBF",
        "Pesquisar endereço individual",
        "Atualizar dados geográficos",
        "Exibir aviso legal",
        "Sair",
    )


def column_dialog(col_name: str, column_list):
    """
    Column selection dialog
    """
    cli.clear_screen()
    cli.print_title("GEOCODIFICAR ARQUIVOS")
    print(
        "Indique a coluna que contém o "
        + color.Fore.GREEN
        + col_name.upper()
        + color.Fore.RESET
        + ":"
    )
    return cli.column_selector(column_list)


def datafile_alert() -> None:
    """
    Shows alert if address database is not detected
    """
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


def wfs_alert() -> str:
    """
    Shows alert about possible connection issues with WFS server
    """
    print(
        (
            color.Fore.YELLOW
            + "Alerta: "
            + color.Fore.RESET
            + """Este processo pode ser demorado, mas só precisa ser feito se esta for
uma instalação nova do programa ou se houver mudanças significativas na base
geográfica da cidade.

Se a conexão com a internet ou o servidor de geosserviços estiverem instáveis,
o script pode ser interrompido com mensagens de erro. Neste caso, tente
novamente em outra ocasião (de preferência em horários de menor tráfego).

Prosseguir?\n"""
        )
    )
    return cli.options("SIM", "NÃO")


def search_single_address() -> None:
    """
    Interface to search individual addresses
    """
    while True:
        cli.clear_screen()
        cli.print_title("PESQUISA INDIVIDUAL DE ENDEREÇOS")
        print("Informe os dados do endereço a ser pesquisado:\n")
        street_name = cli.text_question("Logradouro")
        address_number = cli.text_question("Número")
        result = geocode(
            END, unique_streets, street_name, address_number, SearchMode.BY_NAME
        )
        if (
            result["LOG_LGRD"] == "Não localizado"
            or result["LOG_NUMR"] == "Não localizado"
        ):
            print(color.Fore.RED + "Endereço não localizado")
        else:
            cli.print_result(
                "Endereço procurado",
                result["TIPOLOGR"]
                + " "
                + result["NOMELOGR"]
                + ", "
                + result["NUM_IMOV"]
                + " - CEP "
                + result["CEP"],
            )
            cli.print_result("Código de logradouro", result["COD_LOGR"])
            cli.print_result("Bairro", result["BAIRRO"].upper())
            cli.print_result("Distrito Sanitário", result["REGIONAL"])
            cli.print_result("Área de abrangência da SMSA", result["AA"])
            cli.print_result("Quarteirão", result["QT"])
            cli.print_result(
                "Coordenadas (EPSG: 31983 - SIRGAS 2000 23S)",
                "X: " + result["X"] + " — Y: " + result["Y"],
            )
            cli.print_result("Relatório de localização do imóvel", result["LOG_NUMR"])
        print(color.Fore.GREEN + "\nContinuar?\n")
        street_name = ""
        address_number = ""
        repeat = cli.options("Pesquisar mais um endereço", "Retornar ao menu inicial")
        if repeat == "Retornar ao menu inicial":
            break


def start_geocode_file(
    selected_file, col_street_code, col_street_cep, col_street_name, col_address_number
):
    cli.clear_screen()
    cli.print_title("GEOCODIFICAR ARQUIVOS")
    print("                         Hora de tomar um cafezinho...")
    print(
        color.Fore.YELLOW
        + """

                                         )  (
                                      (   ) )
                                       ) ( (
                                     _______)_
                                  .-'---------|  
                                 ( C|/\/\/\/\/|
                                  '-./\/\/\/\/|
                                    '_________'
                                     '-------'
    
    """
    )
    log = geocode_file(
        END,
        unique_streets,
        file=selected_file,
        col_street_code=col_street_code,
        col_street_cep=col_street_cep,
        col_street_name=col_street_name,
        col_address_number=col_address_number,
    )
    cli.clear_screen()
    cli.print_title("GEOCODIFICAR ARQUIVOS")
    print(
        color.Fore.GREEN
        + color.Style.BRIGHT
        + "\n\n                    Geoprocessamento concluído com sucesso!\n\n"
    )
    output_file, _ = os.path.splitext(os.path.basename(selected_file))
    output_file = os.path.join(ABSOLUTE_PATH, "resultado", output_file + ".csv")
    print("O resultado foi salvo em " + color.Fore.GREEN + f"{output_file}\n")
    print(color.Fore.BLACK + color.Back.WHITE + "  RELATÓRIO:  ")
    for section, content in log.items():
        print("\n >> " + section + ": ", end="")
        if type(content) != dict:
            print(color.Fore.BLUE + color.Style.BRIGHT + f"{content}", end="")
        else:
            for key, value in content.items():
                print(
                    "\n    - "
                    + key
                    + ": "
                    + color.Fore.BLUE
                    + color.Style.BRIGHT
                    + f"{value}",
                    end="",
                )

    input("\n\nPressione <ENTER> para retornar ao menu inicial...")


def process_file():
    """
    Interface to select file and set parameters to geocode
    """
    while True:
        cli.clear_screen()
        cli.print_title("GEOCODIFICAR ARQUIVOS")
        use_default_cols = "NÃO"
        print(
            "Para que os arquivos CSV ou DBF apareçam entre as opções abaixo, é necessário\n"
            + "copiá-los para a pasta "
            + color.Fore.GREEN
            + os.path.join(ABSOLUTE_PATH, "entrada")
            + color.Fore.RESET
            + "\n"
        )

        # File selection dialog
        selection = cli.file_selector(
            os.path.join(ABSOLUTE_PATH, "entrada"), "CSV", "DBF"
        )
        selected_file = os.path.join(ABSOLUTE_PATH, "entrada", selection)

        if selection == "*** Atualizar lista de arquivos":
            continue

        if selection == "<<< Retornar ao menu inicial":
            break

        # Shows alert if datafile has conflicting names with columns that will be used to output geocoding result
        override_columns = "SIM"
        if fp.contains_output_cols(selected_file):
            cli.clear_screen()
            cli.print_title("GEOCODIFICAR ARQUIVOS")
            print(
                color.Fore.YELLOW
                + "\nAlerta: "
                + color.Fore.RESET
                + "O arquivo indicado contém ao menos uma coluna com o nome igual aos que\n"
                + "serão usados para registro do resultado da análise:\n\n"
                + color.Fore.BLUE
                + color.Style.BRIGHT
                + "REGIONAL, AA, QT, BAIRRO, X, Y, LOG_LGRD, LOG_NUMR\n\n"
                + color.Style.RESET_ALL
                + "Para evitar que dados sejam sobrescritos, recomenda-se alterar o nome destas\n"
                + "colunas no arquivo de entrada.\n\n"
                + "Continuar assim mesmo?\n"
            )
            override_columns = cli.options("SIM", "NÃO")
        if override_columns == "NÃO":
            continue

        # If default columns are present, gives option to bypass some dialogs
        if fp.contains_default_cols(selected_file):
            print(
                "O arquivo indicado contém as colunas padrão:"
                + f"{default_input_cols_as_text()}"
                + "Utilizar a configuração padrão de parâmetros de entrada?\n"
            )
            use_default_cols = cli.options("SIM", "NÃO")
        if use_default_cols == "SIM":
            default_cols = default_input_dict()
            start_geocode_file(
                selected_file,
                default_cols["codigo_logradouro"],
                default_cols["cep"],
                default_cols["nome_logradouro"],
                default_cols["numero_imovel"],
            )
            break

        # Show column selection dialogs
        column_list = fp.get_columns(selected_file)
        col_street_code = column_dialog("CÓDIGO DE LOGRADOURO", column_list)
        col_street_cep = column_dialog("CEP", column_list)
        col_street_name = column_dialog("NOME DO LOGRADOURO", column_list)

        # Check if at least one street identifier is given
        if (
            col_street_code == "--- AUSENTE NESTE ARQUIVO ---"
            and col_street_cep == "--- AUSENTE NESTE ARQUIVO ---"
            and col_street_name == "--- AUSENTE NESTE ARQUIVO ---"
        ):
            print(
                color.Fore.RED
                + "Todos os possíveis indicadores de logradouro (nome, código ou cep) foram\n"
                + "apontados como AUSENTES no arquivo.\n"
                + "Ao menos uma coluna precisa ser indicada.\n"
            )
            input("Pressione <ENTER> para tentar novamente...")
            continue

        col_address_number = column_dialog("NÚMERO DO IMÓVEL", column_list)

        # Check if the address number is given
        if col_address_number == "--- AUSENTE NESTE ARQUIVO ---":
            print(
                color.Fore.RED
                + "A geocodificação não é possível sem os números dos imóveis.\n"
            )
            input("Pressione <ENTER> para tentar novamente...")
            continue

        # Confirmation
        cli.clear_screen()
        cli.print_title("GEOCODIFICAR ARQUIVOS")

        print("Os seguintes parâmetros foram informados:\n")
        print("  - Arquivo a ser geocodificado: " + color.Fore.GREEN + f"{selection}")
        print(
            "  - Coluna com o CÓDIGO de logradouro: "
            + color.Fore.GREEN
            + f"{col_street_code}"
        )
        print("  - Coluna com o CEP: " + color.Fore.GREEN + f"{col_street_cep}")
        print(
            "  - Coluna com o NOME do logradouro: "
            + color.Fore.GREEN
            + f"{col_street_name}"
        )
        print(
            "  - Coluna com o NÚMERO do imóvel: "
            + color.Fore.GREEN
            + f"{col_address_number}"
        )
        print("\nProsseguir?")
        start_geocoding = cli.options("SIM", "VOLTAR AO INÍCIO")

        # Start geocoding script
        if start_geocoding == "SIM":
            start_geocode_file(
                selected_file,
                col_street_code,
                col_street_cep,
                col_street_name,
                col_address_number,
            )
            break
        if start_geocode_file == "VOLTAR AO INÍCIO":
            continue


def main() -> None:
    """
    Main interface
    """
    cli.clear_screen()
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
        action_choice = main_menu()
        if action_choice == "Geocodificar arquivo CSV ou DBF":
            if os.path.isfile(DATA):
                process_file()
            else:
                datafile_alert()
        if action_choice == "Pesquisar endereço individual":
            if os.path.isfile(DATA):
                search_single_address()
            else:
                datafile_alert()
        if action_choice == "Atualizar dados geográficos":
            update_geodata = wfs_alert()
            if update_geodata == "SIM":
                update_all()
                if os.path.isfile(DATA):
                    cli.clear_screen()
                    sp = cli.spinner("Carregando a base de endereços atualizada")
                    sp.start()
                    END = pd.read_csv(DATA, sep=";", dtype=datatypes_dict())
                    sp.stop()
        if action_choice == "Exibir aviso legal":
            cli.clear_screen()
            cli.print_title("AVISO LEGAL", color_back=color.Back.YELLOW)
            print(DISCLAIMER)
            input("Pressione <ENTER> para retornar ao menu inicial...")
        if action_choice == "Sair":
            quit()


if __name__ == "__main__":
    main()
