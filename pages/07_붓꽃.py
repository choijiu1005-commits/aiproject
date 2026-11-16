
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("붓꽃 품종 예측 프로그램")
st.write("꽃잎의 길이와 너비를 입력하면 붓꽃의 품종을 예측합니다.")

# CSV 파일 경로 찾기
base_dir = Path(__file__).resolve().parent

file_candidates = [
    base_dir / "Iris.csv",
    base_dir.parent / "Iris.csv"
]

csv_path = next(
    (p for p in file_candidates if p.exists()),
    None
)

if csv_path is None:
    st.error("Iris.csv 파일을 찾을 수 없습니다.")
    st.info("CSV 파일을 app.py와 같은 폴더 또는 상위 폴더에 넣어주세요.")
    st.stop()

# CSV 인코딩 처리
try:
    df = pd.read_csv(csv_path, encoding="cp949")
except UnicodeDecodeError:
    df = pd.read_csv(csv_path, encoding="utf-8-sig")

# 필요한 데이터 선택
X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

# KNN 분류 모델
# 표준화 후 가까운 5개 데이터를 이용해 분류
model = make_pipeline(
    StandardScaler(),
    KNeighborsClassifier(n_neighbors=5)
)

model.fit(X, y)

# 품종 한글 이름
species_names = {
    "Iris-setosa": "세토사 (Setosa)",
    "Iris-versicolor": "버시컬러 (Versicolor)",
    "Iris-virginica": "버지니카 (Virginica)"
}

# 입력 범위
petal_length_min = float(X["꽃잎 길이"].min())
petal_length_max = float(X["꽃잎 길이"].max())
petal_width_min = float(X["꽃잎 너비"].min())
petal_width_max = float(X["꽃잎 너비"].max())

st.subheader("꽃잎 정보 입력")

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "꽃잎 길이 (cm)",
        min_value=petal_length_min,
        max_value=petal_length_max,
        value=3.0,
        step=0.1,
        format="%.1f"
    )

with col2:
    petal_width = st.number_input(
        "꽃잎 너비 (cm)",
        min_value=petal_width_min,
        max_value=petal_width_max,
        value=1.0,
        step=0.1,
        format="%.1f"
    )

st.caption(
    f"꽃잎 길이: {petal_length_min}~{petal_length_max}cm / "
    f"꽃잎 너비: {petal_width_min}~{petal_width_max}cm"
)

# 예측 버튼
if st.button("붓꽃 품종 예측하기", type="primary"):

    input_data = pd.DataFrame({
        "꽃잎 길이": [petal_length],
        "꽃잎 너비": [petal_width]
    })

    prediction = model.predict(input_data)[0]

    st.success("품종 예측이 완료되었습니다!")

    st.subheader("예측 결과")

    st.markdown(
        f"## {species_names.get(prediction, prediction)}"
    )

    st.write(f"꽃잎 길이: {petal_length}cm")
    st.write(f"꽃잎 너비: {petal_width}cm")

    # 그래프
    st.subheader("꽃잎 길이와 너비 그래프")

    fig, ax = plt.subplots(figsize=(9, 6))

    # 기존 데이터 표시
    for species in df["품종"].unique():
        group = df[df["품종"] == species]

        ax.scatter(
            group["꽃잎 길이"],
            group["꽃잎 너비"],
            label=species_names.get(species, species),
            alpha=0.65,
            s=55
        )

    # 사용자가 입력한 값: 노란색 별
    ax.scatter(
        petal_length,
        petal_width,
        color="yellow",
        edgecolors="black",
        marker="*",
        s=400,
        label="사용자 입력값",
        zorder=5
    )

    ax.set_xlabel("꽃잎 길이 (cm)")
    ax.set_ylabel("꽃잎 너비 (cm)")
    ax.set_title("Iris Petal Data Visualization")

    ax.legend()
    ax.grid(True, alpha=0.3)

    st.pyplot(fig)
    plt.close(fig)

    st.info("그래프의 노란색 별이 사용자가 입력한 꽃잎 정보입니다.")

st.divider()

st.subheader("사용한 머신러닝 알고리즘")
st.write("KNN (K-Nearest Neighbors)")
st.write("표준화(StandardScaler) 후 가장 가까운 5개 데이터를 비교하여 품종을 분류합니다.")

