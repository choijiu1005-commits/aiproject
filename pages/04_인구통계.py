
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import re

# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="구리시 연령별 인구 분석",
    page_icon="📊",
    layout="wide"
)

st.title("구리시 연령별 인구 분석")
st.write("행정구역과 연도를 선택하여 연령별 인구수를 확인해 보세요.")

# =====================================
# 2. CSV 파일 위치 자동 검색
# =====================================

def find_csv_file():

    # 현재 파이썬 파일의 위치
    current_file = Path(__file__).resolve()

    # pages 폴더의 상위 폴더
    project_folder = current_file.parent.parent

    # 검색할 폴더 목록
    search_folders = [
        project_folder,
        Path.cwd(),
        Path.cwd().parent,
        current_file.parent
    ]

    # 중복 폴더 제거
    search_folders = list(dict.fromkeys(
        p.resolve() for p in search_folders
    ))

    # 1차: 지정된 위치에서 직접 검색
    for folder in search_folders:

        file_path = folder / "population.csv"

        if file_path.is_file():
            return file_path

    # 2차: 프로젝트 내부의 하위 폴더까지 검색
    for folder in search_folders:

        if folder.is_dir():

            for file_path in folder.rglob("*.csv"):

                if file_path.name.lower() == "population.csv":
                    return file_path

    return None


# =====================================
# 3. CSV 파일 읽기
# =====================================

@st.cache_data
def load_data(file_path, modified_time):

    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    last_error = None

    for encoding in encodings:

        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding
            )

            # 열 이름의 공백 제거
            df.columns = df.columns.astype(str).str.strip()

            return df

        except UnicodeDecodeError as e:
            last_error = e

    raise ValueError(
        f"CSV 인코딩 오류: {last_error}"
    )


# CSV 위치 확인
csv_path = find_csv_file()

if csv_path is None:

    st.error("population.csv 파일을 찾을 수 없습니다.")

    st.write("현재 파이썬 파일 위치:")
    st.code(str(Path(__file__).resolve()))

    st.write("현재 실행 위치:")
    st.code(str(Path.cwd()))

    st.write("검색한 폴더:")

    for folder in [
        Path(__file__).resolve().parent.parent,
        Path.cwd(),
        Path.cwd().parent
    ]:
        st.code(str(folder))

        if folder.exists():
            st.write([
                p.name for p in folder.iterdir()
            ])

    st.warning(
        "GitHub 저장소에 population.csv 파일이 실제로 "
        "업로드되어 있는지 확인해 주세요."
    )

    st.stop()


# 파일 수정 시간 확인
modified_time = csv_path.stat().st_mtime

# 데이터 불러오기
try:

    df = load_data(
        str(csv_path),
        modified_time
    )

except Exception as e:

    st.error(f"CSV 파일 읽기 오류: {e}")
    st.stop()


# =====================================
# 4. 데이터 구조 확인
# =====================================

if "행정구역" not in df.columns:

    st.error(
        "CSV 파일에서 '행정구역' 열을 찾을 수 없습니다."
    )

    st.write("현재 CSV 열 이름:")
    st.write(df.columns.tolist())

    st.stop()


# =====================================
# 5. 숫자 데이터 변환
# =====================================

for col in df.columns:

    if col != "행정구역":

        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(
                ",", "", regex=False
            ),
            errors="coerce"
        )


# =====================================
# 6. 행정구역 이름 정리
# =====================================

def clean_region(name):

    name = str(name).strip()

    name = re.sub(
        r"\s*\(\d+\)\s*$",
        "",
        name
    )

    return name


df["행정구역명"] = df["행정구역"].apply(
    clean_region
)


# =====================================
# 7. 연도 및 연령대 설정
# =====================================

years = [
    2020,
    2021,
    2022,
    2023,
    2024,
    2025
]

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


# =====================================
# 8. 행정구역 선택
# =====================================

st.subheader("분석 조건 선택")

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
        index=5
    )


# =====================================
# 9. 선택한 데이터 가져오기
# =====================================

selected_data = df[
    df["행정구역명"] == selected_region
]

if selected_data.empty:

    st.error("선택한 행정구역의 데이터가 없습니다.")
    st.stop()

selected_data = selected_data.iloc[0]


# =====================================
# 10. 연령별 인구 데이터 추출
# =====================================

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


# =====================================
# 11. 전체 인구수 표시
# =====================================

total_column = (
    f"{selected_year}년_거주자_총인구수"
)

if total_column in df.columns:

    total_population = selected_data[total_column]

else:

    total_population = sum(population)


if pd.isna(total_population):
    total_population = 0

total_population = int(total_population)


st.metric(
    label=f"{selected_region} {selected_year}년 전체 인구",
    value=f"{total_population:,}명"
)


# =====================================
# 12. 꺾은선 그래프
# =====================================

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
        "나이: %{x}<br>" +
        "인구수: %{y:,}명" +
        "<extra></extra>"

    )

)


# =====================================
# 13. 그래프 축 설정
# =====================================

fig.update_layout(

    title=dict(
        text=f"{selected_year}년 {selected_region} 연령별 인구",
        x=0.5,
        xanchor="center"
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

        gridcolor="#D9D9D9",

        gridwidth=1

    ),

    yaxis=dict(

        title="인구수 (명)",

        rangemode="tozero",

        tick0=0,

        dtick=100,

        tickformat=",",

        showgrid=True,

        gridcolor="#D9D9D9",

        gridwidth=1

    ),

    font=dict(
        family="sans-serif",
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


# =====================================
# 14. 그래프 출력
# =====================================

st.plotly_chart(
    fig,
    use_container_width=True
)


# =====================================
# 15. 연령별 인구 데이터 표
# =====================================

with st.expander("연령별 인구수 자세히 보기"):

    display_df = chart_df.copy()

    display_df["인구수"] = display_df[
        "인구수"
    ].apply(
        lambda x: f"{x:,}명"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# =====================================
# 16. 데이터 출처
# =====================================

st.caption(
    "자료: 구리시 인구 통계 CSV 파일"
)

