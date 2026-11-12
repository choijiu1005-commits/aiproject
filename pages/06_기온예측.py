
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from pathlib import Path

# ------------------------------------
# 1. 페이지 기본 설정
# ------------------------------------
st.set_page_config(
    page_title="서울 기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("서울 월별 평균기온 예측")
st.write("과거 기온 데이터를 선형회귀로 학습하여 미래 기온을 예측합니다.")

# ------------------------------------
# 2. CSV 파일 경로 설정
# ------------------------------------
# 현재 파일: aiproject/pages/06_기온예측.py
# CSV 파일: aiproject/temperature.csv

BASE_DIR = Path(__file__).resolve().parent.parent

file_path = BASE_DIR / "temperature.csv"

# temperature(2).csv 이름도 지원
if not file_path.exists():
    file_path = BASE_DIR / "temperature(2).csv"

if not file_path.exists():
    st.error("temperature.csv 파일을 찾을 수 없습니다.")
    st.write("CSV 파일 위치:", BASE_DIR)
    st.info("CSV 파일을 pages 폴더의 상위 폴더에 넣어주세요.")
    st.stop()

# ------------------------------------
# 3. CSV 파일 불러오기
# ------------------------------------
df = None

for encoding in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
    try:
        df = pd.read_csv(file_path, encoding=encoding)
        break
    except UnicodeDecodeError:
        continue

if df is None:
    st.error("CSV 파일의 인코딩을 읽을 수 없습니다.")
    st.stop()

# ------------------------------------
# 4. 데이터 확인 및 전처리
# ------------------------------------
required_columns = ["일시", "평균기온(℃)"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일에 필요한 열이 없습니다.")
    st.write("현재 CSV 열 이름:", list(df.columns))
    st.stop()

# 날짜 변환
df["일시"] = pd.to_datetime(
    df["일시"],
    format="%b-%y",
    errors="coerce"
)

# 평균기온 숫자로 변환
df["평균기온(℃)"] = pd.to_numeric(
    df["평균기온(℃)"],
    errors="coerce"
)

# 결측치 제거
df = df.dropna(
    subset=["일시", "평균기온(℃)"]
).copy()

# 연도와 월 추출
df["연도"] = df["일시"].dt.year
df["월"] = df["일시"].dt.month

df = df.sort_values("일시")

if df.empty:
    st.error("분석할 수 있는 기온 데이터가 없습니다.")
    st.stop()

# ------------------------------------
# 5. 사용자 입력
# ------------------------------------
st.subheader("예측 조건 선택")

col1, col2 = st.columns(2)

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

latest_year = int(df["연도"].max())

with col1:
    selected_month = st.selectbox(
        "예측할 월을 선택하세요.",
        list(month_names.keys()),
        format_func=lambda x: month_names[x]
    )

with col2:
    prediction_year = st.number_input(
        "예측할 연도를 입력하세요.",
        min_value=latest_year + 1,
        max_value=2100,
        value=latest_year + 1,
        step=1
    )

prediction_year = int(prediction_year)

# ------------------------------------
# 6. 선택한 월의 데이터 추출
# ------------------------------------
month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.error("선형회귀 학습을 위해 최소 2개 이상의 데이터가 필요합니다.")
    st.stop()

X = month_df[["연도"]]
y = month_df["평균기온(℃)"]

# ------------------------------------
# 7. 선형회귀 알고리즘 학습
# ------------------------------------
model = LinearRegression()

model.fit(X, y)

# 미래 기온 예측
prediction = model.predict(
    pd.DataFrame({"연도": [prediction_year]})
)[0]

# 실제 데이터에 대한 예측값
fitted_values = model.predict(X)

# 기울기와 절편
slope = model.coef_[0]
intercept = model.intercept_

# 결정계수
r2 = model.score(X, y)

# ------------------------------------
# 8. 예측 결과 출력
# ------------------------------------
st.divider()

st.subheader(
    f"{prediction_year}년 {month_names[selected_month]} 평균기온 예측 결과"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "예측 평균기온",
        f"{prediction:.2f} ℃"
    )

with col2:
    st.metric(
        "학습 데이터 개수",
        f"{len(month_df)}개"
    )

with col3:
    st.metric(
        "결정계수 (R²)",
        f"{r2:.3f}"
    )

# ------------------------------------
# 9. 그래프 작성
# ------------------------------------
st.divider()

st.subheader("과거 평균기온 및 미래 예측 그래프")

fig = go.Figure()

# 실제 기온 데이터
fig.add_trace(
    go.Scatter(
        x=month_df["연도"],
        y=month_df["평균기온(℃)"],
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            color="royalblue",
            size=9
        )
    )
)

# 회귀선 데이터 생성
line_years = np.linspace(
    month_df["연도"].min(),
    prediction_year,
    200
)

line_predictions = model.predict(
    pd.DataFrame({"연도": line_years})
)

# 선형회귀 직선
fig.add_trace(
    go.Scatter(
        x=line_years,
        y=line_predictions,
        mode="lines",
        name="선형회귀 예측선",
        line=dict(
            color="red",
            width=3
        )
    )
)

# 실제 기온과 회귀선 사이의 오차
residual_x = []
residual_y = []

for year, actual, fitted in zip(
    month_df["연도"],
    month_df["평균기온(℃)"],
    fitted_values
):
    residual_x.extend([year, year, None])
    residual_y.extend([actual, fitted, None])

fig.add_trace(
    go.Scatter(
        x=residual_x,
        y=residual_y,
        mode="lines",
        name="예측 오차",
        line=dict(
            color="gray",
            width=1,
            dash="dash"
        ),
        opacity=0.6
    )
)

# 미래 예측 기온
fig.add_trace(
    go.Scatter(
        x=[prediction_year],
        y=[prediction],
        mode="markers+text",
        name="미래 예측 기온",
        marker=dict(
            color="orange",
            size=20,
            symbol="star",
            line=dict(
                color="black",
                width=1
            )
        ),
        text=[f"{prediction:.2f} ℃"],
        textposition="top center"
    )
)

# 예측 연도 표시
fig.add_vline(
    x=prediction_year,
    line_dash="dot",
    line_color="orange"
)

# 그래프 디자인
fig.update_layout(
    title=f"{month_names[selected_month]} 평균기온 변화 및 예측",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    hovermode="closest",
    template="plotly_white",
    height=600,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    )
)

