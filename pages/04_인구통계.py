
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import re

# --------------------------------
# 1. 페이지 설정
# --------------------------------
st.set_page_config(
    page_title="구리시 연령별 인구 분석",
    page_icon="📊",
    layout="wide"
)

st.title("구리시 연령별 인구 분석")
st.write("행정구역과 연도를 선택하여 연령별 인구수를 확인해 보세요.")

# --------------------------------
# 2. CSV 파일 불러오기
# --------------------------------
@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "population.csv"

    # 한글 인코딩 자동 대응
    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]

    for encoding in encodings:
        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding
            )
            return df
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 인코딩을 확인해 주세요.")

try:
    df = load_data()

except FileNotFoundError:
    st.error("population.csv 파일을 찾을 수 없습니다.")
    st.stop()

except Exception as e:
    st.error(f"파일을 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# --------------------------------
# 3. 데이터 전처리
# --------------------------------

# 숫자 데이터의 쉼표 제거 및 숫자 변환
for col in df.columns[1:]:
    df[col] = pd.to_numeric(
        df[col].astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    )

# 행정구역 이름 정리
def clean_region(name):
    name = str(name).strip()

    # 행정구역 코드 제거
    name = re.sub(r"\s*\(\d+\)\s*$", "", name)

    return name

df["행정구역명"] = df["행정구역"].apply(clean_region)

# --------------------------------
# 4. 연도 및 연령대 설정
# --------------------------------

years = [2020, 2021, 2022, 2023, 2024, 2025]

ages = [
    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상"
]

# --------------------------------
# 5. 행정구역 및 연도 선택
# --------------------------------

st.subheader("분석 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_region = st.selectbox(
        "행정구역을 선택하세요.",
        df["행정구역명"].tolist()
    )

with col2:
    selected_year = st.selectbox(
        "연도를 선택하세요.",
        years,
        index=len(years) - 1
    )

# --------------------------------
# 6. 선택한 데이터 추출
# --------------------------------

selected_data = df[
    df["행정구역명"] == selected_region
]

if selected_data.empty:
    st.error("선택한 행정구역의 데이터가 없습니다.")
    st.stop()

selected_data = selected_data.iloc[0]

# 연령별 인구수 가져오기
population = []

for age in ages:
    column_name = f"{selected_year}년_거주자_{age}"

    if column_name in df.columns:
        value = selected_data[column_name]
        population.append(
            0 if pd.isna(value) else int(value)
        )
    else:
        population.append(0)

# 그래프용 데이터프레임
chart_df = pd.DataFrame({
    "나이": ages,
    "인구수": population
})

# --------------------------------
# 7. 선택한 지역의 전체 인구
# --------------------------------

total_column = f"{selected_year}년_거주자_총인구수"

if total_column in df.columns:
    total_population = selected_data[total_column]
else:
    total_population = sum(population)

total_population = (
    0 if pd.isna(total_population)
    else int(total_population)
)

st.metric(
    label=f"{selected_region} {selected_year}년 전체 인구",
    value=f"{total_population:,}명"
)

# --------------------------------
# 8. 꺾은선 그래프 생성
# --------------------------------

st.subheader(
    f"{selected_region} {selected_year}년 연령별 인구 그래프"
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=chart_df["나이"],
        y=chart_df["인구수"],
        mode="lines+markers",
        name="인구수",
        line=dict(
            color="#FFD700",
            width=4
        ),
        marker=dict(
            color="#FFD700",
            size=9,
            line=dict(
                color="#D6A900",
                width=1
            )
        ),
        hovertemplate=
            "연령: %{x}<br>" +
            "인구수: %{y:,}명" +
            "<extra></extra>"
    )
)

# --------------------------------
# 9. 그래프 축 및 구분선 설정
# --------------------------------

fig.update_layout(
    xaxis=dict(
        title="나이",
        type="category",
        categoryorder="array",
        categoryarray=ages,
        tickmode="array",
        tickvals=ages,
        ticktext=ages,
        showgrid=True,
        gridcolor="#D9D9D9",
        gridwidth=1,
        showline=True,
        linecolor="#777777",
        tickfont=dict(
            family="Malgun Gothic, sans-serif",
            size=12
        )
    ),

    yaxis=dict(
        title="인구수 (명)",
        rangemode="tozero",
        dtick=100,
        tick0=0,
        showgrid=True,
        gridcolor="#D9D9D9",
        gridwidth=1,
        showline=True,
        linecolor="#777777",
        tickformat=",",
        tickfont=dict(
            family="Malgun Gothic, sans-serif",
            size=12
        )
    ),

    title=dict(
        text=f"{selected_year}년 {selected_region} 연령별 인구",
        x=0.5,
        xanchor="center"
    ),

    font=dict(
        family="Malgun Gothic, AppleGothic, sans-serif",
        size=13,
        color="#333333"
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",
    height=600,

    margin=dict(
        l=80,
        r=30,
        t=80,
        b=100
    ),

    hovermode="x unified"
)

# --------------------------------
# 10. 스트림릿에 그래프 출력
# --------------------------------

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------
# 11. 연령별 인구 데이터 표
# --------------------------------

with st.expander("연령별 인구수 자세히 보기"):
    display_df = chart_df.copy()

    display_df["인구수"] = display_df["인구수"].apply(
        lambda x: f"{x:,}명"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

st.caption("자료: 제공된 구리시 인구 통계 CSV 파일")
