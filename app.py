import streamlit as st
from parser_pdf import estrai_righe_validi

# Config pagina
st.set_page_config(page_title="Estrazione F24", layout="wide")

# CSS personalizzato per stile moderno
st.markdown(
    """
    <style>
    /* Sfondo blu della pagina */
    .stApp {
        background-color: #0f172a; /* blu scuro tipo slate */
        color: #e5e7eb;           /* testo chiaro */
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    /* Titolo */
    h1, h2, h3 {
        color: #e5e7eb;
    }

    /* Container principale con bordo leggero */
    .main-container {
        background-color: #111827;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #1f2937;
    }

    /* Bottoni viola */
    .stButton>button {
        background: linear-gradient(135deg, #8b5cf6, #7c3aed);
        color: white;
        border-radius: 999px;
        padding: 0.4rem 1.4rem;
        border: none;
        font-weight: 600;
        cursor: pointer;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #a855f7, #8b5cf6);
    }

    /* File uploader box */
    .stFileUploader {
        background-color: #020617;
        padding: 1rem;
        border-radius: 0.75rem;
        border: 1px dashed #4b5563;
    }

    /* Dataframe styling */
    .dataframe tbody tr:nth-child(odd) {
        background-color: #020617 !important;
    }
    .dataframe tbody tr:nth-child(even) {
        background-color: #111827 !important;
    }
    .dataframe thead tr {
        background-color: #1f2937 !important;
        color: #e5e7eb !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.title("Estrazione dati F24 da PDF")
st.write("Carica uno o più PDF e ottieni i dati strutturati per ogni riga valida (codice fiscale, nominativo, ecc.).")

uploaded_files = st.file_uploader(
    "Carica uno o più PDF",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"Hai caricato {len(uploaded_files)} file. Premi **Estrai dati** per procedere.")

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

            # Tabella più moderna: usiamo st.dataframe con altezza dinamica
            st.dataframe(
                normalized_rows,
                use_container_width=True,
            )

            with st.expander("Vedi output JSON (per debug)", expanded=False):
                st.json(normalized_rows)
else:
    st.info("Carica almeno un PDF per iniziare.")

st.markdown('</div>', unsafe_allow_html=True)
