"""Streamlit script automatically fetched from source repo: Yoonsen/Word_to_topics"""

import dhlab as dh
import streamlit as st
import pandas as pd
import re
from collections import Counter

@st.cache(suppress_st_warning=True, show_spinner=False)
def get_topic_counts(corpus = None):
    emneord =  Counter([x.strip() 
                        for y in corpus.subjects.values 
                        for x in set(y.split('/')) 
                        if isinstance(y, str)])
    
    emner = pd.DataFrame.from_dict(emneord, orient='index', columns=["frekvens"]).sort_values(by = 'frekvens', ascending=False)
    return emner

st.set_page_config(
    page_title="Emneord", 
    page_icon=None, 
    layout="wide",
    initial_sidebar_state="auto", 
    menu_items=None
)

st.sidebar.markdown("Velg et korpus fra [corpus-appen](https://beta.nb.no/dhlab/corpus/)" 
                    " eller hent en eller flere URNer fra nb.no eller andre steder")


corpus_defined = False
urner = st.sidebar.text_area("Lim inn URNer:","", help="Lim en tekst som har URNer i seg. Teksten trenger ikke å være formatert")
if urner != "":
    urns = re.findall("URN:NBN[^\s.,]+", urner)
    if urns != []:
        corpus_defined = True
        corpus = dh.Corpus(doctype='digibok',limit=0)
        corpus.extend_from_identifiers(urns)
        #st.write(urns)
    else:
        st.write('Fant ingen URNer')

uploaded_file = st.sidebar.file_uploader("Last opp et korpus", help="Dra en fil over hit, fra et nedlastningsikon, eller velg fra en mappe")
if uploaded_file is not None:
    corpus_defined = True
    dataframe = pd.read_excel(uploaded_file)

    corpus = dh.Corpus(doctype='digibok',limit=0)
    corpus.extend_from_identifiers(list(dataframe.urn))

# if corpus_defined:
#     st.sidebar.subheader('Korpus')
#     st.sidebar.write("Viser et lite utvalg på inntil tyve tekster fra korpuset")
#     st.session_state['corpus'] = corpus
#     corpus.corpus.dhlabid = corpus.corpus.dhlabid.astype(int)
#     corpus.corpus.year = corpus.corpus.year.astype(int)
#     st.sidebar.write(corpus.corpus.sample(min(len(corpus.corpus), 20))["title authors year".split()])

    


st.header('Inspiser emneord')

col1, col2 = st.columns(2)
with col1:
    types = st.selectbox("Vis emneord som starter med:", ['hva som helst', 'stor bokstav', 'liten bokstav'])
with col2:
    st.write("Relativ frekvens")
    percent = st.checkbox("Vis % ", value = False)

if corpus_defined:
    #st.write(corpus_defined, len(corpus.corpus))
    corpusdf = corpus.corpus[~corpus.corpus.subjects.isnull()]
    emner = get_topic_counts(corpusdf)
    if types == "stor bokstav":
        df = emner[emner.index.str.istitle()]
    elif type == "liten bokstav":
        df = emner[emner.index.str.islower()]
    else:
        df = emner
    
    if percent == True:
        df = (df*100/df.sum()).style.format(precision=1)
    
    st.write(df)