import tweepy
import json

# 키, 토큰
API_KEY = "키"
API_KEY_SECRET = "키"
USER_ACCESS_TOKEN = "토큰"
USER_ACCESS_SECRET= "토큰"

# OAuth1
auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET, 'oob') 
auth.set_access_token(USER_ACCESS_TOKEN, USER_ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)
bot = api.verify_credentials() 

# JSON 파일 불러오는 과정
path = "./tweet.json"
with open(path, "r", encoding='UTF8') as json_file:
    tweet_json = json.load(json_file)

# 삭제하는 코드
for i in range(len(tweet_json)):
    delete_id = tweet_json[i]['tweet']['id']
    try:
        api.destroy_status(delete_id)
        print('삭제 성공')
    except Exception as exc:        
        print(exc)