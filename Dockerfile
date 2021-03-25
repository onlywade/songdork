FROM python:3.8.2-alpine3.11

ENV FLASK_APP=twongs.webapp:app
ENV FLASK_ENV=development

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

RUN pip install --editable .

EXPOSE 5000

CMD [ "flask", "run", "--host=0.0.0.0" ]
