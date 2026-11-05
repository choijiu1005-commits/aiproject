
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import re

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="구리시 인구 통계 분석",
    page_icon="📊",
    layout="wide"
)

st.title("구리시 인구 통계 분석")
st.write("행정구역과 연령대를 선택하여 인구 변화를 분석해 보세요.")

st.divider()


# ==========================================
# 2. CSV 파일 위치 찾기
# ==========================================

current_dir = Path(__file__).resolve().parent
project_dir = current_dir.parent

possible_paths = [
    project_dir / "population.csv",
    Path.cwd() / "population.csv",
    Path.cwd().parent / "population.csv",
    project_dir / "data" / "population.csv"
]

csv_path = None

for path in possible_paths:
    if path.is_file():
        csv_path = path
        break

if csv_path is None:
    st.error("population.csv 파일을 찾을 수 없습니다.")
    st.write("검색한 경로:")

    for path in possible_paths:
        st.write(str(path))

    st.stop()


# ==========================================
# 3. CSV 파일 불러오기
# ==========================================

@st.cache_data
def load_data(file_path, modified_time):

    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    for encoding in encodings:
        try:
            data = pd.read_csv(
                file_path,
                encoding=encoding
            )

            data.columns = (
                data.columns.astype(str).str.strip()
            )

            return data

        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 한글 인코딩 오류입니다.")


try:
    df = load_data(
        str(csv_path),
        csv_path.stat().st_mtime
    )

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


# ==========================================
# 4. 데이터 전처리
# ==========================================

if "행정구역" not in df.columns:
    st.error("'행정구역' 열을 찾을 수 없습니다.")
    st.stop()


# 숫자 데이터 변환
for col in df.columns:
    if col != "행정구역":
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(
                ",", "", regex=False
            ),
            errors="coerce"
        )


# 행정구역 이름 정리
df["행정구역명"] = (
    df["행정구역"]
    .astype(str)
    .str.strip()
    .str.replace(
        r"\s*\(\d+\)\s*$",
        "",
        regex=True
    )
)


# ==========================================
# 5. 연령대와 연도 설정
# ==========================================

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

years = []

for col in df.columns:
    match = re.match(
        r"(\d{4})년_거주자_총인구수",
        col
    )

    if match:
        years.append(int(match.group(1)))

years = sorted(set(years))

if not years:
    st.error("연도 데이터를 찾을 수 없습니다.")
    st.stop()


# ==========================================
# 6. 연령별 인구 분석
# ==========================================

st.header("1. 연령별 인구 분석")

col1, col2 = st.columns(2)

with col1:
    regions = df["행정구역명"].drop_duplicates().tolist()

    selected_region = st.selectbox(
        "행정구역 선택",
        regions
    )

with col2:
    selected_year = st.selectbox(
        "연도 선택",
        years,
        index=len(years) - 1
    )


# ==========================================
# 7. 선택한 지역 데이터 추출
# ==========================================

selected_data = df[
    df["행정구역명"] == selected_region
]

if selected_data.empty:
    st.error("선택한 지역의 데이터가 없습니다.")
    st.stop()

selected_data = selected_data.iloc[0]


# 연령별 인구수
population = []

for age in ages:

    column_name = f"{selected_year}년_거주자_{age}"

    if column_name in df.columns:
        value = selected_data[column_name]

        if pd.isna(value):
            population.append(0)
        else:
            population.append(int(value))

    else:
        population.append(0)


chart_df = pd.DataFrame({
    "나이": ages,
    "인구수": population
})


# ==========================================
# 8. 전체 인구수
# ==========================================

total_column = (
    f"{selected_year}년_거주자_총인구수"
)

if total_column in df.columns:
    total_population = selected_data[total_column]
else:
    total_population = sum(population)

if pd.isna(total_population):
    total_population = 0

st.metric(
    f"{selected_region} 전체 인구",
    f"{int(total_population):,}명"
)


# ==========================================
# 9. 연령별 꺾은선 그래프
# ==========================================

st.subheader(
    f"{selected_year}년 연령별 인구수"
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
        "나이: %{x}<br>" +
        "인구수: %{y:,}명" +
        "<extra></extra>"
    )
)

