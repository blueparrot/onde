import unicodedata


def delete_prepositions(text):
    """
    Delete common prepositions
    """
    chunks = text.split()
    if len(chunks) == 0:
        return text
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
    if len(chunks) == 0:
        return text
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
    if len(chunks) == 0:
        return text
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


def num_para_pt(num_str: str) -> str:
    """
    Converts digits to numbers expressed in the Portuguese language, as they are found in the address database
    """
    try:
        num_int = int(num_str)
        num_str = str(num_int)  # Remove leading zeroes
        if num_int > 999999:  # This is for street names, we don't need more than that
            return num_str
    except:
        return num_str
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
    digito_milhares = num_str[:-3]
    digito_unidades = num_str[-3:]
    if len(num_str) > 3:
        if num_int % 1000 == 0:
            return (
                (num_para_pt(digito_milhares) + " MIL").replace("UM MIL", "MIL").strip()
            )
        if int(digito_unidades) < 101:
            sufixo_milhares = "E "
        else:
            sufixo_milhares = ""
        return (
            (
                num_para_pt(digito_milhares)
                + " MIL "
                + sufixo_milhares
                + num_para_pt(digito_unidades)
            )
            .replace("UM MIL", "MIL")
            .replace("  ", " ")
            .strip()
        )
    else:
        resultado = ""
        if len(num_str) > 2:
            if int(digito_unidades) % 100 == 0:
                if digito_unidades == "100":
                    return (resultado + "CEM").strip()
                return (resultado + centenas[int(num_str[0])]).strip()
            if num_str[-2] == "0":
                sufixo_centena = ""
            else:
                sufixo_centena = " E "
            resultado = resultado + centenas[int(num_str[0])] + sufixo_centena
        if len(num_str) > 1:
            if num_str[-2:] in dezenas_irregulares.keys():
                return (resultado + dezenas_irregulares[num_str[-2:]]).strip()
            elif int(num_str[-2:]) % 10 == 0:
                return (resultado + dezenas[int(num_str[-2])]).strip()
            resultado = resultado + dezenas[int(num_str[-2])] + " E "
        resultado = resultado + unidades[int(num_str[-1])]
        return resultado.strip()


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
    chunks = [num_para_pt(p) if p.isdigit() else p for p in chunks]
    return " ".join(chunks)
