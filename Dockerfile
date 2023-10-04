# syntax=docker/dockerfile:1

FROM python:3.11-slim

WORKDIR /root/sflplus
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update \
    && apt-get install curl --yes --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT [ "/usr/local/bin/streamlit", "run",  "/root/sflplus/main.py" ]