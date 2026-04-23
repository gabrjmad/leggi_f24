import io
import os

import pandas as pd
import streamlit as st

from parser_pdf import estrai_righe_validi  # NON modifichiamo questo file

# Nome del file archivio unico
ARCHIVE_FILE = "Conto_f24_inviati.xlsx"

st.set_page_config(page_title="Estrai il tuo PDF", layout="wide")

# ========== STILE ==========

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top, #1d4ed8 0, #020617 60%);
        color: #e5e7eb;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .main-container {
        position: relative;
        background: linear-gradient(90deg, #020617 0%, #020617 30%, #020617 70%, #020617 100%);
        padding: 2.0rem 2.6rem 2.4rem 2.6rem;
        border-radius: 1.2rem;
        border: 1px solid rgba(148, 163, 184, 0.5);
        box-shadow: 0 22px 60px rgba(15, 23, 42, 0.95);
        max-width: 920px;
        margin: 2.5rem auto;
    }
    .title-wrapper {
        text-align: center;
        margin-bottom: 1.4rem;
    }
    .app-title-bar {
        display: inline-block;
        width: 100%;
        max-width: 800px;
        padding: 0.9rem 1.4rem;
        border-radius: 999px;
        background: linear-gradient(90deg, #0f172a 0%, #020617 50%, #111827 100%);
        border: 1px solid rgba(148, 163, 184, 0.5);
        color: #e5e7eb;
        font-size: 1.2rem;
        font-weight: 500;
        text-align: center;
    }
    .app-title-text {
        font-size: 1.15rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .upload-area {
        margin-top: 1.4rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.6rem;
    }
    .upload-label {
        font-size: 0.9rem;
        color: #cbd5f5;
    }
    .stFileUploader > div > div {
        border-radius: 999px !important;
        background-color: #f9fafb !important;
        color: #111827 !important;
        border: 1px solid #cbd5e1 !important;
        padding: 0.5rem 1rem !important;
    }
    .stFileUploader label {
        display: none !important;
    }
    .upload-help {
        font-size: 0.8rem;
        color: #e5e7eb;
        opacity: 0.8;
    }
    .stButton>button {
        background: #0f172a;
        color: #f9fafb;
        border-radius: 999px;
        padding: 0.55rem 1.9rem;
        border: 1px solid #1d4ed8;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.8);
    }
    .stButton>button:hover {
        background: #1d4ed8;
        box-shadow: 0 12px 30px rgba(37, 99, 235, 0.8);
    }
    .feedback-text {
        font-size: 0.9rem;
        color: #a5b4fc;
        margin-top: 0.8rem;
    }
    .divider {
        margin: 1.7rem 0 0.7rem 0;
        border-top: 1px solid rgba(148, 163, 184, 0.5);
    }
    .section-title {
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .small-label {
        font-size: 0.8rem;
        margin-bottom: 0.15rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="title-wrapper">
        <div class="app-title-bar">
            <span class="app-title-text">Estrai il tuo PDF</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ========== FUNZIONI DI SUPPORTO ==========

def carica_archivio(path: str) -> pd.DataFrame:
    """Carica il file archivio se esiste, altrimenti restituisce un DataFrame vuoto con le colonne standard."""
    if os.path.exists(path):
        return pd.read_excel(path)
    # colonne standard come da tuo esempio
    return pd.DataFrame(
        columns=[
            "Anno",
            "Cod_Fisc",
            "Denominazione",
            "gruppo_riferimento",
            "regime_contabile",
            "Codice_ditta",
            "Tipo",
        ]
    )


def aggiorna_archivio_con_nuove_righe(path: str, nuove_righe: list[dict]) -> pd.DataFrame:
    """
    Unisce le nuove righe estratte dall'upload con l'archivio esistente
    e salva il file aggiornato.
    """
    df_archivio = carica_archivio(path)
    if not nuove_righe:
        return df_archivio

    df_nuove = pd.DataFrame(nuove_righe)

    # Garantiamo le colonne nell'ordine desiderato
    colonne = [
        "Anno",
        "Cod_Fisc",
        "Denominazione",
        "gruppo_riferimento",
        "regime_contabile",
        "Codice_ditta",
        "Tipo",
    ]
    df_nuove = df_nuove.reindex(columns=colonne)

    df_aggiornato = pd.concat([df_archivio, df_nuove], ignore_index=True)

    df_aggiornato.to_excel(path, index=False)
    return df_aggiornato


def get_nominativi(df_archivio: pd.DataFrame) -> list[str]:
    """Restituisce la lista di denominazioni uniche, ordinate."""
    if df_archivio.empty:
        return []
    nomi = (
        df_archivio["Denominazione"]
        .astype(str)
        .str.strip()
        .replace("nan", "")
        .unique()
        .tolist()
    )
    nomi = [n for n in nomi if n]
    nomi.sort()
    return nomi


def conta_f24(df_archivio: pd.DataFrame, nominativo: str, tipo: str | None, anno: str | None) -> int:
    """Conta quante righe ci sono per nominativo (e opzionale tipo, anno)."""
    if df_archivio.empty:
        return 0

    df = df_archivio.copy()
    df["Denominazione"] = df["Denominazione"].astype(str).str.strip()
    df["Anno"] = df["Anno"].astype(str).str.strip()
    df["Tipo"] = df["Tipo"].astype(str).str.strip()

    mask = df["Denominazione"] == nominativo

    if anno:
        mask &= df["Anno"] == anno

    if tipo:
        mask &= df["Tipo"] == tipo

    return int(mask.sum())


# ========== UI PRINCIPALE ==========

# 1) Area upload
st.markdown('<div class="upload-area">', unsafe_allow_html=True)

st.markdown('<div class="upload-label">Carica uno o più PDF F24</div>', unsafe_allow_html=True)

pdf_files = st.file_uploader(
    "",
    type=["pdf"],
    accept_multiple_files=True,
    key="pdf_uploader",
)

st.markdown(
    '<div class="upload-help">Puoi trascinare i PDF qui sopra oppure cliccare per selezionarli.</div>',
    unsafe_allow_html=True,
)

# Bottone centrale
col_left, col_center, col_right = st.columns([1, 1, 1])
with col_center:
    estrai_clicked = st.button("Estrai dati dai PDF")

st.markdown("</div>", unsafe_allow_html=True)  # chiude upload-area

righe_trovate = 0
df_archivio = carica_archivio(ARCHIVE_FILE)

if estrai_clicked:
    if not pdf_files:
        st.warning("Carica almeno un PDF prima di estrarre i dati.")
    else:
        all_rows = []
        with st.spinner("Estrazione in corso..."):
            for f in pdf_files:
                righe = estrai_righe_validi(f)
                all_rows.extend(righe)

        righe_trovate = len(all_rows)

        if righe_trovate == 0:
            st.warning("Nessuna riga trovata nei PDF caricati.")
        else:
            # aggiorna archivio
            df_archivio = aggiorna_archivio_con_nuove_righe(ARCHIVE_FILE, all_rows)
            st.success(f"Estrazione completata! Righe trovate: {righe_trovate}.")

# Se abbiamo un archivio (anche solo pre-esistente), permetti il download
if not df_archivio.empty:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Scarica il file aggiornato</div>', unsafe_allow_html=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_archivio.to_excel(writer, sheet_name="Archivio_F24", index=False)
    buffer.seek(0)

    st.download_button(
        label="Scarica Conto_f24_inviati.xlsx",
        data=buffer,
        file_name=ARCHIVE_FILE,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# ========== SEZIONE FILTRO F24 ==========

if not df_archivio.empty:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">Conta F24 inviati</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2, 1, 1])

    nominativi = get_nominativi(df_archivio)
    with col1:
        st.markdown('<div class="small-label">Nominativo</div>', unsafe_allow_html=True)
        nome_sel = st.selectbox(
            "",
            options=[""] + nominativi,
            index=0,
            format_func=lambda x: x if x != "" else "Seleziona un nominativo",
        )

    with col2:
        st.markdown('<div class="small-label">Tipo (opzionale)</div>', unsafe_allow_html=True)
        tipo_input = st.text_input("", placeholder="Es. 4")

    with col3:
        st.markdown('<div class="small-label">Anno (opzionale)</div>', unsafe_allow_html=True)
        anno_input = st.text_input("", placeholder="Es. 2026")

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        conta_clicked = st.button("Conta F24")

    if conta_clicked:
        if not nome_sel:
            st.warning("Seleziona un nominativo prima di contare.")
        else:
            tipo_val = tipo_input.strip() if tipo_input.strip() else None
            anno_val = anno_input.strip() if anno_input.strip() else None

            totale = conta_f24(df_archivio, nome_sel, tipo_val, anno_val)

            # Costruzione frase
            parti = [f"F24 inviati da {nome_sel}"]
            if tipo_val:
                parti.append(f"di tipo {tipo_val}")
            if anno_val:
                parti.append(f"nell'anno {anno_val}")
            frase_intro = " ".join(parti)
            frase = f"{frase_intro} sono {totale}."

            st.markdown(f'<div class="feedback-text">{frase}</div>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # chiude main-container
