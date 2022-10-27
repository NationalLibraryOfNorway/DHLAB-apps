import dhlab as dh
import streamlit as st
import pandas as pd
import re
normal_size = 800
max_doc = 1200

@st.cache(suppress_st_warning=True, show_spinner=False)
def get_counts(words = None, corpus = None):
    try:
        res = dh.Counts(corpus, words=words).counts
    except:
        res = pd.DataFrame()
    return res

st.set_page_config(page_title="DTM", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

st.sidebar.markdown("Velg et korpus fra [corpus-appen](https://beta.nb.no/dhlab/corpus/) eller hent en eller flere URNer fra nb.no eller andre steder")


# todo: add logo dhlab-logo-nb.png

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
    st.sidebar.subheader('Korpus')
    corpus = dh.Corpus(doctype='digibok',limit=0)
    corpus.extend_from_identifiers(list(dataframe.urn))

if corpus_defined:
    if corpus.size > 1:
        st.sidebar.write(f"Korpuset består av {corpus.size} dokumenter")
        if corpus.size > max_doc:
            st.sidebar.write(f"Siden korpuset er ganske stort, arbeides det videre med et utvalg. "
                            "Utvalget vil endre seg fra søk til søk")
            samplesize = st.sidebar.number_input("Utvalgsstørrelse", 1, normal_size, int(normal_size/2))
            corpus.corpus = corpus.corpus.sample(int(samplesize))
            corpus.size = 500
    elif corpus.size == 1:
        st.sidebar.write("Korpuset er ett dokument")
    else:
        st.sidebar.write("Tom korpus")
        
    st.session_state['corpus'] = corpus
    try:
        corpus.corpus.dhlabid = corpus.corpus.dhlabid.astype(int)
        corpus.corpus.year = corpus.corpus.year.astype(int)
    except:
        pass
    #st.sidebar.write(corpus.corpus.sample(min(len(corpus.corpus), 20))["title authors year".split()])

    


st.header('Inspiser ordfrekvenser')
st.markdown("Velg et korpus av bøker, aviser, tidsskrift eller manuskript ved hjelp av sidefeltet. Skriv inn ordene du vil undersøke i feltet under for å se hvor mange ganger de forekommer i de enkelte dokumentene.")

if "search_term" not in st.session_state:
    search = ""
else:
    search = st.session_state['search_term']

if corpus_defined:
    #st.write(corpus_defined, len(corpus.corpus))
    corpusdf = corpus.corpus
    
    with st.form("my_form"):
        col1, col2 = st.columns(2)
        with col1:
            words = st.text_input(
                "Frekvenser for en liste ord", 
                search, 
                key="search_term", 
                help="Skriv inn ordene skilt med komma. For å ta med komma, legg inn et til slutt")
            words = [w.strip() for w in words.split(',')]
            if "" in words:
                words.append(',')
            #st.write(words)
            words = [w for w in words if w != ""]
            if words == [',']:
                words = ['.',',','!',"?", ';']
            words = list(set(words))
            df = get_counts(words = words, corpus = corpus)

        with col2:
            columns = st.multiselect("Hvordan skal dokumentene vises", 
                                     options=list(corpusdf.columns),
                                     default=['authors', 'title', 'year'], 
                                     help="Plukk ut metadata som beskriver "
                                     "dokumentene eller skiller dem fra hverandre")

            if columns == [] or 'urn' != columns[0]:
                columns.insert(0, 'urn')


            names = {x[0]:' '.join([str(z) for z in x[1:]]) for x in corpusdf[columns].values}


        colA, colB = st.columns(2)

        with colA:
            st.write('Kontroller visning')
            transpose = st.checkbox("Tabellen viser ordene i kolonner", 
                                    value=True, 
                                    help="Fjern krysset for å la kolonnene bestå av dokumenter")

        submitted = st.form_submit_button("Klikk her når alt er klart")
        #st.write(words)

        tbl = df.loc[[w for w in words if w in df.index]]
        if submitted:

            tbl = tbl.rename(columns=names)

            try:
                if transpose:
                    t = tbl.transpose()
                    t = t.reset_index()

                    a = list(t.columns[1:])
                    a.append(str(t.columns[0]))
                    t = t[a]
                    st.dataframe(
                        t.sort_values(by = t.columns[0], ascending = False).style.format(precision=0).background_gradient().hide(axis=0)
                    )
                else:
                    st.dataframe(
                        tbl.sort_values(by = tbl.columns[0], ascending = False).style.format(precision=0).background_gradient()
                    )
            except:
                st.markdown("Noe gikk galt - kolonnenavn må være entydig, om dokumentinformasjon antyder kolonner, prøv å legg til _dhlabid_ som del av visningen")