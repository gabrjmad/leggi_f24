import pdfplumber
import re

def is_cf_like(text: str) -> bool:
    """
    True se text è alfanumerico e lungo 11 o 16 caratteri.
    (per CF 16, per P.IVA 11)
    """
    if not re.fullmatch(r"[A-Za-z0-9]+", text):
        return False
    return len(text) in (11, 16)


def estrai_righe_validi(pdf_fp):
    """
    pdf_fp può essere un path (stringa) o un file-like object (es. Streamlit upload).
    Restituisce una lista di dict con info estratte per riga.
    Per ora:
      - codice fiscale (prima parola)
      - nominativo (colonna successiva)
      - riga intera come testo
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
                parole_ordinate = sorted(parole, key=lambda x: x["x0"])
                first_word = parole_ordinate[0]["text"]

                if is_cf_like(first_word):
                    # Ricostruisci intera riga
                    riga_testo = " ".join(p["text"] for p in parole_ordinate)

                    # Come esempio semplice: il nominativo è dopo il CF
                    # (per il tuo layout: CF, poi uno o più token di nominativo
                    #  fino a 'Cod.Contab.'; qui per ora prendiamo solo la parola successiva)
                    nominativo_grezzo = []
                    if len(parole_ordinate) > 1:
                        # per ora prendiamo tutte le parole fino a incontrare qualcosa che
                        # sembra un codice numerico (tipo '0605')
                        for p in parole_ordinate[1:]:
                            if re.fullmatch(r"\d{3,}", p["text"]):
                                break
                            nominativo_grezzo.append(p["text"])
                    nominativo = " ".join(nominativo_grezzo).strip()

                    risultati.append({
                        "page": page.page_number,
                        "y_top": top,
                        "codice_fiscale": first_word,
                        "nominativo": nominativo,
                        "riga_completa": riga_testo,
                    })

    return risultati
