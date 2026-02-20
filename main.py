import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# 1. 페이지 기본 설정
st.set_page_config(page_title="치매 의료 이용률 지도", page_icon="🗺️", layout="wide")

st.markdown("""
    <h1 style='text-align: center; color: #2563eb; margin-bottom: 20px;'>
        🗺️ 지역별 치매 의료 이용률 대시보드
    </h1>
    <p style='text-align: center; color: #64748b;'>지도에서 지역에 마우스를 올리거나 클릭하면 상세 퍼센트가 나타납니다! ✨</p>
""", unsafe_allow_html=True)

file_name = "국민건강보험공단_치매의료이용률_20241231.CSV"

# 2. 데이터 불러오기 함수
@st.cache_data
def load_data(filename):
    try:
        df = pd.read_csv(filename, encoding='cp949')
    except UnicodeDecodeError:
        df = pd.read_csv(filename, encoding='utf-8')
    return df

# GeoJSON 데이터 (대한민국 시도 경계선 데이터) 불러오기
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_provinces_geo_simple.json"
    response = requests.get(url)
    return response.json()

try:
    df = load_data(file_name)
    geo_data = load_geojson()
    
    # 3. 데이터 구조를 모르기 때문에, 사용자가 직접 '지역'과 '이용률' 열을 선택하게 만듭니다.
    st.info("💡 데이터의 어떤 열(Column)을 지도로 그릴지 아래에서 선택해 주세요!")
    col1, col2 = st.columns(2)
    with col1:
        region_col = st.selectbox("📍 '지역(시도명)'이 적힌 열을 선택하세요:", df.columns)
    with col2:
        value_col = st.selectbox("📊 '이용률(%)'이 적힌 열을 선택하세요:", df.columns)

    # 4. 지역별 데이터 그룹화 (평균값 계산)
    # 혹시 숫자 데이터가 텍스트로 되어있을까봐 숫자로 변환합니다.
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    grouped_df = df.groupby(region_col)[value_col].mean().reset_index()

    # 5. 지도와 데이터를 찰떡처럼 연결하기 위한 마법 (이름 자동 매칭)
    # 예: GeoJSON의 '서울특별시'와 데이터의 '서울'을 앞 2글자로 연결해줍니다.
    for feature in geo_data['features']:
        geo_name = feature['properties']['name'] 
        
        # 앞 2글자(예: '서울', '경기', '제주')가 포함된 행 찾기
        matched_row = grouped_df[grouped_df[region_col].astype(str).str.startswith(geo_name[:2])]
        
        if not matched_row.empty:
            feature['properties']['value'] = str(round(matched_row[value_col].values[0], 2)) + " %"
        else:
            feature['properties']['value'] = "데이터 없음"

    # 6. Folium 지도 객체 생성 (초기 중심점: 대한민국)
    m = folium.Map(location=[36.5, 127.5], zoom_start=7, tiles="cartodbpositron")

    # 7. 색상이 칠해진 지역 지도(Choropleth) 및 툴팁 추가
    folium.GeoJson(
        geo_data,
        style_function=lambda feature: {
            'fillColor': '#38bdf8' if feature['properties']['value'] != "데이터 없음" else '#e2e8f0',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.6,
        },
        highlight_function=lambda feature: {
            'weight': 3,
            'fillOpacity': 0.9,
            'color': '#c084fc'
        },
        tooltip=folium.features.GeoJsonTooltip(
            fields=['name', 'value'],
            aliases=['📍 지역:', '📊 이용률:'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 14px; padding: 10px; border-radius: 5px; box-shadow: 3px 3px 5px rgba(0,0,0,0.2);")
        )
    ).add_to(m)

    # 8. 완성된 지도를 Streamlit 화면에 출력!
    st.write("---")
    st_folium(m, width=1000, height=700)
    
    # 9. 그룹화된 데이터 표도 아래에 살짝 보여줍니다.
    with st.expander("📝 그룹화된 지역별 데이터 표로 보기"):
        st.dataframe(grouped_df.style.format({value_col: "{:.2f}%"}), use_container_width=True)

except FileNotFoundError:
    st.error(f"🚨 '{file_name}' 파일을 찾을 수 없습니다. 파이썬 파일과 같은 폴더에 있는지 확인해주세요!")
except Exception as e:
    st.error(f"🚨 오류가 발생했습니다: {e}")
