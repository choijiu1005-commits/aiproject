
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="서울 월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("서울 월별 기온분석")
st.write("월을 선택하면 연도별 최고기온과 최저기온을 비교합니다.")

# CSV 파일 위치 찾기
@st.cache_data
def load_data():

    file_name = "temperature(1).csv"

    # 현재 파일 위치를 기준으로 CSV 찾기
    base_path = Path(__file__).resolve().parent

    possible_paths = [
        base_path.parent / file_name,
        base_path / file_name,
        Path.cwd() / file_name
    ]

    file_path = None

    for path in possible_paths:
        if path.exists():
            file_path = path
            break

    if file_path is None:
        raise FileNotFoundError(
            "temperature(1).csv 파일을 찾을 수 없습니다."
        )

    # 한글 인코딩 처리
    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["일시"],
        format="%b-%y",
        errors="coerce"
    )

    # 날짜 변환 실패 시 일반 형식으로 재시도
    missing_dates = df["날짜"].isna()

    df.loc[missing_dates, "날짜"] = pd.to_datetime(
        df.loc[missing_dates, "일시"],
        errors="coerce"
    )

    # 연도와 월 추출
    df["연도"] = df["날짜"].dt.year
    df["월"] = df["날짜"].dt.month

    # 기온 숫자 변환
    df["최고기온(℃)"] = pd.to_numeric(
        df["최고기온(℃)"],
        errors="coerce"
    )

    df["최저기온(℃)"] = pd.to_numeric(
        df["최저기온(℃)"],
        errors="coerce"
    )

    return df


try:
    df = load_data()

    # 월 선택
    month_names = {
        1: "1월", 2: "2월", 3: "3월",
        4: "4월", 5: "5월", 6: "6월",
        7: "7월", 8: "8월", 9: "9월",
        10: "10월", 11: "11월", 12: "12월"
    }

    selected_month = st.selectbox(
        "분석할 월을 선택하세요.",
        list(month_names.keys()),
        format_func=lambda x: month_names[x]
    )

    # 선택한 월 데이터 추출
    month_data = df[df["월"] == selected_month].copy()

    # 연도별 최고기온과 최저기온 계산
    result = (
        month_data
        .groupby("연도")
        .agg(
            최고기온=("최고기온(℃)", "max"),
            최저기온=("최저기온(℃)", "min")
        )
        .dropna()
        .sort_index()
    )

    if not result.empty:

        # Plotly 그래프 생성
        fig = go.Figure()

        # 최고기온 그래프 (빨간색)
        fig.add_trace(
            go.Scatter(
                x=result.index,
                y=result["최고기온"],
                mode="lines+markers",
                name="최고기온",
                line=dict(
                    color="red",
                    width=3
                ),
                marker=dict(size=8)
            )
        )

        # 최저기온 그래프 (남색)
        fig.add_trace(
            go.Scatter(
                x=result.index,
                y=result["최저기온"],
                mode="lines+markers",
                name="최저기온",
                line=dict(
                    color="navy",
                    width=3
                ),
                marker=dict(size=8)
            )
        )

        # 그래프 제목과 축 설정
        fig.update_layout(
            title={
                "text": "월별 기온분석",
                "x": 0.5
            },
            xaxis_title="연도",
            yaxis_title="온도 (℃)",
            legend_title="기온 종류",
            template="plotly_white",
            hovermode="x unified"
        )

        # 그래프 출력
        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # 데이터 표
        st.subheader("연도별 기온 데이터")
        st.dataframe(
            result,
            use_container_width=True
        )

        # 간단한 분석
        st.subheader("기온 분석 결과")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "가장 높은 최고기온",
                f"{result['최고기온'].max()} ℃"
            )

        with col2:
            st.metric(
                "가장 낮은 최저기온",
                f"{result['최저기온'].min()} ℃"
            )

    else:
        st.warning("선택한 월에 분석할 데이터가 없습니다.")

except FileNotFoundError as e:
    st.error(str(e))

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
