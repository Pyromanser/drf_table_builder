FROM python:3.11-slim as python-base

RUN apt-get update && apt-get upgrade && apt-get clean

FROM python-base as python-build

RUN apt-get install -y --no-install-recommends build-essential gcc libpq-dev

COPY ./requirements.txt .

RUN pip install --no-cache-dir -t /python -r requirements.txt && find /python \( -type d -a -name test -o -name tests \) -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) -exec rm -rf '{}' \+

FROM python-base as drf_table_builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get install -y --no-install-recommends curl libpq-dev && apt-get clean autoclean && apt-get autoremove --yes && rm -rf /var/lib/{apt,dpkg,cache,log}/

RUN addgroup --gid 1001 appuser && adduser --uid 1001 --gid 1001 --shell /bin/bash --disabled-password appuser

COPY --from=python-build /python /home/appuser/python
RUN mkdir /home/appuser/app && chown -R appuser:appuser /home/appuser/app && chmod 755 /home/appuser/app
USER appuser
COPY . /home/appuser/app
COPY ./docker-entrypoint.sh ./runserver.sh ./wait-for-command.sh /home/appuser/

ENV PYTHONPATH=/home/appuser/python
ENV PATH="${PYTHONPATH}/bin:${PATH}"

WORKDIR /home/appuser/app

EXPOSE 8000
ENTRYPOINT ["/bin/bash", "/home/appuser/docker-entrypoint.sh"]
CMD ["sh", "/home/appuser/runserver.sh"]