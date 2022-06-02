import tweepy

API_KEY = ""
API_KEY_SECRET = ""

ACCESS_TOKEN = ""
ACCESS_SECRET = ""

#발급받은 key token 입력

auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET, callback='oob') 
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# 4.퍼블릭 트윗 작성
api.update_status("테스트...(해킹아님)")