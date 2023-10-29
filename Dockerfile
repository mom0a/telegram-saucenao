FROM python:3-slim

RUN mkdir -p /srv/sausenao && \
    apt update && \
    apt install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /srv/sausenao

COPY requirements.txt /srv/sausenao
RUN pip install --no-cache-dir -r requirements.txt

COPY . /srv/sausenao

CMD [ "python", "./main.py" ]