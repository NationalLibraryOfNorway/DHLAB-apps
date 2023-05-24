import datetime
from io import BytesIO

import pandas as pd
import streamlit as st
import dhlab as dh

from sentiment import compute_sentiment_analysis


df_defined = False

@st.cache_data
def to_excel(df):
    """Make an excel object out of a dataframe as an IO-object"""
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)

    processed_data = output.getvalue()
    return processed_data

@st.cache_data
def load_data(doctype, word, city, from_year, to_year, number_of_docs):
    corpus = dh.Corpus(
            doctype=doctype,
            fulltext=word,
            freetext=f"city: {city}" if city is not None else None,
            from_year=from_year,
            to_year = to_year,
            limit=number_of_docs
        )
    return corpus

@st.cache_data
def sentiment_analysis(corpus, word):
    return compute_sentiment_analysis(corpus, word)

@st.cache_data
def plot_result(result):
    r = result[["year","positive", "negative", "sentimentscore"]]
    rgroup = r.groupby("year")[["sentimentscore", "positive", "negative"]].sum()

    st.pyplot(rgroup.plot().figure)


## Page layout
st.set_page_config(page_title="Sentiment", layout="wide", initial_sidebar_state="auto")

## Headers
st.markdown("""<style>
img {
  opacity: 1.0;
}
</style><a href="https://nb.no/dhlab">
  <img src="https://github.com/Sprakbanken/sentimentanalyse/blob/main/dhlab-logo-nb.png" style="width:250px"></a>""",
   unsafe_allow_html = True
)
st.title("Sentimentanalyse")

st.write("Søk etter et nøkkelord, og få ut en graf over positive og negative ord som forekommer sammen med nøkkelordet.")

today = datetime.date.today()
year = today.year

## Sidebar
st.sidebar.header("Tekstutvalg")
loaded_corpus = st.sidebar.file_uploader(
    "Last opp korpusdefinisjon som Excel-ark", type=["xlsx"], accept_multiple_files=False, key="corpus_upload"
)

st.sidebar.subheader("Definer nytt korpus med metadata")
with st.sidebar.form(key='corpus_form'):
    word = st.text_input(
        "Nøkkelord",
        "bibliotek",
        help="Ord som skal forekomme i tekstutvalget.")
    doctype = st.selectbox(
        "Type dokument",
        ["digibok", "digavis", "digitidsskrift", "digimanus", "digistorting"],
        help="Velg dokumenttype som skal inngå i korpuset. Valgmulighetene følger Nasjonalbibliotekets digitale dokumenttyper."
    )
    city= st.text_input(
        "Sted",
        "Kristiansand",
        disabled=(doctype not in ['digavis', 'digibok']),
        help='Dersom dokumenttypen er "digavis" eller "digibok" kan du også avgrense på publiseringssted.'
    )
    if city == "":
        city = None
    from_year = st.number_input('Fra år', min_value=1800, max_value=year, value=2000)
    to_year = st.number_input('Til år', min_value=1800, max_value=year, value=year)
    number_of_docs = st.number_input("Antall dokumenter", value=5000)
    submit_button = st.form_submit_button(label='Hent tekstutvalg')
    if submit_button:
        load_text = st.text('Laster inn korpus...')
        corpus = load_data(doctype, word, city, from_year, to_year, number_of_docs).frame
        load_text.text('Korpuset er lastet inn.')

if st.session_state.corpus_upload is not None:
    corpus = pd.read_excel(loaded_corpus)

st.sidebar.write("---")
st.sidebar.write("Flere apper fra [DH-laben](https://www.nb.no/dh-lab) finner du [her](https://www.nb.no/dh-lab/apper/).")

## User input
with st.form(key="analysis_form"):
    word = st.text_input("Sentimentord", word, help="Ord som skal analyseres. Sentimentscoren regnes ut fra hvor mange av ordene i konteksten rundt sentimentordet som er positive eller negative.")
    # Submit form
    submit_button = st.form_submit_button(label = "Kjør!")

if submit_button:
    try:
        #("Regner ut sentimentscore for ordet i korpuset")
        result = sentiment_analysis(corpus, word)
        df_defined = True
    except NameError:
        st.write("Last inn et korpus og prøv igjen.")

if df_defined:
    plot_result(result)
    filnavn = st.text_input("Filnavn for nedlasting", f"sentimentscore_{word}_{today}.xlsx")
    if st.download_button('Last ned data i excelformat', to_excel(result), filnavn, help = "Åpnes i Excel eller tilsvarende regnearkprogram."):
        pass
