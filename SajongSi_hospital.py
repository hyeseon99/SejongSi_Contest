from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import urllib.parse
import time
import pandas as pd

def SajongSi_hospital(keyword, num_pages):
    
    # 크롬 드라이버 위치 설정 및 옵션 지정
    chrome_options = Options()
    service = Service("C:\\data\\chromedriver-win32\\chromedriver-win32\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 검색 키워드 입력
    text1 = urllib.parse.quote(keyword)

    # 최종 병원 정보를 담을 리스트
    hospital_data = []  
    
    # 카카오맵 검색 URL
    url = f"https://map.kakao.com/?q={text1}"
   
    # 크롬으로 해당 URL 접속
    driver.get(url)
    time.sleep(2)

    # 첫 번째 페이지에서 "장소 더보기" 클릭
    try:
        more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "info.search.place.more"))
        )
        driver.execute_script("arguments[0].click();", more_button) 
        time.sleep(2)
    except TimeoutException:
        print("장소 더보기 버튼을 찾을 수 없습니다. 계속 진행합니다.")
    
    # 페이지 넘기기
    for i in range(1, num_pages + 1):
        try:
            # HTML 파싱 및 병원 정보 추출
            soup = BeautifulSoup(driver.page_source, "html.parser")
            list_url = [a_tag.get("href") for a_tag in soup.select("a.moreview")]

            for hospital_url in list_url:
                # 병원 상세 페이지로 이동
                driver.get(hospital_url)
                time.sleep(2)

                # 병원 정보 수집
                soup = BeautifulSoup(driver.page_source, "html.parser")
                try:
                    # 병원 이름 추출
                    name_tag = soup.select_one('div.inner_place > h2.tit_location')
                    hospital_name = name_tag.text.strip() if name_tag else "이름 없음"

                    # 병원 연락처 추출 
                    call_number_tag = soup.select_one("#mArticle > div.cont_essential > div.details_placeinfo > div.placeinfo_default.placeinfo_contact > div > div > span")
                    call_number = call_number_tag.text.strip() if call_number_tag else "병원 연락처 정보 없음"

                    # 병원 운영 시간 추출 
                    open_hours_tag = soup.select_one("#mArticle > div.cont_essential > div.details_placeinfo > div:nth-child(3) > div > div.fold_floor > div > div:nth-child(1)")
                    open_hours = open_hours_tag.text.strip() if open_hours_tag else "운영 시간 정보 없음"

                    # 병원 닫는 시간 추출 
                    close_hours_tag = soup.select_one("#mArticle > div.cont_essential > div.details_placeinfo > div:nth-child(3) > div > div.fold_floor > div > div:nth-child(2)")
                    close_hours = close_hours_tag.text.strip() if close_hours_tag else "닫는 시간 정보 없음"

                    # 병원 휴무일 추출 
                    rest_days_tag = soup.select_one("#mArticle > div.cont_essential > div.details_placeinfo > div:nth-child(3) > div > div.fold_floor > div > div:nth-child(2)")
                    rest_days = rest_days_tag.text.strip() if rest_days_tag else "휴무일 정보 없음"

                    # 병원 주소 추출
                    address_tag = soup.select_one("span.txt_address")
                    hospital_address = address_tag.text.strip() if address_tag else "주소 정보 없음"

                    # 수집한 정보를 리스트에 추가
                    hospital_data.append({
                        "병원명": hospital_name,
                        "운영시간": open_hours,
                        "휴게시간": close_hours,
                        "공휴일시간": rest_days,
                        "주소": hospital_address,
                        "연락처": call_number
                    })

                except Exception as e:
                    print(f"병원 정보를 추출하는 중 오류 발생: {e}")
                    continue

                # 병원 정보를 수집한 후 목록 페이지로 다시 돌아가기
                driver.back()
                time.sleep(2)

            # 1~5번째 페이지까지는 번호로 페이지 이동
            if i < 5 and i < num_pages:
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
                    
                    #  5페이지 이후 페이지 이동 코드
            elif i > 5 and i < num_pages and i % 5 != 0:
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
    
    return hospital_data


# 함수 호출 예시
hospital_list = SajongSi_hospital('세종시병원', 36)

# 최종적으로 수집된 병원 데이터를 CSV 파일로 저장
df = pd.DataFrame(hospital_list)
df.to_csv('C:\\sejong\\hospital_list.csv', index=False, encoding='utf-8-sig')# CSV 파일로 저장
print(f"C:\\sejong\\hospital_list.csv 파일이 저장되었습니다.")

# 결과 출력
for hospital in hospital_list:
    print("=" * 50)
    print(f"병원이름: {hospital['병원명']}")
    print(f"주소: {hospital['주소']}")
    print(f"연락처: {hospital['연락처']}")
    print("=" * 50)
    print("[병원 운영시간]" )
    print(f">>> {hospital['운영시간']}")
    print(f">>> {hospital['공휴일시간']}")
    print("=" * 50)
