import io
import os

import pandas as pd
import streamlit as st

from parser_pdf import estrai_righe_validi

st.set_page_config(page_title="Estrai il tuo PDF", layout="wide")

EXCEL_ARCHIVIO = "Conto_f24_inviati.xlsx"

# =======================
# STILI
# =======================
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top, #2563eb 0, #0f172a 60%);
        color: #e5e7eb;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .main-container {
        position: relative;
        background-color: rgba(15, 23, 42, 0.96);
        padding: 1.8rem 2.2rem 2.2rem 2.2rem;
        border-radius: 1rem;
        border: 1px solid rgba(148, 163, 184, 0.5);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.9);
        max-width: 900px;
        margin: 2rem auto;
        overflow: hidden;
    }
    .main-container::before,
    .main-container::after {
        content: "";
        position: absolute;
        border-radius: 999px;
        filter: blur(24px);
        opacity: 0.3;
        z-index: 0;
    }
    .main-container::before {
        width: 220px;
        height: 220px;
        background: radial-gradient(circle, #38bdf8, #6366f1);
        top: -80px;
        left: -40px;
    }
    .main-container::after {
        width: 260px;
        height: 260px;
        background: radial-gradient(circle, #a855f7, #3b82f6);
        top: -100px;
        right: -60px;
    }
    .header-wrapper {
        position: relative;
        z-index: 1;
        text-align: center;
        margin-bottom: 1.8rem;
    }
    .app-title {
        display: inline-block;
        padding: 0.5rem 1.4rem;
        border-radius: 999px;
        background-color: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(148, 163, 184, 0.7);
        font-size: 1.8rem;
        color: #f9fafb;
        font-weight: 700;
    }
    .app-subtitle {
        font-size: 0.95rem;
        color: #cbd5f5;
        margin-top: 0.4rem;
    }
    .stFileUploader {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.9rem;
        border: 1px dashed rgba(15, 23, 42, 0.3);
        color: #020617;
    }
    .stFileUploader label, .stFileUploader span {
        color: #020617 !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #6366f1, #3b82f6);
        color: #f9fafb;
        border-radius: 999px;
        padding: 0.45rem 1.7rem;
        border: none;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.5);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #818cf8, #60a5fa);
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.7);
    }
    .summary-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #e5e7eb;
        margin-top: 1rem;
        margin-bottom: 0.2rem;
    }
    .summary-count {
        font-size: 0.9rem;
        color: #a5b4fc;
        margin-bottom: 0.6rem;
    }
    .section-divider {
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.3);
    }
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
        color: #e5e7eb;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="header-wrapper">
        <div class="app-title">Estrai il tuo PDF</div>
        <div class="app-subtitle">
            Carica uno o più PDF con i dati F24 e aggiorna l'archivio Excel degli F24 inviati.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =======================
# 1) Upload PDF
# =======================
pdf_files = st.file_uploader(
    "Carica uno o più PDF",
    type=["pdf"],
    accept_multiple_files=True
)

# 2) Bottone per estrarre
st.write("")
center_col = st.columns(3)
with center_col[1]:
    estrai_clicked = st.button("Estrai dati dai PDF")

# =======================
# FUNZIONI DI SUPPORTO
# =======================

def carica_archivio():
    """Legge il file Excel di archivio se esiste, altrimenti restituisce None."""
    if os.path.exists(EXCEL_ARCHIVIO):
        return pd.read_excel(EXCEL_ARCHIVIO)
    return None

def salva_archivio(df_archivio):
    """Salva il DataFrame completo come archivio unico."""
    df_archivio.to_excel(EXCEL_ARCHIVIO, index=False)

