FROM python:3.6-alpine
RUN apk update && apk upgrade
RUN apk add --no-cache --virtual build-deps build-base gcc python3-dev openssl-dev \
    libressl-dev libffi-dev screen curl
WORKDIR /code
COPY . /code
RUN pip3 install --no-cache-dir -r requirements-dev.txt
EXPOSE 5555
CMD ["gunicorn", "-b", "0.0.0.0:5555", "-w", "4", "wsgi:app"]