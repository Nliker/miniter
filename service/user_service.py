import bcrypt
import jwt
from datetime import datetime, timedelta
import os
import boto3

jwtExpireTime=  timedelta(seconds=600)

class UserService:
    def __init__(self,user_dao,config,s3_client):
        self.user_dao=user_dao
        self.config=config
        self.s3=s3_client
        
    def get_user_id_and_password(self,email):
        return self.user_dao.get_user_id_and_password(email)
        
    def create_new_user(self,new_user):
        new_user['password']=bcrypt.hashpw(
            new_user['password'].encode('utf-8'),bcrypt.gensalt()
        ).decode('utf-8')
        
        new_user_id=self.user_dao.insert_user(user=new_user)
        return new_user_id
    
    def login(self,credential):
        email=credential['email']
        password=credential['password']
        user_credential=self.user_dao.get_user_id_and_password(email)
        authorized=user_credential and bcrypt.checkpw(password.encode('utf-8'),user_credential['hashed_password'].encode('utf-8'))
        return authorized
    
    def generate_access_token(self,user_id):
        payload={
            'user_id':user_id,
            'exp':datetime.utcnow()+jwtExpireTime,
            'iat':datetime.utcnow()
        }
        
        token=jwt.encode(payload,self.config['JWT_SECRET_KEY'],'HS256')
        print(token)
        return token

    def follow(self,user_id,follow_id):
        return self.user_dao.insert_follow(user_id,follow_id)

    def unfollow(self,user_id,unfollow_id):
        return self.user_dao.insert_unfollow(user_id,unfollow_id)

    # def save_profile_picture(self,picture,filename,user_id):
    #     profile_pic_path_and_name=os.path.join(self.config['UPLOAD_DIR'],filename)
    #     print(profile_pic_path_and_name)
    #     picture.save(profile_pic_path_and_name)
    #     print(os.path.os.getcwd())
    #     return self.user_dao.save_profile_picture(profile_pic_path_and_name,user_id)
    
    def get_profile_picture(self,user_id):
        
        return self.user_dao.get_profile_picture(user_id)
    
    def save_profile_picture(self,picture,filename,user_id):
        self.s3.upload_fileobj(
            picture,
            self.config['S3_BUCKET'],
            filename
        )
        img_url=f"{self.config['S3_BUCKET_URL']}{filename}"
        return self.user_dao.save_profile_picture(img_url,user_id)
       