# =======================
# 3) Estrazione e aggiornamento archivio
# =======================
if estrai_clicked:
    if not pdf_files:
        st.warning("Carica almeno un PDF prima di estrarre i dati.")
    else:
        all_rows = []
        # Carico archivio esistente (se presente) solo per avviso PDF già caricati
        df_archivio_esistente = carica_archivio()
        files_gia_caricati = set()
        if df_archivio_esistente is not None and "file_origine" in df_archivio_esistente.columns:
            files_gia_caricati = set(
                df_archivio_esistente["file_origine"].dropna().astype(str).unique()
            )

        with st.spinner("Estrazione in corso..."):
            for f in pdf_files:
                # Avviso se il file risulta già in archivio
                if f.name in files_gia_caricati:
                    st.warning(f"Attenzione: il file '{f.name}' risulta già in archivio. Le righe verranno comunque aggiunte.")
                righe = estrai_righe_validi(f)
                # Aggiungo il nome del file come colonna per ogni riga
                for r in righe:
                    r["file_origine"] = f.name
                all_rows.extend(righe)

        if not all_rows:
            st.warning("Nessuna riga trovata con codice fiscale a 11/16 caratteri nei PDF caricati.")
        else:
            # DataFrame dalle righe estratte (NON modifico la logica dei campi di base)
            df = pd.DataFrame(all_rows)

            df_excel = pd.DataFrame({
                "Anno": df.get("anno", ""),
                "Cod_Fisc": df.get("codice_fiscale", ""),
                "Denominazione": df.get("nominativo", ""),
                "gruppo_riferimento": df.get("gruppo_riferimento", ""),
                "regime_contabile": df.get("regime_contabile", ""),
                "Codice_ditta": df.get("codice_ditta", ""),
                "Tipo": df.get("tipo_f24", ""),
            })

            # Aggiungo colonna nome file all'archivio
            df_excel["file_origine"] = df.get("file_origine", "")

            # Append all'archivio esistente (se c'è), altrimenti creo nuovo
            df_archivio = carica_archivio()
            if df_archivio is not None:
                df_archivio = pd.concat([df_archivio, df_excel], ignore_index=True)
            else:
                df_archivio = df_excel

            # Salvo archivio aggiornato
            salva_archivio(df_archivio)

            # Salvo anche in session_state per evitare riletture immediate se non vuoi
            st.session_state["df_archivio"] = df_archivio

            # Feedback unico
            st.success(f"Estrazione completata! Righe trovate: {len(df_excel)}.")

# =======================
# 4) Sezione download archivio + conteggio F24
# =======================
# Carico sempre l'archivio aggiornato (da session_state o da disco)
df_archivio = st.session_state.get("df_archivio", None)
if df_archivio is None:
    df_archivio = carica_archivio()
    if df_archivio is not None:
        st.session_state["df_archivio"] = df_archivio

if df_archivio is not None and not df_archivio.empty:
    # --- Pulsante download archivio ---
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Archivio F24 inviati</div>', unsafe_allow_html=True)

    # Preparo il file Excel aggiornato in memoria per il download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_archivio.to_excel(writer, sheet_name="Foglio1", index=False)
    output.seek(0)

    download_col = st.columns(3)
    with download_col[1]:
        st.download_button(
            label="Scarica Conto_f24_inviati.xlsx",
            data=output,
            file_name=EXCEL_ARCHIVIO,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # --- Sezione filtro: Conta F24 inviati ---
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Conta F24 inviati</div>', unsafe_allow_html=True)

    # Nominativi unici dalla colonna Denominazione
    if "Denominazione" in df_archivio.columns:
        nominativi = sorted(df_archivio["Denominazione"].dropna().astype(str).unique())
    else:
        nominativi = []

    if nominativi:
        nominativo = st.selectbox("Seleziona nominativo", options=nominativi)
        tipo = st.text_input("Tipo (opzionale)")
        anno = st.text_input("Anno (opzionale)")

        conta_clicked = st.button("Conta F24")

        if conta_clicked:
            df_filtrato = df_archivio.copy()

            # Filtro base sul Nominativo
            mask = df_filtrato["Denominazione"].astype(str) == str(nominativo)

            # Filtro opzionale su Tipo
            if tipo.strip():
                mask &= df_filtrato["Tipo"].astype(str) == tipo.strip()

            # Filtro opzionale su Anno
            if anno.strip():
                mask &= df_filtrato["Anno"].astype(str) == anno.strip()

            n = df_filtrato[mask].shape[0]

            # Costruzione frase
            frase = f"F24 inviati da {nominativo}"
            if tipo.strip():
                frase += f" di tipo {tipo.strip()}"
            if anno.strip():
                frase += f" nell’anno {anno.strip()}"
            frase += f" sono {n}"

            st.info(frase)
    else:
        st.warning("Nessuna denominazione trovata nell'archivio. Carica prima dei PDF per popolare i dati.")
else:
    st.info("Nessun archivio ancora presente. Carica e estrai almeno un PDF per creare Conto_f24_inviati.xlsx.")

st.markdown('</div>', unsafe_allow_html=True)
