FROM python:3.12 as builder

RUN pip install poetry

ENV \
	POETRY_VIRTUALENVS_IN_PROJECT=1 \
	POETRY_VIRTUALENVS_CREATE=1 \
	POETRY_NO_INTERACTION=1 \
	POETRY_CACHE_DIR=/tmp/poetry_cache

RUN mkdir -p /app /data

WORKDIR /app

COPY ./poetry.lock ./pyproject.toml ./

RUN poetry install --no-root

FROM python:3.12-slim as base

ARG USERNAME=${USERNAME:-app}
ARG	USER_UID=${UID:-1000}
ARG	USER_GID=${USER_UID}

ENV \
	VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

ENV \
	PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PYTHONFAULTHANDLER=1

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY ./src /app/

RUN groupadd --gid ${USER_GID} ${USERNAME} && \
		useradd --uid ${USER_UID} --gid ${USER_GID} --shell /bin/bash -m ${USERNAME} && \
		chown -R ${USERNAME}:${USERNAME} /app

USER ${USERNAME}

WORKDIR /app

CMD [ "python", "/app/main.py" ]