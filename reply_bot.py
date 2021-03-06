import tweepy
import time
import random
import datetime
import gspread
import pprint


API_KEY = "키"
API_KEY_SECRET = "키"
USER_ACCESS_TOKEN = "토큰"
USER_ACCESS_SECRET= "토큰"

# OAuth1
auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET, 'oob') 
auth.set_access_token(USER_ACCESS_TOKEN, USER_ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

gc = gspread.service_account(filename='-') #json파일 이름

wks = gc.open("-") #시트 이름

def select_sheet(sheet_name):
    worksheet = wks.worksheet(sheet_name)
    return worksheet

##################################################################


bot = api.verify_credentials() # 봇의 user obj 반환 
bot_id = bot.id # 봇 id (고유값, 주소) 
timeline_list = api.user_timeline(user_id =bot_id)
last_reply_id = timeline_list[0].id_str
# last_reply_id = 1 # 최근에 답장한 멘션의 id값을 저장, 이후 새로 온 멘션에만 답장한다.
keywords = ['판매'] # 키워드

#키워드 타입 1 : 주사위 2: 자판기 3:YN 

# 주의!!! 리트윗과 멘션 합해서 3시간에 300개 가능


# 새 멘션 확인하는 함수
def check_new_mention():
    print("! 멘션을 확인하는 함수를 호출합니다")
    global last_reply_id
    mention_return = api.mentions_timeline(since_id=last_reply_id) # since_id 이후의 트윗만 가져온다.
    mention_return_length = len(mention_return) # 받아온 새 멘션의 개수

    # 새 멘션이 있나?
    if mention_return_length > 0: 
        print('! 키워드를 체크하는 함수를 호출합니다.')
        check_keyword(mention_return_length, mention_return) # 키워드 체크하는 함수. 새 멘션 개수와, 새 멘션들을 매개변수로 넘긴다.
        print('! 다음 동작 시간을 기다립니다')
        return # return을 만났으니 44줄로는 가지 않고 mention_return_length 함수를 빠져나간다

    print('! 새 멘션이 없습니다.')

# 키워드 체크 함수
def check_keyword(mention_return_length, mention_return): 
    for i in range(mention_return_length-1, -1, -1): # 최신 멘션부터 불러오기 때문에 거꾸로 순회
        mention = mention_return[i] # 현재 보고 있는 멘션
        mention_text = mention.text # 의 내용
        keyword_type = -1 # 초기 키워드 타입. 마지막에도 -1이면 미리 지정된 키워드를 넣지 않은 사용자 오류
        reply_content = "키워드 오류입니다." # 초기 답멘 내용. 키워드 오류 때문에 다음 함수로 넘어가지 않으면 이 내용이 답멘으로 출력된다.
        keyword_action_return = ''

        try: 
            if mention.author.id != bot_id: # 내가 보낸 멘션이 아닐때만 답멘한다
                # [] 가 존재하나?
                start = mention_text.find('[')
                end = mention_text.find(']')
                
                if (start != -1 and end != -1) and start<end: # [] 조건 찾기. [, ]가 존재해야 하고, 닫는 괄호가 여는 괄호보다 앞에 있으면 안된다.
                    if 'd' in mention_text[start+1:end] or 'D' in mention_text[start+1:end]: #키워드 없는 명령어
                        mention_keyword = mention_text[start+1:end]
                        keyword_action_return = roll_dice(mention_keyword)
                        if keyword_action_return != (-1, -1, -1): # 리턴값이 정상이면
                                keyword_type = 1 # 키워드 타입 갱신
                    elif mention_text[start+1:end] == '자판기':
                        keyword_action_return = use_japangi(mention) # 스프레드 시트 내의 상점 데이터를 확인하고 후처리하는 함수
                        if keyword_action_return != -1: # 리턴값이 -1이 아니어야 정상이므로
                            keyword_type = 2
                    elif mention_text[start+1:end] == 'yn' or mention_text[start+1:end] == 'YN':
                        keyword_action_return = -1
                        keyword_action_return = random.choice(["Yes", "No"])
                        if keyword_action_return != -1: # 리턴값이 -1이 아니어야 정상이므로
                            keyword_type = 3
                    else: #키워드 있는 명령어
                        mention_keyword = mention_text[start+1:end].strip().split('/') # /를 기준으로 나눠 리스트로 저장. 받은 멘션 내용이 [다이스/1d2] 라면 ['다이스', '1d2'] 로 저장된다.
                        first_keyword = mention_keyword[0].strip() # 나눠 저장한 리스트가 비었으면 공란(''), 아니라면 첫번째 값을 저장한다. 위의 예시에서는 '다이스' 가 저장된다.

                        ###################### 키워드 별 함수 호출. 키워드가 늘어나면 여기가 길어진다. ######################
                        if first_keyword in keywords: 
                            if first_keyword == '판매': 
                                keyword_action_return = update_inventory(mention, mention_keyword[1], 2) # 스프레드 시트 내의 상점 데이터를 확인하고 후처리하는 함수
                                if keyword_action_return != -1: # 리턴값이 -1이 아니어야 정상이므로
                                    keyword_type = 4
                        #################################################################################################
            
                
                if keyword_type != -1: # 키워드 오류가 없으면
                    reply_content= make_reply_content(keyword_type, keyword_action_return) # 타입, 키워드 별 함수의 호출의(66~76) 결과(리턴)값을 매개변수로 넣어 답멘 내용을 만드는 함수 호출
            
                # 답멘하는 함수
                # 키워드 오류가 있든없든 이 함수는 호출된다
                reply_function(mention, reply_content) # 현재 보고 있는 멘션, 만든 답멘 내용
                print('! 답멘이 완료되었습니다.')
        except:
            print('! 키워드 체크 도중 오류가 발생했습니다.')

# 다이스 굴리는 함수
def roll_dice(mention_keyword):
    print('! 다이스 굴리는 함수를 호출합니다.')
    dice_info = []
    dice_result_list = []

    if len(mention_keyword) > 2: # 넘겨받은 매개변수의 길이가 1 초과라면 (예시 : ['다이스', '1d2'] 이므로 길이는 2다)
        second_keyword = mention_keyword.strip() # 두번째 키워드를 보정한다. strip()은 앞뒤 공백을 지우는 함수다. (ex: ' 1d2 ' 였다면 '1d2'로 만든다)
        
        if 'd' in second_keyword: # 두번째 키워드 중에 d가 있다면
            dice_info = second_keyword.split('d') # d를 기준으로 나누고 dice_info에 저장 (ex: '1d2' -> ['1', 'd', '2'])
        elif 'D' in second_keyword: # 두번째 키워드 중에 D가 있다면
            dice_info = second_keyword.split('D') # D를 기준으로 나누고 dice_info에 저장 (ex: '1D2' -> ['1', 'D', '2'])
        
        if len(dice_info) == 2: # D 앞뒤로 숫자 있나확인
            try:
                dice_f_num = int(dice_info[0]) # 첫번째 값은 '몇 번 굴릴것'인가 
                dice_s_num = int(dice_info[1]) # 두번째 값은 '몇 면체'인가
                for _ in range(dice_f_num): # 첫번째 값만큼 반복
                    dice = random.randrange(1, dice_s_num+1) # 1 ~ 몇면체 사이의 값을 랜덤하게 뽑아서 dice에 저장
                    dice_result_list.append(dice) # tmp_list에 굴린 다이스를 순서대로 추가 
                return (dice_f_num, dice_s_num, dice_result_list) # 몇 번, 몇 면체, 총합, 다이스 숫자를 담아서 리턴
            except:
                print("에러 발생")
                pass

    print("! 다이스 키워드가 잘못됐습니다")    
    return(-1, -1, -1)


# 자판기
def use_japangi(mention):
    worksheet = select_sheet('자판기') # 21번째 줄에서 입력한 '내 스프레드 시트 이름' 시트의 '자판기' 이라는 탭을 선택
    all_shop_info = worksheet.get_all_records() # 전체 데이터를 가져온다
    #pprint.pprint(all_shop_info)  

    user = api.get_user(screen_name=mention.user.screen_name) #멘션한 계정의 정보를 불러오는 함수
    name = user.name #멘션한 계정의 정보를 불러오는 함수
    username = name.split()

    randomItem = random.choice(all_shop_info)

    answer = username[0] + '은(는) ' + randomItem['1'] +'을(를) 뽑았다! \n\n' +randomItem['2']

    update_inventory(mention, randomItem['1'], 1)

    return answer # 같은 아이템을 찾지 못했다면 -1 리턴

#상점
def use_shop(mention, mention_keyword):
    worksheet = select_sheet('자판기') # 21번째 줄에서 입력한 '내 스프레드 시트 이름' 시트의 '포스팅_무료상점' 이라는 탭을 선택
    all_shop_info = worksheet.get_all_records() # 전체 데이터를 가져온다
    pprint.pprint(all_shop_info)  # 데이터 확인이 쉽도록 터미널에 print 해본다. 익숙해졌다면 지워도 된다.
    for i in range(len(all_shop_info)):
        if (all_shop_info[i]['1']) == mention_keyword[1]: # 상점 내에 있는 아이템 이름 == 멘션으로 받은 키워드 중 두번째 키워드 라면
            return all_shop_info[i]['2'] # 그 아이템의 설명을 리턴
    return -1 # 같은 아이템을 찾지 못했다면 -1 리턴




#인벤토리 업데이트

def update_inventory(mention, values, type):
    worksheet = select_sheet('자판기')
    worksheet2 = select_sheet(mention.user.screen_name)
    cell = worksheet2.find(values)
    price_cell = worksheet.find(values)
    price = int(worksheet.acell('E'+str(price_cell.row)).value)

    now_money = int(worksheet2.acell('E1').value)

    # 1 : 아이템 획득 2 : 아이템 판매 3 : 골드 획득 4 : 골드 판매
    if type == 1 :
        if cell is None:
            worksheet2.append_row(values)
            worksheet2.update('B'+str(cell.row), 1)
        else:
            cnt = int(worksheet2.acell('B'+str(cell.row)).value)
            cnt += 1
            worksheet2.update('B'+str(cell.row), cnt)
    if type == 2 :
        cnt = int(worksheet2.acell('B'+str(cell.row)).value)
        if cell is None or cnt == 0:
            return values+'를(을) 소지하고 있지 않습니다.'
        else:
            cnt -= 1
            now_money += price
            worksheet2.update('B'+str(cell.row), cnt)
            worksheet2.update('E1', now_money)
            return values+'의 판매가 완료되었습니다. \n' + '현재 소지금은 ' + str(now_money) + '골드 입니다.'




# 답멘 내용 만드는 함수
def make_reply_content(type_of_keyword, keyword_action_return):
    print('! 답멘 내용 만드는 함수를 호출합니다.')
    reply_content = ''
    try:
        if type_of_keyword == 1: # 키워드 타입이 다이스일 경우
            dice_results = str(keyword_action_return[2])[1:-1] # ex: [2, 6] (리스트)-> '[2, 6]' (문자열) -> '2, 6' (앞뒤 자름)
            reply_content += str(keyword_action_return[0]) +'D' + str(keyword_action_return[1]) + ' 다이스를 굴립니다. \n' + dice_results + '. 총 ' + str(sum(keyword_action_return[2])) + '입니다.'         
        elif type_of_keyword == 2 or type_of_keyword == 3 or type_of_keyword == 4: # 키워드 타입이 자판기거나 YN일 경우
            reply_content = keyword_action_return

    except:
        print('! 오류가 발생했습니다.')
        pass
    return reply_content


def reply_function(mention, reply_content):
    print('! 답멘하는 함수를 호출합니다.')
    global last_reply_id
    reply_to ="@" + mention.author.screen_name+ ' ' # 맨 앞에 붙일 @아이디
    now = datetime.datetime.now() # 현재 시간, 중복트 방지 용
    nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S') # 현재 시간을 보기에 예쁜 모양으로 바꿈
    total_reply_content = reply_to + reply_content + '\n\n' + nowDatetime # 전체 답멘 내용은 @답멘대상 답멘내용 엔터두번(\n\n) 현재시간
    try:
        api.update_status(total_reply_content, in_reply_to_status_id=mention.id_str) # 답멘 하는 함수
        last_reply_id = mention.id_str # 어디까지 답멘했나 확인하는 용도.
    except:
        print("! 답멘하는 함수에서 발생한에러입니다")
        pass
    return

while True:
    check_new_mention()
    time.sleep(60)