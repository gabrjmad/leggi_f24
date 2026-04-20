import streamlit as st
from parser_pdf import estrai_righe_validi

st.set_page_config(page_title="Estrazione F24", layout="wide")

# Stile base ma leggibile
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
    '<div class="app-subtitle">Carica uno o più PDF e visualizza le righe con codice fiscale (11/16 caratteri).</div>',
    unsafe_allow_html=True,
)

uploaded_files = st.file_uploader(
    "Carica uno o più PDF",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"Hai caricato {len(uploaded_files)} file. Premi **Estrai dati** per procedere.")

    if st.button("Estrai dati da tutti i PDF"):
        all_rows = []
        with st.spinner("Estrazione in corso..."):
            for f in uploaded_files:
                righe = estrai_righe_validi(f)
                for r in righe:
                    r["nome_file"] = f.name
                all_rows.extend(righe)

        if not all_rows:
            st.warning("Nessuna riga trovata con codice fiscale a 11/16 caratteri nei file caricati.")
        else:
            st.success(f"Estrazione completata! Trovate {len(all_rows)} righe valide.")

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

            st.dataframe(normalized_rows, use_container_width=True)
else:
    st.info("Carica almeno un PDF per iniziare.")

st.markdown('</div>', unsafe_allow_html=True)
