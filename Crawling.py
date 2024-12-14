from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options  # Options를 임포트
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import urllib.parse
import time
import pandas as pd

def SajongSi_food(keyword, num_pages):
    # 크롬 드라이버 위치 설정 및 옵션 지정
    chrome_options = Options()  # Options 사용
    service = Service("C:\\data\\chromedriver-win32\\chromedriver-win32\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 검색 키워드 입력
    text1 = urllib.parse.quote(keyword)

    # 최종 음식점 정보를 담을 리스트
    food_data = []  
    
    # 카카오맵 검색 URL
    url = f"https://map.kakao.com/?q={text1}"

    # 크롬으로 해당 URL 접속
    driver.get(url)
    time.sleep(2)
    
    # 페이지 넘기기
    for i in range(1, num_pages + 1):
        try:
            # HTML 파싱 및 음식점 정보 추출
            soup = BeautifulSoup(driver.page_source, "html.parser")
            list_url = [a_tag.get("href") for a_tag in soup.select("a.moreview")]

            for food_url in list_url:
                # 음식점 상세 페이지로 이동
                driver.get(food_url)
                time.sleep(2)

                # 음식점 정보 수집
                soup = BeautifulSoup(driver.page_source, "html.parser")
                try:
                    # 음식점 이름 추출
                    name_tag = soup.select_one('div.inner_place > h2.tit_location')
                    food_name = name_tag.text.strip() if name_tag else "이름 없음"

                    # 음식점 연락처 추출 
                    call_number_tag = soup.select_one("#mArticle > div.cont_essential > div.details_placeinfo > div.placeinfo_default.placeinfo_contact > div > div > span")
                    call_number = call_number_tag.text.strip() if call_number_tag else "음식점 연락처 정보 없음"

                    # 음식점 운영 시간 추출 
                    open_hours_tag = soup.select_one("#mArticle > div.cont_essential > div.details_placeinfo > div:nth-child(3) > div > div.fold_floor > div > div:nth-child(1)")
                    open_hours = open_hours_tag.text.strip() if open_hours_tag else "운영 시간 정보 없음"

                    # 음식점 닫는 시간 추출 
                    close_hours_tag = soup.select_one("#mArticle > div.cont_essential > div.details_placeinfo > div:nth-child(3) > div > div.fold_floor > div > div:nth-child(2)")
                    close_hours = close_hours_tag.text.strip() if close_hours_tag else "닫는 시간 정보 없음"

                    # 음식점 휴무일 추출 
                    rest_days_tag = soup.select_one("#mArticle > div.cont_essential > div.details_placeinfo > div:nth-child(3) > div > div.fold_floor > div > div:nth-child(2)")
                    rest_days = rest_days_tag.text.strip() if rest_days_tag else "휴무일 정보 없음"

                    # 음식점 주소 추출
                    address_tag = soup.select_one("span.txt_address")
                    food_address = address_tag.text.strip() if address_tag else "주소 정보 없음"
                    
                    # 음식점 분류 태그 추출
                    category_tag = soup.select_one("span.txt_location")
                    food_category = category_tag.text.strip() if category_tag else "분류 태그 정보 없음"

                    # 음식점 별점 추출
                    review_tag = soup.select_one("#mArticle > div.cont_essential > div:nth-child(1) > div.place_details > div > div.location_evaluation > a:nth-child(3) > span.color_b")
                    review_count = review_tag.text.strip() if review_tag else "별점 정보 없음"
                    
                    # 음식점 태그 정보등 추출
                    reservation_tag = soup.select_one("#mArticle > div.cont_essential > div.details_placeinfo > div:nth-child(6) > div")
                    reservation_info = reservation_tag.text.strip() if reservation_tag else "음식점 태그 정보 없음"

                    # 음식점 예약/배달/포장 정보등 추출
                    delivery_tag = soup.select_one("#mArticle > div.cont_essential > div.details_placeinfo > div:nth-child(7) > div")
                    delivery_info = delivery_tag.text.strip() if delivery_tag else "음식점 예약/배달/포장 정보 없음"
                    
                    # 음식점 시설 정보 추출
                    facility_tag = soup.select_one("#mArticle > div.cont_essential > div.details_placeinfo > div.placeinfo_default.placeinfo_facility > ul")
                    facility_info = facility_tag.text.strip() if facility_tag else "시설 정보 없음"
                
                    # 음식점 가격 추출
                    menu_info_list = []
                    menu_tags = soup.select("#mArticle > div.cont_menu > ul > li > div > em.price_menu")
                    for menu_tag in menu_tags:
                        menu_info = menu_tag.text.strip() if menu_tag else "메뉴 정보 없음"
                        menu_info_list.append(menu_info)
                        
                    # 메뉴 이름 추출
                    menu_name_list = []
                    menu_names = soup.select("#mArticle > div.cont_menu > ul > li > div > span.loss_word")
                    for menu_name in menu_names:
                        menu_name_info = menu_name.text.strip() if menu_name else "메뉴 이름 정보 없음"
                        menu_name_list.append(menu_name_info)
                                
                    # 수집한 정보를 리스트에 추가
                    food_data.append({
                        "음식점명": food_name,
                        "운영시간": open_hours,
                        "휴게시간": close_hours,
                        "휴무일": rest_days,
                        "주소": food_address,
                        "연락처": call_number,
                        "분류": food_category,
                        "별점": review_count,
                        "태그": reservation_info,
                        "예약/배달/포장": delivery_info,
                        "시설": facility_info,
                        "메뉴": {name: price for name, price in zip(menu_name_list, menu_info_list)}  
                    })

                except Exception as e:
                    print(f"음식점 정보를 추출하는 중 오류 발생: {e}")
                    continue

                # 음식점 정보를 수집한 후 목록 페이지로 다시 돌아가기
                driver.back()
                time.sleep(2)

        # 1~5번째 페이지까지는 번호로 페이지 이동
            if i == 1 and i < num_pages:
                # 첫 번째 페이지에서 "장소 더보기" 클릭
                try:
                    more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "info.search.place.more"))
                    )
                    driver.execute_script("arguments[0].click();", more_button) 
                    time.sleep(2)
                except TimeoutException:
                    print("장소 더보기 버튼을 찾을 수 없습니다. 계속 진행합니다.")
                    
            elif i < 5 and i < num_pages:
                try:
                    # 페이지 넘기기 버튼 클릭 
                    next_page_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, f"info.search.page.no{i+1}"))
                    )
                    driver.execute_script("arguments[0].click();", next_page_button)
                    time.sleep(2)  
                except TimeoutException:
                    print(f"{i+1}번째 페이지를 찾을 수 없습니다.")
                    break
                    
            # 5페이지 이후 페이지 이동 코드
            elif i > 5 and i < num_pages and i % 5 != 0 :
                try:
                    t = (i+1)%5
                    if t == 0:
                        t = 5
                    next_page_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, f"info.search.page.no{t}"))
                    )
                    driver.execute_script("arguments[0].click();", next_page_button)
                    time.sleep(2)  
                except TimeoutException:
                    print(f"{i+1}번째 페이지를 찾을 수 없습니다.")
                    break
                    
            # 5,10,15,20,25,30,35번째 페이지 이후 클릭 버튼 
            elif i % 5 == 0:
                try:
                    # 5번째 페이지 이후 '다음' 버튼 클릭
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "info.search.page.next"))
                    )
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(2)  # 페이지 로딩 대기
                except Exception as e:
                    print("다음 버튼을 찾을 수 없습니다. 더 이상 페이지가 없을 수 있습니다.")
                    break 

        except TimeoutException:
            print(f"{i}번째 페이지를 찾을 수 없습니다.")
        except Exception as e:
            print(f"오류 발생: {e}")
            continue

    # 브라우저 종료
    driver.quit()
    
    return food_data


