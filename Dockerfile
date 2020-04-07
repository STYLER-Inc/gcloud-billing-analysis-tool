FROM python:3.8.2-slim AS test-base

# Install dependencies
RUN pip install pipenv

FROM test-base AS test-overlay

COPY ./Pipfile* /app/
WORKDIR /app

ENV PIPENV_PIPFILE /app/Pipfile

RUN pipenv install --dev