# syntax=docker/dockerfile:1

FROM python:slim

WORKDIR /root/sflplus
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT [ "/usr/local/bin/streamlit", "run",  "/root/sflplus/main.py" ]