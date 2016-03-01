FROM kkost/uwsgi-flask

ENV HOME /root

CMD ["/sbin/my_init"]

ADD . /home/app/
RUN pip install -r /home/app/requirements.txt

RUN rm -f /etc/service/uwsgi/down /etc/service/nginx/down