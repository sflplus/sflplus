# syntax=docker/dockerfile:1

FROM python:slim

WORKDIR /root/sflplus
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT [ "/usr/local/bin/streamlit", "run",  "/root/sflplus/main.py" ]