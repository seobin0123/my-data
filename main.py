import streamlit as st
import pandas as pd

# 서울 기상 데이터 주소
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/seoul.csv"
)

# 페이지 설정
st.set_page_config(
    page_title="서울 100년 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

# 제목
st.title("🌡️ 서울의 100년 연평균 기온 변화")
st.write(
    "서울의 일별 기상 관측자료를 연도별로 집계하여 "
    "연평균 기온의 변화를 보여줍니다."
)


# 데이터 불러오기
@st.cache_data
def load_data():

    df = pd.read_csv(
        DATA_URL,
        encoding="utf-8-sig"
    )

    # 날짜를 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    # 평균기온을 숫자로 변환
    df["평균기온"] = pd.to_numeric(
        df["평균기온"],
        errors="coerce"
    )

    # 결측값 제거
    df = df.dropna(
        subset=["날짜", "평균기온"]
    )

    # 연도 추출
    df["연도"] = df["날짜"].dt.year

    # 연도별 평균기온 계산
    annual = (
        df.groupby("연도")["평균기온"]
        .mean()
        .reset_index()
    )

    # 열 이름 변경
    annual = annual.rename(
        columns={
            "평균기온": "연평균기온"
        }
    )

    return annual


# 데이터 불러오기
try:

    annual = load_data()

    # 분석 가능한 연도
    min_year = int(annual["연도"].min())
    max_year = int(annual["연도"].max())

    # --------------------------------
    # 사이드바
    # --------------------------------

    st.sidebar.header("조회 기간")

    start_year, end_year = st.sidebar.slider(
        "연도 범위",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1
    )

    # 선택한 기간만 필터링
    chart_data = annual[
        (annual["연도"] >= start_year)
        & (annual["연도"] <= end_year)
    ].copy()

    # --------------------------------
    # 주요 지표
    # --------------------------------

    first_temp = chart_data.iloc[0]["연평균기온"]
    last_temp = chart_data.iloc[-1]["연평균기온"]

    temperature_change = last_temp - first_temp

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "분석 기간",
            f"{start_year}~{end_year}"
        )

    with col2:
        st.metric(
            "시작 연도 평균기온",
            f"{first_temp:.1f} ℃"
        )

    with col3:
        st.metric(
            "기온 변화",
            f"{temperature_change:+.1f} ℃"
        )

    # --------------------------------
    # 그래프
    # --------------------------------

    st.subheader("연도별 연평균 기온")

    graph_data = chart_data.set_index("연도")

    st.line_chart(
        graph_data["연평균기온"],
        height=500
    )

    st.caption(
        "※ 연평균 기온은 해당 연도의 일별 평균기온을 "
        "평균하여 계산했습니다."
    )

    # --------------------------------
    # 데이터 표
    # --------------------------------

    with st.expander("연도별 연평균 기온 데이터 보기"):

        display_data = chart_data.copy()

        display_data["연평균기온"] = (
            display_data["연평균기온"].round(2)
        )

        display_data = display_data.rename(
            columns={
                "연도": "연도",
                "연평균기온": "연평균 기온(℃)"
            }
        )

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )

        # CSV 다운로드
        csv = display_data.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            label="연평균 기온 데이터 다운로드",
            data=csv,
            file_name="서울_연평균기온.csv",
            mime="text/csv"
        )

    # --------------------------------
    # 출처
    # --------------------------------

    st.divider()

    st.caption(
        "데이터 출처: 서울 기상 관측자료(seoul.csv)"
    )

except Exception as e:

    st.error(
        "데이터를 불러오는 중 오류가 발생했습니다."
    )

    st.exception(e)
