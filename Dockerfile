FROM python:3

RUN mkdir -p /srv/sausenao
WORKDIR /srv/sausenao

COPY . /srv/sausenao
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]