FROM python:3.10
RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --system
COPY alembic.ini .
COPY /tests/tests.sh .
CMD /tests.sh