from schemas.companies import CompanyCreateSchema, CompanySchema, CompanyAlterSchema, RequestSchema, MemberSchema, QuizCreateSchema, QuizSchema, QuizAlterSchema, QuizAnswerSchema, ResultSchema, AverageScoreSchema, LastTimeQuiz, AverageScoreUserSchema
from schemas.users import UserCreateSchema, UserSchema, UserLoginSchema, UserAlterSchema




user1 = UserCreateSchema(username='user1', email='mail1@mail.com',  description='first', password1='password1', password2='password1')
user2 = UserCreateSchema(username='user2', email='mail2@mail.com',  description='second', password1='password2', password2='password2')
user3 = UserCreateSchema(username='user3', email='mail3@mail.com',  description='third', password1='password3', password2='password3')
db_user1 = UserSchema(id=1, username='user1', email='mail1@mail.com', description='first')
db_user2 = UserSchema(id=2, username='user2', email='mail2@mail.com', description='second')
db_user3 = UserSchema(id=3, username='user3', email='mail3@mail.com', description='third')
login_user1 = UserLoginSchema(email='mail1@mail.com', password='password1')
login_user2 = UserLoginSchema(email='mail2@mail.com', password='password2')
user1_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im1haWwxQG1haWwuY29tIn0.EcpfIAdciAmoZlYDRw_eTChS6yYvBCL6-rirXeOsaWg'
user2_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im1haWwyQG1haWwuY29tIn0.HRwEMwkwvW7_88G8XKCx-EkMq4_WmulnRqoArewd74Q'
user3_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im1haWwzQG1haWwuY29tIn0.Q6huf10yJ_lvIsXfQwCgXp6NXXqUMEIBBjgTtC_yY1o'
company1 = CompanyCreateSchema(name='company1', description='my company', visible=True)
company2 = CompanyCreateSchema(name='company2', description='hidden company', visible=False)
db_company1 = CompanySchema(id=1, name='company1', owner='user1', description='my company', visible=True)
db_company2 = CompanySchema(id=2, name='company2', owner='user1', description='hidden company', visible=False)
quiz = QuizCreateSchema(name='quiz', description='initial quiz', frequency=1, questions=['question1', 'question2', 'question3'], answer_options=[['opt1', 'opt2', 'opt3'], ['opt1', 'opt2', 'opt3'], ['opt1', 'opt2', 'opt3']], correct_answers=[1, 2, 3])
