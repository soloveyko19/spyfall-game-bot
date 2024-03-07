FROM python:3.10

RUN mkdir src
WORKDIR /src

RUN pip install --upgrade pip
COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY ./bot/ ./bot/

ENV PYTHONPATH=/src/bot

WORKDIR /src/bot

CMD pybabel compile -d ./locales && \
    python3 -m alembic upgrade head && \
    python3 main.py