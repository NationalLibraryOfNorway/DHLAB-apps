import streamlit as st
import dhlab as dh
import pandas as pd
import datetime
from PIL import Image
from sentiment import compute_sentiment_analysis
from io import BytesIO

df_defined = False

@st.cache(suppress_st_warning=True, show_spinner=False)
def to_excel(df):
    """Make an excel object out of a dataframe as an IO-object"""
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    worksheet = writer.sheets['Sheet1']
    writer.save()
    processed_data = output.getvalue()
    return processed_data

@st.cache
def load_data(word, city, from_year, to_year, number_of_docs):
    corpus = dh.Corpus(
            doctype="digavis", 
            fulltext=word, 
            freetext=f"city: {city}",
            from_year=from_year,
            to_year = to_year,
            limit=number_of_docs
        )
    return corpus

@st.cache
def sentiment_analysis(corpus, word):
    return compute_sentiment_analysis(corpus, word)
    
st.set_page_config(page_title="Korpus", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

st.header("Sentimentanalyse")

with st.form(key="my_form"):
    word = st.text_input("Sentimentord", "biblioteket") 
    city= st.text_input("Sted", "Kristiansand") 
    today = datetime.date.today()
    year = today.year
    years = st.slider(
        'Årsspenn',
        1810, year, (1950, year))
    from_year=years[0]     
    to_year=years[1]        
    number_of_docs = st.number_input("Number of documents", value=5000)
    filnavn = st.text_input("Filnavn for nedlasting", "korpus.xlsx")

    # Submit form
    submit_button = st.form_submit_button(label = "Kjør!")

if submit_button:
    data_load_state = st.text('Loading data...')
    corpus = load_data(word, city, from_year, 
                    to_year, number_of_docs)
    data_load_state.text('Loading data...done!')

    compute_text = st.text("Computing sentiment for corpus")
    result = sentiment_analysis(corpus, word)
    compute_text.text("Finished!")

    r = result[["year","positive", "negative", "sentimentscore"]]
    rgroup = r.groupby("year")[["sentimentscore", "positive", "negative"]].sum() 
    st.pyplot(rgroup.plot().figure)

    df_defined = True
    
if df_defined:
     if st.download_button('Last ned data i excelformat', to_excel(result), filnavn, help = "Åpnes i Excel eller tilsvarende"):
        pass