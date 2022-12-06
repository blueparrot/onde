import unicodedata


def delete_prepositions(text):
    """
    Delete common prepositions
    """
    chunks = text.split()
    prep = ("DE", "DO", "DA", "DOS", "DAS")
    for p in prep:
        while p in chunks:
            chunks.remove(p)
    return " ".join(chunks)


def delete_street_type(text):
    """
    Remove common street *types* from the street name
    """
    chunks = text.split()
    street_types = (
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
    if chunks[0] in street_types:
        del chunks[0]
    return " ".join(chunks)


def expand_abreviations(text):
    """
    Expand common abreviations in street names, as they are found in the address database
    """
    if len(text) == 0:
        return text
    chunks = text.split()
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
    if chunks[0] in abrev.keys():
        chunks[0] = abrev[chunks[0]]
    return " ".join(chunks)


def number_to_portuguese(num):
    """
    Converts digits to numbers expressed in the Portuguese language, as they are found in the address database
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
                (number_to_portuguese(n_milhares) + " MIL")
                .replace("UM MIL", "MIL")
                .strip()
            )
        if int(n_unidades) % 100 == 0:
            pre = "E "
        else:
            pre = ""
        return (
            (
                number_to_portuguese(n_milhares)
                + " MIL "
                + pre
                + number_to_portuguese(n_unidades)
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


def standardize_street_names(t):
    """
    Apply all the standardizations in this module
    """
    t = t.strip()
    t = t.upper()
    t = t.translate(str.maketrans("", "", ",.-'\"():;+/?$°@"))  # Delete punctuations
    t = "".join(
        c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn"
    )  # Delete special characters
    t = delete_prepositions(t)
    t = delete_street_type(t)
    t = expand_abreviations(t)
    chunks = t.split()
    chunks = [number_to_portuguese(p) if p.isdigit() else p for p in chunks]
    return " ".join(chunks)
