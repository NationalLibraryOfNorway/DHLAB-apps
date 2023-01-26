FROM python:3.10-slim
        EXPOSE 8501
        WORKDIR /sentiment-app.py
        COPY requirements.txt ./requirements.txt
        RUN pip3 install -r requirements.txt
        COPY . .
        CMD streamlit run sentiment-app.py
        