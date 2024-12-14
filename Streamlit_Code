import streamlit as st
import time
import pandas as pd
from PIL import Image
from streamlit_option_menu import option_menu
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
import requests
from streamlit_chat import message
import urllib3
import json
import base64
import re
 
# 페이지 레이아웃 설정
st.set_page_config(layout="wide")

# 전역 폰트 적용
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Song+Myung:wght@400&display=swap');

    body, h1, h2, h3, p, div, span, li, a {
        font-family: 'MaruBuri', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)
    
# 사이드바 메뉴 및 폼 생성
with st.sidebar:
    st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; align-items: center; margin-right: 50px; margin-left: 50px;">
                    <img src="data:image/png;base64,{base64.b64encode(open("C:/images/logo.png", 'rb').read()).decode()}" style="width: 325px;">
                </div>
            """, unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid rgba(0, 0, 0, 0.1);'>", unsafe_allow_html=True)
    
    # 메뉴 선택 후 배경 색상 결정
    selected = option_menu(
        None,  # 타이틀 없이
        ["음식점", "병원 챗봇"],  # 메뉴 항목
        icons=["house", "robot"],  # 아이콘 설정
        menu_icon="cast",  # 상단 메인 메뉴 아이콘
        default_index=0,  # 기본 선택
        orientation="vertical",  # 수직 메뉴
        styles={
            "container": {
                "padding": "5px",  # 전체 padding
                "background-color": "#E8E8E8",  # 기본 배경 색상
                "border-radius": "10px",  # 모서리를 부드럽게
                "box-shadow": "0px 4px 12px rgba(0, 0, 0, 0.1)"  # 그림자 효과 추가
            },
            "icon": {
                "color": "#282828",  # 아이콘 색상
                "font-size": "22px",  # 아이콘 크기 조정
            },
            "nav-link": {
                "font-size": "18px",  # 메뉴 텍스트 크기
                "color": "#000000",  # 기본 텍스트 색상
                "text-align": "left",
                "margin": "5px 0",  # 메뉴 항목 간 간격
                "padding": "5px",  # 메뉴 항목 padding
                "--hover-color": "#f0f0f0",  # 마우스 오버 시 배경 색상
                "border-radius": "10px",  # 메뉴 항목 모서리 둥글게
            },
            "nav-link-selected": {
                "background-color": "#FF5A5A",  # 선택된 메뉴 배경색
                "color": "#FFFFFF",  # 선택된 메뉴 텍스트 색상
                "border-radius": "10px",  # 선택된 메뉴 모서리 둥글게
                "box-shadow": "0px 2px 10px rgba(0, 0, 0, 0.2)",  # 선택된 메뉴 그림자
            },
        }
    )


# 선택된 메뉴에 따라 화면 구성 변경
if selected == "음식점":
    # 위도경도로 거리 구하기
    def haversine(lat1, lon1, row):
        lat2 = row['위도']
        lon2 = row['경도']
        
        # 지구 반지름 (킬로미터 단위)
        R = 6371.0
        
        # 위도와 경도를 라디안으로 변환
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        # 위도와 경도 차이 계산
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine 공식 적용
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        # 거리 계산
        distance = R * c
        return distance

    # 동적 가중치 설정 함수 (점심과 저녁 시간에 따라)
    def dynamic_weight_adjustment(current_time):
        # 점심 시간: 11:00 ~ 14:00, 저녁 시간: 18:00 ~ 21:00
        lunch_start, lunch_end = "11:00", "14:00"
        dinner_start, dinner_end = "18:00", "21:00"
        
        if lunch_start <= current_time <= lunch_end:
            # 점심 시간: 거리 가중치가 더 높음
            return {'rating': 0.4, 'distance': 0.6}
        elif dinner_start <= current_time <= dinner_end:
            # 저녁 시간: 별점 가중치가 더 높음
            return {'rating': 0.4, 'distance': 0.6}
        else:
            # 기타 시간대: 기본 가중치
            return {'rating': 0.5, 'distance': 0.5}

    # 자정을 넘기는 시간을 처리하는 함수
    def is_open(open_time, close_time, check_time):
        if close_time < open_time:
            return check_time >= open_time or check_time < close_time
        return open_time <= check_time < close_time
        
    # 시간 문자열을 datetime 객체로 변환하는 함수 (휴게시간 포함)
    def time_in_range1(start_time_m, end_time_m, start_time_r, end_time_r, check_time):
        start_time_m = datetime.strptime(start_time_m, '%H:%M')
        end_time_m = datetime.strptime(end_time_m, '%H:%M')
        start_time_r = datetime.strptime(start_time_r, '%H:%M')
        end_time_r = datetime.strptime(end_time_r, '%H:%M')
        check_time = datetime.strptime(check_time, '%H:%M')

        if start_time_m == end_time_m:
            return True

        if is_open(start_time_m, end_time_m, check_time):
            if start_time_r <= check_time <= end_time_r:
                return False
            return True
        return False

    # 휴게 시간 없이 자정을 넘기는 시간 처리
    def time_in_range2(start_time_m, end_time_m, check_time):
        start_time_m = datetime.strptime(start_time_m, '%H:%M')
        end_time_m = datetime.strptime(end_time_m, '%H:%M')
        check_time = datetime.strptime(check_time, '%H:%M')

        if start_time_m == end_time_m:
            return True

        return is_open(start_time_m, end_time_m, check_time)


    # 특정 음식점의 시간 확인
    def check_availability(row, day, check_time):
        start_time_m = f'{day}요일 영업 시작시간'
        end_time_m = f'{day}요일 영업 종료시간'
        start_time_r = f'{day}요일 휴게 시작시간'
        end_time_r = f'{day}요일 휴게 종료시간'

        if row[start_time_m] != '정보 없음' and row[end_time_m] != '정보 없음' and row[start_time_r] != '정보 없음' and row[end_time_r] != '정보 없음':
            return time_in_range1(row[start_time_m], row[end_time_m], row[start_time_r], row[end_time_r], check_time)
        elif row[start_time_m] != '정보 없음' and row[end_time_m] != '정보 없음':
            return time_in_range2(row[start_time_m], row[end_time_m], check_time)
        else:
            return False

    # 순위에 따른 가중치 계산 함수 (연령대 또는 성별에 대한 가중치 적용)
    def rank_weight(row, group, column_name):
        if group:
            # '최종분류'를 슬래시(/)로 구분하여 각 항목을 개별적으로 확인
            categories = row['최종분류'].split('/')
            matching_ranks = []
            
            for category in categories:
                if category in age_rankings_df[group].values:
                    rank = list(age_rankings_df[group]).index(category) + 1  # 순위는 0부터 시작하므로 +1
                    matching_ranks.append(1 / (rank+1))  # 순위가 높을수록 가중치가 높음
            
            # 해당 그룹에서 가장 높은 가중치 (즉, 가장 작은 순위) 선택
            if matching_ranks:
                return max(matching_ranks)
        
        return 0  # 해당 항목이 없거나 그룹이 선택되지 않은 경우 가중치 0

    # 선택 음식 필터링 (슬래시로 구분된 항목 중 하나라도 음식 리스트와 일치하면 포함)
    def filter_food_by_category(df, food_list):
        return df[df['최종분류'].apply(lambda x: any(food in x.split('/') for food in food_list))]

    # 최종 점수 계산 함수에 연령대와 성별 가중치 반영
    def check_time_in_range(df, day, check_time, lat, lon, star, food_list, age_group=None, gender=None):
        # 가중치 설정 (점심, 저녁 시간에 따른 거리와 별점 가중치)
        weights = dynamic_weight_adjustment(check_time)
        
        # 영업 여부 및 거리 계산
        df[f'{day}요일 {check_time} 운영 여부'] = df.apply(lambda row: check_availability(row, day, check_time), axis=1)
        df['거리(km)'] = df.apply(lambda row: haversine(lat, lon, row), axis=1)
        
        # 별점과 거리 가중치 적용한 최종 점수 계산
        df['rating_weighted'] = df['별점'] * weights['rating']
        df['distance_weighted'] = (1 / (df['거리(km)'] + 1)) * weights['distance']  # 거리가 가까울수록 점수 높게
        
        # 연령대별 순위 가중치 적용 (연령대가 있을 경우에만)
        df['rank_weight_age'] = df.apply(lambda row: rank_weight(row, age_group, '연령대'), axis=1)
        
        # 성별 순위 가중치 적용 (성별이 있을 경우에만)
        df['rank_weight_gender'] = df.apply(lambda row: rank_weight(row, gender, '성별'), axis=1)
        
        # 최종 점수 계산 (별점, 거리, 연령대 및 성별 선호 순위 가중치 포함)
        df['final_score'] = df['rating_weighted'] + df['distance_weighted'] + df['rank_weight_age'] + df['rank_weight_gender']

        # 최소 별점으로 필터링
        df = df.loc[df.별점 >= star]

        # 선택 음식 필터링 (슬래시로 구분된 항목 중 하나라도 음식 리스트와 일치하면 포함)
        df = filter_food_by_category(df, food_list)
        
        # 최종 점수에 따라 음식점 정렬
        result_df = df[df[f'{day}요일 {check_time} 운영 여부'] == True].sort_values(by='final_score', ascending=False)
        
        return result_df

    def get_lat_lng(address):
        api_key = 'AIzaSyA5mAdbPEjXRhfOA7_wfF8l8fB9PHI7NT0'  # Google API 키를 여기에 입력
        base_url = 'https://maps.googleapis.com/maps/api/geocode/json'

        params = {
            'address': address,
            'key': api_key
        }

        # Google Geocoding API 요청
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            if len(data['results']) > 0:
                location = data['results'][0]['geometry']['location']
                return location['lat'], location['lng']
            else:
                return None, None
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None, None

    # 데이터 불러오기 cp949
    df = pd.read_csv("C:\\images\\음식점정보홈페이지활용_메뉴최종.csv", encoding='utf-8')
    age_rankings_df = pd.read_csv("C:\\images\\나이대성별선호음식순위.csv",encoding='utf-8')


    # 현재 날짜와 시간 가져오기
    now = datetime.now()

    # 요일 영어로 매핑
    weekday_map = {
        'Monday': '월',
        'Tuesday': '화',
        'Wednesday': '수',
        'Thursday': '목',
        'Friday': '금',
        'Saturday': '토',
        'Sunday': '일'
    }

    # 영어 요일 가져오기
    english_weekday = now.strftime('%A')

    # 한글 요일로 변환
    korean_weekday = weekday_map[english_weekday]

    minute = now.strftime('%H:%M')   # 현재 시간 (예: 05:30)

    # 배너 생성 함수
    def create_banner():
        left_col, right_col = st.columns([1, 2])  # 왼쪽에 이미지, 오른쪽에 텍스트 배치

        with left_col:
            st.image("C:/images/2food.png", width=600)  # 원하는 이미지로 변경

        with right_col:
            st.markdown("""
            <div style="text-align: left;">
                <h1 style="font-size: 60px; font-weight: bold; margin-bottom: 15px;">세, 먹자 세종시</h1>
                <p style="font-size: 20px; color: #555555; margin-top: 10px;">
                    나이, 취향, 별점, 카테고리를 선택하시면 음식 고민 없이 빠르게 맞춤형 추천 메뉴를 제공받을 수 있는 시스템입니다.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # 배너 표시
    create_banner()

    # 구분선 추가
    st.markdown("<hr style='border:2px solid black;'>", unsafe_allow_html=True)

    # 페이지와 사이드바 스타일링
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #E8E8E8;
        }
        [data-testid="stSidebar"] {
            background-color: #E8E8E8;
        }
        [data-testid="stSidebar"] .css-1d391kg {
            color: #000000;
        }
        [role="slider"] {
            background-color: #FFA07A;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    # 기본값 설정 함수
    def set_default():
        st.session_state['gender'] = None
        st.session_state['age_group'] = '20대'
        st.session_state['address'] = ''
        st.session_state['rating'] = 0.0
        st.session_state['food_categories'] = ['한식', '중식', '일식', '양식', '아시안(기타 외국식)', '분식', '주점업', '패스트푸드', '치킨전문점']
        st.session_state['cafe_dessert'] = ['카페', '간식', '제과점']

    # 초기화 함수
    def reset_form():
        st.session_state['gender'] = None
        st.session_state['age_group'] = '20대'
        st.session_state['address'] = ''
        st.session_state['rating'] = 0.0
        st.session_state['food_categories'] = ['한식', '중식', '일식', '양식', '아시안(기타 외국식)', '분식', '주점업', '패스트푸드', '치킨전문점']
        st.session_state['cafe_dessert'] = ['카페', '간식', '제과점']

    # 페이지 기본값 설정
    if 'gender' not in st.session_state:
        set_default()

    # 사이드바 메뉴 및 폼 생성
    with st.sidebar:
        # 폼 시작
        st.markdown('<p style="font-size:22px; font-weight:bold;">👨🏻‍💼👩🏻‍💼 성별을 선택해 주세요:</p>', unsafe_allow_html=True)

        # 성별 선택을 체크박스로 구현
        col1, col2 = st.columns(2)
        with col1:
            female = st.checkbox('여성', value=(st.session_state['gender'] == '여성'), key="female_checkbox")
        with col2:
            male = st.checkbox('남성', value=(st.session_state['gender'] == '남성'), key="male_checkbox")

        # 성별 선택 처리
        gender = None
        if female and not male:
            gender = "여성"
        elif male and not female:
            gender = "남성"
        st.session_state['gender'] = gender

        st.markdown(f"<p style='font-size:20px; font-weight:bold;'>선택한 성별: {st.session_state['gender']}</p>", unsafe_allow_html=True)

        st.write("")

        # 연령대 선택
        st.markdown('<p style="font-size:22px; font-weight:bold;">✔️ 연령대를 선택해 주세요:</p>', unsafe_allow_html=True)
        age_group = st.selectbox("", [None,'20대 미만', '20대', '30대', '40대', '50대', '60대', '70대 이상'], 
                                index=[None,'20대 미만', '20대', '30대', '40대', '50대', '60대', '70대 이상'].index(st.session_state['age_group']), 
                                key="age_group_selectbox")
        st.session_state['age_group'] = age_group
        st.write("")

        # 주소 입력하는 칸
        st.markdown('<p style="font-size:20px; font-weight:bold;">🏡 주소를 입력해 주세요:</p>', unsafe_allow_html=True)
        address = st.text_input("", value=st.session_state['address'], key="address_input")
        st.session_state['address'] = address
        st.markdown(f"<p style='font-size:20px; font-weight:bold;'>입력된 주소: {st.session_state['address']} </p>", unsafe_allow_html=True)
        st.write("")

        # 음식점 평점 선택
        st.markdown('<p style="font-size:22px; font-weight:bold;">⭐ 음식점 평점을 선택해주세요:</p>', unsafe_allow_html=True)
        rating = st.slider("", min_value=0.0, max_value=5.0, value=st.session_state['rating'], step=0.1, key="rating_slider")
        st.session_state['rating'] = rating
        st.markdown(f"<p style='font-size:20px; font-weight:bold;'>선택한 별점: {st.session_state['rating']} </p>", unsafe_allow_html=True)
        st.write("")

        # 음식 카테고리 선택
        st.markdown('<p style="font-size:22px; font-weight:bold;">🍲 음식 카테고리를 선택해주세요:</p>', unsafe_allow_html=True)
        food_categories = st.multiselect(
            "", ['한식', '중식', '일식', '양식', '아시안(기타 외국식)', '분식', '주점업', '패스트푸드', '치킨전문점'],
            default=st.session_state['food_categories'], key="food_category_multiselect"
        )
        st.session_state['food_categories'] = food_categories
        st.write("")

        # 카페 및 디저트 선택
        st.markdown('<p style="font-size:22px; font-weight:bold;">🍰 카페 및 디저트를 선택해주세요:</p>', unsafe_allow_html=True)
        cafe_dessert = st.multiselect(
            "", ['카페', '간식', '제과점'],
            default=st.session_state['cafe_dessert'], key="cafe_dessert_multiselect"
        )
        st.session_state['cafe_dessert'] = cafe_dessert
        st.write("")

        # 확인 버튼과 초기화 버튼을 나란히 배치
        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.button("확인")
        with col2:
            reset_button = st.button("초기화", on_click=reset_form)

    # 로딩 애니메이션 및 필터링
    combined_categories = st.session_state['cafe_dessert'] + st.session_state['food_categories']

    #제출 버튼이 눌렸을 때 처리
    combined_categories = cafe_dessert + food_categories  

    filtered_df = pd.DataFrame()

    if submit_button:
        # 성별 선택 처리
        if female and male:
            st.error("성별을 하나만 선택해 주세요")
        elif female and not male:
            st.session_state['gender'] = "여자"
        elif male and not female:
            st.session_state['gender'] = "남자"
        else:
            st.session_state['gender'] = None
            
        lat,lon = get_lat_lng(address)

        if lat == None or lon == None:
            st.error("유효한 주소를 입력해주세요.")
        else:
            with st.spinner('로딩 중입니다...'):
                time.sleep(3)  # 실제 작업 대신 로딩 시간 시뮬레이션
                filtered_df = check_time_in_range(df,korean_weekday,minute,lat,lon,rating,combined_categories,age_group,gender)

    else:
        filtered_df = df
        filtered_df['거리(km)'] = 0

    # 카드 생성 함수 정의
    def create_card(image_path, store_name, a, b, menu, hours, rating, reviews, address,distance):
        try:
            image = Image.open(image_path)
            resized_image = image.resize((600, 300))
            st.image(resized_image)

            # 메뉴를 문자열로 변환하고 줄바꿈 처리를 적용
            menu_html = ""  # 기본 값을 빈 문자열로 설정

            if isinstance(menu, str):
                if menu != '없음':
                    menu_html = menu.replace('\n', '<br>')  # 메뉴 줄바꿈 처리
                else:
                    menu_html = '메뉴 없음'  # 메뉴가 '없음'일 때 메시지
            else:
                menu_html = '메뉴 없음'  # 메뉴가 문자열이 아닐 경우 메시지

            st.markdown(f"""
            <div style="background-color: #f9f9f9; padding: 20px; 
                        border-radius: 10px; box-shadow: 2px 2px 12px rgba(0, 0, 0, 5.1); 
                        margin-bottom: 10px; max-width: 600px;">
                <div>
                    <h3 style="margin-top: 10px; font-weight: bold;">{store_name} <b style="font-size: 0.7em;">{a} ({b})</b></h3>
                    <p>평점: ⭐{rating} 리뷰수: {reviews} 거리: {round(distance,3)}km</p>
                    <p>메뉴 <br>{menu_html}</p> 
                    <p>{hours}</p>
                    <p>주소: {address}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"이미지 로딩 중 오류가 발생했습니다: {e}")
            
    # # 음식점 추천이 잘 돌아가는지 확인 하는 함수
    #st.write(filtered_df)

    # 그리드 형태로 이미지 및 정보 출력
    for i in range(0, len(filtered_df), 3):
        cols = st.columns(3)
        
        with cols[0]:
            if i < len(filtered_df):
                image_file = f"C:/images/{filtered_df.iloc[i]['이미지파일명']}"
                st.write("")
                st.write("")
                create_card(image_file, filtered_df.iloc[i]['음식점명'], filtered_df.iloc[i]['분류'], filtered_df.iloc[i]['최종분류'], filtered_df.iloc[i]['메뉴'], filtered_df.iloc[i]['운영시간'], filtered_df.iloc[i]['별점'], filtered_df.iloc[i]['리뷰수'], filtered_df.iloc[i]['주소'],filtered_df.iloc[i]['거리(km)'])
                
                
        if i + 1 < len(filtered_df):
            with cols[1]:
                image_file = f"C:/images/{filtered_df.iloc[i+1]['이미지파일명']}"
                st.write("")
                st.write("")
                create_card(image_file, filtered_df.iloc[i+1]['음식점명'], filtered_df.iloc[i+1]['분류'], filtered_df.iloc[i+1]['최종분류'], filtered_df.iloc[i+1]['메뉴'], filtered_df.iloc[i+1]['운영시간'], filtered_df.iloc[i+1]['별점'], filtered_df.iloc[i+1]['리뷰수'], filtered_df.iloc[i+1]['주소'],filtered_df.iloc[i+1]['거리(km)'])
                
                
        if i + 2 < len(filtered_df):
            with cols[2]:
                image_file = f"C:/images/{filtered_df.iloc[i+2]['이미지파일명']}"
                st.write("")
                st.write("")
                create_card(image_file, filtered_df.iloc[i+2]['음식점명'], filtered_df.iloc[i+2]['분류'], filtered_df.iloc[i+2]['최종분류'], filtered_df.iloc[i+2]['메뉴'], filtered_df.iloc[i+2]['운영시간'], filtered_df.iloc[i+2]['별점'], filtered_df.iloc[i+2]['리뷰수'], filtered_df.iloc[i+2]['주소'],filtered_df.iloc[i+2]['거리(km)'])
    
elif selected == "병원 챗봇":
    # ETRI API 설정
    openApiURL = "http://aiopen.etri.re.kr:8000/WiseQAnal"
    accessKey = "074c136c-f5d7-4063-811b-9cf8b8060803"  # 본인의 API 키로 변경하세요.

    # ETRI API 응답 함수
    def get_response(question):
        requestJson = {
            "access_key": accessKey,
            "argument": {
                "text": question,
                "analysis_code": "QA"
            }
        }
        http = urllib3.PoolManager()
        response = http.request(
            "POST",
            openApiURL,
            headers={"Content-Type": "application/json; charset=UTF-8"},
            body=json.dumps(requestJson)
        )
        return json.loads(response.data.decode('utf-8'))

    # 위도경도로 거리 구하기
    def haversine(lat1,lon1,row):
        lat2 = row['위도']
        lon2 = row['경도']
        
        # 지구 반지름 (킬로미터 단위)
        R = 6371.0
        
        # 위도와 경도를 라디안으로 변환
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        # 위도와 경도 차이 계산
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine 공식 적용
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        # 거리 계산
        distance = R * c
        
        return distance
        
    # 시간 문자열을 datetime 객체로 변환하는 함수
    def time_in_range1(start_time_m,end_time_m,start_time_r,end_time_r,check_time):
        start_time_m = datetime.strptime(start_time_m,'%H:%M')
        end_time_m = datetime.strptime(end_time_m,'%H:%M')
        start_time_r = datetime.strptime(start_time_r,'%H:%M')
        end_time_r = datetime.strptime(end_time_r,'%H:%M')
        check_time = datetime.strptime(check_time,'%H:%M')
        
        # 휴게 시간일 경우 False 반환
        if start_time_r <= check_time <= end_time_r:
            return False
        elif start_time_m <= check_time <= end_time_m:
            return True
        else:
            return False

    def time_in_range2(start_time_m,end_time_m,check_time):
        start_time_m = datetime.strptime(start_time_m,'%H:%M')
        end_time_m = datetime.strptime(end_time_m,'%H:%M')
        check_time = datetime.strptime(check_time,'%H:%M')
        
        # 종료 시간이 자정을 넘길 경우를 처리
        if start_time_m <= check_time <= end_time_m:
            return True
        else:
            return False
        
    def check_availability(row,day,check_time):
        start_time_m = f'{day}요일진료시작시간'
        end_time_m = f'{day}요일진료종료시간'
        start_time_r = f'{day}요일휴게시작시간'
        end_time_r = f'{day}요일휴게종료시간'
        
        if row[start_time_m] != '정보 없음' and row[end_time_m] != '정보 없음' and row[start_time_r] != '정보 없음' and row[end_time_r] != '정보 없음':
            return time_in_range1(row[start_time_m], row[end_time_m], row[start_time_r], row[end_time_r], check_time)
        elif row[start_time_m] != '정보 없음' and row[end_time_m] != '정보 없음':
            return time_in_range2(row[start_time_m], row[end_time_m],check_time)
        else:
            return False

    def hospital_filter(df, category):
        if category == '종합병원':
            data = df.loc[df.세부진단 == '종합병원']
        else:
            # category가 리스트일 경우, 리스트 내의 값 중 하나라도 세부진단에 일치하는 경우 필터링
            data = df.loc[df.세부진단.isin(category)]
            # 세부진단에서 필터링된 데이터가 없을 경우, 종합병원 데이터로 대체
            if len(data) == 0:
                data = df.loc[df.세부진단 == '종합병원']
                # 여전히 데이터가 없을 경우, 진료과목내용명을 기준으로 필터링
                if len(data) == 0:
                    # category가 리스트이므로, 각 리스트의 요소가 진료과목내용명에 있는지 확인
                    pattern = '|'.join(category)  # 리스트의 값을 '|'로 연결하여 정규식 패턴으로 변환
                    data = df[df.진료과목내용명.str.contains(pattern, na=False)]
        
        return data

        
    # 특정 병원의 시간 확인 (예시로 월요일 진료시간)
    def check_time_in_range(df,day,check_time,lat,lon,category=None):

        # 각 병원에 대해 입력한 시간이 진료시간 내에 있는지 확인
        df[f'{day}요일 {check_time} 내 진료 여부'] = df.apply(lambda row: check_availability(row, day, check_time), axis=1)
        df['거리(km)'] = df.apply(lambda row: haversine(lat, lon,row), axis=1)
        result = df[df[f'{day}요일 {check_time} 내 진료 여부'] == True].sort_values(by = '거리(km)',ascending = True)
        result = hospital_filter(result,category)

        return result

    def get_lat_lng(address):
        api_key = 'AIzaSyA5mAdbPEjXRhfOA7_wfF8l8fB9PHI7NT0'  # Google API 키를 여기에 입력
        base_url = 'https://maps.googleapis.com/maps/api/geocode/json'

        params = {
            'address': address,
            'key': api_key
        }

        # Google Geocoding API 요청
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            if len(data['results']) > 0:
                location = data['results'][0]['geometry']['location']
                return location['lat'], location['lng']
            else:
                return None, None
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None, None

    # 요일 영어로 매핑
    weekday_map = {
        'Monday': '월',
        'Tuesday': '화',
        'Wednesday': '수',
        'Thursday': '목',
        'Friday': '금',
        'Saturday': '토',
        'Sunday': '일'
    }

    # 특정 키워드에 따른 병원 정보 필터링 함수
    def filter_hospital_by_department(department,lat, lon):
        # 병원 정보 데이터 불러오기
        df = pd.read_csv('c:\\images\\병원정보홈페이지활용수정.csv', encoding='cp949')

        # 현재 날짜와 시간 가져오기
        now = datetime.now()

        # 영어 요일 가져오기
        english_weekday = now.strftime('%A')

        # 한글 요일로 변환
        korean_weekday = weekday_map[english_weekday]
        minute = now.strftime('%H:%M') 

        filtered_df = check_time_in_range(df,korean_weekday,'15:00',lat,lon,department)
        
        if len(filtered_df) != 0:
            first_hospital = filtered_df.iloc[0]  # 첫 번째 병원 정보 가져오기
            # 병원 정보에 줄바꿈과 필요한 정보만 남기기
            hospital_info = (
                f"병원명: {first_hospital['의료기관명']}<br>"
                f"주소: {first_hospital['의료기관주소']}<br>"
                f"운영시간: {first_hospital['운영시간']}<br>"
                f"전화번호: {first_hospital['의료기관전화번호']}<br>"
                f"거리: {round(first_hospital['거리(km)'],3)}km"
            )
        else:
            hospital_info = 0
            
        return hospital_info

    # 메인 페이지 설정
    st.markdown("""
        <style>
        .chat-bot-title {  
            font-size: 36px;
            color: #FFFFFF; /* 병원 느낌의 진한 파란색 */
            font-weight: bold;
            text-align: center;
        }
        .message-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
        }
        .user-emoji {
            font-size: 60px;
            margin-left: 20px;
        }
        .bot-emoji {
            font-size: 60px;
            margin-right: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        .center {
            display: block;
            margin-left: 100px; /* 왼쪽 간격을 50px로 설정 */
            margin-right: auto;
        } 
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        /* 입력창과 버튼의 레이아웃 조정 */
        .stButton {
            display: block !important;  /* 버튼을 블록 요소로 변경 */
            margin: 20px 0px 0px 30px !important;  /* 버튼 위쪽 여백 추가 */
            width: 150px !important;  /* 버튼 너비를 입력창과 동일하게 설정 */
            font-size: 30px !important;
        }
        .stButton > button {
            background-color: #c5dcf1 !important;  /* 기본 버튼 배경색 */
            color: black !important;  /* 기본 버튼 텍스트 색상 */
            border-radius: 10px !important;
            padding: 15px !important;
            border: none !important;
            font-size: 50px !important;
            transition: background-color 0.3s ease !important;  /* 배경색 전환 애니메이션 */
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);  /* 약간의 그림자 추가 */
        }
        .stButton > button:hover {
            background-color: #98c1ea !important;  /* 마우스를 올렸을 때의 배경색 */
            color: white !important;
            box-shadow: 0px 6px 8px rgba(0, 0, 0, 0.3);  /* 그림자 확대 */
        }
        .stButton > button:active {
            background-color: #98c1ea !important;  /* 클릭한 상태일 때 배경색 */
            color: white !important;  /* 클릭한 상태일 때 텍스트 색상 */
        }
        .stButton > button:focus:not(:hover) {
            background-color: #c5dcf1 !important;  /* 포커스 상태일 때 배경색 */
            color: black !important;  /* 포커스 상태일 때 텍스트 색상 */
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        /* 챗봇 응답 메시지 */
        .bot-message {
            background-color: #c5dcf1 !important;  /* 눈에 잘 띄는 밝은 파란색 */
            color: black !important;  /* 흰색 텍스트 */
            border-radius: 20px !important;
            padding: 20px !important;
            font-size: 20px !important;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);  /* 그림자 효과 */
            max-width: 70%;
            margin-right: auto;
            margin-bottom: 10px;
        }

        /* 사용자 메시지 */
        .user-message {
            background-color: #ecf2f8 !important;  /* 밝은 초록색 */
            color: black !important;  /* 흰색 텍스트 */
            border-radius: 20px !important;
            padding: 20px !important;
            font-size: 20px !important;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);  /* 그림자 효과 */
            max-width: 70%;
            margin-left: auto;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        .stApp {
            background-color: #F6F6F6;
        }
        [data-testid="stSidebar"] {
            background-color: #E8E8E8;
        }
        [data-testid="stSidebar"] .css-1d391kg {
            color: #000000;
        }
        [role="slider"] {
            background-color: #FFA07A;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    image_path = 'c:\\images\\hospital_logo.png'
    
    # 배너 생성 함수
    def create_banner():
        left_col, right_col = st.columns([1, 2])  # 왼쪽에 이미지, 오른쪽에 텍스트 배치

        with left_col:
            st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; align-items: center; margin-right: 100px;">
                    <img src="data:image/png;base64,{base64.b64encode(open(image_path, 'rb').read()).decode()}" style="width: 400px;">
                </div>
            """, unsafe_allow_html=True)

        with right_col:
            st.markdown("""
            <div style="text-align: left;">
                <h1 style="font-size: 60px; font-weight: bold; margin-bottom: 15px;">병원 추천 챗봇</h1>
                <p style="font-size: 20px; color: #555555; margin-top: 10px;">
                    아프신 부위에 맞는 병원을 신속하게 찾아드리는 시스템입니다.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # 배너 표시
    create_banner()

    # 사이드바 메뉴 및 이미지 추가
    with st.sidebar:
        st.markdown("""
            <h3 style='font-size: 30px; font-weight: bold; margin-bottom: 15px; color: #333333;'>🤖 챗봇 소개</h3>
            <p style='font-size: 25px; line-height: 1.6; color: #555555;'>
            저희 챗봇은 여러분의 건강을 위해, 현재 아프신 부위에 맞는 과가 있는 가장 가까운 병원을 신속히 찾아드립니다. 필요한 정보를 언제든지 질문해 주세요!
            </p>
        """, unsafe_allow_html=True)
    
    # 초기화: 세션 상태 초기화
    if 'past' not in st.session_state:
        st.session_state['past'] = []

    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'address_saved' not in st.session_state:
        st.session_state['address_saved'] = False

    # 질문과 주소를 구분하는 함수
    def extract_address(user_input):
        # 주소 패턴을 정의 (단순 도로명 주소 패턴)
        address_pattern = re.compile(r'\b(세종|서울|부산|대구|인천|광주|대전|울산|경기|강원|충청|전라|경상|제주)[^\d]*(\d+).*\b')
        match = address_pattern.search(user_input)

        if match:
            address = match.group(0)  # 주소 부분
        else:
            address = None

        return address

    # 질문 전송 함수
    def process_input():
        user_input = st.session_state.input_text

        if 'address_saved' not in st.session_state or not st.session_state['address_saved']:
            address = extract_address(user_input)

            if address:
                # 주소로 위도 경도 계산
                lat, lon = get_lat_lng(address)
                if lat is None or lon is None:
                    bot_response = "유효한 주소를 입력해주세요."
                else:
                    st.session_state['address'] = address
                    st.session_state['address_saved'] = True
                    st.session_state['lat'] = lat
                    st.session_state['lon'] = lon
                    bot_response = "주소가 확인되었습니다. 아프신 부위를 입력해주세요."
            else:
                bot_response = "유효한 주소를 입력해주세요."
        else:
            question = user_input
            lat = st.session_state['lat']
            lon = st.session_state['lon']
            # 챗봇 응답 처리 및 병원 필터링
            if any(keyword in user_input for keyword in ['안녕','반가워','누구야','하이']):
                bot_response = "안녕하세요! 병원 추천 챗봇입니다. 아픈 부위를 입력해주시면 가까운 병원을 소개해드릴게요!"
            elif any(keyword in user_input for keyword in ['콧물','발열','기침','복통','변비','구토','내시경','소화','가슴']) or ("컨디션" in user_input and "저하" in user_input) or ("체력" in user_input and "저하" in user_input):
                hos = '내과'
                filtered_hospital_info = filter_hospital_by_department([hos],lat, lon)
                if filtered_hospital_info == 0:
                    bot_response = "죄송합니다. 현재 해당 진료과목의 운영중인 병원을 찾을 수 없습니다."
                else:
                    bot_response = f"해당 부위는 {hos}에 가시면 될 것 같습니다.<br> 현재 운영중인 가장 가까운 {hos} 병원을 알려드리겠습니다."
                    bot_response += "\n\n" + filtered_hospital_info  # 병원 정보 챗봇 응답에 추가
                    
            elif any(keyword in user_input for keyword in ['머리','기절','두통','편두통','유즙','마비','기억력']) or ("뇌" in user_input and "검사" in user_input):
                hos = '신경과'
                filtered_hospital_info = filter_hospital_by_department([hos],lat, lon)
                if filtered_hospital_info == 0:
                    bot_response = "죄송합니다. 현재 해당 진료과목의 운영중인 병원을 찾을 수 없습니다."
                else:
                    bot_response = f"해당 부위는 {hos}에 가시면 될 것 같습니다.<br> 현재 운영중인 가장 가까운 {hos} 병원을 알려드리겠습니다."
                    bot_response += "\n\n" + filtered_hospital_info  # 병원 정보 챗봇 응답에 추가
            
            elif any(keyword in user_input for keyword in ['허리','거북목','디스크']) or ("목" in user_input and "디스크" in user_input) or ("다리" in user_input and "저림" in user_input) or ("다리" in user_input and "쥐" in user_input):
                hos = '신경외과'
                filtered_hospital_info = filter_hospital_by_department([hos],lat, lon)
                if filtered_hospital_info == 0:
                    bot_response = "죄송합니다. 현재 해당 진료과목의 운영중인 병원을 찾을 수 없습니다."
                else:
                    bot_response = f"해당 부위는 {hos}에 가시면 될 것 같습니다.<br> 현재 운영중인 가장 가까운 {hos} 병원을 알려드리겠습니다."
                    bot_response += "\n\n" + filtered_hospital_info  # 병원 정보 챗봇 응답에 추가
                    
            elif any(keyword in user_input for keyword in ['예민','하지 정맥류','맹장','탈장']) or ("유방" in user_input and "검사" in user_input) or ("혹" in user_input and "제거" in user_input):
                hos = '외과'
                filtered_hospital_info = filter_hospital_by_department([hos],lat, lon)
                if filtered_hospital_info == 0:
                    bot_response = "죄송합니다. 현재 해당 진료과목의 운영중인 병원을 찾을 수 없습니다."
                else:
                    bot_response = f"해당 부위는 {hos}에 가시면 될 것 같습니다.<br> 현재 운영중인 가장 가까운 {hos} 병원을 알려드리겠습니다."
                    bot_response += "\n\n" + filtered_hospital_info  # 병원 정보 챗봇 응답에 추가
                    
            elif any(keyword in user_input for keyword in ['다리','어깨','관절','손목','발목','인대','힘줄','근육']) or ("뼈" in user_input and "부러" in user_input) or ("발" in user_input and "통증" in user_input):
                hos = '정형외과'
                filtered_hospital_info = filter_hospital_by_department([hos],lat, lon)
                if filtered_hospital_info == 0:
                    bot_response = "죄송합니다. 현재 해당 진료과목의 운영중인 병원을 찾을 수 없습니다."
                else:
                    bot_response = f"해당 부위는 {hos}에 가시면 될 것 같습니다.<br> 현재 운영중인 가장 가까운 {hos} 병원을 알려드리겠습니다."
                    bot_response += "\n\n" + filtered_hospital_info  # 병원 정보 챗봇 응답에 추가
                    
            elif any(keyword in user_input for keyword in ['내성발톱','뾰루지','보톡스','여드름','두드러기','피부','트러블','두피','제모']):
                hos = '피부과'
                filtered_hospital_info = filter_hospital_by_department([hos],lat, lon)
                if filtered_hospital_info == 0:
                    bot_response = "죄송합니다. 현재 해당 진료과목의 운영중인 병원을 찾을 수 없습니다."
                else:
                    bot_response = f"해당 부위는 {hos}에 가시면 될 것 같습니다.<br> 현재 운영중인 가장 가까운 {hos} 병원을 알려드리겠습니다."
                    bot_response += "\n\n" + filtered_hospital_info  # 병원 정보 챗봇 응답에 추가
                    
            elif any(keyword in user_input for keyword in ['몸살','기침','볼거리','성대']) or ("코" in user_input and "막" in user_input) or ("목" in user_input and "피" in user_input) or ("귀" in user_input and "물" in user_input) or ("귀" in user_input and "벌레" in user_input) or ("귀" in user_input and "먹먹" in user_input) or ("목" in user_input and "부" in user_input):
                hos = '이비인후과'
                filtered_hospital_info = filter_hospital_by_department([hos],lat, lon)
                if filtered_hospital_info == 0:
                    bot_response = "죄송합니다. 현재 해당 진료과목의 운영중인 병원을 찾을 수 없습니다."
                else:
                    bot_response = f"해당 부위는 {hos}에 가시면 될 것 같습니다.<br> 현재 운영중인 가장 가까운 {hos} 병원을 알려드리겠습니다."
                    bot_response += "\n\n" + filtered_hospital_info  # 병원 정보 챗봇 응답에 추가
                    
            elif any(keyword in user_input for keyword in ['건강검진','금연','금주','영양','비만','스트레스']):
                hos = '가정의학과'
                filtered_hospital_info = filter_hospital_by_department([hos],lat, lon)
                if filtered_hospital_info == 0:
                    bot_response = "죄송합니다. 현재 해당 진료과목의 운영중인 병원을 찾을 수 없습니다."
                else:
                    bot_response = f"해당 부위는 {hos}에 가시면 될 것 같습니다.<br> 현재 운영중인 가장 가까운 {hos} 병원을 알려드리겠습니다."
                    bot_response += "\n\n" + filtered_hospital_info  # 병원 정보 챗봇 응답에 추가
                    
            elif any(keyword in user_input for keyword in ['애들','아이','아기']):
                hos = '소아청소년과'
                filtered_hospital_info = filter_hospital_by_department([hos],lat, lon)
                if filtered_hospital_info == 0:
                    bot_response = "죄송합니다. 현재 해당 진료과목의 운영중인 병원을 찾을 수 없습니다."
                else:
                    bot_response = f"해당 부위는 {hos}에 가시면 될 것 같습니다.<br> 현재 운영중인 가장 가까운 {hos} 병원을 알려드리겠습니다."
                    bot_response += "\n\n" + filtered_hospital_info  # 병원 정보 챗봇 응답에 추가
                    
            elif any(keyword in user_input for keyword in ['임신','생리','질염','자궁']) or ("여성" in user_input and "질환" in user_input):
                hos = '산부인과'
                filtered_hospital_info = filter_hospital_by_department([hos],lat, lon)
                if filtered_hospital_info == 0:
                    bot_response = "죄송합니다. 현재 해당 진료과목의 운영중인 병원을 찾을 수 없습니다."
                else:
                    bot_response = f"해당 부위는 {hos}에 가시면 될 것 같습니다.<br> 현재 운영중인 가장 가까운 {hos} 병원을 알려드리겠습니다."
                    bot_response += "\n\n" + filtered_hospital_info  # 병원 정보 챗봇 응답에 추가
                    
            elif any(keyword in user_input for keyword in ['배뇨','요로','전립선','생식기','방광','신장']):
                hos = '비뇨의학과'
                filtered_hospital_info = filter_hospital_by_department([hos],lat, lon)
                if filtered_hospital_info == 0:
                    bot_response = "죄송합니다. 현재 해당 진료과목의 운영중인 병원을 찾을 수 없습니다."
                else:
                    bot_response = f"해당 부위는 {hos}에 가시면 될 것 같습니다.<br> 현재 운영중인 가장 가까운 {hos} 병원을 알려드리겠습니다."
                    bot_response += "\n\n" + filtered_hospital_info  # 병원 정보 챗봇 응답에 추가
            
            elif any(keyword in user_input for keyword in ['눈','결막','각막','수정체','녹내장','사시','시신경','눈꺼풀','시력']) or ("눈" in user_input and "외상" in user_input):
                hos = '안과'
                filtered_hospital_info = filter_hospital_by_department([hos],lat, lon)
                if filtered_hospital_info == 0:
                    bot_response = "죄송합니다. 현재 해당 진료과목의 운영중인 병원을 찾을 수 없습니다."
                else:
                    bot_response = f"해당 부위는 {hos}에 가시면 될 것 같습니다.<br> 현재 운영중인 가장 가까운 {hos} 병원을 알려드리겠습니다."
                    bot_response += "\n\n" + filtered_hospital_info  # 병원 정보 챗봇 응답에 추가
            
            elif any(keyword in user_input for keyword in ['한의원']):
                hos = '한의원'
                filtered_hospital_info = filter_hospital_by_department([hos],lat, lon)
                if filtered_hospital_info == 0:
                    bot_response = "죄송합니다. 현재 운영중인 한의원을 찾을 수 없습니다."
                else:
                    bot_response = f"현재 운영중인 가장 가까운 {hos} 병원을 알려드리겠습니다."
                    bot_response += "\n\n" + filtered_hospital_info  # 병원 정보 챗봇 응답에 추가
            
            elif any(keyword in user_input for keyword in ['치과']):
                hos = '치과'
                filtered_hospital_info = filter_hospital_by_department([hos],lat, lon)
                if filtered_hospital_info == 0:
                    bot_response = "죄송합니다. 현재 운영중인 치과병원을 찾을 수 없습니다."
                else:
                    bot_response = f"현재 운영중인 가장 가까운 {hos} 병원을 알려드리겠습니다."
                    bot_response += "\n\n" + filtered_hospital_info  # 병원 정보 챗봇 응답에 추가
            
            elif any(keyword in user_input for keyword in ['성형외과']):
                hos = '성형외과'
                filtered_hospital_info = filter_hospital_by_department([hos],lat, lon)
                if filtered_hospital_info == 0:
                    bot_response = "죄송합니다. 현재 운영중인 성형외과을 찾을 수 없습니다."
                else:
                    bot_response = f"현재 운영중인 가장 가까운 {hos} 병원을 알려드리겠습니다."
                    bot_response += "\n\n" + filtered_hospital_info  # 병원 정보 챗봇 응답에 추가
            elif any(keyword in user_input for keyword in ['종합병원']):
                hos = '종합병원'
                filtered_hospital_info = filter_hospital_by_department([hos],lat, lon)
                if filtered_hospital_info == 0:
                    bot_response = "죄송합니다. 현재 운영중인 종합병원을 찾을 수 없습니다."
                else:
                    bot_response = f"현재 운영중인 가장 가까운 {hos} 병원을 알려드리겠습니다."
                    bot_response += "\n\n" + filtered_hospital_info  # 병원 정보 챗봇 응답에 추가
            else:
                bot_response = "🔍 관련 정보를 찾을 수 없습니다."

        st.session_state['generated'].append(bot_response)
        st.session_state['past'].append(user_input)
        st.session_state.input_text = ""

    # 대화 초기화 함수
    def reset_conversation():
        st.session_state['past'].clear()
        st.session_state['generated'].clear()
        st.session_state['greeted'] = False
        st.session_state['address_saved'] = False  # 주소 저장 상태도 초기화
        st.session_state['address'] = ""  # 저장된 주소도 초기화

    # 처음에 인사 메시지를 한 번만 출력
    if 'greeted' not in st.session_state or not st.session_state['greeted']:
        st.session_state['generated'].append("안녕하세요, 병원 추천 챗봇입니다. 주소를 입력해주세요!")
        st.session_state['greeted'] = True 

    # 대화 표시 (streamlit_chat 사용)
    chat_placeholder = st.empty()
    
    with chat_placeholder.container():
        if len(st.session_state['generated']) > 0:
            st.markdown(f"""
                <div class="message-container">
                    <span class="bot-emoji">🤖</span>
                    <div class="bot-message">{st.session_state['generated'][0]}</div>
                </div>
            """, unsafe_allow_html=True)

        for i in range(len(st.session_state['past'])):
            st.markdown(f"""
                <div class="message-container">
                    <div class="user-message">{st.session_state['past'][i]}</div>
                    <span class="user-emoji">😊</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <div class="message-container">
                    <span class="bot-emoji">🤖</span>
                    <div class="bot-message">{st.session_state['generated'][i+1]}</div>
                </div>
            """, unsafe_allow_html=True)


    
    # 기본 레이아웃을 사용하여 입력창과 버튼을 정리
    st.markdown("""
        <style>
        /* 입력창의 기본 스타일 조정 */
        input[type="text"] {
            font-size: 22px !important;  /* 입력 문자의 크기를 키움 */
            width: 100% !important;  /* 너비를 100%로 설정 */
            padding: 10px !important;  /* 입력창 내부 여백 */
            box-sizing: border-box !important;  /* 패딩 포함 크기 계산 */
            border-radius: 8px !important;  /* 모서리를 둥글게 설정 */
            border: 2px solid #FFFFFF !important;  /* 테두리 색상 */
            background-color: #FFFFFF !important;  /* 입력창 배경색 */
        }
        </style>
    """, unsafe_allow_html=True)


    # 대화창 아래에 질문과 주소 입력창 배치
    with st.container():
        st.text_input("질문을 입력하세요:", key="input_text", on_change=process_input)
        st.button("대화 초기화", on_click=reset_conversation, key="reset_button")


