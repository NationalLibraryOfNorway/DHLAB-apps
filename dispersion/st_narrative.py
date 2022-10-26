import streamlit as st
import dhlab.text as dh
from PIL import Image



@st.cache(suppress_st_warning=True, show_spinner = False)
def get_corpus(freetext=None, title=None, from_year=1900, to_year=2020):
    c = dh.Corpus(freetext=freetext, title=title,from_year=from_year, to_year=to_year)
    return c.corpus

@st.cache(suppress_st_warning=True, show_spinner = False)
def get_dispersion(urn = None, wordbag = None, window=1500, pr=100):
    d = dh.Dispersion(urn=urn, wordbag=wordbag, window=window, pr=pr)
    return d



#st.set_page_config(layout="wide")

image = Image.open("dhlab-logo-nb.png")
st.image(image)
st.markdown("""Les mer på [DHLAB-siden](https://nb.no/dh-lab)""")


st.title('Ord i tekst - Narrative buer')

window = st.sidebar.number_input("Størrelse på tekst det telles i (vindu)", min_value = 300, value=500)
pr = st. sidebar.number_input("Antall steg mellom hvert vindu", min_value = 100, value=100)

stikkord = st.text_input('Angi noen stikkord for å forme et utvalg tekster, og velg fra listen under')
period = st.slider('Begrens listen til år', 1800, 2022, (1980, 2020))
#tittel = st.text_input("Tittel på bok eller avis")

if stikkord == '':
    stikkord = None
corpus = get_corpus(freetext=stikkord, from_year=period[0], to_year=period[1])

#st.write(corpus)
choices = [', '.join([str(z) for z in x]) for x in corpus[['authors','title', 'year','urn']].values.tolist()]
valg = st.selectbox("Velg et dokument", choices)

urn = valg.split(', ')[-1]


words = st.text_input('Angi ord som skal telles', '. ,')
words = words.split()

try:
    dispersion = get_dispersion(urn=urn, wordbag=words, window=window, pr=pr)
    st.line_chart(dispersion.dispersion)
except:
    st.write(f"Noe gikk galt med {' '.join(valg.split()[:-1])}, prøve et annet dokument")
