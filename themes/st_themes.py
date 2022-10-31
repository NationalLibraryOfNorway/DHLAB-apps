"""Streamlit script automatically fetched from source repo: Yoonsen/Document_thematic_analysis"""

import streamlit as st
import dhlab.text as dh
import dhlab.api.dhlab_api as api
from dhlab import graph_networkx_louvain as gnl
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image
import requests
from streamlit_agraph import agraph, TripleStore, Config, Node, Edge
import re

maxlen = 250
antall_dokument = 30


@st.cache(suppress_st_warning=True, show_spinner = False)
def theme_book(urn = None, reference = None, chunksize= 1000, maxval = 0.9, minval = 0.2):
    chunk0 = dh.Chunks(urn= urn, chunks = chunksize)
    df0 = pd.DataFrame(chunk0.chunks).transpose().fillna(0)
    count0 = df0.sum(axis = 1)
    if not reference is None: 
        relevance0 = ((count0/count0.sum())/(reference[reference.columns[0]]/reference[reference.columns[0]].sum())).dropna()
    else:
        units = df0/df0
        (rows, cols) = units.shape
        words_from_chunks = units[minval < units.sum(axis = 1)/cols][units.sum(axis = 1)/cols < maxval].index
        relevance0 = count0.loc[words_from_chunks]/count0.loc[words_from_chunks].sum()
    words = relevance0.sort_values(ascending=False).head(250).index
    prod = df0.loc[words].dot(df0.loc[words].transpose())
    return prod

@st.cache(suppress_st_warning=True, show_spinner = False)
def theme_book_list(urn = None, words = None, chunksize= 1000):
    chunk0 = dh.Chunks(urn= urn, chunks = chunksize)
    df0 = pd.DataFrame(chunk0.chunks).transpose().fillna(0)
    count0 = df0.sum(axis = 1)
    prod = []
    small_list = [x for x in words[:maxlen] if x in df0.index]
    if small_list != []:
        prod = df0.loc[small_list].dot(df0.loc[small_list].transpose())
    return prod


@st.cache(suppress_st_warning=True, show_spinner = False)
def get_corpus(freetext=None, title=None, number = 20):
    if not freetext is None:
        c = dh.Corpus(freetext=freetext, title=title, limit = number)
    else:
        c = dh.Corpus(doctype="digibok", limit = number)
    return c.corpus

@st.cache(suppress_st_warning=True, show_spinner = False)
def totals(n = 300000):
    return api.totals(n)



st.image("dhlab-logo-nb.png")
st.markdown("""Les mer på [DHLAB-siden](https://nb.no/dh-lab)""")



st.title('Temaer i tekst')

uploaded_corpus = st.sidebar.file_uploader(
    "Last opp korpusdefinisjon som Excel-ark", type=["xlsx"], accept_multiple_files=False, key="corpus_upload"
)


# select URN
# Using the "with" syntax

if st.session_state.corpus_upload is None:
    stikkord = st.text_input('Angi noen stikkord for å forme et utvalg tekster, og velg fra listen under. For å se en avis, skriv navnet på avisen eventuelt sammen med årstall, eller bare lim inn en URN')
else:
    stikkord = ''

urn = []
if stikkord == '':
    stikkord = None

# elif uploaded_corpus.boolean:
#      urn =   uploaded_corpus.urn 

else:
    urn = re.findall("URN:NBN[^ ]+", stikkord)
    if urn != []:
        urn = urn[0]
        
 #, from_year=period[0], to_year=period[1])

relevance_list = st.checkbox("Bruk automatisk ordliste", value = True, help="klikk for å legge inn egen kommaseparert ordlist")
if relevance_list:
    with st.form(key='my_form'):
            refsize = st.number_input("Størrelse på referansekorpus", 
                                      min_value = 20000, max_value = 500000, value = 200000)
            ref = totals(refsize)
            chunksize = st.number_input("Størrelse på chunk (300 og oppover)", 
                                        min_value = 300, value = 1000)

            #antall_dokument = st.number_input("Antall dokument fra 10 til 100", 
            #                                  min_value = 10, max_value = 100, value = 20)
            if urn == []:
                # corpus = get_corpus(freetext=stikkord, number = antall_dokument)
                
                if st.session_state.corpus_upload is None:
                    corpus = get_corpus(freetext=stikkord, number = antall_dokument)
                else:
                    corpus = pd.read_excel(uploaded_corpus)
                
                choices = [', '.join([str(z) for z in x]) for x in corpus[['authors','title', 'year','urn']].values.tolist()]
                valg = st.selectbox("Velg et dokument", choices)
                urn = valg.split(', ')[-1]
                
            submit_button = st.form_submit_button(label='Finn tema!')

            #create graph and themes

            prod = theme_book(urn = urn, reference = ref, maxval = 0.4, chunksize= chunksize)
            try:
                G = nx.from_pandas_adjacency(prod)
                comm =  gnl.community_dict(G)
            except:
                comm = dict()
            
            if submit_button:
                st.markdown("## Temaer")
                st.write('\n\n'.join(['**{label}** {value}'.format(label = key, value = ', '.join(comm[key])) for key in comm]))

else:
    with st.form(key='my_form'):
            words = st.text_input("Angi en liste av ord skilt med komma", "")
            try:
                wordlist = [x.strip() for x in words.split(',')]
            except:
                wordlist = []

            chunksize = st.number_input("Størrelse på chunk (300 og oppover)", min_value = 300, value = 1000)

            #antall_dokument = st.number_input("Antall dokument fra 10 til 100", min_value = 10, max_value = 100, value = 20)
            if st.session_state.corpus_upload is None:
                corpus = get_corpus(freetext=stikkord, number = antall_dokument)
            else:
                corpus = pd.read_excel(uploaded_corpus)
            
            choices = [', '.join([str(z) for z in x]) for x in corpus[['authors','title', 'year','urn']].values.tolist()]
            valg = st.selectbox("Velg et dokument", choices)
            urn = valg.split(', ')[-1]
            submit_button = st.form_submit_button(label='Finn tema!')

            # create graph and themes

            prod = theme_book_list(urn = urn, words = wordlist, chunksize = chunksize)
            try:
                G = nx.from_pandas_adjacency(prod)
                comm =  gnl.community_dict(G)
            except:
                comm = dict()
            if submit_button:
                st.markdown("## Temaer")
                st.write('\n\n'.join(['**{label}** {value}'.format(label = key, value = ', '.join(comm[key])) for key in comm]))



