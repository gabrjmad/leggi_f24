import io
import pandas as pd
import streamlit as st
from parser_pdf import estrai_righe_validi

st.set_page_config(page_title="PDF → Excel F24", layout="wide")

# CSS per UI centrata, colori leggibili
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top, #1d4ed8 0, #020617 55%);
        color: #e5e7eb;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .center-wrapper {
        display: flex;
        justify-content: center;
        align-items: flex-start;
        min-height: 100vh;
    }

    .card {
        background-color: rgba(15, 23, 42, 0.96);
        padding: 2rem 2.5rem;
        border-radius: 1rem;
        border: 1px solid rgba(148, 163, 184, 0.5);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.9);
        max-width: 900px;
        width: 100%;
        margin-top: 2rem;
    }

    .app-title {
        font-size: 1.7rem;
        margin-bottom: 0.3rem;
        color: #f9fafb;
        font-weight: 650;
        text-align: center;
    }

    .app-subtitle {
        font-size: 0.95rem;
        color: #c7d2fe;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* Bottoni */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1, #3b82f6);
        color: #f9fafb;
        border-radius: 999px;
        padding: 0.45rem 1.7rem;
        border: none;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.5);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #818cf8, #60a5fa);
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.7);
    }

    /* File uploader leggibile */
    .stFileUploader {
        background-color: #020617;
        padding: 0.9rem;
        border-radius: 0.75rem;
        border: 1px dashed rgba(148, 163, 184, 0.8);
        color: #e5e7eb;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-size: 0.9rem;
        color: #e5e7eb !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="center-wrapper"><div class="card">', unsafe_allow_html=True)

st.markdown('<div class="app-title">PDF → Excel F24</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Estrai righe valide dai PDF e aggiungile in fondo al tuo file Excel.</div>',
    unsafe_allow_html=True,
)

st.write("### 1. Carica i file")

col1, col2 = st.columns(2)

with col1:
    pdf_files = st.file_uploader(
        "PDF (uno o più file)",
        type=["pdf"],
        accept_multiple_files=True,
        help="File con elenco modelli / codici fiscali"
    )

with col2:
    excel_file = st.file_uploader(
        "File Excel base (Cartel1.xlsx)",
        type=["xlsx"],
        help="Verrà usato come base e aggiornato con nuove righe"
    )

extracted_rows = None

st.write("---")
st.write("### 2. Estrai dati dai PDF")

if st.button("Estrai righe valide dai PDF"):
    if not pdf_files:
        st.warning("Carica almeno un PDF prima di estrarre i dati.")
    elif not excel_file:
        st.warning("Carica il file Excel base (Cartel1.xlsx) prima di procedere.")
    else:
        all_rows = []
        with st.spinner("Estrazione in corso..."):
            for f in pdf_files:
                righe = estrai_righe_validi(f)
                all_rows.extend(righe)

        if not all_rows:
            st.warning("Nessuna riga con codice fiscale (11/16 caratteri) trovata nei PDF caricati.")
        else:
            extracted_rows = all_rows
            st.success(f"Estrazione completata: trovate {len(all_rows)} righe valide.")

            # Riepilogo sintetico
            st.write("#### Riepilogo righe da aggiungere")
            st.write("Vedrai un elenco compatto delle nuove righe che verranno inserite in fondo all'Excel:")

            # Mostra solo uno snapshot testuale, non una grande tabella
            preview_lines = []
            for r in all_rows:
                line = (
                    f"Anno={r.get('Anno', '')} | "
                    f"Cod_Fisc={r.get('Cod_Fisc', '')} | "
                    f"Denominazione={r.get('Denominazione', '')} | "
                    f"Gruppo={r.get('gruppo_riferimento', '')} | "
                    f"Regime={r.get('regime_contabile', '')} | "
                    f"Cod_ditta={r.get('Codice_ditta', '')} | "
                    f"Tipo={r.get('Tipo', '')}"
                )
                preview_lines.append(line)

            # Per non inondare, mostra tutte ma in un expander scrollabile
            with st.expander("Mostra elenco completo delle righe che verranno aggiunte", expanded=True):
                for line in preview_lines:
                    st.text(line)

            # Salviamo nelle session_state per usarlo nel passo 3
            st.session_state["extracted_rows"] = all_rows
            st.session_state["excel_file_bytes"] = excel_file.read()

st.write("---")
st.write("### 3. Conferma e scarica l'Excel aggiornato")

if "extracted_rows" in st.session_state and "excel_file_bytes" in st.session_state:
    if st.button("Conferma e scarica"):
        # Carica l'Excel base in DataFrame (Foglio1)
        base_bytes = st.session_state["excel_file_bytes"]
        base_buffer = io.BytesIO(base_bytes)
        xls = pd.ExcelFile(base_buffer)
        df_base = pd.read_excel(xls, sheet_name="Foglio1")

        # Converte le righe estratte in DataFrame con le stesse colonne
        nuovi_df = pd.DataFrame(st.session_state["extracted_rows"])
        # Riordino le colonne per sicurezza
        nuovi_df = nuovi_df[["Anno", "Cod_Fisc", "Denominazione",
                             "gruppo_riferimento", "regime_contabile",
                             "Codice_ditta", "Tipo"]]

        # Aggiungi in fondo
        df_aggiornato = pd.concat([df_base, nuovi_df], ignore_index=True)

        # Scrivi su un nuovo Excel in memoria, preservando anche Foglio2
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Scrivi Foglio1 aggiornato
            df_aggiornato.to_excel(writer, sheet_name="Foglio1", index=False)

            # Copia eventuali altri fogli (es. Foglio2) se presenti
            for sheet_name in xls.sheet_names:
                if sheet_name == "Foglio1":
                    continue
                df_other = pd.read_excel(xls, sheet_name=sheet_name)
                df_other.to_excel(writer, sheet_name=sheet_name, index=False)

        output.seek(0)

        st.success("File Excel aggiornato pronto per il download.")
        st.download_button(
            label="Scarica file Excel aggiornato",
            data=output,
            file_name="Cartel1_aggiornato.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
else:
    st.info("Prima estrai i dati dai PDF e verifica il riepilogo, poi potrai confermare e scaricare l'Excel aggiornato.")
    
st.markdown("</div></div>", unsafe_allow_html=True)
