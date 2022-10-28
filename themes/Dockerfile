# set base image (host OS)
FROM python:3.10-slim

# set the working directory in the container
WORKDIR /code

# copy requirements
COPY requirements.txt /code

# install dependencies
RUN pip install -r requirements.txt

# copy working files to the working directory
COPY . /code

# command to run on container start
CMD streamlit run st_themes.py --server.port 5001
