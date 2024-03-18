FROM python:3.11.8

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV WORKDIR=/app/
ENV POETRY_VERSION=1.7.1
ENV POETRY_HOME=/opt/poetry

WORKDIR $WORKDIR

RUN curl -sSL https://install.python-poetry.org | python \
    && ln -s ${POETRY_HOME}/bin/poetry /usr/local/bin/poetry \
    && poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock $WORKDIR
RUN poetry install --no-root

EXPOSE 8000
COPY ./ $WORKDIR
