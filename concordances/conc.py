import streamlit as st
import dhlab.api.dhlab_api as d2
import dhlab.text.conc_coll as cc
import pandas as pd
import datetime
import base64
from io import BytesIO
from random import sample

doctypes = {'Alle dokumenter': 'all', 'Aviser': 'digavis', 'Bøker': 'digibok', 'Tidsskrift': 'digitidsskrift', 'Stortingsdokumenter': 'digistorting'}

# ADAPTED FROM: https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def get_table_download_link(content, link_content="XLSX", filename="corpus.xlsx"):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    try:
        b64 = base64.b64encode(content.encode()).decode()  # some strings <-> bytes conversions necessary here
    except:
        b64 = base64.b64encode(content).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_content}</a>'
    return href

def to_excel(df, index_arg=False):
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=index_arg)

    processed_data = output.getvalue()
    return processed_data

@st.cache(suppress_st_warning=True, show_spinner = False)
def get_corpus(doctype="digibok", from_year=1990, to_year=2020, limit=1000, freetext=None, fulltext=None):
    try:
        corpus = d2.document_corpus(doctype=doctype, from_year=from_year, to_year=to_year, limit=limit, freetext=freetext, fulltext=fulltext)
    except:
        st.error("Korpus kunne ikke hentes. Se på parametrene for korpuset eller prøv igjen.")
        st.stop()
    return corpus

@st.cache(suppress_st_warning=True, show_spinner = False)
def get_concordances(corpus, query, limit=5000, window=20):
    try:
        conc = cc.Concordance(corpus, query, limit=5000, window=window)
    except:
        st.error("Konkordanser kunne ikke hentes. Se på parametrene for konkordans eller prøv igjen.")
        st.stop()
    return conc

def print_concordances(conc):
    for row in conc.show(n=min(limit_conc, conc.size), style = False).iterrows():
        urn = row[1]["urn"]
        metadata = corpus[corpus["urn"] == urn][['title', 'authors', 'year', 'timestamp']]
        metadata = metadata.iloc[0]

        if 'digavis' in urn:
            timestamp = metadata["timestamp"]
        else:
            timestamp = metadata["year"]

        if metadata["authors"] is None:
            metadata["authors"] = ""
        if metadata["title"] is None:
            metadata["title"] = ""

        url = "https://urn.nb.no/%s" % (urn)
        link = "<a href='%s' target='_blank'>%s – %s – %s</a>" % (url, metadata["title"], metadata["authors"], timestamp)

        conc_markdown = row[1]["concordance"].replace('<b>', '**')
        conc_markdown = conc_markdown.replace('</b>', '**')
        html = "%s %s" % (link, conc_markdown)
        st.markdown(html, unsafe_allow_html=True)

st.set_page_config(page_title="NB DH-LAB – Konkordanser", layout='wide')

# Streamlit stuff
st.title('Konkordanser')

st.sidebar.image('dhlab-logo-nb.png')

st.write("Appen gir deg konkordanser - nøkkelord med kontekst - fra [DH-LAB](https://www.nb.no/dh-lab) ved Nasjonalbiblioteket. Andre apper fra oss finner du [her](https://www.nb.no/dh-lab/apper/).")

query = st.text_input("Søk", "", placeholder="Skriv inn søkeuttrykk her")

uploaded_corpus = st.sidebar.file_uploader(
    "Last opp korpusdefinisjon som Excel-ark", type=["xlsx"], accept_multiple_files=False,  key="corpus_upload"
)

