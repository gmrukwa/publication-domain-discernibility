FROM python:3.6

EXPOSE 8888

RUN pip install --no-cache-dir jupyterlab

RUN apt-get install -y curl &&\
    curl -sL https://deb.nodesource.com/setup_12.x | bash - &&\
    apt-get install -y nodejs &&\
    export NODE_OPTIONS=--max-old-space-size=4096 &&\
    jupyter labextension install @jupyter-widgets/jupyterlab-manager@0.38 --no-build &&\
    jupyter labextension install plotlywidget@0.10.0 --no-build &&\
    jupyter labextension install @jupyterlab/plotly-extension@0.18.2 --no-build &&\
    jupyter labextension install jupyterlab-chart-editor@1.1 --no-build &&\
    jupyter lab build &&\
    unset NODE_OPTIONS &&\
    apt-get purge -y nodejs &&\
    apt-get purge -y curl

RUN apt-get update && apt-get install -qq \
    build-essential \
    libpoppler-cpp-dev \
    pkg-config \
    python-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /

RUN pip install --no-cache-dir -r /requirements.txt &&\
    rm /requirements.txt

RUN pip install --no-cache-dir matplotlib plotly &&\
    echo "backend : Agg" > /root/.config/matplotlib/matplotlibrc

VOLUME /app

WORKDIR /app

ENTRYPOINT ["jupyter"]

CMD ["lab", "--no-browser", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.iopub_data_rate_limit=1.0e10"]
