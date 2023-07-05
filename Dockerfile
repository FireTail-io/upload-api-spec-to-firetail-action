ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bullseye as runtime-image
COPY ./src/ /src/
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && rm -f requirements.txt

CMD ["/src/process_api_spec.py"]
ENTRYPOINT ["python"]