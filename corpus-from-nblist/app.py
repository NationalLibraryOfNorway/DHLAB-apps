# build streamlit app that takes user input in box and parses to dataframe with regex
import streamlit as st
import pandas as pd
import re
import dhlab as dh
import requests
from io import BytesIO

API = "https://api.nb.no/shared/v1/itemlists/"

@st.cache_data(show_spinner=False)
def to_excel(df):
    """Make an excel object out of a dataframe as an IO-object"""
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    worksheet = writer.sheets['Sheet1']
    writer.save()
    processed_data = output.getvalue()
    return processed_data


def get_urn(link):
    p1 = r"^https://www\.nb\.no/services/image/resolver/(URN:[^/]+)"
    
    long_urn = re.match(p1, link).group(1)
    
    if "digavis" in long_urn:
        p2 = r"(URN:NBN:no-nb_digavis(?:_[^_]*){7})-1"
        short_urn = re.match(p2, long_urn).group(1)
    else:
        short_urn = "_".join(long_urn.split("_")[:-1])
        
    return short_urn    
    
### User input ###
st.title('Bygg korpus fra liste på nb.no')
text = st.text_input("Skriv inn lenke til liste på nb.no",
                     value= "2bbddc4d-d889-43a1-be14-e5246845090c",
                    # autocomplete= "https://www.nb.no/shared/itemlists/a6b91841-c7e2-4cf3-a8f0-081b39553726",
                     )

response = requests.get(API + text).json()

df = pd.DataFrame(response["items"])

df["urn"] = df["thumbnailUrl"].apply(get_urn)


st.write(response.get("name", "No title"))

corpus = dh.Corpus.from_identifiers(df["urn"].tolist())
st.write(corpus.frame)

df_defined = True

if df_defined:
    if st.download_button('Last ned data i excelformat', to_excel(corpus.corpus), "corpus.xlsx", help = "Åpnes i Excel eller tilsvarende"):
        pass