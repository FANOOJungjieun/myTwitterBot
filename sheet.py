import gspread
import pprint

gc = gspread.service_account(filename='-') #json파일 이름

wks = gc.open("테스트 시트") #시트 이름

# 시트 탭 선택 함수
def select_sheet(sheet_name):
    worksheet = wks.worksheet(sheet_name)
    return worksheet

# 시트 전체 정보 터미널에 프린트하는 함수
def shop_sheet(worksheet):    
    all_shop_info= worksheet.get_all_records()
    pprint.pprint(all_shop_info)
    

worksheet = select_sheet('MAIN') #스프레드 시트 하단 탭 이름
shop_sheet(worksheet)    