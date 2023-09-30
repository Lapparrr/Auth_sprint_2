FROM python:3.10

WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN  mkdir -p /opt/app/static/ \
     && pip install --no-cache-dir --upgrade pip==22.3 \
     && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd -r web && useradd -d /opt/app/ -r -g web web \
    && chown web:web -R /opt/app/
USER web

RUN python helpers.py

ENTRYPOINT ["python", "etl.py"]
