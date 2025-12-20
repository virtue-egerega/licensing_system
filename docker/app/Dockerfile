FROM python:3.11-slim

RUN set -xe;

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ALLOW_ASYNC_UNSAFE="true"
ENV DJANGO_SETTINGS_MODULE=license_service.settings.prod

RUN groupadd -r app && useradd --create-home --no-log-init -u 1000 -r -g app app && mkdir /app && chown app:app /app
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends tini && rm -rf /var/lib/apt/lists/*

RUN mkdir /app/requirements/

COPY ./docker/app/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh
ADD ./requirements/* /app/requirements/
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements/prod.txt
ADD . /app

USER app

ENV PATH="${PATH}:/home/app/.local/bin"

EXPOSE 8000/tcp
ENTRYPOINT ["tini", "--", "entrypoint.sh"]
CMD ["uwsgi", "--ini", "uwsgi.ini"]
