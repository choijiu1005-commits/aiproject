
import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="국가별 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)

# 제목
st.title("🌍 세계 국가별 MBTI 분석")
st.write("158개 국가의 MBTI 유형별 비율을 확인해 보세요!")

st.divider()

# CSV 파일 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

try:
    df = load_data()

    # MBTI 유형 목록
    mbti_types = [
        "INFJ", "ISFJ", "INTP", "ISFP",
        "ENTP", "INFP", "ENTJ", "ISTP",
        "INTJ", "ESFP", "ESTJ", "ENFP",
        "ESTP", "ISTJ", "ENFJ", "ESFJ"
    ]

    # 사이드바
    st.sidebar.title("분석 메뉴")
    menu = st.sidebar.radio(
        "원하는 메뉴를 선택하세요.",
        [
            "국가별 MBTI 분석",
            "MBTI 유형별 국가 비교",
            "전체 데이터 확인"
        ]
    )

    # 국가별 MBTI 분석
    if menu == "국가별 MBTI 분석":

        st.header("국가별 MBTI 분석")

        country = st.selectbox(
            "분석할 국가를 선택하세요.",
            sorted(df["Country"].tolist())
        )

        country_data = df[df["Country"] == country].iloc[0]

        # 데이터 정리
        result = pd.DataFrame({
            "MBTI": mbti_types,
            "비율": [country_data[t] * 100 for t in mbti_types]
        })

        result = result.sort_values(
            by="비율", ascending=False
        )

        # 가장 높은 유형
        top_mbti = result.iloc[0]

        col1, col2, col3 = st.columns(3)

        col1.metric("선택 국가", country)
        col2.metric("가장 높은 MBTI", top_mbti["MBTI"])
        col3.metric("MBTI 비율", f'{top_mbti["비율"]:.2f}%')

        st.divider()

        st.subheader(f"{country}의 MBTI 유형별 비율")

        chart_data = result.set_index("MBTI")
        st.bar_chart(chart_data)

        st.subheader("MBTI 순위")

        result_display = result.copy()
        result_display.index = range(1, len(result_display) + 1)
        result_display.index.name = "순위"
        result_display["비율"] = result_display["비율"].map(
            lambda x: f"{x:.2f}%"
        )

        st.dataframe(
            result_display,
            use_container_width=True
        )

    # MBTI 유형별 국가 비교
    elif menu == "MBTI 유형별 국가 비교":

        st.header("MBTI 유형별 국가 비교")

        selected_mbti = st.selectbox(
            "비교할 MBTI 유형을 선택하세요.",
            mbti_types
        )

        compare_data = df[["Country", selected_mbti]].copy()

        compare_data[selected_mbti] = (
            compare_data[selected_mbti] * 100
        )

        compare_data = compare_data.sort_values(
            by=selected_mbti,
            ascending=False
        )

        st.subheader(
            f"전 세계 {selected_mbti} 비율 비교"
        )

        st.bar_chart(
            compare_data.set_index("Country")
        )

        st.subheader("비율이 높은 상위 10개 국가")

        top10 = compare_data.head(10).copy()
        top10.columns = ["국가", "비율"]
        top10["비율"] = top10["비율"].map(
            lambda x: f"{x:.2f}%"
        )

        st.dataframe(
            top10,
            use_container_width=True,
            hide_index=True
        )

    # 전체 데이터 확인
    elif menu == "전체 데이터 확인":

        st.header("전체 국가 데이터")

        st.write(
            f"현재 총 {len(df)}개 국가의 데이터가 저장되어 있습니다."
        )

        # 검색
        search = st.text_input(
            "국가 이름 검색",
            placeholder="예: Korea"
        )

        if search:
            filtered_df = df[
                df["Country"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]
        else:
            filtered_df = df

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        # CSV 다운로드
        csv = filtered_df.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            label="데이터 CSV 다운로드",
            data=csv,
            file_name="MBTI_country_data.csv",
            mime="text/csv"
        )

    st.divider()

    st.caption(
        "※ 본 앱은 제공된 CSV 데이터에 기록된 국가별 MBTI 비율을 시각화합니다. "
        "실제 모든 국민의 성격을 대표하는 통계로 해석해서는 안 됩니다."
    )

except FileNotFoundError:
    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "app.py와 countriesMBTI_16types.csv 파일이 "
        "같은 폴더에 있는지 확인해 주세요."
    )

except Exception as e:
    st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")

