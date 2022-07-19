FROM python:3.10

WORKDIR /code

COPY ./Pipfile* /code/

RUN pip install pipenv
RUN pipenv sync --system

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
