import streamlit as st
from parser_pdf import estrai_righe_validi

# Config pagina
st.set_page_config(page_title="Estrazione F24", layout="wide")

# CSS personalizzato per stile moderno
st.markdown(
    """
    <style>
    /* Sfondo blu acceso */
    .stApp {
        background: radial-gradient(circle at top left, #3b82f6 0, #0f172a 45%, #020617 100%);
        color: #e5e7eb;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    /* Container centrale "card" */
    .main-container {
        background-color: rgba(15, 23, 42, 0.92);
        padding: 1.75rem;
        border-radius: 1rem;
        border: 1px solid rgba(59, 130, 246, 0.35);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.9);
    }

    /* Header compatta, solo testo + bottoni */
    .header-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .header-title-left {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }

    .header-title-left h1 {
        font-size: 1.6rem;
        margin: 0;
        color: #f9fafb;
    }

    .header-subtitle {
        font-size: 0.9rem;
        color: #cbd5f5;
        margin: 0;
        opacity: 0.9;
    }

    /* Bottoni moderni */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1, #3b82f6);
        color: #f9fafb;
        border-radius: 999px;
        padding: 0.45rem 1.6rem;
        border: none;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.45);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #818cf8, #60a5fa);
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.65);
    }

    /* Upload box */
    .stFileUploader {
        background-color: #020617;
        padding: 0.9rem;
        border-radius: 0.75rem;
        border: 1px dashed rgba(148, 163, 184, 0.7);
    }

    /* Messaggi (success, warning, info) */
    .stAlert {
        border-radius: 0.75rem;
    }

    /* Tabella: bordi e colori in tema */
    .dataframe {
        border-radius: 0.75rem !important;
        overflow: hidden !important;
        border: 1px solid rgba(148, 163, 184, 0.5);
    }
    .dataframe table {
        border-collapse: collapse !important;
        width: 100%;
        font-size: 0.88rem;
    }
    .dataframe thead tr {
        background-color: #0f172a !important;
        color: #e5e7eb !important;
        border-bottom: 1px solid rgba(148, 163, 184, 0.8);
    }
    .dataframe thead th {
        padding: 0.55rem 0.75rem !important;
        white-space: nowrap;
    }
    .dataframe tbody tr {
        border-bottom: 1px solid rgba(31, 41, 55, 0.9);
    }
    .dataframe tbody tr:nth-child(odd) {
        background-color: #020617 !important;
    }
    .dataframe tbody tr:nth-child(even) {
        background-color: #02081f !important;
    }
    .dataframe tbody td {
        padding: 0.4rem 0.75rem !important;
        color: #e5e7eb !important;
    }
    .dataframe tbody tr:hover {
        background-color: rgba(37, 99, 235, 0.25) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header compatta
st.markdown(
    """
    <div class="header-title">
        <div class="header-title-left">
            <h1>Estrazione dati F24 da PDF</h1>
            <p class="header-subtitle">
                Carica uno o più file PDF e visualizza i dati strutturati per ogni riga con codice fiscale.
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_files = st.file_uploader(
    "Carica uno o più PDF",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"Hai caricato {len(uploaded_files)} file. Quando sei pronto, clicca su **Estrai dati**.")

    if st.button("Estrai dati da tutti i PDF"):
        all_rows = []
        with st.spinner("Estrazione in corso, attendi qualche secondo..."):
            for f in uploaded_files:
                righe = estrai_righe_validi(f)
                for r in righe:
                    r["nome_file"] = f.name
                all_rows.extend(righe)

        if not all_rows:
            st.warning("Nessuna riga trovata con codice fiscale a 11/16 caratteri nei file caricati.")
        else:
            st.success(f"Estrazione completata! Trovate {len(all_rows)} righe valide.")

            st.subheader("Risultati estratti")

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
                nr = {}
                for c in cols_order:
                    nr[c] = r.get(c, "")
                normalized_rows.append(nr)

            st.dataframe(
                normalized_rows,
                use_container_width=True,
            )

            with st.expander("Vedi output JSON (per debug)", expanded=False):
                st.json(normalized_rows)
else:
    st.info("Carica almeno un PDF per iniziare.")

st.markdown('</div>', unsafe_allow_html=True)