if st.session_state.corpus_upload is None:
    title = st.sidebar.title("Korpus")

    with st.sidebar.form(key='corpus_form'):
        doctype = st.selectbox("Velg dokumenttype", doctypes.keys(), index=2, help="Velg dokumenttype som skal inngå i korpuset. Valget 'Alle dokumenter' innebærer gjerne noe mer ventetid enn å velge spesifikke dokumenttyper.")
        fulltext = st.text_input("Som inneholder fulltekst (kan stå tomt)", placeholder="jakt AND fiske", help="""Tar bare med dokumenter som inneholder ordene i dette feltet. Spørringene kan innehold enkeltord kombinert med logiske operatorer, f.eks. jakt AND fiske_, _jakt OR fiske_, fraser som "i forhold til" eller nærhetsspørringer: _NEAR(jakt fiske, 5)_. Sistnevnte finner dokumenter hvor to ord _jakt_ and _fiske_ opptrer innenfor et vindu av fem ord.""")
        from_year = st.number_input('Fra år', min_value=1500, max_value=2030, value=1990)
        to_year = st.number_input('Til år', min_value=1500, max_value=2030, value=2020)
        freetext = st.text_input("Metadata (kan stå tomt)", placeholder="""ddc:\"641.5\" """, help="""Forenklet metadatasøk. Ved å søke på enkeltord eller fraser søkes innenfor alle felt i metadatabasen. Du kan begrense spørringen til enkeltflet ved å bruke nøkkel:verdi-notasjon, f.eks. title:fisk finner alle dokumenter med _fisk_ i tittelen. Felt som kan brukes i spørringen er: _title_, _authors_, _urn_, _city_, _timestamp_ (YYYYMMDD), _year (YYYY)_, _publisher_, _langs_, _subjects_, _ddc_, _genres_, _literaryform_, _doctype_. Søk som inneholder tegnsetting, må generelt omgis med anførselstegn, f.eks. ddc: "641.5". Kombinasjoner er mulig: title:fisk AND ddc:"641.5".""")
        limit = st.number_input('Antall dokumenter i sample', value=1000)
        submit_button = st.form_submit_button(label='Bygg korpus!')

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

title = st.sidebar.title("Parametre for konkordans")

limit_conc = st.sidebar.number_input('Antall konkordanser i sample', value=10)

window = st.sidebar.number_input('Konkordansevindu (antall ord rundt søkeord)', min_value=1, max_value=25, value=20)

if query == "":
    st.info("For å søke, skriv inn et ord, flere ord eller en frase i anførselstegn. Søkemotoren gir treff på avsnittsnivå. Hvis det er flere treff innenfor et avsnitt, vil kun første treff fra det aktuelle avsnittet vises. Hvis det ikke oppgis en logisk operator (AND, OR, NOT), vil logisk AND brukes. Søket __vaksine forskning__ gir altså treff i avsnitt som inneholder både ordet __vaksine__ og __forskning__. Det er også mulig å angi et to ord skal stå i nærheten av hverandre, f.eks. vil NEAR(vaksine forskning, 5) gi kontekster der __vaksine__ og __forskning__ opptrer innenfor et vindu av fem ord. ")
    st.warning("Appen lager et tilfeldig uttrekk (sample) fra hele samlingen basert på parameterne i menyen til venstre. Det kan være lurt å stille på disse paramaterne for å få mer kontroll over korpuset. Hvis du søker på et sjeldent ord og/eller ønsker et større uttrekk, øk sample-verdien. For å være sikker på at ord du ønsker å søke på faktisk er inneholdt i uttrekket, bruk feltet 'som inneholder fulltekst'.")
    st.stop()

with st.spinner('Henter konkordanser...'):
    conc = get_concordances(corpus, query, limit=5000, window=window)

excel_corpus = to_excel(corpus)
excel_conc = to_excel(conc.concordance)

show_number = min(conc.size, limit_conc)

col1, col2, col3 = st.columns(3)

if st.session_state.corpus_upload is None:
    with col1:
        st.markdown("__Korpusstørrelse:__ " + str(len(corpus)) + " dokumenter. " + "Last ned " + get_table_download_link(excel_corpus, link_content="korpusdefinisjon.", filename="corpus.xlsx"), unsafe_allow_html=True)
else:
    with col1:
        st.markdown("__Korpusstørrelse:__ " + str(len(corpus)) + " dokumenter (__opplastet korpusdefinsjon__). ",  unsafe_allow_html=True)

with col2:
    st.markdown("__Treff__: " + str(conc.size) + " treff, viser " + str(show_number) + "." + " Last ned " + get_table_download_link(excel_conc, link_content="konkordanser", filename="concordances.xlsx") + ".", unsafe_allow_html=True)

if conc.size > limit_conc:
    with col3:
        st.button('Hent flere konkordanser')

st.markdown("- - -")

print_concordances(conc)





