FROM python:3.7 as millicord_base

USER root

RUN apt-get update && apt-get install -y -q --no-install-recommends \
    python3-dev \
    libgl1-mesa-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/list/* && \
    pip install --upgrade --no-cache-dir pip

FROM millicord_base as build

COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir pipenv torch torchvision
RUN pipenv install --system

FROM build as develop

FROM millicord_base as release

WORKDIR /app
RUN mkdir -p /app

COPY --from=build /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages
COPY --from=build /app/millicord /app/millicord
COPY --from=build /app/resources /app/resources
COPY --from=build /app/*.py /app/
COPY --from=build /app/*.cfg /app/
