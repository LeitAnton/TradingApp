FROM python:3.10.12-alpine as builder

WORKDIR /usr/src/web

COPY Pipfile.lock Pipfile ./

RUN apk --no-cache add \
    gcc\
    jpeg-dev\
    libc-dev\
    libffi-dev\
    musl-dev\
    postgresql-dev\
    python3-dev\
    zlib-dev\
    && pip3 install pipenv\
    && pipenv requirements > requirements.txt\
    && pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/web/wheels -r requirements.txt

FROM python:3.10.12-alpine

ENV USER=TradingApp \
    PYTHONFONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN mkdir -p /home/$USER
RUN addgroup -S $USER && adduser -S $USER -G $USER

ENV HOME=/home/$USER
ENV APP_HOME=/home/$USER/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

COPY --from=builder /usr/src/web/wheels /wheels
COPY --from=builder /usr/src/web/requirements.txt .
RUN pip install --no-cache-dir /wheels/*

COPY . $APP_HOME

RUN chown -R $USER:$USER $APP_HOME
USER $USER

RUN chmod +x $APP_HOME/web-entrypoint.sh
RUN chmod +x $APP_HOME/worker-entrypoint.sh
RUN chmod +x $APP_HOME/celery-beat-entrypoint.sh
