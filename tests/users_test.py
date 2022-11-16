from httpx import AsyncClient
from pytest import mark
from services.services import create_token
from schemas_mock import *


@mark.anyio
async def test_healthcheck(client: AsyncClient, refresh_db):
    response = await client.get('/')
    assert response.status_code == 200
    assert response.json() == {'status': 'Working!'}


@mark.anyio
async def test_user_invalid_create(client: AsyncClient):
    invalid_user = dict(username='user', email='mail@mail.com', password1='password1', password2='password2')
    response = await client.post('/users', json=invalid_user)
    assert response.status_code == 422
    data = response.json()
    assert data['detail'][0]['msg'] == 'passwords do not match'


@mark.anyio
async def test_user_create(client: AsyncClient):
    response = await client.post('/users', json=user1.dict())
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == 1
    assert data['username'] == user1.username
    assert data['email'] == user1.email
    assert data['description'] == user1.description


@mark.anyio
async def test_user_double_create(client: AsyncClient):
    user = UserCreateSchema(username='user1', email='some@mail.com', password1='password', password2='password')
    response = await client.post('/users', json=user.dict())
    assert response.status_code == 404
    assert response.json() == {'detail': 'username or email already in use'}
    user = UserCreateSchema(username='some', email='mail1@mail.com', password1='password', password2='password')
    response = await client.post('/users', json=user.dict())
    assert response.status_code == 404
    assert response.json() == {'detail': 'username or email already in use'}


@mark.anyio
async def test_user_list(client: AsyncClient):
    await client.post('/users', json=user2.dict())
    await client.post('/users', json=user3.dict())
    response = await client.get('/users')
    assert response.status_code == 200
    assert response.json() == [db_user1, db_user2, db_user3]


@mark.anyio
async def test_user_get(client: AsyncClient):
    response = await client.get('/users/1')
    assert response.status_code == 200
    assert response.json() == db_user1


@mark.anyio
async def test_user_login(client: AsyncClient):
    response = await client.post('/users/login', json=login_user1.dict())
    assert response.status_code == 200
    assert response.json() == create_token({'email': user1.email})


@mark.anyio
async def test_user_invalid_login(client: AsyncClient):
    invalid_user = UserLoginSchema(email='some@mail.com', password='somepass')
    response = await client.post('/users/login', json=invalid_user.dict())
    assert response.status_code == 404
    assert response.json() == {'detail': 'user not found'}


@mark.anyio
async def test_user_validate_auth0(client: AsyncClient):
    user = UserSchema(id=4, username='bogdanpizuk@outlook.com', email='bogdanpizuk@outlook.com')
    response = await client.get('/users/validate', headers={'Token': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImgzeFduUjlNVERDbEQtUjBNTWI0bSJ9.eyJ1c2VyX2VtYWlsIjoiYm9nZGFucGl6dWtAb3V0bG9vay5jb20iLCJpc3MiOiJodHRwczovL2Rldi04MG9kazY5ci51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjM0ZTgyOTU5YWU5NWQ3NGEzNzRjZTkyIiwiYXVkIjpbInBpemh1a0FwaSIsImh0dHBzOi8vZGV2LTgwb2RrNjlyLnVzLmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE2NjcxNTMwMTAsImV4cCI6MTY2NzIzOTQxMCwiYXpwIjoiaEtpVW5WSFVPSkVJOFVnRlRjZGdEZlpJeDBpQXVIUE4iLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIn0.eZmnqUfSx4V4lpgSPnuHfJnej1GcfDdsqjcwb4IM2siKegRFS82mGG5Xkp4tQbNurLMnpefyUCRrVxkaPVYYtxWfIC3UUFt5Z1Pkdi2j0flhdLrtS82eGG4zZIe1BEpN1i-iCC9k58P7XKjvcSGj1D5XmvZNh9q1xS_-DY0e6oqGi-DageLsVeac4qWBNsFVz_Gg8fF5lWrmDkUaLN53IqgUG2rSvdZuUtSYsncxog98I1T1r75mV_CFXqjABnUS_CDkTnum9Yq6n7TJSNpdaPiAZo9dqLNcHdHWxBdL1s361YmCC-uxeB0rYoniy3WdymmwYwJkRRBtwuNd9ItubQ', 'TokenType': 'auth0'})
    assert response.status_code == 200
    assert response.json() == user.dict()


@mark.anyio
async def test_user_validate_app(client: AsyncClient):
    token = create_token({'email': user1.email})
    response = await client.get('/users/validate', headers={'Token': token, 'TokenType': 'app'})
    assert response.status_code == 200
    assert response.json() == db_user1.dict()


@mark.anyio
async def test_user_validate_app(client: AsyncClient):
    user = UserAlterSchema(username='new_username', description='new one', password='new_pass')
    token = await client.post('/users/login', json=login_user1.dict())
    token = token.json()
    response = await client.patch('/users', headers={'Token': token, 'TokenType': 'app'}, json=user.dict())
    assert response.status_code == 200
    assert response.json() == UserSchema(id=1, username=user.username, email=user1.email, description=user.description).dict()
    response = await client.get('/users/validate', headers={'Token': token, 'TokenType': 'app'})
    assert response.json() == UserSchema(id=1, username=user.username, email=user1.email, description=user.description).dict()
    new_token = await client.post('/users/login', json={'email': user1.email, 'password': user.password})
    new_token = new_token.json()
    assert token == new_token


@mark.anyio
async def test_user_delete(client: AsyncClient):
    token = await client.post('/users/login', json=login_user2.dict())
    print(token.json())
    assert token.status_code == 200
    token = token.json()
    response = await client.delete('/users', headers={'Token': token, 'TokenType': 'app'})
    assert response.status_code == 200
    assert response.json() == db_user2.dict()
    response = await client.get('/users/2')
    assert response.status_code == 404
    assert response.json() == {'detail': 'user not found'}


@mark.anyio
async def test_healthcheck_end(client: AsyncClient, clear_db):
    response = await client.get('/')
    assert response.status_code == 200
    assert response.json() == {'status': 'Working!'}
