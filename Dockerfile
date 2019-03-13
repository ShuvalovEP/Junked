FROM python:3.7.2

RUN mkdir app
WORKDIR /app
COPY . /app/

EXPOSE 5000

RUN pip install -r requirements.txt

CMD ["gunicorn"  , "-b", "0.0.0.0:5000", "server:app"]

