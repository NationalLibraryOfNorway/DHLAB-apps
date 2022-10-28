"""Streamlit script automatically fetched from source repo: Yoonsen/ngram_gui"""

import streamlit as st
import dhlab.text as dh
import dhlab.ngram as ng
import dhlab.api.dhlab_api as api

import datetime

import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image



@st.cache(suppress_st_warning=True, show_spinner=False)
def get_ngram(words=None,
    from_year=None,
    to_year=None,
    doctype=None,
    lang='nob',
             mode = 'relative'):
    
    a = ng.Ngram(words, from_year=from_year, to_year=to_year, doctype=doctype, lang=lang, mode = mode).ngram
    a.index = pd.to_datetime(a.index, format='%Y')
    return a

st.set_page_config(layout="wide")

if 'smooth' not in st.session_state:
    st.session_state['smooth'] = 4

if 'years' not in st.session_state:
    st.session_state['years'] = (1954, datetime.date.today().year)


text = st.text_input("Ord og fraser", "")
words = [x.strip() for x in text.split(',')]

cola1, cola2, cola3 = st.columns(3)

with cola1:
    korpus = st.selectbox("Korpus", options = ['avis', 'bok'], help="Velg mellom bøker og aviser")

with cola2:
    if korpus != 'avis':
        lang = st.selectbox("Språk-kode", options = ['nob','nno', 'sme', 'fkv'], help = "Sett ISO språk-kode for å velge språk eller målform")
    else:
        st.write("___")
        lang = None
        
with cola3:
    kumulativ = False
    kohort = False
    mode = st.selectbox("Frekvenstype", ['relativ', 'abslutt', 'kumulativ', 'kohort'], help = "Vis kurven med relative tall, absolutt frekvens (sett glatting til minimum) eller kumulativ frekvens. Alternativet kohort viser innbyrdes forhold mellom ordene.")
    if mode == 'kumulativ':
        kumulativ = True
        mode = 'absolutt'
    if mode == 'kohort':
        kohort = True
        mode = 'absolutt'

    
ngram = get_ngram(
    words=words, 
    from_year = st.session_state['years'][0], 
    to_year = st.session_state['years'][1], 
    doctype = korpus, 
    lang = lang, 
    mode=mode
)

if kumulativ:
    chart = ngram.cumsum()
    
elif kohort:
    chart = (ngram.transpose()/ngram.sum(axis=1)).transpose().rolling(window = st.session_state['smooth'], win_type='triang').mean()
    
else:
    chart = ngram.rolling(window = st.session_state['smooth'], win_type='triang').mean()

st.line_chart(chart)

colb1, colb2 = st.columns(2)
with colb1:
    smooth = st.slider("Glatting", min_value=1, max_value = 10, value=st.session_state['smooth'], key='smooth', help="Angir hvordan kurven jevnes ut - uten effekt for kumulativ graf")
    
with colb2:
    years = st.slider('Periode', 1810, datetime.date.today().year, st.session_state['years'], key="years", help = "Start- og sluttår for kurven")

    
st.session_state.update()