# 함수 호출 예시
food_list = SajongSi_food('세종시 나성동 음식점', 35)

# 최종적으로 수집된 데이터를 CSV 파일로 저장
df = pd.DataFrame(food_list)
df.to_csv('C:\\data\\음식점정보_나성동.csv', index=False, encoding='utf-8-sig')  # CSV 파일로 저장
print(f"C:\\data\\음식점정보_나성동.csv 파일이 저장되었습니다.")

# 결과 출력
for food in food_list:
    print("=" * 50)
    print(f"음식점이름: {food['음식점명']}")
    print(f"주소: {food['주소']}")
    print(f"연락처: {food['연락처']}")
    print("=" * 50)
    print("[음식점 운영시간]" )
    print(f">>> {food['운영시간']}")
    print(f">>> {food['휴무일']}")
    print(f">>> {food['연락처']}")
    print("=" * 50)
    print(f"분류: {food['분류']}")
    print(f"별점: {food['별점']}")
    print(f"태그: {food['태그']}")
    print(f"예약/배달/포장: {food['예약/배달/포장']}")
    print(f"시설: {food['시설']}")
    print("=" * 50)

    # 이름과 가격을 함께 출력
    print("[메뉴와 가격 정보]")
    for name, price in food['메뉴'].items():  
        print(f"메뉴: {name}\n {price}")
        print("-" * 30)
    print("=" * 50)
