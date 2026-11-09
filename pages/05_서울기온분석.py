
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib

# 페이지 설정
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("월별 기온분석")
st.write("원하는 월을 선택하여 연도별 최고기온과 최저기온을 비교해 보세요.")

# 1. CSV 파일 불러오기
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(
            "temperature(1).csv",
            encoding="cp949"
        )
    except UnicodeDecodeError:
        df = pd.read_csv(
            "temperature(1).csv",
            encoding="utf-8-sig"
        )

    # 날짜 데이터 변환
    df["날짜"] = pd.to_datetime(
        df["일시"],
        format="%b-%y",
        errors="coerce"
    )

    # 연도와 월 추출
    df["연도"] = df["날짜"].dt.year
    df["월"] = df["날짜"].dt.month

    # 기온 데이터 숫자로 변환
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

    # 2. 월 선택
    month_names = {
        1: "1월",
        2: "2월",
        3: "3월",
        4: "4월",
        5: "5월",
        6: "6월",
        7: "7월",
        8: "8월",
        9: "9월",
        10: "10월",
        11: "11월",
        12: "12월"
    }

    selected_month = st.selectbox(
        "분석할 월을 선택하세요.",
        options=list(month_names.keys()),
        format_func=lambda x: month_names[x]
    )

    # 3. 선택한 월의 데이터 추출
    month_data = df[df["월"] == selected_month].copy()

    # 연도별 최고기온과 최저기온 정리
    result = (
        month_data
        .groupby("연도")
        .agg({
            "최고기온(℃)": "max",
            "최저기온(℃)": "min"
        })
        .dropna()
        .sort_index()
    )

    # 4. 그래프 그리기
    if not result.empty:

        fig, ax = plt.subplots(figsize=(12, 6))

        # 최고기온: 빨간색
        ax.plot(
            result.index,
            result["최고기온(℃)"],
            color="red",
            marker="o",
            linewidth=2,
            label="최고기온"
        )

        # 최저기온: 남색
        ax.plot(
            result.index,
            result["최저기온(℃)"],
            color="navy",
            marker="o",
            linewidth=2,
            label="최저기온"
        )

        # 그래프 제목과 축
        ax.set_title(
            "월별 기온분석",
            fontsize=20,
            pad=20
        )

        ax.set_xlabel("연도", fontsize=13)
        ax.set_ylabel("온도 (℃)", fontsize=13)

        # 범례 표시
        ax.legend(
            loc="best",
            fontsize=12
        )

        # 격자 표시
        ax.grid(
            True,
            linestyle="--",
            alpha=0.4
        )

        ax.set_xticks(result.index)
        ax.tick_params(axis="x", rotation=45)

        plt.tight_layout()

        # Streamlit에 그래프 출력
        st.pyplot(fig)
        plt.close(fig)

        # 5. 데이터 표 출력
        st.subheader("연도별 기온 데이터")
        st.dataframe(
            result.rename(columns={
                "최고기온(℃)": "최고기온",
                "최저기온(℃)": "최저기온"
            }),
            use_container_width=True
        )

    else:
        st.warning("선택한 월에 해당하는 데이터가 없습니다.")

except FileNotFoundError:
    st.error("temperature(1).csv 파일을 찾을 수 없습니다.")

except Exception as e:
    st.error(f"데이터 분석 중 오류가 발생했습니다: {e}")
