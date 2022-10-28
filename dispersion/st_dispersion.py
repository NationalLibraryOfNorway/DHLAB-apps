"""Streamlit script fetched and modified from source repo: Yoonsen/narrative-buer, file: st_narrative.py"""

import streamlit as st
import dhlab.text as dh
from PIL import Image
import pandas as pd


@st.cache(suppress_st_warning=True, show_spinner = False)
def get_corpus(freetext=None, title=None, from_year=1900, to_year=2020):
    try: 
        c = dh.Corpus(freetext=freetext, title=title,from_year=from_year, to_year=to_year)
    except: 
        st.error("Korpus kunne ikke hentes. Se på parametrene for korpuset eller prøv igjen.")
        st.stop()
    return c.corpus


@st.cache(suppress_st_warning=True, show_spinner = False)
def get_dispersion(urn = None, wordbag = None, window=1500, pr=100):
    d = dh.Dispersion(urn=urn, wordbag=wordbag, window=window, pr=pr)
    return d


st.title('Ord i tekst - Narrative buer')


#st.set_page_config(layout="wide")

st.sidebar.image('dhlab-logo-nb.png')
st.sidebar.markdown("""Les mer om DH-laben [her](https://nb.no/dh-lab).""")

uploaded_corpus = st.sidebar.file_uploader(
    "Last opp en ferdig korpusdefinisjon fra et Excel-ark", type=["xlsx"], accept_multiple_files=False, key="corpus_upload"
)

window = st.sidebar.number_input("Størrelse på tekst det telles i (vindu)", min_value = 300, value=500)
pr = st. sidebar.number_input("Antall steg mellom hvert vindu", min_value = 100, value=100)


if st.session_state.corpus_upload is None:
    st.markdown("""Definer et korpus med stikkord og velg en tekst fra nedtrekkslisten.""")
    stikkord = st.text_input("Angi noen stikkord")
    stikkord = stikkord if stikkord != '' else None
    from_year,to_year = st.slider('Begrens tidsperioden for tekstutvalget', 1800, 2022, (1980, 2020))

# override if uploaded
if st.session_state.corpus_upload is None:
    with st.spinner('Sampler nytt korpus...'):
        corpus = get_corpus(freetext=stikkord, from_year=from_year, to_year=to_year)
else:
    corpus = pd.read_excel(uploaded_corpus)

#st.write(corpus)
choices = [', '.join([str(z) for z in x]) for x in corpus[['authors','title', 'year','urn']].values.tolist()]
valg = st.selectbox("Velg et dokument fra korpuset", choices)

urn = valg.split(', ')[-1]


words = st.text_input('Angi ord som skal telles', '. ,')
words = words.split()

try:
    dispersion = get_dispersion(urn=urn, wordbag=words, window=window, pr=pr)
    st.line_chart(dispersion.dispersion)
except:
    st.write(f"Noe gikk galt med {' '.join(valg.split()[:-1])}, prøve et annet dokument")
