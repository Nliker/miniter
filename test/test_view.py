import sys,os
import bcrypt
import json
sys.path.append((os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
import config
from app import create_app
import pytest
from sqlalchemy import create_engine,text

database=create_engine(config.test_config['DB_URL'],encoding='utf-8',max_overflow=0)

@pytest.fixture()
def api():
    app=create_app(test_config=config.test_config)
    app.config['TEST']=True
    api=app.test_client()
    return api

def setup_function():

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

def test_ping(api):
    resp=api.get('/ping')
    
    assert b"pong" in resp.data

def test_sign_up(api):
    resp=api.post('/sign-up',
        data=json.dumps({
        'email':"test25@naver.com",
        'name':"test3",
        'profile':"test3",
        'password':"test3"}),
        content_type='application/json')

    assert resp.status_code==200

    resp_json=json.loads(resp.data.decode('utf-8'))

    assert resp_json=={
        'email':"test25@naver.com",
        'name':"test3",
        'profile':"test3",
    }

def test_login(api):
    resp=api.post('/login',data=json.dumps({
        'email':'test1@naver.com',
        'password':'test'
    }),content_type='application/json')
    
    assert resp.status_code==200
    
    assert b'access_token' in resp.data and b'id' in resp.data

def test_unauthorized(api):
    resp=api.post('/login',data=json.dumps({
        'email':'test1@naver.com',
        'password':'unauthorized'
    }),content_type='application/json')

    assert resp.status_code==401
    
    resp=api.post('/follow',data=json.dumps({
        'follow':2
    }),content_type="application/json")

    assert resp.status_code==401

    resp=api.post('/unfollow',data=json.dumps({
        'unfollow':2
    }),content_type="application/json")

    assert resp.status_code==401

    resp=api.post('/tweet',data=json.dumps({
        'tweet':"testing"
    }),content_type="application/json")

    assert resp.status_code==401
    
    resp=api.get('/timeline')
    
    assert resp.status_code==401

def test_tweet(api):
    resp=api.post('/login',data=json.dumps({
        'email':'test1@naver.com',
        'password':'test'
    }),content_type='application/json')


    json_data=json.loads(resp.data.decode('utf-8'))
    access_token=json_data["access_token"]
    
    resp=api.post('/tweet',data=json.dumps({
        'tweet':"im testing"
    }),
    headers={
        "Authorization":access_token
    },
    content_type="application/json")
    
    assert resp.status_code==200

    resp=api.get('/timeline/1')
    print(resp.data)
    tweet=json.loads(resp.data.decode('utf-8'))

    assert resp.status_code==200
    assert tweet=={
        'user_id':1,
        'timeline':[
            {
                'user_id':1,
                'tweet':"im testing"
            }
        ]
    }
    
def test_follow(api):
    resp=api.post('/login',data=json.dumps({
        'email':'test1@naver.com',
        'password':'test'
    }),content_type='application/json')
    
    json_data=json.loads(resp.data.decode('utf-8'))
    access_token=json_data["access_token"]
    
    resp=api.get('/timeline/1')
    tweets=json.loads(resp.data.decode('utf-8'))

    assert resp.status_code==200
    assert tweets=={
        'user_id':1,
        'timeline':[]
    }

    resp=api.post('/follow',data=json.dumps({
        'follow':2
    }),
    headers={
        'Authorization':access_token},
    content_type='application/json')
    
    resp.status_code==200
    
    resp=api.get('/timeline/1')
    tweets=json.loads(resp.data.decode('utf-8'))

    assert resp.status_code==200
    assert tweets=={
        'user_id':1,
        'timeline':[
            {
                'user_id':2,
                'tweet':"hellow wordl!"
            }
        ]
    }
    
def test_unfollow(api):
    resp=api.post('/login',data=json.dumps({
        'email':'test1@naver.com',
        'password':'test'
    }),content_type='application/json')
    
    json_data=json.loads(resp.data.decode('utf-8'))
    access_token=json_data["access_token"]
    
    resp=api.post('/follow',data=json.dumps({
        'follow':2
    }),
    headers={
        'Authorization':access_token},
    content_type='application/json')
    
    resp.status_code==200
    
    resp=api.get('/timeline/1')
    tweets=json.loads(resp.data.decode('utf-8'))

    assert resp.status_code==200
    assert tweets=={
        'user_id':1,
        'timeline':[
            {
                'user_id':2,
                'tweet':"hellow wordl!"
            }
        ]
    }
    
    resp=api.post('/unfollow',data=json.dumps({
        'unfollow':2
    }),
    headers={
        'Authorization':access_token},
    content_type='application/json')
    
    resp=api.get('/timeline/1')
    tweets=json.loads(resp.data.decode('utf-8'))

    assert resp.status_code==200
    assert tweets=={
        'user_id':1,
        'timeline':[]
    }