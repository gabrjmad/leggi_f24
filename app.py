import io

import pandas as pd
import streamlit as st

from parser_pdf import estrai_righe_validi

st.set_page_config(page_title="Estrazione F24", layout="wide")

# Stile base ma leggibile (come versione funzionante)
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top, #1d4ed8 0, #020617 55%);
        color: #e5e7eb;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .main-container {
        background-color: rgba(15, 23, 42, 0.96);
        padding: 1.5rem 2rem;
        border-radius: 1rem;
        border: 1px solid rgba(148, 163, 184, 0.5);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.9);
        max-width: 1100px;
        margin: 2rem auto;
    }
    .app-title {
        font-size: 1.7rem;
        margin-bottom: 0.3rem;
        color: #f9fafb;
        font-weight: 650;
        text-align: left;
    }
    .app-subtitle {
        font-size: 0.95rem;
        color: #c7d2fe;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #6366f1, #3b82f6);
        color: #f9fafb;
        border-radius: 999px;
        padding: 0.4rem 1.4rem;
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
    .stFileUploader {
        background-color: #020617;
        padding: 0.9rem;
        border-radius: 0.75rem;
        border: 1px dashed rgba(148, 163, 184, 0.8);
        color: #e5e7eb;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown('<div class="app-title">Estrazione dati F24 da PDF</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Carica uno o più PDF e un file Excel base (Cartel1.xlsx). '
    'Le righe estratte verranno aggiunte in fondo al Foglio1.</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    uploaded_files = st.file_uploader(
        "Carica uno o più PDF",
        type=["pdf"],
        accept_multiple_files=True
    )

with col2:
    excel_file = st.file_uploader(
        "Carica file Excel base (Cartel1.xlsx)",
        type=["xlsx"],
        help="Verrà usato come base per aggiungere le nuove righe"
    )

st.write("---")
st.write("### 1. Estrai i dati dai PDF")

if uploaded_files and excel_file:
    st.success(f"Hai caricato {len(uploaded_files)} PDF e un file Excel. Premi **Estrai dati** per procedere.")
elif uploaded_files and not excel_file:
    st.info("Hai caricato dei PDF. Carica anche il file Excel base per poter aggiornare i dati.")
elif excel_file and not uploaded_files:
    st.info("Hai caricato il file Excel base. Carica almeno un PDF per estrarre i dati.")
else:
    st.info("Carica almeno un PDF e il file Excel base per iniziare.")

if st.button("Estrai dati da tutti i PDF"):
    if not uploaded_files:
        st.warning("Carica almeno un PDF prima di estrarre i dati.")
    elif not excel_file:
        st.warning("Carica il file Excel base (Cartel1.xlsx) prima di estrarre i dati.")
    else:
        all_rows = []
        with st.spinner("Estrazione in corso..."):
            for f in uploaded_files:
                righe = estrai_righe_validi(f)
                for r in righe:
                    r["nome_file"] = f.name
                all_rows.extend(righe)

        if not all_rows:
            st.warning("Nessuna riga trovata con codice fiscale a 11/16 caratteri nei PDF caricati.")
        else:
            st.success(f"Estrazione completata! Trovate {len(all_rows)} righe valide.")

            # Salva in session_state per il passo successivo (riepilogo+Excel)
            st.session_state["extracted_rows"] = all_rows
            # Leggiamo il file Excel una sola volta e memorizziamo i bytes
            st.session_state["excel_base_bytes"] = excel_file.read()

            # Tabella (utile per verificare che la logica funzioni ancora)
            cols_order = [
                "nome_file",
                "pagina",
                "codice_fiscale",
                "nominativo",
                "gruppo_riferimento",
                "regime_contabile",
                "codice_ditta",
                "anno",
                "tipo_f24",
                "quantita_f24_inviati",
            ]
            normalized_rows = []
            for r in all_rows:
                nr = {c: r.get(c, "") for c in cols_order}
                normalized_rows.append(nr)

            st.write("Tabella di controllo dei dati estratti (per verifica):")
            st.dataframe(normalized_rows, use_container_width=True)

            # Riepilogo sintetico delle righe che andranno in Excel
            st.write("#### Riepilogo righe che verranno aggiunte al Foglio1 dell'Excel:")
            preview_lines = []
            for r in all_rows:
                line = (
                    f"Anno={r.get('anno', '')} | "
                    f"Cod_Fisc={r.get('codice_fiscale', '')} | "
                    f"Denominazione={r.get('nominativo', '')} | "
                    f"Gruppo={r.get('gruppo_riferimento', '')} | "
                    f"Regime={r.get('regime_contabile', '')} | "
                    f"Cod_ditta={r.get('codice_ditta', '')} | "
                    f"Tipo={r.get('tipo_f24', '')}"
                )
                preview_lines.append(line)

            for line in preview_lines:
                st.text(line)

st.write("---")
st.write("### 2. Conferma e scarica il file Excel aggiornato")

if "extracted_rows" in st.session_state and "excel_base_bytes" in st.session_state:
    if st.button("Conferma e scarica"):
        # Carichiamo l'Excel base
        base_bytes = st.session_state["excel_base_bytes"]
        base_buffer = io.BytesIO(base_bytes)
        xls = pd.ExcelFile(base_buffer)

        # Foglio1 esistente
        df_base = pd.read_excel(xls, sheet_name="Foglio1")

        # Nuove righe dai PDF, mappate nell'ordine richiesto da Cartel1.xlsx
        nuovi = st.session_state["extracted_rows"]
        df_nuovi = pd.DataFrame(nuovi)

        # Selezioniamo e rinominiamo le colonne per matchare l'Excel:
        # Anno, Cod_Fisc, Denominazione, gruppo_riferimento, regime_contabile, Codice_ditta, Tipo
        df_nuovi_excel = pd.DataFrame({
            "Anno": df_nuovi.get("anno", ""),
            "Cod_Fisc": df_nuovi.get("codice_fiscale", ""),
            "Denominazione": df_nuovi.get("nominativo", ""),
            "gruppo_riferimento": df_nuovi.get("gruppo_riferimento", ""),
            "regime_contabile": df_nuovi.get("regime_contabile", ""),
            "Codice_ditta": df_nuovi.get("codice_ditta", ""),
            "Tipo": df_nuovi.get("tipo_f24", ""),
        })

        # Append in fondo
        df_aggiornato = pd.concat([df_base, df_nuovi_excel], ignore_index=True)

        # Scriviamo un nuovo Excel in memoria, preservando gli altri fogli
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Foglio1 aggiornato
            df_aggiornato.to_excel(writer, sheet_name="Foglio1", index=False)

            # Copia altri fogli (es. Foglio2) se presenti
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
    st.info("Per abilitare il download devi prima estrarre i dati dai PDF e vedere il riepilogo.")

st.markdown('</div>', unsafe_allow_html=True)
