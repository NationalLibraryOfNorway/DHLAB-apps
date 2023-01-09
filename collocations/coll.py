import warnings
import matplotlib.pyplot as plt
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from st_aggrid.shared import GridUpdateMode
import dhlab.api.dhlab_api as d2
import dhlab.text.conc_coll as cc
import pandas as pd
import datetime
import base64
from io import BytesIO
from random import sample
from collections import Counter
import wordcloud
import json

warnings.simplefilter(action='ignore', category=FutureWarning)

limit_conc = 10

doctypes = {'Alle dokumenter': 'all', 'Aviser': 'digavis', 'Bøker': 'digibok', 'Tidsskrift': 'digitidsskrift', 'Stortingsdokumenter': 'digistorting'}

references = {
    "generisk referanse (1800-2022)": "reference/nob-nno_1800_2022.csv",
    "nåtidig bokmål (2000-)": "reference/nob_2000_2022.csv",
    "nåtidig nynorsk (2000-)": "reference/nno_2000_2022.csv",
    "bokmål (1950-2000)": "reference/nob_1950_2000.csv",
    "nynorsk (1950-2000)": "reference/nno_1950_2000.csv",
    "bokmål (1920-1950)": "reference/nob_1920_1950.csv",
    "nynorsk (1920-1950)": "reference/nno_1920_1950.csv",
    "bokmål (1875-1920)": "reference/nob_1875_1920.csv",
    "nynorsk (1875-1920)": "reference/nno_1875_1920.csv",
    "tidlig dansk-norsk/bokmål (før 1875)": "reference/nob_1800_1875.csv",
    "tidlig nynorsk (før 1875)": "reference/nob_1848_1875.csv"
}

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

# ADAPTED FROM: https://github.com/streamlit/example-app-interactive-table/blob/main/streamlit_app.py
def aggrid_interactive_table(df: pd.DataFrame):
    """Creates an st-aggrid interactive table based on a dataframe.
    Args:
        df (pd.DataFrame]): Source dataframe
    Returns:
        dict: The selected row
    """
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True
    )

    #options.configure_side_bar()

    options.configure_selection("single")
    selection = AgGrid(
        df,
        enable_enterprise_modules=False,
        gridOptions=options.build(),
        theme="alpine",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=False
    )

    return selection

def to_excel(df, index_arg=False):
    output = BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=index_arg)

    processed_data = output.getvalue()
    return processed_data

def sampling(a, b):
    res = a
    if b < len(a):
        res = sample(a, b)
    return res

@st.cache(suppress_st_warning=True, show_spinner = False)
def get_collocation(words, corpus, before = 5, after = 5, reference = None):
    try:
        colls = cc.Collocations(words=words, corpus=corpus, before=before, after=after, reference=reference)
        colls = colls.show(sortby="relevance")
    except:
        st.error("Kollokasjoner kunne ikke hentes. Se på parametrene for korpuset/kollokasjonene eller prøv igjen. Problemet kan oppstå hvis du bruker et veldig stort korpus som strekker seg over mange år.")
        st.stop()
    return colls

def make_cloud(json_text, top=100, background='white', stretch=lambda x: 2**(10*x), width=500, height=500, font_path=None, prefer_horizontal=0.9):
    pairs0 = Counter(json_text).most_common(top)
    pairs = {x[0]:stretch(x[1]) for x in pairs0}
    wc = wordcloud.WordCloud(
        font_path=font_path,
        background_color=background,
        width=width,
        #color_func=my_colorfunc,
        ranks_only=True,
        height=height,
        prefer_horizontal=prefer_horizontal
        ).generate_from_frequencies(pairs)
    return wc

@st.cache(suppress_st_warning=True, show_spinner=False)
def get_wordcloud(data, top=10):
    scaled_data = data.sum(axis=1) / data.sum()[0]
    wc = make_cloud(json.loads(scaled_data.to_json()), top=top, background='white', font_path=None, stretch=lambda x: 2**(10*x), width=1000, height=1000, prefer_horizontal=1.0)
    return wc

@st.cache(suppress_st_warning=True, show_spinner = False)
def get_reference(corpus, from_year = 1990, to_year = 2020, limit=50000):
    return d2.get_reference(corpus, from_year = from_year, to_year = to_year, limit=limit)

@st.cache(suppress_st_warning=True, show_spinner = False)
def get_corpus(doctype="digibok", from_year=1990, to_year=2020, limit=1000, freetext=None, fulltext=None):
    try:
        corpus = d2.document_corpus(doctype=doctype, from_year=from_year, to_year=to_year, limit=limit, freetext=freetext, fulltext=fulltext)
    except:
        st.error("Korpus kunne ikke hentes. Se på parametrene for korpuset eller prøv igjen.")
        st.stop()
    return corpus

