
from collections import Counter
import streamlit as st
#import spacy_streamlit

import pandas as pd
from PIL import Image
import urllib

import datetime


#print(year)

import dhlab as dh
import dhlab.api.dhlab_api as api
from dhlab.text.nbtokenizer import tokenize
# for excelnedlastning
from io import BytesIO

st.set_page_config(page_title="Korpus", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)


max_size_corpus = 20000
max_rows = 1200
min_rows = 800
default_size = 10 # percent of max_size_corpus

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

def v(x):
    if x != "":
        res = x
    else:
        res = None
    return res

### Headers

col_zero, col_one, col_two, col_three = st.columns(4)
with col_two:
    st.header("Konstruer et korpus" )
    st.markdown("""Les mer om DH-labens apper på [DHLAB-siden](https://nb.no/dh-lab)""")

with col_zero:    
    image = Image.open("DHlab_logo_web_en_black.png")
    st.image(image, width=250)

    
df_defined = False
with st.form(key='my_form'):
    st.subheader('Tekst-type og periode')
    col1, col2 = st.columns(2)
    
    with col1:
        doctype = st.selectbox(
            "Type dokument", 
            ["digibok", "digavis", "digitidsskrift", "digimanus"], 
            help="Dokumenttypene følger Nasjonalbibliotekets digitale typer")
        
    with col2:
        today = datetime.date.today()
        year = today.year
        years = st.slider(
        'Årsspenn',
        1810, year, (1950, year))

   
    
    st.subheader("Forfatter og tittel") ###################################################
    cola, colb = st.columns(2)
    with cola:
            author = st.text_input("Forfatter", "", help="Feltet blir kun tatt hensyn til for digibok")

    with colb:
            title = st.text_input("Tittel", "", help = "Søk etter titler. For aviser vil tittel matche avisnavnet.")

    st.subheader("Meta- og innholdsdata") ##########################################################

    
    cold, cole, colf, colg = st.columns(4)
    with cold:        
        fulltext = st.text_input(
            "Ord eller fraser i teksten", 
            "", 
            help = "Matching på innholdsord skiller ikke mellom stor og liten bokstav."
                " Trunkert søk er mulig, slik at demokrat* vil finne bøker som inneholder demokrati og demokratisk blant andre treff")
    
    with cole:
        ddk = st.text_input("Dewey desimaltall", "", help="Input matcher et deweynummer. For å matche hele serien føy til en `*`. Bruk OR for å kombinere: 364* OR 916*")
        # if ddk != "" and not ddk.endswith("!"):
        #     ddk = f"{ddk}*"
        # if ddk.endswith("!"):
        #     ddk = ddk[:-1]
            
    with colf:
        subject = st.text_input("Emneord","", help="For å matche på flere emner, skill med OR for alternativ"
                                " og AND for begrense. Trunkert søk går også — for eksempel vil barne* matche barnebok og barnebøker")
        
    with colg:
        lang = st.multiselect(
            "Språk", 
            ["nob", "nno", "dan", "swe", "sme", "smj", "fkv", "eng", "fra", "spa", "ger"],  
            default = "nob",                   
            help="Velg fra listen"
        )
        lang = " OR ".join(list(lang))
        if lang == "":
            lang = None
    
    st.subheader("Organisering") ######################################################################
    
    colx, coly = st.columns(2)
    with colx:
        limit = st.number_input(f"Maksimum antall dokument i korpuset, inntil {max_size_corpus}", min_value=1, max_value = max_size_corpus, value = int(default_size*max_size_corpus/100))
    
    with coly:
        filnavn = st.text_input("Filnavn for nedlasting", "korpus.xlsx")
    
        
    if doctype in ['digimanus']:
        df = dh.Corpus(doctype=v(doctype), limit=limit)
        columns = ['urn','title']
    elif doctype in ['digavis']:
        df = dh.Corpus(doctype=v(doctype), fulltext= v(fulltext), from_year = years[0], to_year = years[1], title=v(title), limit=limit)
        columns = ['urn','title', 'year', 'timestamp', 'city']
    elif doctype in ['digitidsskrift']:
        df = dh.Corpus(doctype=v(doctype), author=v(author), fulltext=fulltext, from_year = years[0], to_year = years[1], title=v(title), subject=v(subject), ddk= v(ddk), lang=lang, limit=limit)
        columns = ['dhlabid', 'urn', 'title','city','timestamp','year', 'publisher', 'ddc', 'langs']
    else:
        df = dh.Corpus(doctype=v(doctype), author=v(author), fulltext=v(fulltext), from_year = years[0], to_year = years[1], title=v(title), subject=v(subject), ddk= v(ddk), lang=lang, limit=limit)
        columns = ['dhlabid', 'urn', 'authors', 'title','city','timestamp','year', 'publisher', 'ddc','subjects', 'langs']

    

    submit_button = st.form_submit_button(label = "Trykk her når korpusdefinisjonen er klar")
    
    if submit_button:
        st.markdown(f"Fant totalt {df.size} dokumenter")
        if df.size >= max_rows:
            st.markdown(f"Viser {min_rows} rader.")
            st.dataframe(df.corpus.sample(min(min_rows, max_rows)))
        else:
            st.dataframe(df.corpus[columns])
        df_defined = True
        
    
if df_defined:
    if st.download_button('Last ned data i excelformat', to_excel(df.corpus), filnavn, help = "Åpnes i Excel eller tilsvarende"):
        pass
