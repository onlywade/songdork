FROM python:3.8.2-alpine3.11

ENV FLASK_APP=songdork.webapp:app
ENV FLASK_ENV=development

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app
RUN pip install --editable .

EXPOSE 5000

CMD [ "flask", "run", "--host=0.0.0.0" ]
