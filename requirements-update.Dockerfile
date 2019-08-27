FROM python:3.6

COPY requirements-base.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt &&\
    rm /requirements.txt &&\
    pip freeze
