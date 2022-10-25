db={
    "user":"codakcodak",
    "password":"dkdrmaghEl83!",
    "host":"miniter.cnvmcb0pomhk.ap-northeast-2.rds.amazonaws.com",
    "port":3306,
    "database":"miniter"
}
JWT_SECRET_KEY="codak"
test_db={
    'user':'codakcodak',
    'password':'dkdrmaghEl83!',
    'host':'localhost',
    'port':3306,
    'database':'test_miniter'
}

DB_URL=f"mysql+mysqlconnector://{test_db['user']}:{test_db['password']}@{test_db['host']}:{test_db['port']}/{test_db['database']}?charset=utf8"
test_config={
    'DB_URL':f"mysql+mysqlconnector://{test_db['user']}:{test_db['password']}@{test_db['host']}:{test_db['port']}/{test_db['database']}?charset=utf8",
    'JWT_SECRET_KEY':"codak",
    'S3_BUCKET':"test",
    'S3_ACCESS_KEY':"test_access_key",
    'S3_SECRET_KEY':"test_secret_key",
    'S3_BUCKET_URL':"http://s3.amazonaws.com/"
}

UPLOAD_DIR='./profile_pictures'

S3_BUCKET="miniter"
S3_ACCESS_KEY="AKIA4JNNATB765B7AZK6"
S3_SECRET_KEY="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",
S3_BUCKET_URL=f"http://{S3_BUCKET}.s3.amazonaws.com/"

