import tweepy

API_KEY = ""
API_KEY_SECRET = ""

#my ACCESS_TOKEN
#ACCESS_TOKEN = ""
#ACCESS_SECRET = ""

auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET, callback='oob') 

try: # 성공 했을 때
    redirect_url = auth.get_authorization_url() 
    print(redirect_url)
except tweepy.TweepError: # 에러 떴을 때 
    print('리퀘스트 토큰을 가져오는 데에 실패했습니다.')


# 핀 번호 저장 및 세팅
pin_number = input("핀 번호:")
auth.get_access_token(pin_number)

#사용자의 토큰을 세팅, Twitter API wrapper 생성
USER_ACCESS_TOKEN = auth.access_token
USER_ACCESS_SECRET= auth.access_token_secret
auth.set_access_token(USER_ACCESS_TOKEN, USER_ACCESS_SECRET)
print(USER_ACCESS_TOKEN)
print(USER_ACCESS_SECRET)
api = tweepy.API(auth)

#트윗하기 
api.update_status("다른 계정 트윗 작성")