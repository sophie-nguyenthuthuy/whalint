FROM python:3.12-slim
ENV PIP_NO_CACHE_DIR=1
RUN pip install -r requirements.txt
