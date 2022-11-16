
from collections import Counter
import streamlit as st
#import spacy_streamlit

import pandas as pd
from PIL import Image
import urllib


import dhlab as dh
import dhlab.api.dhlab_api as api
from dhlab.text.nbtokenizer import tokenize
# for excelnedlastning
from io import BytesIO

import re

@st.cache(suppress_st_warning=True, show_spinner = False)
def get_corpus(freetext=None, title=None, from_year=1900, to_year=2020):
    c = dh.Corpus(freetext=freetext, title=title,from_year=from_year, to_year=to_year)
    return c.corpus


@st.cache(suppress_st_warning=True, show_spinner = False)
def get_ner(urn, model):
    df = dh.NER(urn = urn, model = model).ner.set_index('token')
    df_defined = True
    personer = df[df["ner"].str.contains("PER")] 
    steder = df[df['ner'].str.contains('LOC')]
    organisasjoner = df[df["ner"].str.contains("ORG")]
    produkter =  df[df["ner"].str.contains("PROD")]

    andre = df[
        (~df["ner"].str.contains("PER")) &
        (~df.ner.str.contains('ORG')) &
        (~df.ner.str.contains('PROD')) &
        (~df['ner'].str.contains('LOC'))]
    return df, personer, steder, organisasjoner, produkter, andre

@st.cache(suppress_st_warning=True, show_spinner = False)
def get_pos(urn, model):
    df = dh.POS(urn = urn, model = model).pos.set_index('token')
    df_defined = True
    noun = df[df.pos.str.contains('NOUN')]
    verb = df[df.pos.str.contains('VERB')]
    adj = df[df.pos.str.contains('ADJ')]
    prep = df[df.pos.str.contains('ADP')]
    andre = df[
        (~df.pos.str.contains("NOUN")) &
        (~df.pos.str.contains('VERB')) &
        (~df.pos.str.contains('ADJ')) &
        (~df.pos.str.contains('ADP'))]
    return df, noun, verb, adj, prep, andre

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

############################################################################################3
#
#   C O D E
#
#

st.set_page_config(layout="wide")

head_col1,_,_,head_col2, head_col3 = st.columns(5)

with head_col1:
    st.title('Navn og steder')
with head_col2:
    st.markdown('Les mer om [Digital Humaniora - DH](https://nb.no/dh-lab)')
    st.markdown('og språkmodellen i [spaCy](https://spacy.io/models/nb). ')
with head_col3:
    image = Image.open("DHlab_logo_web_en_black.png")
    st.image(image)
# Three possible corpora

corpus_defined = False

st.markdown("----")
st.markdown("####  Definer en gruppe tekster fra URNer, korpus eller stikkord")

icol1, icol2 = st.columns(2)
with icol1:
    method = st.selectbox("Metode", options=['Stikkord', 'Urnliste', 'Excelkorpus'], help="Lim inn en tekst med URNer, eller last opp et excelark med korpus"
                         " lagd for eksempel med https://beta.nb.no/dhlab/korpus/, eller antyd en grupper tekster ved hjelp av stikkord")
with icol2:
    if method == 'Urnliste':
        urner = st.text_area("Lim inn URNer:","", help="Lim en tekst som har URNer i seg. Teksten trenger ikke å være formatert")
        if urner != "":
            urns = re.findall("URN:NBN[^\s.,]+", urner)
            if urns != []:
                corpus_defined = True
                corpus = dh.Corpus(doctype='digibok',limit=0)
                corpus.extend_from_identifiers(urns)
                corpus = corpus.corpus
                #st.write(corpus)
            else:
                st.write('Fant ingen URNer')
    elif method == 'Excelkorpus':
        uploaded_file = st.file_uploader("Last opp et korpus", help="Dra en fil over hit, fra et nedlastningsikon, eller velg fra en mappe")
        if uploaded_file is not None:
            corpus_defined = True
            dataframe = pd.read_excel(uploaded_file)
            corpus = dh.Corpus(doctype='digibok',limit=0)
            corpus.extend_from_identifiers(list(dataframe.urn))
            corpus = corpus.corpus
        
    else:
        stikkord = st.text_input('Angi noen stikkord for å forme et utvalg tekster','', 
                                 help="For eksempel forfatter og tittel for bøker eller avisnavn. For aviser kan du også velge dato på formaet YYYYMMDD.")

        if stikkord == '':
            stikkord = None
        corpus_defined = True
        corpus = get_corpus(freetext=stikkord)

if corpus_defined:
    choices = [', '.join([str(z) for z in x]) for x in corpus[['authors','title', 'year','urn']].values.tolist()]
else:
    choices = []
 
st.markdown("#### Velg tekst for analyse og navn på resultatfil")
    
df_defined = False

if choices != []:
    txt_col1, txt_col2 = st.columns(2)
    with txt_col1:
        valg = st.selectbox("Tekst", choices)
        urn = valg.split(', ')[-1]
        fname = urn.split('-')[-1]
    with txt_col2:
        filename = st.text_input('Foreslått filnavn', f"{fname}.xlsx")
        
    if not filename.endswith('.xlsx'):
        filename = f"{filename}.xlsx"
    
    st.markdown("#### Angi språkmodell og type analyse NER eller POS")
    with st.form(key='my_form'):
            
        
            
        colA, colB = st.columns(2)
        
        with colA:
            analyse_type = st.selectbox("Analysetype - navn (NER) eller kategorier (POS)", ['NER', 'POS'])
            
        with colB:
            model = st.selectbox("Språkmodell", dh.Models().models, help= "Forskjellige modeller gir \
        forskjellig resultat - da for dansk og nb for norsk bokmål")
            
        submit_button = st.form_submit_button(label=f'Analyser URN', help = "det kan ta inntil \
        et halvt minutt å analysere teksten")
        
        if submit_button and analyse_type == 'NER':
            df, personer, steder, organisasjoner, produkter, andre = get_ner(urn, model)
            df_defined = True

            col1, col2, col3, col4, col5 = st.columns(5)
            

            with col1:

                st.header("Navn")
                st.dataframe(personer.sort_values(by='frekv', ascending = False))

            with col2:

                st.header("Steder")
                st.dataframe(steder.sort_values(by='frekv', ascending = False))    

            with col3:

                st.header("Organisasjoner")
                st.dataframe(organisasjoner.sort_values(by='frekv', ascending = False))

            with col4:

                st.header("Produkter")
                st.dataframe(produkter.sort_values(by='frekv', ascending = False))

            with col5:

                st.header("Andre")
                st.dataframe(andre)
        elif submit_button and analyse_type == 'POS':
            df, noun, verb, adjektiv, prep, andre = get_pos(urn, model)
            df_defined = True

            col1, col2, col3, col4, col5 = st.columns(5)
            

            with col1:

                st.header("Substantiv")
                st.dataframe(noun.sort_values(by='frekv', ascending = False))

            with col2:

                st.header("Verb")
                st.dataframe(verb.sort_values(by='frekv', ascending = False))    

            with col3:

                st.header("Adjektiv")
                st.dataframe(adjektiv.sort_values(by='frekv', ascending = False))

            with col4:

                st.header("Preposisjoner")
                st.dataframe(prep.sort_values(by='frekv', ascending = False))

            with col5:

                st.header("Andre")
                st.dataframe(andre)
            
    if df_defined:
        if st.download_button('Last ned data i excelformat', to_excel(df),filename, help = "Åpnes i Excel eller tilsvarende"):
            True
else:
    st.write("Her dukker det opp en tekstvelger så snart listen av tekster er definert")