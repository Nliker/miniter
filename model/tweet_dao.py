from sqlalchemy import text
from collections import deque
from flask import jsonify

class TweetDao:
    def __init__(self,database):
        self.db=database
    
    def insert_tweet(self,user_id,tweet):
        return self.db.execute(text("""
        insert into tweets(
            user_id,
            tweet
        ) values(
            :user_id,
            :tweet
        )
        """),{'user_id':user_id,'tweet':tweet}).rowcount

    def get_timeline(self,user_id):
        timeline=self.db.execute(text("""
            select 
                t.user_id,
                t.tweet
            from tweets as t
            left join users_follow_list ufl on ufl.user_id=:user_id
            where t.user_id=:user_id 
            or ufl.follow_user_id=t.user_id
        """),{'user_id':user_id}).fetchall()
        
        data=[  {"tweet":row['tweet'], "user_id":row['user_id']} for row in timeline]

        data=deque(data)
        sub=deque()
        
        for tweet in data:
            if tweet not in sub:
                sub.append(tweet)
            else:
                continue
        data=list(sub)
        
        return data
            
        