from flask import jsonify,request,g,current_app
from functools import wraps
import jwt
from datetime import datetime
def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kargs):
        access_token=request.headers.get('Authorization')
        if access_token is not None:
            print(access_token)
            try:
                print("-========")
                print(current_app.config)
                payload=jwt.decode(access_token,current_app.config['JWT_SECRET_KEY'],'HS256')
                print(payload['iat'])
                print(payload)
                print(datetime.fromtimestamp(payload['iat']))
            except:
                return jsonify({"message":"유효하지 않은 토큰이거나 토큰 검증과정에서 에러가 났습니다."}),401
            if 'user_id' in payload and payload['user_id'] is not None:
                user_id=payload['user_id']
                g.user_id=user_id
                
            else:
                return jsonify({"message":"필수정보가 없는 토큰입니다."}),401
                
        else:
            return jsonify({"message":"토큰이 없습니다."}),401
        print("================")
        print(g)
        return f(*args,**kargs)
    return decorated_function