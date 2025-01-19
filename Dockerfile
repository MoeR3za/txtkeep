FROM python:3.11-slim

# create and set working directory
RUN mkdir /app
WORKDIR /app

RUN apt-get update \
    && apt-get install -y libpq-dev gcc default-libmysqlclient-dev pkg-config

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

# Pre deployment check
RUN python manage.py migrate

## FOR PROD
EXPOSE 8000

ENTRYPOINT [ "entrypoint.sh" ]

# CMD ["gunicorn", "txtkeep.wsgi:application", "--bind", "0.0.0.0:8000"]