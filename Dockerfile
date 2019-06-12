FROM python:3.6

RUN apt-get update && apt-get install -qq \
    build-essential \
    libpoppler-cpp-dev \
    pkg-config \
    python-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /

RUN pip install --no-cache-dir -r /requirements.txt

RUN python -c 'import nltk; nltk.download('stopwords')'

COPY . /app

WORKDIR /app
