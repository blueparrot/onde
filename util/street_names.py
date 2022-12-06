import unicodedata


def apagar_preposicoes(texto):
    """
    Remove as preposições "DE, DO, DA, DOS, DAS" do texto de entrada.
    """
    lista = texto.split()
    preposicoes = ("DE", "DO", "DA", "DOS", "DAS")
    for p in preposicoes:
        while p in lista:
            lista.remove(p)
    return " ".join(lista)


def apagar_tipo_logradouro(texto):
    """
    Remove os termos que indicam tipo de logradouro do início do texto de entrada.
    """
    lista = texto.split()
    tipos = (
        "ALAMEDA",
        "ALA",
        "AVENIDA",
        "AVE",
        "AV",
        "BECO",
        "BEC",
        "ESTRADA",
        "EST",
        "PRACA",
        "PCA",
        "RODOVIA",
        "ROD",
        "RUA",
        "R",
        "TRAVESSA",
        "TRV",
    )
    if lista[0] in tipos:
        del lista[0]
    return " ".join(lista)


def converter_abreviacoes(texto):
    """
    Converte abreviações comuns em palavras completas.
    """
    if len(texto) == 0:
        return texto
    lista = texto.split()
    abrev = {
        "ALM": "ALMIRANTE",
        "ARQ": "ARQUITETO",
        "BRIG": "BRIGADEIRO",
        "CB": "CABO",
        "CPT": "CAPITAO",
        "CAP": "CAPITAO",
        "CAR": "CARDEAL",
        "COM": "COMENDADOR",
        "CON": "CONEGO",
        "CONS": "CONSELHEIRO",
        "CEL": "CORONEL",
        "DEL": "DELEGADO",
        "DEP": "DEPUTADO",
        "DES": "DESEMBARGADOR",
        "DET": "DETETIVE",
        "DR": "DOUTOR",
        "EMB": "EMBAIXADOR",
        "ENG": "ENGENHEIRO",
        "EXP": "EXPEDICIONARIO",
        "FARM": "FARMACEUTICO",
        "GEN": "GENERAL",
        "GOV": "GOVERNADOR",
        "JORN": "JORNALISTA",
        "MJ": "MAJOR",
        "MAR": "MARECHAL",
        "MIN": "MINISTRO",
        "MON": "MONSENHOR",
        "NSA": "NOSSA",
        "NSRA": "NOSSA SENHORA",
        "PE": "PADRE",
        "PRES": "PRESIDENTE",
        "PROF": "PROFESSOR",
        "RAD": "RADIALISTA",
        "STA": "SANTA",
        "STO": "SANTO",
        "SGT": "SARGENTO",
        "SEN": "SENADOR",
        "SRA": "SENHORA",
        "TEN": "TENENTE",
        "VER": "VEREADOR",
    }
    if lista[0] in abrev.keys():
        lista[0] = abrev[lista[0]]
    return " ".join(lista)


def numero_por_extenso(num):
    """
    Interpreta o número representado em algarismos para texto por extenso.
    Caso o parâmetro de entrada não possa ser interpretado como um número ou seja um valor maior que 999999,
    a função retorna o mesmo parâmetro sem alterações, apenas convertido em string.
    """
    try:
        n = int(num)
        if n > 999999:
            return str(num)
    except:
        return str(num)
    unidades = (
        "ZERO",
        "UM",
        "DOIS",
        "TRES",
        "QUATRO",
        "CINCO",
        "SEIS",
        "SETE",
        "OITO",
        "NOVE",
    )
    dezenas = (
        "",
        "DEZ",
        "VINTE",
        "TRINTA",
        "QUARENTA",
        "CINQUENTA",
        "SESSENTA",
        "SETENTA",
        "OITENTA",
        "NOVENTA",
    )
    dezenas_irregulares = {
        "11": "ONZE",
        "12": "DOZE",
        "13": "TREZE",
        "14": "QUATORZE",
        "15": "QUINZE",
        "16": "DEZESSEIS",
        "17": "DEZESSETE",
        "18": "DEZOITO",
        "19": "DEZENOVE",
    }
    centenas = (
        "",
        "CENTO",
        "DUZENTOS",
        "TREZENTOS",
        "QUATROCENTOS",
        "QUINHENTOS",
        "SEISCENTOS",
        "SETECENTOS",
        "OITOCENTOS",
        "NOVECENTOS",
    )
    n = str(num)
    if len(n) > 3:
        n_milhares = n[:-3]
        n_unidades = n[-3:]
        if int(n) % 1000 == 0:
            return (
                (numero_por_extenso(n_milhares) + " MIL")
                .replace("UM MIL", "MIL")
                .strip()
            )
        if int(n_unidades) % 100 == 0:
            pre = "E "
        else:
            pre = ""
        return (
            (
                numero_por_extenso(n_milhares)
                + " MIL "
                + pre
                + numero_por_extenso(n_unidades)
            )
            .replace("UM MIL", "MIL")
            .replace("  ", " ")
            .strip()
        )
    else:
        texto = ""
        if len(n) > 2:
            if int(n[-3:]) % 100 == 0:
                if n[-3:] == "100":
                    return (texto + "CEM").strip()
                return (texto + centenas[int(n[0])]).strip()
            if n[-2] == "0":
                sufixo_centena = ""
            else:
                sufixo_centena = " E "
            texto = texto + centenas[int(n[0])] + sufixo_centena
        if len(n) > 1:
            if n[-2:] in dezenas_irregulares.keys():
                return (texto + dezenas_irregulares[n[-2:]]).strip()
            elif int(n[-2:]) % 10 == 0:
                return (texto + dezenas[int(n[-2])]).strip()
            texto = texto + dezenas[int(n[-2])] + " E "
        texto = texto + unidades[int(n[-1])]
        return texto.strip()


def padronizar_logradouro(t):
    """
    Função principal do módulo, que padroniza o formato dos nomes dos logradouros para busca no banco de dados.
    """
    t = t.strip()  # Remove espaços no começo e no fim
    t = t.upper()  # Converte para maiúsculas
    t = t.translate(str.maketrans("", "", ",.-'\"():;+/?$°@"))  # Elimina pontuações
    t = "".join(
        c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn"
    )  # Elimina caracteres especiais
    # As funçôes a seguir presumem que o texto já foi previamente convertido
    # em maiúsculas e que caracteres especiais e pontuações foram eliminados.
    t = apagar_preposicoes(t)  # Apaga preposições
    t = apagar_tipo_logradouro(t)  # Apaga tipo de logradouro
    t = converter_abreviacoes(t)  # Converte abreviações comuns em palavras completas
    # O código a seguir identifica dígitos no texto e os converte para números escritos por extenso
    lista = t.split()
    lista = [numero_por_extenso(p) if p.isdigit() else p for p in lista]
    return " ".join(lista)
