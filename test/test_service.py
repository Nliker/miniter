import jwt
import bcrypt
import pytest
import sys,os

sys.path.append((os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
import config

from model import UserDao,TweetDao
from service import UserService,TweetService
from sqlalchemy import create_engine,text

database=create_engine(config.test_config['DB_URL'],encoding='utf-8',max_overflow=0)

@pytest.fixture
def user_service():
    return UserService(UserDao(database),config.test_config)

@pytest.fixture
def tweet_service():
    return TweetService(TweetDao(database))

def setup_function():
    hashed_password=bcrypt.hashpw(
        b"test",
        bcrypt.gensalt()
    )
    
    new_users=[{
        'id':1,
        'name':'test1',
        'email':'test1@naver.com',
        'profile':'test1',
        'hashed_password':hashed_password
    },{
        'id':2,
        'name':'test2',
        'email':'test2@naver.com',
        'profile':'test2',
        'hashed_password':hashed_password
    }]
    
    database.execute(text("""
        insert into users (
            id,
            name,
            email,
            profile,
            hashed_password
        ) values (
            :id,
            :name,
            :email,
            :profile,
            :hashed_password
        )"""),new_users)
    database.execute(text("""
    insert into tweets (
        user_id,
        tweet
    ) values (
        2,
        "hellow wordl!"
    )"""))
    print("===========데이터 삽입 완료===========")
def teardown_function():
    print("======teardown_function======")
    print("테이블 초기화중")
    database.execute(text("""
        set foreign_key_checks=0
    """))
    database.execute(text("""
        truncate users
    """))
    database.execute(text("""
        truncate tweets
    """))
    database.execute(text("""
        truncate users_follow_list
    """))
    database.execute(text("""
        set foreign_key_checks=1
    """))
    print("테이블 초기화 완료!!!")
    print("==========================")

def get_user(user_id):
    row=database.execute(text("""
        select
            id,
            name,
            email,
            profile
        from users
        where id=:user_id
    """),{'user_id':user_id}).fetchone()
    return {
        'id':row['id'],
        'name':row['name'],
        'email':row['email'],
        'profile':row['profile']
    } if row else None
    
def get_follow_list(user_id):
    rows=database.execute(text("""
        select follow_user_id as id
        from users_follow_list
        where user_id=:user_id
    """),{'user_id':user_id}).fetchall()
    
    return [int(row['id']) for row in rows]

def test_create_new_user(user_service):
    new_user={
        'id':3,
        'name':'test3',
        'email':'test3@naver.com',
        'password':'test3',
        'profile':'test3'
    }
    new_user_id=user_service.create_new_user(new_user)
    created_user=get_user(new_user_id)
    assert created_user=={
        'id':new_user_id,
        'name':new_user['name'],
        'email':new_user['email'],
        'profile':new_user['profile']
    }

def test_login(user_service):
    assert user_service.login({
        'email':'test1@naver.com',
        'password':'test'
    })
    #잘못된 비번일 때도 확인
    assert not user_service.login({
        'email':'test1@naver.com',
        'password':'test11111'
    })
    
def test_generate_access_token(user_service):
    token=user_service.generate_access_token(1)

    payload=jwt.decode(token,config.JWT_SECRET_KEY,'HS256')

    assert payload['user_id']==1
    
def test_follow(user_service):
    user_service.follow(1,2)
    
    assert get_follow_list(1)==[2]

def test_unfollow(user_service):
    user_service.follow(1,2)
    user_service.unfollow(1,2)

    assert get_follow_list(1)==[]
    
def test_tweet(tweet_service):
    tweet_service.tweet(1,"hollow im 1 user")
    timeline=tweet_service.get_timeline(1)
    
    assert timeline==[
        {
            'user_id':1,
            'tweet':"hollow im 1 user"
        }
    ]
def test_timeline(user_service,tweet_service):
    tweet_service.tweet(1,"hellow im 1 user")
    tweet_service.tweet(2,"test2")
    user_service.follow(1,2)
    
    timeline=tweet_service.get_timeline(1)
    
    assert timeline==[{
        'user_id':2,
        'tweet':"hellow wordl!"
    },
    {
        'user_id':1,
        'tweet':"hellow im 1 user"
    },
    {
        'user_id':2,
        'tweet':"test2"
    }]
    