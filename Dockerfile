FROM python:3.8.2-slim AS test-base

# Install dependencies
RUN pip install pipenv

FROM test-base AS test-overlay

COPY ./Pipfile* /workspace/
WORKDIR /workspace

RUN pipenv install --dev