FROM python:3.10-slim
ENV PYTHONUNBUFFERED 1
COPY ./ /bot
WORKDIR /bot

RUN pip install -r requirements.txt --no-cache-dir