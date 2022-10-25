from flask import Flask
from sqlalchemy import create_engine
from flask_cors import CORS

import boto3
from model import UserDao,TweetDao
from service import UserService,TweetService
from view import UserEndpoint,TweetEndpoint

class Services:
    pass

def create_app(test_config=None):
    app=Flask(__name__)
    
    CORS(app)
    
    if test_config is None:
        app.config.from_pyfile("config.py")

    else:
        app.config.update(test_config)
        
    database=create_engine(app.config['DB_URL'],encoding='utf-8',max_overflow=0)
    print("데이터베이스 연결 성공!")
    user_dao=UserDao(database)
    tweet_dao=TweetDao(database)
    
    s3_client=boto3.client(
            "s3",
            aws_access_key_id=app.config['S3_ACCESS_KEY'],
            aws_secret_access_key=app.config['S3_SECRET_KEY']
        )
    
    services=Services
    services.user_service=UserService(user_dao,app.config,s3_client)
    services.tweet_service=TweetService(tweet_dao)
    
    @app.route("/ping",methods=["GET"])
    def ping():
        return "pong",200    
        
    UserEndpoint(app,services)
    TweetEndpoint(app,services)
    
    return app