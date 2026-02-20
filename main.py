import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(page_title="치매 의료 이용률 대시보드", page_icon="🏥", layout="wide")

# 2. 메인 타이틀
st.markdown("""
    <h1 style='text-align: center; color: #2563eb; margin-bottom: 20px;'>
        🏥 국민건강보험공단 치매 의료 이용률 대시보드
    </h1>
""", unsafe_allow_html=True)

st.write("업로드해주신 CSV 데이터를 표와 요약 정보로 한눈에 확인해보세요! 👀")

# 파일 이름 설정 (올려주신 파일명 그대로 사용)
file_name = "국민건강보험공단_치매의료이용률_20241231.CSV"

# 3. 데이터 불러오기 함수 (캐싱을 적용해서 앱 속도를 빠르게!)
@st.cache_data
def load_data(filename):
    try:
        # 한국 공공데이터는 주로 cp949 인코딩을 사용합니다.
        df = pd.read_csv(filename, encoding='cp949')
    except UnicodeDecodeError:
        # cp949로 에러가 나면 utf-8로 다시 시도합니다.
        df = pd.read_csv(filename, encoding='utf-8')
    return df

# 4. 화면에 데이터 보여주기
try:
    # 데이터 로드
    df = load_data(file_name)
    
    # 탭을 만들어서 깔끔하게 분리해볼게요!
    tab1, tab2 = st.tabs(["📊 전체 데이터 보기", "💡 데이터 요약 정보"])
    
    with tab1:
        st.subheader("전체 데이터 미리보기")
        # 데이터프레임을 예쁘고 인터랙티브하게 보여줍니다.
        st.dataframe(df, use_container_width=True)
        
    with tab2:
        st.subheader("데이터 통계 요약")
        # 수치형 데이터의 평균, 최댓값, 최솟값 등을 보여줍니다.
        st.dataframe(df.describe(), use_container_width=True)

    # 안내 메시지
    st.success("데이터를 성공적으로 불러왔습니다! 🎉")
    st.info("💡 팁: 만약 지역별, 연도별 비교 차트(그래프)를 추가하고 싶으시다면, 데이터의 어떤 컬럼(열)을 비교하고 싶으신지 알려주세요! 멋진 차트 코드도 추가해 드릴게요.")

except FileNotFoundError:
    st.error(f"🚨 앗! '{file_name}' 파일을 찾을 수 없습니다.")
    st.warning("파이썬 코드를 실행하는 폴더와 CSV 파일이 같은 폴더에 있는지 다시 한번 확인해 주세요! 📂")
except Exception as e:
    st.error(f"🚨 알 수 없는 오류가 발생했습니다: {e}")
