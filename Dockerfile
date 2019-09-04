FROM python:3.6

RUN pip install --no-cache-dir dvc[all]

COPY requirements.txt /

RUN pip install --no-cache-dir -r /requirements.txt

RUN python -c 'import nltk; nltk.download("stopwords"); nltk.download("wordnet")'

COPY . /app

WORKDIR /app
