FROM python:3.11-slim as builder

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PATH="$PATH:/root/.local/bin" \
    APP_HOME=/usr/src/app

RUN apt-get update && apt-get install -y gcc && \
    pip install --upgrade pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR $APP_HOME

COPY ./requirements.txt requirements.txt

RUN --mount=type=cache,target=/root/.cache pip install -r requirements.txt

COPY . .

FROM python:3.11-slim as runner

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/home/ecom_ms_wb

RUN apt-get update && apt-get install -y libpq-dev && \
    apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR $APP_HOME

COPY --from=builder /usr/src/app $APP_HOME
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

ENTRYPOINT ["python", "main.py"]
