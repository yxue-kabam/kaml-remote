FROM python:2.7-slim

COPY setup.py ./
COPY src src

RUN python setup.py bdist_egg

ENTRYPOINT ["kaml-remote"]
