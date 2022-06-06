import tweepy

API_KEY = "토큰"
API_KEY_SECRET = "토큰"

auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET, callback='oob') 

try: # 성공 했을 때
    redirect_url = auth.get_authorization_url() 
    print(redirect_url)
except tweepy.TweepError: # 에러 떴을 때 
    print('리퀘스트 토큰을 가져오는 데에 실패했습니다.')


# 5. 받은 핀 번호 저장 및 세팅
pin_number = input("핀 번호:")
auth.get_access_token(pin_number)

# 6. 사용자의 토큰을 세팅, Twitter API wrapper 생성
USER_ACCESS_TOKEN = auth.access_token
USER_ACCESS_SECRET= auth.access_token_secret
auth.set_access_token(USER_ACCESS_TOKEN, USER_ACCESS_SECRET)
print("액세스 토큰 : ", USER_ACCESS_TOKEN, "\n", "액세스 시크릿 토큰 : ", USER_ACCESS_SECRET)
api = tweepy.API(auth)

# 7. 트윗하기 
api.update_status("연결 테스트 트윗입니다.")