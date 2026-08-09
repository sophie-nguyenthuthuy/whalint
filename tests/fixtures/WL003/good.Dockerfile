FROM python:3.12-slim
RUN useradd --create-home app
USER app
