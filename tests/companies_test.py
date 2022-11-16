from httpx import AsyncClient
from pytest import mark
from csv import writer, QUOTE_NONNUMERIC
from io import StringIO
from datetime import datetime
from schemas_mock import *


@mark.anyio
async def test_healthcheck(client: AsyncClient, refresh_db):
    response = await client.get('/')
    assert response.status_code == 200
    assert response.json() == {'status': 'Working!'}


@mark.anyio
async def test_company_create(client: AsyncClient):
    await client.post('/users', json=user1.dict())
    await client.post('/users', json=user2.dict())
    await client.post('/users', json=user3.dict())
    response = await client.post('/companies', json=company1.dict(), headers=dict(Token=user1_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == db_company1.dict()
    response = await client.post('/companies', json=company2.dict(), headers=dict(Token=user1_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == db_company2.dict()


@mark.anyio
async def test_company_get_auth(client: AsyncClient):
    response = await client.get('/companies/2', headers=dict(Token=user1_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == db_company2.dict()


@mark.anyio
async def test_company_get_unauth(client: AsyncClient):
    response = await client.get('/companies/2', headers=dict(Token=user2_token, TokenType='app'))
    assert response.status_code == 404
    assert response.json() == {'detail': 'company hidden'}


@mark.anyio
async def test_company_get_list(client: AsyncClient):
    response = await client.get('/companies', headers=dict(Token=user2_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == [db_company1.dict()]


@mark.anyio
async def test_company_patch_auth(client: AsyncClient):
    company = CompanyAlterSchema(name='new name', description='altered company', visible=True)
    response = await client.patch('/companies/2', headers=dict(Token=user1_token, TokenType='app'), json=company.dict())
    assert response.status_code == 200
    assert response.json() == CompanySchema(id=2, name=company.name, owner='user1', description=company.description, visible=company.visible)
    response = await client.get('/companies/2', headers=dict(Token=user1_token, TokenType='app'))
    assert response.json() == CompanySchema(id=2, name=company.name, owner='user1', description=company.description, visible=company.visible)


@mark.anyio
async def test_company_patch_unauth(client: AsyncClient):
    company = CompanyAlterSchema(name='new name', description='altered company', visible=True)
    response = await client.patch('/companies/2', headers=dict(Token=user2_token, TokenType='app'), json=company.dict())
    assert response.status_code == 404
    assert response.json() == {'detail': 'no access'}


@mark.anyio
async def test_company_delete_noauth(client: AsyncClient):
    response = await client.delete('/companies/2', headers=dict(Token=user2_token, TokenType='app'))
    assert response.status_code == 404
    assert response.json() == {'detail': 'no access'}


@mark.anyio
async def test_company_delete_auth(client: AsyncClient):
    response = await client.delete('/companies/2', headers=dict(Token=user1_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == CompanySchema(id=2, name='new name', owner='user1', description='altered company', visible=True)
    response = await client.get('/companies/2', headers=dict(Token=user1_token, TokenType='app'))
    assert response.status_code == 404
    assert response.json() == {'detail': 'company not found'}


@mark.anyio
async def test_company_invite(client: AsyncClient):
    response = await client.get('/companies/invite/1?user_id=2', headers=dict(Token=user1_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == RequestSchema(id=1, user='user2', company='company1', side='Company invites user').dict()


@mark.anyio
async def test_user_request(client: AsyncClient):
    response = await client.get('/companies/join/1', headers=dict(Token=user3_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == RequestSchema(id=2, user='user3', company='company1', side='User requests access to company').dict()


@mark.anyio
async def test_company_request_list(client: AsyncClient):
    response = await client.get('/companies/request_list/1', headers=dict(Token=user1_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == [RequestSchema(id=1, user='user2', company='company1', side='Company invites user').dict(), RequestSchema(id=2, user='user3', company='company1', side='User requests access to company').dict()]


@mark.anyio
async def test_user_request_list(client: AsyncClient):
    response = await client.get('/request_list', headers=dict(Token=user2_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == [RequestSchema(id=1, user='user2', company='company1', side='Company invites user').dict()]


@mark.anyio
async def test_user_rewiev_request(client: AsyncClient):
    response = await client.get('/request/review/1?response=accept', headers=dict(Token=user2_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == MemberSchema(company='company1', user='user2', admin=False).dict()


@mark.anyio
async def test_company_rewiev_request(client: AsyncClient):
    response = await client.get('/request/review/2?response=accept', headers=dict(Token=user1_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == MemberSchema(company='company1', user='user3', admin=False).dict()


@mark.anyio
async def test_company_admin(client: AsyncClient):
    response = await client.get('/companies/admin/1?user_id=2&admin=true', headers=dict(Token=user1_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == MemberSchema(company='company1', user='user2', admin=True).dict()


@mark.anyio
async def test_remove_member(client: AsyncClient):
    response = await client.get('/companies/remove/1?user_id=3', headers=dict(Token=user1_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == MemberSchema(company='company1', user='user3', admin=False).dict()


@mark.anyio
async def test_quiz_create(client: AsyncClient):
    response = await client.post('/companies/quiz/1', headers=dict(Token=user1_token, TokenType='app'), json=quiz.dict())
    assert response.status_code == 200
    assert response.json() == QuizSchema(id=1, name=quiz.name, description=quiz.description, frequency=quiz.frequency, quiz={'questions': quiz.questions, 'answer_options': quiz.answer_options, 'correct_answers': quiz.correct_answers}).dict()


@mark.anyio
async def test_quiz_patch(client: AsyncClient):
    response = await client.patch('/companies/quiz/1?quiz_id=1', headers=dict(Token=user1_token, TokenType='app'), json=QuizAlterSchema(name='new name', frequency=3).dict())
    assert response.status_code == 200
    assert response.json() == QuizSchema(id=1, name='new name', description=quiz.description, frequency=3, quiz={'questions': quiz.questions, 'answer_options': quiz.answer_options, 'correct_answers': quiz.correct_answers}).dict()


@mark.anyio
async def test_quiz_list(client: AsyncClient):
    response = await client.get('/companies/quiz_list/1', headers=dict(Token=user1_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == [QuizSchema(id=1, name='new name', description=quiz.description, frequency=3, quiz={'questions': quiz.questions, 'answer_options': quiz.answer_options, 'correct_answers': quiz.correct_answers}).dict()]


@mark.anyio
async def test_take_quiz(client: AsyncClient):
    response = await client.post('/companies/take_quiz/1?quiz_id=1', headers=dict(Token=user2_token, TokenType='app'), json=QuizAnswerSchema(answers=[1, 2, 3]).dict())
    assert response.status_code == 200
    assert response.json() == ResultSchema(id=1, user_id=2, quiz_id=1, company_id=1, overall_questions=3, correct_answers=3).dict()


@mark.anyio
async def test_user_dump_results(client: AsyncClient):
    await client.post('/companies/take_quiz/1?quiz_id=1', headers=dict(Token=user2_token, TokenType='app'), json=QuizAnswerSchema(answers=[2, 2, 2]).dict())
    await client.post('/companies/take_quiz/1?quiz_id=1', headers=dict(Token=user2_token, TokenType='app'), json=QuizAnswerSchema(answers=[2, 2, 3]).dict())
    response = await client.get('/users/dump_results/', headers=dict(Token=user2_token, TokenType='app'))
    assert response.status_code == 200
    csv = StringIO()
    write = writer(csv, quoting=QUOTE_NONNUMERIC)
    csvheader = ['user_id', 'quiz_id', 'overall_questions', 'correct_answers']
    write.writerow(csvheader)
    write.writerow([2, 1, 3, 3])
    write.writerow([2, 1, 3, 1])
    write.writerow([2, 1, 3, 2])
    assert response.text == csv.getvalue()


@mark.anyio
async def test_user_dump_answers(client: AsyncClient):
    response = await client.get('/users/dump_answers/', headers=dict(Token=user2_token, TokenType='app'))
    assert response.status_code == 200
    data = []
    for line in response.text.split('\r\n'):
        data.append(line)
    assert '"2","1","[1, 2, 3]"' in data
    assert '"2","1","[2, 2, 2]"' in data
    assert '"2","1","[2, 2, 3]"' in data


@mark.anyio
async def test_company_dump_results(client: AsyncClient):
    response = await client.get('/companies/dump_results/1?user_id=2&quiz_id=1', headers=dict(Token=user1_token, TokenType='app'))
    assert response.status_code == 200
    csv = StringIO()
    write = writer(csv, quoting=QUOTE_NONNUMERIC)
    csvheader = ['user_id', 'quiz_id', 'overall_questions', 'correct_answers']
    write.writerow(csvheader)
    write.writerow([2, 1, 3, 3])
    write.writerow([2, 1, 3, 1])
    write.writerow([2, 1, 3, 2])
    assert response.text == csv.getvalue()


@mark.anyio
async def test_company_dump_answers(client: AsyncClient):
    response = await client.get('/companies/dump_answers/1?user_id=2&quiz_id=1', headers=dict(Token=user1_token, TokenType='app'))
    assert response.status_code == 200
    data = []
    for line in response.text.split('\r\n'):
        data.append(line)
    assert '"2","1","[1, 2, 3]"' in data
    assert '"2","1","[2, 2, 2]"' in data
    assert '"2","1","[2, 2, 3]"' in data


@mark.anyio
async def test_company_average_score(client: AsyncClient):
    response = await client.get('/companies/average_score/1?user_id=2', headers=dict(Token=user1_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == [AverageScoreSchema(date=str(datetime.utcnow().date()), average_score=6/9).dict()]


@mark.anyio
async def test_company_last_time_quiz(client: AsyncClient):
    response = await client.get('/companies/last_time_quiz/1', headers=dict(Token=user1_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == [LastTimeQuiz(user_id=2, quiz_id=1, last_time=str(datetime.utcnow().date())).dict()]


@mark.anyio
async def test_user_average_score(client: AsyncClient):
    response = await client.get('/users/average_score/?user_id=2&quiz_id=1')
    assert response.status_code == 200
    assert response.json() == AverageScoreUserSchema(user_id=2, average_score=6/9).dict()


@mark.anyio
async def test_user_average_score(client: AsyncClient):
    response = await client.get('/users/last_time_quiz/', headers=dict(Token=user2_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == [LastTimeQuiz(user_id=2, quiz_id=1, last_time=str(datetime.utcnow().date())).dict()]


@mark.anyio
async def test_delete_quiz(client: AsyncClient):
    response = await client.delete('/companies/quiz/1?quiz_id=1', headers=dict(Token=user1_token, TokenType='app'))
    assert response.status_code == 200
    assert response.json() == QuizSchema(id=1, name='new name', description=quiz.description, frequency=3, quiz={'questions': quiz.questions, 'answer_options': quiz.answer_options, 'correct_answers': quiz.correct_answers}).dict()


@mark.anyio
async def test_healthcheck_end(client: AsyncClient, clear_db):
    response = await client.get('/')
    assert response.status_code == 200
    assert response.json() == {'status': 'Working!'}
