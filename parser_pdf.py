import pdfplumber
import re
from typing import List, Dict, Union, IO

def is_cf_like(text: str) -> bool:
    """
    True se text è alfanumerico e lungo 11 o 16 caratteri.
    (per CF 16, per P.IVA 11)
    """
    if not re.fullmatch(r"[A-Za-z0-9]+", text):
        return False
    return len(text) in (11, 16)


def parse_riga_tokens(tokens: List[str]) -> Dict[str, str]:
    """
    tokens: lista di parole della riga, già ordinate da sinistra a destra.
    Formato atteso (esempio reale):
    CF NOME COGNOME ... 0600 B 55418 2026 04 01 01 ...
    """
    if not tokens:
        return {}

    cf = tokens[0]

    # Trova indice del gruppo (es. "0600")
    idx = 1
    while idx < len(tokens) and not re.fullmatch(r"\d+", tokens[idx]):
        idx += 1

    nominativo = " ".join(tokens[1:idx]).strip()

    gruppo_rif = tokens[idx] if idx < len(tokens) else ""
    regime_contabile = tokens[idx + 1] if idx + 1 < len(tokens) else ""
    codice_ditta = tokens[idx + 2] if idx + 2 < len(tokens) else ""
    anno = tokens[idx + 3] if idx + 3 < len(tokens) else ""
    tipo_f24 = tokens[idx + 4] if idx + 4 < len(tokens) else ""
    quantita_f24 = tokens[idx + 5] if idx + 5 < len(tokens) else ""

    return {
        "codice_fiscale": cf,
        "nominativo": nominativo,
        "gruppo_riferimento": gruppo_rif,
        "regime_contabile": regime_contabile,
        "codice_ditta": codice_ditta,
        "anno": anno,
        "tipo_f24": tipo_f24,
        "quantita_f24_inviati": quantita_f24,
    }


def estrai_righe_validi(pdf_fp: Union[str, IO]) -> List[Dict[str, str]]:
    """
    pdf_fp può essere un path o un file-like (upload Streamlit).
    Restituisce una lista di dict con i campi estratti per ogni riga valida.
    """
    risultati = []

    with pdfplumber.open(pdf_fp) as pdf:
        for page in pdf.pages:
            words = page.extract_words()

            righe = {}
            for w in words:
                top = round(w["top"])
                righe.setdefault(top, []).append(w)

            for top, parole in righe.items():
                parole_ordinate = sorted(parole, key=lambda x: x["x0"])
                tokens = [p["text"] for p in parole_ordinate]
                first_word = tokens[0]

                if not is_cf_like(first_word):
                    continue

                campi = parse_riga_tokens(tokens)
                campi["pagina"] = page.page_number
                risultati.append(campi)

    return risultati
