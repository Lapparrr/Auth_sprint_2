FROM python:3.9.6

WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN  mkdir -p /opt/app/static/ \
     && pip install --no-cache-dir --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd -r web && useradd -d /opt/app/ -r -g web web \
    && chown web:web -R /opt/app/
USER web

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "main:app"]