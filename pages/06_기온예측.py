
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from pathlib import Path

# --------------------------------
# 1. 페이지 설정
# --------------------------------
st.set_page_config(
    page_title="서울 월별 기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("서울 월별 평균기온 예측")
st.write("과거 기온 데이터를 학습하여 미래의 평균기온을 예측합니다.")

# --------------------------------
# 2. CSV 파일 경로 설정
# --------------------------------
# 현재 py 파일은 pages 폴더 안에 있음
# CSV 파일은 pages 폴더의 상위 폴더에 있음

BASE_DIR = Path(__file__).resolve().parent.parent

file_path = BASE_DIR / "temperature.csv"

# 파일 존재 여부 확인
if not file_path.exists():
    st.error(f"CSV 파일을 찾을 수 없습니다: {file_path}")
    st.info("temperature.csv 파일을 pages 폴더의 상위 폴더에 넣어주세요.")
    st.stop()

# --------------------------------
# 3. CSV 데이터 불러오기
# --------------------------------
df = None

for encoding in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
    try:
        df = pd.read_csv(file_path, encoding=encoding)
        break
    except UnicodeDecodeError:
        continue

if df is None:
    st.error("CSV 파일의 인코딩을 확인해주세요.")
    st.stop()

# --------------------------------
# 4. 데이터 전처리
# --------------------------------
if "일시" not in df.columns or "평균기온(℃)" not in df.columns:
    st.error("CSV 파일에 일시 또는 평균기온(℃) 열이 없습니다.")
    st.write("현재 CSV 열 이름:", list(df.columns))
    st.stop()

df["일시"] = pd.to_datetime(
    df["일시"],
    errors="coerce"
)

df["평균기온(℃)"] = pd.to_numeric(
    df["평균기온(℃)"],
    errors="coerce"
)

df = df.dropna(
    subset=["일시", "평균기온(℃)"]
).copy()

df["연도"] = df["일시"].dt.year
df["월"] = df["일시"].dt.month

df = df.sort_values("일시")

if df.empty:
    st.error("분석할 수 있는 데이터가 없습니다.")
    st.stop()

# --------------------------------
# 5. 월과 예측 연도 선택
# --------------------------------
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

# --------------------------------
# 6. 선택한 월의 데이터 추출
# --------------------------------
month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.error("선형회귀 학습에는 최소 2개 이상의 데이터가 필요합니다.")
    st.stop()

X = month_df[["연도"]]
y = month_df["평균기온(℃)"]

# --------------------------------
# 7. 선형회귀 모델 학습
# --------------------------------
model = LinearRegression()

model.fit(X, y)

# 미래 기온 예측
prediction = model.predict(
    pd.DataFrame({"연도": [prediction_year]})
)[0]

# 기울기와 절편
slope = model.coef_[0]
intercept = model.intercept_

# 결정계수
r2 = model.score(X, y)

# --------------------------------
# 8. 예측 결과 출력
# --------------------------------
st.divider()

st.subheader(
    f"{prediction_year}년 {month_names[selected_month]} 평균기온 예측"
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
        "결정계수 R²",
        f"{r2:.3f}"
    )

# --------------------------------
# 9. 그래프 작성
# --------------------------------
st.subheader("과거 기온 및 미래 예측 그래프")

# 한글 폰트 설정
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(12, 6))

# 실제 기온 데이터
ax.scatter(
    month_df["연도"],
    month_df["평균기온(℃)"],
    color="blue",
    s=55,
    label="실제 평균기온",
    zorder=3
)

# 회귀선에 사용할 연도
line_years = np.linspace(
    month_df["연도"].min(),
    prediction_year,
    200
)

line_df = pd.DataFrame({
    "연도": line_years
})

line_predictions = model.predict(line_df)

# 선형회귀 직선
ax.plot(
    line_years,
    line_predictions,
    color="red",
    linewidth=2.5,
    label="선형회귀 예측선"
)

# 실제 기온과 회귀선의 오차
fitted_values = model.predict(X)

ax.vlines(
    month_df["연도"],
    month_df["평균기온(℃)"],
    fitted_values,
    color="gray",
    alpha=0.4,
    linestyle="dashed",
    label="예측 오차"
)

# 미래 예측 기온
ax.scatter(
    prediction_year,
    prediction,
    color="orange",
    marker="*",
    s=350,
    edgecolors="black",
    label="미래 예측 기온",
    zorder=5
)

# 예측값 표시
ax.annotate(
    f"{prediction:.2f} ℃",
    (prediction_year, prediction),
    xytext=(10, 15),
    textcoords="offset points",
    fontsize=11,
    fontweight="bold"
)

# 그래프 설정
ax.set_title(
    f"{month_names[selected_month]} 평균기온 변화 및 예측",
    fontsize=16
)

ax.set_xlabel("연도", fontsize=12)
ax.set_ylabel("평균기온 (℃)", fontsize=12)

ax.grid(True, alpha=0.3)
ax.legend()

fig.tight_layout()

st.pyplot(fig)

plt.close(fig)

# --------------------------------
# 10. 선형회귀 알고리즘 설명
# --------------------------------
st.divider()

st.subheader("선형회귀 알고리즘이란?")

st.write("""
선형회귀는 과거 데이터를 이용하여 변수 사이의 관계를
직선으로 나타내고 미래의 값을 예측하는 알고리즘입니다.

이번 프로그램에서는 연도와 평균기온의 관계를 학습하여
미래의 평균기온을 예측합니다.
""")

st.latex(r"y = ax + b")

st.markdown("""
- x : 연도
- y : 평균기온
- a : 기울기 (연도에 따른 기온 변화량)
- b : 절편

빨간색 직선은 실제 데이터와의 오차 제곱합이
최소가 되도록 계산된 회귀선입니다.
""")

st.subheader("그래프 읽는 방법")

st.markdown("""
- 파란색 점 : 실제 과거 평균기온
- 빨간색 직선 : 선형회귀 예측선
- 회색 점선 : 실제 기온과 예측선의 차이
- 주황색 별 : 미래 예측 평균기온
""")

st.subheader("선형회귀 알고리즘의 작동 과정")

st.write("""
1. 과거 연도와 평균기온 데이터를 수집합니다.
2. 데이터의 전체적인 변화 방향을 분석합니다.
3. 실제 데이터와 예측선 사이의 오차 제곱합이
   최소가 되는 직선을 찾습니다.
4. 완성된 직선을 이용해 미래 기온을 예측합니다.
""")

st.info("""
주의: 실제 기온은 다양한 기후 요인의 영향을 받습니다.
따라서 선형회귀로 계산한 결과는 실제 미래 기온과
차이가 발생할 수 있습니다.
""")

# --------------------------------
# 11. 과거 데이터 확인
# --------------------------------
with st.expander("선택한 월의 과거 기온 데이터 확인하기"):

    st.dataframe(
        month_df[["연도", "평균기온(℃)"]],
        use_container_width=True,
        hide_index=True
    )

# --------------------------------
# 12. 회귀식 출력
# --------------------------------
st.subheader("학습된 선형회귀 공식")

st.write(
    f"평균기온 = {slope:.4f} × 연도 + ({intercept:.4f})"
)

st.caption("서울 월별 평균기온 선형회귀 분석 프로그램")