fig.update_layout(

    title=dict(
        text=f"{selected_region} {selected_year}년 연령별 인구",
        x=0.5
    ),

    xaxis=dict(
        title="나이",
        type="category",
        categoryorder="array",
        categoryarray=ages,
        tickmode="array",
        tickvals=ages,
        ticktext=ages,
        showgrid=True,
        gridcolor="#D9D9D9"
    ),

    yaxis=dict(
        title="인구수 (명)",
        rangemode="tozero",
        tick0=0,
        dtick=100,
        tickformat=",",
        showgrid=True,
        gridcolor="#D9D9D9"
    ),

    font=dict(
        family="sans-serif",
        size=13,
        color="#333333"
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",
    height=600,
    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 10. 연령별 인구 표
# ==========================================

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


# ==========================================
# 11. 연령대별 행정구역 순위 분석
# ==========================================

st.divider()

st.header("2. 연령대별 인구가 가장 많은 행정구역")

st.write(
    "연령대와 연도를 선택하면 해당 연령의 인구가 "
    "많은 행정구역부터 막대그래프로 보여줍니다."
)


# ==========================================
# 12. 연령대 및 연도 선택
# ==========================================

rank_col1, rank_col2 = st.columns(2)

with rank_col1:
    rank_year = st.selectbox(
        "순위 분석 연도",
        years,
        index=len(years) - 1,
        key="rank_year"
    )

with rank_col2:
    selected_age = st.selectbox(
        "분석할 연령대",
        ages,
        key="rank_age"
    )


# ==========================================
# 13. 행정동 데이터 추출
# ==========================================

# 구리시 전체가 아닌 실제 행정동만 추출
district_df = df[
    df["행정구역명"].str.contains(
        r"동$",
        regex=True,
        na=False
    )
].copy()


# 데이터 확인
if district_df.empty:
    st.error("행정동 데이터를 찾을 수 없습니다.")

    st.write("현재 행정구역 목록:")
    st.write(df["행정구역명"].tolist())

    st.stop()


# ==========================================
# 14. 선택한 연령대 인구수 추출
# ==========================================

rank_column = (
    f"{rank_year}년_거주자_{selected_age}"
)

if rank_column not in district_df.columns:

    st.error(
        f"선택한 데이터 열을 찾을 수 없습니다: {rank_column}"
    )

    st.write("실제 CSV 열 이름:")
    st.write(district_df.columns.tolist())

    st.stop()


rank_df = district_df[
    ["행정구역명", rank_column]
].copy()


rank_df = rank_df.rename(
    columns={
        "행정구역명": "행정구역",
        rank_column: "인구수"
    }
)


# 숫자형 변환 및 결측값 처리
rank_df["인구수"] = pd.to_numeric(
    rank_df["인구수"],
    errors="coerce"
).fillna(0)


# ==========================================
# 15. 인구 순위 정렬
# ==========================================

rank_df = rank_df.sort_values(
    by="인구수",
    ascending=False
).reset_index(drop=True)


rank_df["순위"] = range(
    1,
    len(rank_df) + 1
)


# 데이터가 있는지 확인
if rank_df.empty or rank_df["인구수"].sum() == 0:

    st.warning(
        "선택한 연령대의 인구 데이터가 없습니다."
    )

    st.stop()


# ==========================================
# 16. 인구 1위 행정구역 표시
# ==========================================

first_place = rank_df.iloc[0]

metric1, metric2 = st.columns(2)

with metric1:
    st.metric(
        "인구 1위 행정구역",
        first_place["행정구역"]
    )

with metric2:
    st.metric(
        "1위 인구수",
        f"{int(first_place['인구수']):,}명"
    )


# ==========================================
# 17. 막대그래프 출력
# ==========================================

st.subheader(
    f"{rank_year}년 {selected_age} 행정구역별 인구 순위"
)

# 세로 막대그래프
bar_fig = go.Figure()

bar_fig.add_trace(
    go.Bar(

        x=rank_df["행정구역"].tolist(),

        y=rank_df["인구수"].tolist(),

        marker=dict(
            color="#FFD700",
            line=dict(
                color="#D6A900",
                width=1
            )
        ),

        text=[
            f"{int(value):,}명"
            for value in rank_df["인구수"]
        ],

        textposition="outside",

        cliponaxis=False,

        hovertemplate=
        "행정구역: %{x}<br>" +
        "인구수: %{y:,.0f}명" +
        "<extra></extra>"
    )
)


# 막대그래프 디자인
bar_fig.update_layout(

    title=dict(
        text=f"{selected_age} 인구 순위",
        x=0.5,
        xanchor="center"
    ),

    xaxis=dict(
        title="행정구역",
        type="category",
        categoryorder="array",
        categoryarray=rank_df["행정구역"].tolist(),
        tickangle=-30
    ),

    yaxis=dict(
        title="인구수 (명)",
        rangemode="tozero",
        tickformat=",",
        showgrid=True,
        gridcolor="#D9D9D9"
    ),

    font=dict(
        family="sans-serif",
        size=13,
        color="#333333"
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",

    height=550,

    margin=dict(
        l=70,
        r=50,
        t=90,
        b=120
    ),

    showlegend=False
)


# 실제 그래프 화면 출력
st.plotly_chart(
    bar_fig,
    use_container_width=True,
    key="district_population_bar_chart"
)


# ==========================================
# 18. 행정구역 순위표
# ==========================================

with st.expander("행정구역별 인구 순위 자세히 보기"):

    result_df = rank_df[
        ["순위", "행정구역", "인구수"]
    ].copy()

    result_df["인구수"] = result_df["인구수"].apply(
        lambda x: f"{int(x):,}명"
    )

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 19. 데이터 출처
# ==========================================

st.divider()

st.caption(
    "자료: 제공된 구리시 인구 통계 CSV 파일"
)