fig.update_xaxes(
    showgrid=True,
    dtick=2
)

fig.update_yaxes(
    showgrid=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ------------------------------------
# 10. 선형회귀 알고리즘 설명
# ------------------------------------
st.divider()

st.subheader("선형회귀 알고리즘이란?")

st.write("""
선형회귀는 과거 데이터를 분석하여 변수 사이의 관계를
직선으로 나타내고 미래의 값을 예측하는 알고리즘입니다.

이번 프로그램에서는 과거 연도와 평균기온을 학습하여
미래의 평균기온을 예측합니다.
""")

st.latex(r"y = ax + b")

st.markdown("""
- x : 연도
- y : 평균기온
- a : 기울기 (연도에 따른 기온 변화량)
- b : 절편

빨간색 직선은 실제 데이터와의 오차 제곱합이
최소가 되도록 계산한 회귀선입니다.
""")

# ------------------------------------
# 11. 그래프 읽는 방법
# ------------------------------------
st.subheader("그래프 읽는 방법")

st.markdown("""
- 파란색 점 : 실제 과거 평균기온
- 빨간색 직선 : 선형회귀 알고리즘이 계산한 예측선
- 회색 점선 : 실제 기온과 예측선 사이의 오차
- 주황색 별 : 미래 예측 평균기온
""")

# ------------------------------------
# 12. 선형회귀 작동 과정
# ------------------------------------
st.subheader("선형회귀 알고리즘의 작동 과정")

st.write("""
1. 과거 연도와 평균기온 데이터를 수집합니다.
2. 데이터의 전체적인 변화 방향을 분석합니다.
3. 실제 데이터와 예측선 사이의 오차 제곱합이
   최소가 되는 직선을 찾습니다.
4. 완성된 직선을 이용하여 미래의 평균기온을 예측합니다.
""")

# ------------------------------------
# 13. 학습된 회귀식
# ------------------------------------
st.divider()

st.subheader("학습된 선형회귀 공식")

st.write(
    f"평균기온 = {slope:.4f} × 연도 + ({intercept:.4f})"
)

st.write(f"기울기: {slope:.4f}")

if slope > 0:
    st.write("분석 결과: 과거 데이터에서는 평균기온이 상승하는 경향이 있습니다.")
elif slope < 0:
    st.write("분석 결과: 과거 데이터에서는 평균기온이 하락하는 경향이 있습니다.")
else:
    st.write("분석 결과: 과거 데이터에서 뚜렷한 변화 경향이 없습니다.")

# ------------------------------------
# 14. 과거 데이터 확인
# ------------------------------------
with st.expander("선택한 월의 과거 기온 데이터 확인하기"):

    st.dataframe(
        month_df[["연도", "평균기온(℃)"]],
        use_container_width=True,
        hide_index=True
    )

# ------------------------------------
# 15. 주의사항
# ------------------------------------
st.info("""
기온은 계절, 강수량, 대기 상태 등 다양한 요인의 영향을 받습니다.
따라서 선형회귀로 계산한 미래 기온은 실제 기온과 차이가 발생할 수 있으며,
특히 먼 미래를 예측할수록 오차가 커질 수 있습니다.
""")

st.caption("서울 월별 평균기온 선형회귀 분석 프로그램")