@st.cache(suppress_st_warning=True, show_spinner = False)
def get_dynamic_reference(doctype="digibok", corpus=None, limit=1000):
    try:
        # get year
        min_year = min(list(corpus["year"]))
        max_year = max(list(corpus["year"]))

        if max_year - min_year == 0:
            min_year = min_year - 1

        reference = get_reference(corpus=doctype, from_year=min_year, to_year=max_year, limit=50000)
    except:
        st.error("Dynamisk referansekorpus kunne ikke hentes. Se på parametrene for korpuset eller prøv igjen.")
        st.stop()
    return reference

@st.cache(suppress_st_warning=True, show_spinner = False)
def get_static_reference(path=None):
    try:
        reference = pd.read_csv(path, header=None)
        reference.columns = ["word", "freq"]
        reference = reference.set_index("word")
    except:
        st.error("Statisk referansekorpus kunne ikke hentes. Se på parametrene for korpuset eller prøv igjen.")
        st.stop()
    return reference

def get_concordances(corpus, query, limit=5000, window=20):
    try:
        conc = cc.Concordance(corpus, query, limit=5000, window=window)
    except:
        st.error("Konkordanser kunne ikke hentes.")
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

# Streamlit stuff
st.set_page_config(page_title="NB DH-LAB – Kollokasjoner", layout='wide')
st.title('Kollokasjoner')

st.sidebar.image('dhlab-logo-nb.png')

st.write("Appen gir deg kollokasjoner fra [DH-LAB](https://www.nb.no/dh-lab) ved Nasjonalbiblioteket. Andre apper fra oss finner du [her](https://www.nb.no/dh-lab/apper/).")

words = st.text_input("Søk", "", placeholder="Skriv inn basisord her")

uploaded_corpus = st.sidebar.file_uploader(
    "Last opp korpusdefinisjon som Excel-ark", type=["xlsx"], accept_multiple_files=False, key="corpus_upload"
)

if st.session_state.corpus_upload is None:
    title = st.sidebar.title("Korpus")
    with st.sidebar.form(key='corpus_form'):
        doctype = st.selectbox("Velg dokumenttype", doctypes.keys(), index=2, help="Velg dokumenttype som skal inngå i korpuset. Valget 'Alle dokumenter' innebærer gjerne noe mer ventetid enn å velge spesifikke dokumenttyper.")
        fulltext = st.text_input("Som inneholder fulltekst (kan stå tomt)", placeholder="jakt AND fiske", help="""Tar bare med dokumenter som inneholder ordene i dette feltet. Spørringene kan innehold enkeltord kombinert med logiske operatorer, f.eks. jakt AND fiske_, _jakt OR fiske_, fraser som "i forhold til" eller nærhetsspørringer: _NEAR(jakt fiske, 5)_. Sistnevnte finner dokumenter hvor to ord _jakt_ and _fiske_ opptrer innenfor et vindu av fem ord.""")
        from_year = st.number_input('Fra år', min_value=1500, max_value=2030, value=1990)
        to_year = st.number_input('Til år', min_value=1500, max_value=2030, value=2020)
        freetext = st.text_input("Metadata (kan stå tomt)", placeholder="""ddc:\"641.5\"""", help="""Forenklet metadatasøk. Ved å søke på enkeltord eller fraser søkes innenfor alle felt i metadatabasen. Du kan begrense spørringen til enkeltflet ved å bruke nøkkel:verdi-notasjon, f.eks. title:fisk finner alle dokumenter med _fisk_ i tittelen. Felt som kan brukes i spørringen er: _title_, _authors_, _urn_, _city_, _timestamp_ (YYYYMMDD), _year (YYYY)_, _publisher_, _langs_, _subjects_, _ddc_, _genres_, _literaryform_, _doctype_. Søk som inneholder tegnsetting, må generelt omgis med anførselstegn, f.eks. ddc: "641.5". Kombinasjoner er mulig: title:fisk AND ddc:"641.5".""")
        limit = st.number_input('Antall dokumenter i sample', value=5000)        
        submit_button = st.form_submit_button(label='Bygg korpus!')

    if freetext == "":
        freetext = None

    if fulltext == "":
        fulltext = None

    if doctype == "Alle dokumenter":
        doctype = None
    else:
        doctype = doctypes[doctype]

title = st.sidebar.title("Parametre")

reference_corpus = st.sidebar.selectbox("Velg referansekorpus", references.keys(), index=0, help="Velg referansekorpus som kollokasjonene skal beregnes på bakgrunn av.")

