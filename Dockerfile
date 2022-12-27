# Pull base image
FROM python:3.8


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# Set work directory
WORKDIR /bmg

# Install dependencies
RUN pip install --upgrade pip
COPY Pipfile Pipfile.lock /bmg/
RUN pip install pipenv && pipenv install --system


# Copy project
COPY . /bmg/