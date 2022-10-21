from flask import request,jsonify
import sys,os
sys.path.append((os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
from auth import login_required,g

def TweetEndpoint(app,services):
    tweet_service=services.tweet_service
    
    @app.route("/tweet",methods=["POST"])
    @login_required
    def tweet():
        user_tweet=request.json
        tweet=user_tweet['tweet']
        user_id=g.user_id
        
        result=tweet_service.tweet(user_id,tweet)
        
        if result is None:
            return '300자를 초과했습니다.',400
        return f"{result}개 저장 성공!",200
    
    @app.route("/timeline/<int:user_id>",methods=["GET"])
    def timeline(user_id):
        timeline=tweet_service.get_timeline(user_id)
        
        return jsonify({
            'user_id':user_id,
            'timeline':timeline
        })
    
    @app.route("/timeline",methods=["GET"])
    @login_required
    def user_timeline():
        timeline=tweet_service.get_timeline(g.user_id)

        return jsonify({
            'timeline':timeline
        })
        