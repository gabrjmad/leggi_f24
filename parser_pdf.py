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
    Ritorna un dict strutturato con i campi richiesti.
    Si assume il formato:
    CF NOME COGNOME ... 0600 B 55418 2026 04 01 01 IT 59 P 01030 03005 000000454165 762,04
    """
    if not tokens:
        return {}

    cf = tokens[0]

    # Trova l'indice in cui inizia il blocco numerico "0600" (gruppo)
    # cioè il primo token dopo il CF che è tutto numerico
    idx = 1
    while idx < len(tokens) and not re.fullmatch(r"\d+", tokens[idx]):
        idx += 1

    # tutto ciò che sta tra CF e il primo blocco numerico è nominativo
    nominativo = " ".join(tokens[1:idx]).strip()

    # ora ci aspettiamo i campi in ordine fisso
    # idx -> gruppo di riferimento (0600)
    gruppo_rif = tokens[idx] if idx < len(tokens) else ""
    regime_contabile = tokens[idx + 1] if idx + 1 < len(tokens) else ""
    codice_ditta = tokens[idx + 2] if idx + 2 < len(tokens) else ""
    anno = tokens[idx + 3] if idx + 3 < len(tokens) else ""
    tipo_f24 = tokens[idx + 4] if idx + 4 < len(tokens) else ""
    quantita_f24 = tokens[idx + 5] if idx + 5 < len(tokens) else ""
    documenti_contenuti = tokens[idx + 6] if idx + 6 < len(tokens) else ""

    # saldo = ultimo token che assomiglia a importo tipo 762,04
    saldo = ""
    for t in reversed(tokens):
        if re.fullmatch(r"\d{1,3}(\.\d{3})*,\d{2}", t) or re.fullmatch(r"\d+,\d{2}", t):
            saldo = t
            break

    return {
        "codice_fiscale": cf,
        "nominativo": nominativo,
        "gruppo_riferimento": gruppo_rif,
        "regime_contabile": regime_contabile,
        "codice_ditta": codice_ditta,
        "anno": anno,
        "tipo_f24": tipo_f24,
        "quantita_f24_inviati": quantita_f24,
        "documenti_contenuti": documenti_contenuti,
        "saldo": saldo,
    }


def estrai_righe_validi(pdf_fp: Union[str, IO]) -> List[Dict[str, str]]:
    """
    pdf_fp può essere un path (stringa) o un file-like object (es. Streamlit upload).
    Restituisce una lista di dict con tutti i campi estratti per ogni riga valida.
    """
    risultati = []

    with pdfplumber.open(pdf_fp) as pdf:
        for page in pdf.pages:
            words = page.extract_words()

            # Raggruppiamo le parole per riga usando 'top'
            righe = {}
            for w in words:
                top = round(w["top"])
                righe.setdefault(top, []).append(w)

            for top, parole in righe.items():
                # ordina parole da sinistra a destra
                parole_ordinate = sorted(parole, key=lambda x: x["x0"])
                tokens = [p["text"] for p in parole_ordinate]
                first_word = tokens[0]

                # filtro per CF/p.IVA
                if not is_cf_like(first_word):
                    continue

                # parsa la riga in colonne
                campi = parse_riga_tokens(tokens)

                # aggiungi info di contesto (pagina, posizioni, riga originale)
                campi["pagina"] = page.page_number
                campi["y_top"] = top
                campi["riga_completa"] = " ".join(tokens)

                risultati.append(campi)

    return risultati
