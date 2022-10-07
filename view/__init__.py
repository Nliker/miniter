from flask import jsonify,request

def create_endpoints(app,services):
    user_service=services.user_service
    
    @app.route("/sign-up",methods=['POSR'])
    def sign_up():
        new_user=request.json
        new_user_id=user_service.create_new_user(new_user)
        
        new_user=user_service.get_user(new_user_id)
        
        return jsonify(new_user)