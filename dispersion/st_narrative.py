import streamlit as st
import dhlab.text as dh
from PIL import Image
import pandas as pd


@st.cache(suppress_st_warning=True, show_spinner = False)
def get_corpus(doctype="digibok", from_year=1990, to_year=2020, limit=1000, freetext=None, fulltext=None):
    try:
        corpus = dh.Corpus(doctype=doctype, from_year=from_year, to_year=to_year, limit=limit, freetext=freetext, fulltext=fulltext)
    except:
        st.error("Korpus kunne ikke hentes. Se på parametrene for korpuset eller prøv igjen.")
        st.stop()
    return corpus.corpus


@st.cache(suppress_st_warning=True, show_spinner = False)
def get_dispersion(urn = None, wordbag = None, window=1500, pr=100):
    d = dh.Dispersion(urn=urn, wordbag=wordbag, window=window, pr=pr)
    return d



#st.set_page_config(layout="wide")

st.sidebar.image('dhlab-logo-nb.png')
st.sidebar.markdown("""Les mer om DH-laben [her](https://nb.no/dh-lab).""")


st.title('Ord i tekst - Narrative buer')


doctypes = {'Alle dokumenter': 'all', 'Aviser': 'digavis', 'Bøker': 'digibok', 'Tidsskrift': 'digitidsskrift', 'Stortingsdokumenter': 'digistorting'}

title = st.sidebar.title("Korpus")
uploaded_corpus = st.sidebar.file_uploader(
    "Last opp korpusdefinisjon som Excel-ark", type=["xlsx"], accept_multiple_files=False, key="corpus_upload"
)

if st.session_state.corpus_upload is None:
    st.sidebar.markdown("""Bygg korpus selv""")

    with st.sidebar.form(key='corpus_form'):
        doctype = st.selectbox("Velg dokumenttype", doctypes.keys(), index=2, help="Velg dokumenttype som skal inngå i korpuset.")
        fulltext = st.text_input("Som inneholder fulltekst (kan stå tomt)", placeholder="jakt AND fiske", help="""Tar bare med dokumenter som inneholder ordene i dette feltet. Spørringene kan innehold enkeltord kombinert med logiske operatorer, f.eks. jakt AND fiske_, _jakt OR fiske_, fraser som "i forhold til" eller nærhetsspørringer: _NEAR(jakt fiske, 5)_. Sistnevnte finner dokumenter hvor to ord _jakt_ and _fiske_ opptrer innenfor et vindu av fem ord.""")
        stikkord = st.text_input('Angi noen stikkord.')
        from_year,to_year = st.slider('Begrens listen til årsperiode', 1800, 2022, (1980, 2020))
        freetext = st.text_input("Metadata (kan stå tomt)", placeholder="""ddc:"641.5" """, help="""Forenklet metadatasøk. Ved å søke på enkeltord eller fraser søkes innenfor alle felt i metadatabasen. Du kan begrense spørringen til enkeltflet ved å bruke nøkkel:verdi-notasjon, f.eks. title:fisk finner alle dokumenter med _fisk_ i tittelen. Felt som kan brukes i spørringen er: _title_, _authors_, _urn_, _city_, _timestamp_ (YYYYMMDD), _year (YYYY)_, _publisher_, _langs_, _subjects_, _ddc_, _genres_, _literaryform_, _doctype_. Tegnsetting kan generelt ikke brukes i søket, unntaket er i ddc. Kombinasjoner er mulig: title:fisk AND ddc:641.5.""")
        limit = st.number_input('Antall dokumenter i sample', value=1000)
        submit_button = st.form_submit_button(label='Hent korpus!')

    if fulltext == "":
        fulltext = None

    if freetext == "":
        freetext = None

    if doctype == "Alle dokumenter":
        doctype = None
    else:
        doctype = doctypes[doctype]

# override if uploaded
if st.session_state.corpus_upload is None:
    with st.spinner('Sampler nytt korpus...'):
        corpus = get_corpus(doctype=doctype, from_year=from_year, to_year=to_year, limit=limit, freetext=freetext, fulltext=fulltext)
else:
    corpus = pd.read_excel(uploaded_corpus)


title2 = st.sidebar.title("Parametere for graf")
window = st.sidebar.number_input("Størrelse på tekst det telles i (vindu)", min_value = 300, value=500)
pr = st.sidebar.number_input("Antall steg mellom hvert vindu", min_value = 100, value=100)


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