before = st.sidebar.slider(
    'Ord før basisord', min_value=0, max_value=50, value=5
)
after = st.sidebar.slider(
    'Ord etter basisord', min_value=0, max_value=50, value=5
)
relevance_min = st.sidebar.number_input('Terskelverdi: Relevans', value=10)
counts_min = st.sidebar.number_input('Terskelverdi: Råfrekvens', value=5)
head = st.sidebar.number_input('Maks. antall kollokasjoner som vises ', value=20)
sort_by = st.sidebar.selectbox("Sorter etter", ["Relevans", "Råfrekvens"], index=0, help="Velg om kollokasjoner skal sorteres etter relevans eller råfrekvens (etter kutting).")
reference = ""

if words == "":
    st.info("For å hente ut kollokasjoner, skriv inn basisordet som danner grunnlaget for kollokasjonsanalysen. Det er kun mulig å søke på enkeltord. Søk f.eks. på __vaksine__ for å finne ord (enkeltord) som opptrer sammen med __vaksine__.")
    st.warning("Appen lager et tilfeldig uttrekk (sample) fra hele samlingen basert på parameterne i menyen til venstre. Trykk til slutt _Bygg korpus_. Det kan være lurt å stille på disse paramaterne for å få mer kontroll over korpuset. Hvis du søker på et sjeldent ord og/eller ønsker et større uttrekk, øk sample-verdien. For å være sikker på at ord du ønsker å søke på faktisk er inneholdt i uttrekket, bruk feltet 'som inneholder fulltekst'.")
    st.stop()

if st.session_state.corpus_upload is None:
    with st.spinner('Sampler nytt korpus...'):
        corpus = get_corpus(doctype=doctype, from_year=from_year, to_year=to_year, limit=limit, freetext=freetext, fulltext=fulltext)
else:
    corpus = pd.read_excel(uploaded_corpus)

# get reference corpus
reference = get_static_reference(references[reference_corpus])

# get colls
with st.spinner('Henter kollokasjoner...'):
    colls = get_collocation(words=words, corpus=corpus, before=before, after=after, reference=reference)
colls = colls[(colls.relevance > relevance_min) & (colls.counts > counts_min)].head(head)

colls = colls.reset_index()
colls.columns = ['Kollokat', 'Råfrekvens', 'Relevans']

if sort_by == "Råfrekvens":
    colls = colls.sort_values(by="Råfrekvens", ascending=False)

# round
colls["Relevans"] = colls["Relevans"].round(2)
    
excel_colls = to_excel(colls)
excel_corpus = to_excel(corpus)

col1, col2 = st.columns(2)

if st.session_state.corpus_upload is None:
    with col1:
        st.markdown("__Korpusstørrelse:__ " + str(len(corpus)) + " dokumenter. " + "Last ned " + get_table_download_link(excel_corpus, link_content="korpusdefinisjon.", filename="corpus.xlsx"), unsafe_allow_html=True)
else:
    with col1:
        st.markdown("__Korpusstørrelse:__ " + str(len(corpus)) + " dokumenter (__opplastet korpusdefinsjon__). ",  unsafe_allow_html=True)

with col2:
    st.markdown("Last ned " + get_table_download_link(excel_colls, link_content="kollokasjonstbaell", filename="collocations.xlsx") + ".", unsafe_allow_html=True)


with col1:
    selection = aggrid_interactive_table(df=colls)
    #st.write(colls.to_html(escape=False, index=False), unsafe_allow_html=True)
with col2:
    try:
        wc = get_wordcloud(colls[["Kollokat", sort_by]].set_index("Kollokat"), top=head)
        fig, ax = plt.subplots(figsize = (5, 5))
        ax.imshow(wc)
        plt.axis("off")
        st.pyplot(fig)
    except:
        pass

try:
    if selection["selected_rows"] != []:
        selected_collword = selection["selected_rows"][0]["Kollokat"]

        query = """NEAR("%s" "%s", %s)""" % (words, selected_collword, str(int(before) + int(after)))

        with st.spinner('Henter konkordanser...'):
            conc = get_concordances(corpus, query, limit=5000, window=20)
            st.markdown("### Eksempler fra korpuset")
            print_concordances(conc)
            if conc.size > limit_conc:
                st.button('Vis flere konkordanser')
except:
    pass

st.write('\n')
st.write('\n__Bakgrunn__: Det statistiske kollokasjonsmålet som brukes her, er en variant av PMI (pointwise mutual information), med sannsynligheter som proporsjoner av frekvens, på formen: 𝑝𝑚𝑖(𝑥,𝑦)=𝑝(𝑥|𝑦)𝑝(𝑥)=𝑝(𝑦|𝑥)𝑝(𝑦). Det kan ses på som en probabilistisk versjon av relevans, dvs. at y er relevant x og omvendt. PMI er brukt i stedet for tf-idf for å beregne assosisasjoner mellom ord. PMI-verdiene er beregnet på normaliserte frekvenser (relativfrekvenser) som betyr at det faktiske tallet kan tolkes som et disproporsjonalt tall.')
