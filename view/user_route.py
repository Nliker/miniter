from flask import request,jsonify

def UserEndpoint(app,service):
    user_service=service.user_service
    
    @app.route("/sign-up",methods=["POST"])
    def sing_up():
        new_user=request.json
        new_user_id=user_service.create_new_user(new_user)
        
        return jsonify(new_user)
    
    @app.route("login",methods=["POST"])
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