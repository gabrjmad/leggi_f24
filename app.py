import io

import pandas as pd
import streamlit as st

from parser_pdf import estrai_righe_validi

st.set_page_config(page_title="Estrai il tuo PDF", layout="wide")

# Stile leggero ma leggibile + titolo integrato nel container
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
    /* Forme di sfondo integrate nel titolo */
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
        background-color: #020617;
        padding: 1rem;
        border-radius: 0.9rem;
        border: 1px dashed rgba(148, 163, 184, 0.9);
        color: #e5e7eb;
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
    .summary-box {
        background-color: #f3f4f6;
        border-radius: 0.75rem;
        padding: 1rem 1.2rem;
        border: 1px solid rgba(148, 163, 184, 0.7);
        max-height: 260px;
        overflow-y: auto;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        font-size: 0.8rem;
        color: #111827;
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
            Carica uno o più PDF con i dati F24 e genera un file Excel con le righe estratte.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 1) Upload PDF
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

if estrai_clicked:
    if not pdf_files:
        st.warning("Carica almeno un PDF prima di estrarre i dati.")
    else:
        all_rows = []
        with st.spinner("Estrazione in corso..."):
            for f in pdf_files:
                righe = estrai_righe_validi(f)
                all_rows.extend(righe)

        if not all_rows:
            st.warning("Nessuna riga trovata con codice fiscale a 11/16 caratteri nei PDF caricati.")
        else:
            st.success(f"Estrazione completata! Trovate {len(all_rows)} righe valide.")

            # Salva in session_state per fase successiva
            st.session_state["extracted_rows"] = all_rows

            # Riepilogo: solo numero + elenco
            st.markdown('<div class="summary-title">Righe individuate</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="summary-count">Totale: <strong>{len(all_rows)}</strong></div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div class="summary-box">', unsafe_allow_html=True)
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
                st.text(line)
            st.markdown('</div>', unsafe_allow_html=True)

# 3) Genera subito e scarica (senza tasto Conferma)
if "extracted_rows" in st.session_state:
    rows = st.session_state["extracted_rows"]
    if rows:
        df = pd.DataFrame(rows)

        df_excel = pd.DataFrame({
            "Anno": df.get("anno", ""),
            "Cod_Fisc": df.get("codice_fiscale", ""),
            "Denominazione": df.get("nominativo", ""),
            "gruppo_riferimento": df.get("gruppo_riferimento", ""),
            "regime_contabile": df.get("regime_contabile", ""),
            "Codice_ditta": df.get("codice_ditta", ""),
            "Tipo": df.get("tipo_f24", ""),
        })

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_excel.to_excel(writer, sheet_name="Foglio1", index=False)
        output.seek(0)

        st.success("File Excel generato. Ora puoi scaricarlo.")

        download_col = st.columns(3)
        with download_col[1]:
            st.download_button(
                label="Scarica file Excel",
                data=output,
                file_name="Cartel1_estratto.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

st.markdown('</div>', unsafe_allow_html=True)
