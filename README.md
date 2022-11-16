To create DB migrations:
    alembic revision --autogenerate -m 'init'
Start app by executing:
    uvicorn src.main:app --reload
Docker:
    docker compose up --build -d
Run tests:
    docker compose -f 'compose.tests.yml' up --build --abort-on-container-exit
Deploy host:
    http://myenv.eba-drzkqu8p.eu-north-1.elasticbeanstalk.com/