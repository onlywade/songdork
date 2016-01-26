FROM python
WORKDIR /usr/src/twongs

ADD . /usr/src/twongs
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "twongs.py"]
