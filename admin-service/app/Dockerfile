FROM python:3.9

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'config.settings'

RUN apt update -y \
    && apt upgrade -y \
    && apt install -y \
    netcat-traditional

COPY entrypoint.sh /home
COPY requirements.txt  requirements.txt
COPY uwsgi/uwsgi.ini uwsgi.ini


RUN  mkdir -p /var/www/static/ \
     && mkdir -p /var/www/media/ \
     && mkdir -p /opt/app/static/ \
     && mkdir -p /opt/app/media/ \
     && pip install --upgrade pip \
     && pip install -r requirements.txt


COPY . .


EXPOSE 8000


RUN chmod +x /home/entrypoint.sh

ENTRYPOINT ["/home/entrypoint.sh"]