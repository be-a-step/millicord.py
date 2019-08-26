FROM python:3.7

RUN apt-get update && apt-get install -y -q --no-install-recommends \
    python3-dev &&\
    apt-get clean && \
    rm -rf /var/lib/apt/list/* && \
    pip install --upgrade --no-cache-dir pip && \
    pip install --no-cache-dir pipenv

CMD "/bin/bash"