
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

# 페이지 설정
st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("월별 평균기온 분석 및 예측")
st.write("세 가지 회귀 알고리즘으로 미래의 평균기온을 예측해 보세요.")

# CSV 파일 경로
BASE_DIR = Path(__file__).resolve().parent.parent

file_path = BASE_DIR / "temperature.csv"

# 파일 이름이 다른 경우를 위한 대체 경로
if not file_path.exists():
    file_path = BASE_DIR / "temperature(2).csv"

# 데이터 불러오기
if not file_path.exists():
    st.error("temperature.csv 파일을 찾을 수 없습니다.")
    st.info("CSV 파일을 py 파일의 상위 폴더에 넣어주세요.")
    st.stop()

try:
    df = pd.read_csv(file_path, encoding="cp949")
except UnicodeDecodeError:
    df = pd.read_csv(file_path, encoding="utf-8-sig")

# 날짜와 기온 데이터 정리
df["일시"] = pd.to_datetime(
    df["일시"],
    format="%b-%y",
    errors="coerce"
)

df["평균기온(℃)"] = pd.to_numeric(
    df["평균기온(℃)"],
    errors="coerce"
)

df = df.dropna(subset=["일시", "평균기온(℃)"])

df["연도"] = df["일시"].dt.year
df["월"] = df["일시"].dt.month

# 월 선택
month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

st.subheader("예측 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "예측할 월을 선택하세요.",
        list(month_names.keys()),
        format_func=lambda x: month_names[x]
    )

with col2:
    min_year = int(df["연도"].min())
    max_year = int(df["연도"].max())

    prediction_year = st.number_input(
        "예측할 연도를 입력하세요.",
        min_value=max_year + 1,
        max_value=max_year + 100,
        value=max_year + 1,
        step=1
    )

# 선택한 월의 데이터
month_df = df[df["월"] == selected_month].copy()
month_df = month_df.sort_values("연도")

if len(month_df) < 3:
    st.error("예측에 필요한 데이터가 부족합니다.")
    st.stop()

# 학습 데이터
base_year = int(month_df["연도"].min())

X = (
    month_df["연도"].values - base_year
).reshape(-1, 1)

y = month_df["평균기온(℃)"].values

future_X = np.array([
    [prediction_year - base_year]
])

# 세 가지 알고리즘 모두 준비
models = {
    "선형회귀": LinearRegression(),

    "랜덤 포레스트 회귀": RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        min_samples_leaf=2
    ),

    "다항 회귀": make_pipeline(
        PolynomialFeatures(
            degree=2,
            include_bias=False
        ),
        LinearRegression()
    )
}

# 세 알고리즘 모두 학습하고 예측
predictions = {}
scores = {}
fitted_values = {}

for name, model in models.items():

    model.fit(X, y)

    predictions[name] = float(
        model.predict(future_X)[0]
    )

    scores[name] = float(
        model.score(X, y)
    )

    fitted_values[name] = model.predict(X)

# 알고리즘 선택
st.subheader("회귀 알고리즘 선택")

selected_algorithm = st.radio(
    "사용할 알고리즘을 선택하세요.",
    options=[
        "선형회귀",
        "랜덤 포레스트 회귀",
        "다항 회귀"
    ],
    horizontal=True,
    key="algorithm_choice"
)

# 선택된 알고리즘 예측 결과
selected_prediction = predictions[selected_algorithm]

st.divider()

st.subheader(
    f"{prediction_year}년 {month_names[selected_month]} 평균기온 예측"
)

st.metric(
    label=f"{selected_algorithm} 예측 결과",
    value=f"{selected_prediction:.2f} ℃"
)

# 세 가지 알고리즘 예측값 비교
st.subheader("세 가지 알고리즘 예측 결과 비교")

result_col1, result_col2, result_col3 = st.columns(3)

with result_col1:
    st.metric(
        "선형회귀",
        f"{predictions['선형회귀']:.2f} ℃"
    )

with result_col2:
    st.metric(
        "랜덤 포레스트 회귀",
        f"{predictions['랜덤 포레스트 회귀']:.2f} ℃"
    )

with result_col3:
    st.metric(
        "다항 회귀",
        f"{predictions['다항 회귀']:.2f} ℃"
    )

# 그래프 만들기
st.subheader("과거 기온 및 세 가지 예측 그래프")

fig = go.Figure()

# 실제 과거 기온
fig.add_trace(
    go.Scatter(
        x=month_df["연도"],
        y=month_df["평균기온(℃)"],
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            size=9,
            color="black"
        )
    )
)

# 예측 그래프를 그릴 연도 범위
graph_years = np.linspace(
    month_df["연도"].min(),
    prediction_year,
    200
)

graph_X = (
    graph_years - base_year
).reshape(-1, 1)

# 세 가지 알고리즘의 회귀선 모두 표시
line_colors = {
    "선형회귀": "red",
    "랜덤 포레스트 회귀": "blue",
    "다항 회귀": "green"
}

for name, model in models.items():

    graph_predictions = model.predict(graph_X)

    fig.add_trace(
        go.Scatter(
            x=graph_years,
            y=graph_predictions,
            mode="lines",
            name=f"{name} 예측선",
            line=dict(
                width=3,
                color=line_colors[name]
            )
        )
    )

    # 미래 예측 지점
    fig.add_trace(
        go.Scatter(
            x=[prediction_year],
            y=[predictions[name]],
            mode="markers",
            name=f"{name} 예측값",
            marker=dict(
                size=11,
                symbol="star",
                color=line_colors[name]
            )
        )
    )

fig.update_layout(
    xaxis_title="연도",
    yaxis_title="평균기온(℃)",
    hovermode="x unified",
    legend_title="데이터 및 알고리즘",
    template="plotly_white",
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# 알고리즘 설명
st.divider()
st.subheader("세 가지 알고리즘의 작동 원리")

st.markdown("""
### 1. 선형회귀 (Linear Regression)
- 과거 기온 데이터의 전체적인 증가 또는 감소 추세를 직선으로 나타냅니다.
- 연도와 기온 사이의 관계를 학습하여 미래 기온을 예측합니다.
- 직선 형태로 변화하는 데이터를 분석할 때 유용합니다.

### 2. 랜덤 포레스트 회귀 (Random Forest Regression)
- 여러 개의 의사결정나무를 만들어 예측 결과를 종합합니다.
- 다양한 데이터 패턴을 학습할 수 있습니다.
- 여러 나무의 예측값을 평균 내어 결과를 만듭니다.

### 3. 다항 회귀 (Polynomial Regression)
- 직선뿐 아니라 곡선 형태의 관계도 학습합니다.
- 여기서는 2차식을 사용하여 기온의 변화 추세를 분석합니다.
- 기온이 일정하게 증가하거나 감소하지 않는 경우에도 활용할 수 있습니다.
""")

# 알고리즘별 점수
st.subheader("알고리즘별 학습 데이터 설명력 비교")

score_df = pd.DataFrame({
    "알고리즘": list(scores.keys()),
    "학습 데이터 R² 점수": list(scores.values())
})

st.dataframe(
    score_df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "R² 점수는 학습 데이터에 대한 적합도를 나타냅니다. "
    "점수가 높다고 미래 예측이 반드시 더 정확한 것은 아닙니다."
)

# 실제 데이터 확인
with st.expander("선택한 월의 과거 기온 데이터 확인하기"):
    st.dataframe(
        month_df[["연도", "월", "평균기온(℃)"]],
        use_container_width=True,
        hide_index=True
    )
