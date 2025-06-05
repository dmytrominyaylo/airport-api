FROM python:3.12-alpine3.21
LABEL maintainer="dimon9660@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p  /app/uploads

RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user

RUN chown -R my_user /app/uploads
RUN chmod -R 775 /app/uploads

USER my_user
