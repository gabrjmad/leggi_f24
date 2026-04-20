import streamlit as st
from parser_pdf import estrai_righe_validi

st.set_page_config(page_title="Lettore PDF CF", layout="wide")

st.title("Estrazione dati da PDF (multi-file)")
st.write("Carica uno o più PDF con elenco modelli/codici fiscali per estrarre le righe valide.")

uploaded_files = st.file_uploader(
    "Carica uno o più PDF",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} file caricati. Premi 'Estrai dati' per procedere.")

    if st.button("Estrai dati da tutti i PDF"):
        all_rows = []
        with st.spinner("Elaborazione in corso..."):
            for f in uploaded_files:
                righe = estrai_righe_validi(f)
                # aggiungo nome file come campo di contesto
                for r in righe:
                    r["nome_file"] = f.name
                all_rows.extend(righe)

        if not all_rows:
            st.warning("Nessuna riga trovata con codice fiscale a 11/16 caratteri nei file caricati.")
        else:
            st.subheader("Righe trovate")
            st.write(f"Totale righe valide: {len(all_rows)}")

            # Ordine di colonne desiderato
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
                "documenti_contenuti",
                "saldo",
                "y_top",
                "riga_completa",
            ]

            # Normalizza i dict perché alcune chiavi potrebbero mancare in casi limite
            normalized_rows = []
            for r in all_rows:
                nr = {}
                for c in cols_order:
                    nr[c] = r.get(c, "")
                normalized_rows.append(nr)

            st.dataframe(normalized_rows)

            with st.expander("Vedi output raw (JSON)", expanded=False):
                st.json(normalized_rows)
else:
    st.info("Carica almeno un PDF per iniziare.")
