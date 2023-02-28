FROM python:3.9-alpine3.13
LABEL maintainer="radubila"

ENV PYTHONUNBUFFERED 1

# Copy requirements and app directory in the docker image
COPY ./requirements.txt /tmp/requirements.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

# Install dependencies in the machine
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

# Update path to auto run from the venv
ENV PATH="py/bin:$PATH"

# Switch to non root user
USER django-user