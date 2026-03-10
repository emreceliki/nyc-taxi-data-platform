FROM spark:3.5.3-java17

USER root

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY spark_on_k8s_app.py .