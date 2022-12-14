# Onde@BH
O objetivo deste script é geocodificar endereços de Belo Horizonte com base nos dados disponibilizados publicamente pela Prefeitura através do servidor [WFS BHMAP](https://bhmap.pbh.gov.br/v2/api/idebhgeo/wfs). Ele oferece as seguintes alternativas de busca:
- Pesquisa individual de endereços
- Geocodificação de arquivos CSV ou DBF que contenham colunas identificando o número dos imóveis e o logradouro (por nome, CEP ou código de logradouro)

## Instalação no Windows
Este passo a passo pressupõe que o **Python 3** já esteja instalado no sistema. O script faz uso de alguns módulos externos que precisam ser baixados da internet. Isso é feito de forma "semi-automática" pela ferramenta **pip**, que faz parte do Python.

O processo pode ser ligeiramente diferente a dependar da distribuição do Python que estiver instalada (Anaconda, WinPython, etc), mas na versão básica é o seguinte:

1. Através da opção **Code > Download ZIP** (acima), baixar o arquivo com o conteúdo deste repositório

2. Extrair o arquivo ZIP na pasta de sua preferência

3. Navegar até esse local pelo **Explorador de Arquivos** do Windows

4. Com a pasta aberta, segure a tecla **shift** do teclado e clique em qualquer espaço da janela com o botão **direito** do mouse

5. No menu "pop up", selecione a opção **Abrir janela do PowerShell aqui** (ou **Abrir janela de comando aqui**, em versões mais antigas do Windows)

6. Checar se a linha de comando exibe o caminho da pasta correta. Opcionalmente, digite o comando **dir** (e tecle **Enter**) para se certificar de que o arquivo *requirements.txt* é listado

7. O ideal é que os módulos a serem baixados fiquem instalados em um *ambiente virtual* exclusivo deste script. Para criar esse ambiente, digite o comando: `python3 -m venv env` e tecle **Enter**

8. A depender da versão de terminal que estiver usando, digite um destes comandos para ativar o ambiente virtual:
    - **PowerShell:** `env\Scripts\activate.ps1`
    - **Prompt de Comando:** `env\Scripts\activate.bat`
    
    Atenção ao "S" maiúsculo.

9. Se o ambiente virtual foi ativado com sucesso, o indicador **(env)** vai aparecer antes da linha de comando. Isso feito, digite o comando `pip install -r requirements.txt` e tecle **Enter**

10. Os pacotes necessários serão instalados. Caso precise de informações mais detalhadas sobre ambientes virtuais, consulte as referências a seguir:
    - https://docs.python.org/pt-br/3/tutorial/venv.html
    - https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html

## Execução do programa

1. Navegar até a pasta do programa pelo **PowerShell** ou pelo **Prompt de Comando**, como descrito acima

2. Ativar o ambiente virtual:
    - **PowerShell:** `env\Scripts\activate.ps1`
    - **Prompt de Comando:** `env\Scripts\activate.bat`

3. Executar o comando: `python onde.py`

**NOTA: Caso opte por instalar os pacotes na "raiz" do Python, sem o uso de ambiente virtual, os passos 7 e 8 da instalação e o passo 2 da execução podem ser ignorados.**

## Aviso legal

O script Onde@BH não tem fins comerciais e pode ser livremente utilizado alterado e distribuído. Ele é disponibilizado com a expectativa de que seja útil, mas sem NENHUMA GARANTIA.

Adicionalmente, vale ressaltar que este programa realiza o processamento de dados geográficos disponibilizados publicamente no servidor WFS mantido pela Empresa de Informática e Informação do Município de Belo Horizonte (PRODABEL), mas nem a Prefeitura Municipal de Belo Horizonte nem a PRODABEL tem qualquer responsabilidade pelo software em si. Trata-se de um projeto pessoal desenvolvido individualmente pelo autor em seu tempo livre (com eventuais contribuições voluntárias que possam vir a ser propostas por outros programadores, em se tratando de um projeto de código aberto sob a licença "GNU General Public License v3.0").

Alertas sobre "bugs", sugestões e contribuições são muito bem vindos, mas o autor reitera que o desenvolvimento, suporte e manutenção deste projeto não fazem parte de suas atribuições profissionais.