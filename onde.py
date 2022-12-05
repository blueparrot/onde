import os
import colorama as color
import util.cli as cli

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
contribuições que possam vir a ser livremente propostas por outros
programadores, em se tratando de um projeto de código aberto sob a licença
"GNU General Public License v3.0").

Alertas sobre "bugs", sugestões e contribuições são muito bem vindos, mas o
autor reitera que o desenvolvimento, suporte e manutenção do projeto não fazem
parte de suas atribuições profissionais.

O código-fonte está disponível em: https://github.com/blueparrot/onde

================================================================================
Autor: João Pedro Costa da Fonseca
Médico Veterinário, servidor da Secretaria Municipal de Saúde de Belo Horizonte
no cargo de Técnico Superior de Saúde (BM 88183-3)
Contato: joao.pfonseca@pbh.gov.br
"""
)


def main_menu() -> str:
    os.system("cls" if os.name == "nt" else "clear")
    cli.print_title(f"Onde@BH v{VERSION}", color_back=color.Back.GREEN)
    print("Selecione a ação:\n")
    return cli.options(
        "Geocodificar arquivo CSV ou DBF",
        "Consultar endereço individual",
        "Atualizar dados geográficos",
        "Exibir aviso legal",
        "Sair",
    )


def wfs_alert() -> None:
    print(
        color.Fore.YELLOW
        + "Alerta: "
        + color.Fore.RESET
        + "Se a conexão com a internet ou o servidor de geosserviços estiverem \n"
        + "instáveis, este script pode ser interrompido com mensagens de erro. Caso isso \n"
        + "aconteça, tente novamente em outra ocasião (de preferência em horários de \n"
        + "menor tráfego). \n\n"
        + "Prosseguir?\n"
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
    if action_choice == "Exibir aviso legal":
        os.system("cls" if os.name == "nt" else "clear")
        cli.print_title("AVISO LEGAL", color_back=color.Back.YELLOW)
        print(DISCLAIMER)
    if action_choice == "Sair":
        quit()

    color.deinit()
