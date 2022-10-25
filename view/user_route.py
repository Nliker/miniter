from flask import request,jsonify,send_file
import json
from werkzeug.utils import secure_filename
import sys,os
sys.path.append((os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
from auth import login_required,g

def UserEndpoint(app,service):
    user_service=service.user_service
    
    @app.route("/sign-up",methods=["POST"])
    def sign_up():
        new_user=request.json
        new_user_id=user_service.create_new_user(new_user)
  
        return jsonify({
            'email':new_user["email"],
            'name':new_user["name"],
            'profile':new_user["profile"]
        }),200 
       
    @app.route("/login",methods=["POST"])
    def login():
        credential=request.json
        authorized=user_service.login(credential)
        
        if authorized:
            user_credential=user_service.get_user_id_and_password(credential['email'])
            user_id=user_credential['id']
            token=user_service.generate_access_token(user_id)
            
            return jsonify({
                'user_id':user_id,
                'access_token':token
            })
        else:
            return '옳바르지 않은 비밀번호 입니다.',401
        
    @app.route("/follow",methods=["POST"])
    @login_required
    def follow():
        payload=request.json
        user_id=g.user_id
        follow_id=payload['follow']

        result=user_service.follow(user_id,follow_id)
        
        return f"{result}개 저장성공!",200
    
    @app.route("/unfollow",methods=["POST"])
    @login_required
    def unfollow():
        payload=request.json
        user_id=g.user_id
        unfollow_id=payload['unfollow']
        
        result=user_service.unfollow(user_id,unfollow_id)
        
        return f"{result}개 저장성공!",200
    
    @app.route("/profile-picture",methods=["POST"])
    @login_required
    def upload_profile_picture():
        user_id=g.user_id

        if 'profile_pic' not in request.files:
            return 'File is missong',404
        
        profile_pic=request.files['profile_pic']

        if profile_pic.filename=='':
            return 'File is missing',404
        
        filename=secure_filename(profile_pic.filename)

        result=user_service.save_profile_picture(profile_pic,filename,user_id)
        
        return f"{result}개 저장완료!",200
    
    # @app.route("/profile-picture/<int:user_id>",methods=["GET"])
    # def get_profile_picture(user_id):
    #     profile_picture=user_service.get_profile_picture(user_id)
        
    #     if profile_picture:
    #         return send_file(profile_picture)
        
    #     else:
    #         return '',404
        
    @app.route("/profile-picture/<int:user_id>",methods=["GET"])
    def get_profile_picture(user_id):
        profile_picture=user_service.get_profile_picture(user_id)
        
        if profile_picture:
            return jsonify({'img_url':profile_picture})
        
        else:
            return '',404
        