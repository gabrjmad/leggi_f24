import streamlit as st
from parser_pdf import estrai_righe_validi

st.set_page_config(page_title="Lettore PDF CF", layout="centered")

st.title("Estrazione dati da PDF")
st.write("Carica un PDF con elenco modelli / codici fiscali per estrarre le righe valide.")

uploaded_file = st.file_uploader("Carica il PDF", type=["pdf"])

if uploaded_file is not None:
    st.success("File caricato. Premi 'Estrai dati' per procedere.")

    if st.button("Estrai dati"):
        with st.spinner("Elaborazione in corso..."):
            righe = estrai_righe_validi(uploaded_file)

        if not righe:
            st.warning("Nessuna riga trovata con codice fiscale a 11/16 caratteri.")
        else:
            st.subheader("Righe trovate")
            st.write(f"Totale righe valide: {len(righe)}")

            # Mostra in tabella
            # Trovi solo alcune colonne chiave, puoi aggiungerne altre dalla funzione
            st.dataframe(
                [
                    {
                        "Pagina": r["page"],
                        "Y_top": r["y_top"],
                        "Codice Fiscale": r["codice_fiscale"],
                        "Nominativo": r["nominativo"],
                        "Riga completa": r["riga_completa"],
                    }
                    for r in righe
                ]
            )

            # Mostra anche il JSON raw se ti è utile per debug
            with st.expander("Vedi output raw (JSON)", expanded=False):
                st.json(righe)
else:
    st.info("Carica un PDF per iniziare.")
