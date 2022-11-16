FROM python:3.8
        EXPOSE 8501
        WORKDIR /ner_app_urn.py
        COPY requirements.txt ./requirements.txt
        RUN pip3 install -r requirements.txt
        COPY . .
        CMD streamlit run ner_app_urn.py
        