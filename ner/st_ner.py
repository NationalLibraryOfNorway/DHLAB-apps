"""Streamlit script automatically fetched from source repo: Yoonsen/NER"""

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

st.set_page_config(layout="wide")

@st.cache(suppress_st_warning=True, show_spinner = False)
def get_corpus(freetext=None, title=None, from_year=1900, to_year=2020):
    c = dh.Corpus(freetext=freetext, title=title,from_year=from_year, to_year=to_year)
    return c.corpus


@st.cache(suppress_st_warning=True, show_spinner = False)
def get_ner(urn, model):
    df = dh.NER(urn = urn, model = model).ner
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
    df = dh.POS(urn = urn, model = model).pos
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

image = Image.open('NB-logo-no-eng-svart.png')
st.image(image, width = 200)
st.markdown('Les om [Digital Humaniora - DH](https://nb.no/dh-lab) ved Nasjonalbiblioteket. Koden benytter modeller for norsk utviklet for [spaCy](https://spacy.io/models/nb). ')


st.title('Personer og steder')


stikkord = st.text_input('Angi noen stikkord for å forme et utvalg tekster, som for eksempel forfatter og tittel for bøker eller avisnavn. For aviser kan du også velge dato på formaet YYYYMMDD. Velg deretter et dokument fra listen under og trykk på knappen "Finn navn og steder"')
period = st.slider('Begrens listen til en periode', 1800, 2022, (1800, 2022))
if stikkord == '':
    stikkord = None
corpus = get_corpus(freetext=stikkord, from_year=period[0], to_year=period[1])

choices = [', '.join([str(z) for z in x]) for x in corpus[['authors','title', 'year','urn']].values.tolist()]

df_defined = False


if choices != []:
    with st.form(key='my_form'):
        filename = st.text_input('For å lagre dataene angir du et filnavn og trykker på \
        nedlastningsknappen som dukker opp under dataene', 'analyse.xlsx')
        if not filename.endswith('.xlsx'):
            filename = f"{filename}.xlsx"
        valg = st.selectbox("Velg et dokument", choices)
        urn = valg.split(', ')[-1]

        colA, colB = st.columns(2)
        
        with colA:
            analyse_type = st.selectbox("Velg analysetype - navn (NER) eller kategorier (POS)", ['NER', 'POS'])
            
        with colB:
            model = st.selectbox("Velg en språkmodell", dh.Models().models, help= "Forskjellige modeller gir \
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
        