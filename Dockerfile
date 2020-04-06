FROM python:3.8.2-slim AS test-base

# Install dependencies
RUN pip install pipenv

FROM test-base AS test-overlay

ENV PIPENV_PIPFILE /app/Pipfile

COPY ./Pipfile* /app/
WORKDIR /app

RUN pipenv install --dev