import bcrypt
import pytest
import sys,os
sys.path.append((os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
import config

from model import UserDao,TweetDao
from sqlalchemy import create_engine,text

database=create_engine(config.test_config['DB_URL'],encoding='utf-8',max_overflow=0)

@pytest.fixture
def user_dao():
    return UserDao(database)

@pytest.fixture
def tweet_dao():
    return TweetDao(database)

def setup_function():
    print("======setup function======")
    print("데이터베이스 저장중")
    hashed_password1=bcrypt.hashpw(
        b"test1password",
        bcrypt.gensalt()
    )
    hashed_password2=bcrypt.hashpw(
        b"test2password",
        bcrypt.gensalt()
    )
    new_users={
        'id' :1,
        'name':'test1',
        'email':'test1@naver.com',
        'profile':'testuser1',
        'hashed_password':hashed_password1
    },{
        'id' :2,
        'name':'test2',
        'email':'test2@naver.com',
        'profile':'testuser2',
        'hashed_password':hashed_password2
    }
    
    database.execute(text("""
        insert into users (
            id,name,email,profile,hashed_password
        ) values(
            :id,:name,:email,:profile,:hashed_password
        )
    """),new_users)
    database.execute(text("""
        insert into tweets (
            user_id,tweet 
        ) value (
            :user_id,:tweet
        )
    """),{'user_id':2,'tweet':"im testing a tweet"})
    print("데이터베이스 저장성공!!!")
    print("==========================")
    
    
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
    select
        follow_user_id as id
    from users_follow_list
    where user_id=:user_id
    """),{'user_id':user_id}).fetchall()
    
    return [int(row['id']) for row in rows]

def test_insert_user(user_dao):
    new_user={
        'name':'test3',
        'email':'test3@naver.com',
        'profile':'testuser3',
        'password':'test3'
    }
    new_user_id=user_dao.insert_user(new_user)
    user=get_user(new_user_id)
    
    assert user=={
        'id':new_user_id,
        'name':new_user['name'],
        'email':new_user['email'],
        'profile':new_user['profile']
    }
    
def test_get_user_id_and_password(user_dao):
    user_credential=user_dao.get_user_id_and_password(email='test1@naver.com')
    
    assert user_credential['id']==1
    password="test1password"
    assert type(user_credential['hashed_password'])==type("sd")
    authorized=bcrypt.checkpw(password.encode('UTF-8'),user_credential['hashed_password'].encode('UTF-8'))

    assert authorized== True

def test_insert_follow(user_dao):
    user_dao.insert_follow(user_id=1,follow_id=2)
    
    follow_list=get_follow_list(1)
    
    assert follow_list==[2]

def test_insert_unfollow(user_dao):
    #이미 insert_follow 는 위에서 검증했으니 한번더 검증 안해도 된다.
    user_dao.insert_follow(user_id=1,follow_id=2)
    user_dao.insert_unfollow(user_id=1,unfollow_id=2)
    
    follow_list=get_follow_list(1)
    
    assert follow_list==[]
    
def test_insert_tweet(tweet_dao):
    user=get_user(1)
    assert user=={
        'id':1,
        'name':'test1',
        'email':'test1@naver.com',
        'profile':'testuser1',
    }
    tweet="im testing tweet for id 1 user"
    
    assert 1==tweet_dao.insert_tweet(user_id=1,tweet=tweet)
    timeline=tweet_dao.get_timeline(user_id=1)
    
    assert timeline==[{
        'user_id':1,
        'tweet':tweet
    }]
    
def test_get_timeline(user_dao,tweet_dao):
    tweet_dao.insert_tweet(1,"tweet test1")
    tweet_dao.insert_tweet(2,"tweet test2")

    user_dao.insert_follow(1,2)
    timeline=tweet_dao.get_timeline(1)
    assert timeline==[
        {
            'user_id':2,
            'tweet':'im testing a tweet'
        },
        {
            'user_id':1,
            'tweet':'tweet test1'
        },
        {
            'user_id':2,
            'tweet':'tweet test2'
        }
    ]