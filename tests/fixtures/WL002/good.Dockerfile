FROM python:3.12-slim
COPY requirements.txt /app/requirements.txt
ADD https://example.com/releases/tool.tar.gz /opt/
ADD vendor.tar.gz /opt/vendor/
