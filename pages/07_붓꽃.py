
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier


# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="붓꽃 품종 예측 AI",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 AI")
st.write(
    "꽃의 길이와 너비를 입력하면 머신러닝 알고리즘으로 "
    "붓꽃 품종을 예측하고 결과를 비교할 수 있습니다."
)


# =====================================
# 2. CSV 파일 불러오기
# =====================================

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
    st.stop()

try:
    df = pd.read_csv(csv_path, encoding="cp949")
except UnicodeDecodeError:
    df = pd.read_csv(csv_path, encoding="utf-8-sig")


# 영어 열 이름도 한글로 변환
column_mapping = {
    "SepalLengthCm": "꽃받침 길이",
    "SepalWidthCm": "꽃받침 너비",
    "PetalLengthCm": "꽃잎 길이",
    "PetalWidthCm": "꽃잎 너비",
    "Species": "품종",
    "sepal_length": "꽃받침 길이",
    "sepal_width": "꽃받침 너비",
    "petal_length": "꽃잎 길이",
    "petal_width": "꽃잎 너비",
    "species": "품종"
}

df.rename(columns=column_mapping, inplace=True)

required_columns = [
    "꽃받침 길이",
    "꽃받침 너비",
    "꽃잎 길이",
    "꽃잎 너비",
    "품종"
]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해주세요.")
    st.write("현재 CSV 열 이름:", list(df.columns))
    st.stop()

df = df[required_columns].copy()

for col in required_columns[:-1]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna().copy()


# =====================================
# 3. 품종 이름
# =====================================

species_names = {
    "Iris-setosa": "세토사 (Setosa)",
    "Iris-versicolor": "버시컬러 (Versicolor)",
    "Iris-virginica": "버지니카 (Virginica)"
}


# =====================================
# 4. 알고리즘 설명
# =====================================

algorithm_info = {

    "KNN": """
    **KNN (K-최근접 이웃)**

    입력한 데이터와 기존 데이터 사이의 거리를 계산합니다.

    가장 가까운 5개의 데이터를 찾고,
    가장 많이 나타난 품종을 예측합니다.

    특징: 주변 데이터의 영향을 받아 품종을 분류합니다.
    """,

    "SVM": """
    **SVM (서포트 벡터 머신)**

    서로 다른 품종을 가장 잘 구분할 수 있는
    결정 경계선을 찾는 알고리즘입니다.

    새로운 데이터가 어느 영역에 위치하는지 판단하여
    품종을 예측합니다.

    특징: 데이터 사이의 구분 경계를 학습합니다.
    """,

    "랜덤 포레스트": """
    **Random Forest (랜덤 포레스트)**

    여러 개의 결정 트리를 만들어 각각 예측하게 합니다.

    여러 트리의 예측 결과를 투표 방식으로 종합하여
    최종 품종을 결정합니다.

    특징: 여러 트리의 결과를 종합하는 앙상블 알고리즘입니다.
    """,

    "결정 트리": """
    **Decision Tree (결정 트리)**

    데이터를 특정 조건에 따라 여러 단계로 나눕니다.

    꽃잎과 꽃받침의 측정값을 기준으로
    가지를 나누면서 품종을 구분합니다.

    특징: 나무 모양의 조건을 따라 품종을 분류합니다.
    """
}


# =====================================
# 5. 머신러닝 모델 생성
# =====================================

def create_models():

    models = {

        "KNN": make_pipeline(
            StandardScaler(),
            KNeighborsClassifier(n_neighbors=5)
        ),

        "SVM": make_pipeline(
            StandardScaler(),
            SVC(kernel="rbf")
        ),

        "랜덤 포레스트": RandomForestClassifier(
            n_estimators=100,
            random_state=42
        ),

        "결정 트리": DecisionTreeClassifier(
            random_state=42
        )
    }

    return models


# =====================================
# 6. 예측 함수
# =====================================

def run_prediction(feature_columns, input_values):

    X = df[feature_columns]
    y = df["품종"]

    models = create_models()

    input_df = pd.DataFrame(
        [input_values],
        columns=feature_columns
    )

    results = {}
    fitted_models = {}

    for name, model in models.items():

        model.fit(X, y)

        prediction = model.predict(input_df)[0]

        results[name] = prediction
        fitted_models[name] = model

    return results, fitted_models


# =====================================
# 7. 2차원 그래프
# =====================================

def draw_2d_graph(input_values):

    fig, ax = plt.subplots(figsize=(9, 6))

    for species in df["품종"].unique():

        group = df[df["품종"] == species]

        ax.scatter(
            group["꽃잎 길이"],
            group["꽃잎 너비"],
            s=55,
            alpha=0.65,
            label=species_names.get(species, species)
        )

    # 사용자 입력값 노란색 별
    ax.scatter(
        input_values["꽃잎 길이"],
        input_values["꽃잎 너비"],
        color="yellow",
        edgecolors="black",
        marker="*",
        s=450,
        label="사용자 입력값",
        zorder=5
    )

    ax.set_xlabel("Petal Length (cm)")
    ax.set_ylabel("Petal Width (cm)")
    ax.set_title("Iris Petal Data Visualization")

    ax.legend()
    ax.grid(alpha=0.3)

    st.pyplot(fig)
    plt.close(fig)


# =====================================
# 8. 3차원 그래프
# =====================================

def draw_3d_graph(input_values):

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")

    for species in df["품종"].unique():

        group = df[df["품종"] == species]

        ax.scatter(
            group["꽃잎 길이"],
            group["꽃잎 너비"],
            group["꽃받침 너비"],
            s=45,
            alpha=0.6,
            label=species_names.get(species, species)
        )

    # 사용자 입력값 노란색 별
    ax.scatter(
        input_values["꽃잎 길이"],
        input_values["꽃잎 너비"],
        input_values["꽃받침 너비"],
        color="yellow",
        edgecolors="black",
        marker="*",
        s=450,
        label="사용자 입력값",
        depthshade=False
    )

    ax.set_xlabel("Petal Length (cm)")
    ax.set_ylabel("Petal Width (cm)")
    ax.set_zlabel("Sepal Width (cm)")

    ax.set_title("3D Iris Data Visualization")
    ax.legend()

    st.pyplot(fig)
    plt.close(fig)


# =====================================
# 9. 알고리즘별 결과 비교
# =====================================

def show_comparison(results, selected_algorithms):

    st.subheader("알고리즘별 품종 예측 결과 비교")

    comparison_data = []

    for name in selected_algorithms:

        prediction = results[name]

        comparison_data.append({
            "알고리즘": name,
            "예측 품종": species_names.get(
                prediction, prediction
            )
        })

    comparison_df = pd.DataFrame(comparison_data)

    # 표 출력
    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )

    # 세 알고리즘의 결과가 같은지 확인
    predictions = [
        results[name]
        for name in selected_algorithms
    ]

    if len(set(predictions)) == 1:

        st.success(
            "선택한 3개 알고리즘의 예측 결과가 모두 같습니다."
        )

        st.write(
            "공통 예측 품종: "
            + species_names.get(predictions[0], predictions[0])
        )

    else:

        st.warning(
            "알고리즘에 따라 예측 결과가 다릅니다."
        )

        st.write(
            "각 알고리즘의 예측 결과를 비교해 보세요."
        )

    # 예측 결과 빈도 그래프
    st.subheader("품종별 예측 결과 개수")

    result_counts = (
        comparison_df["예측 품종"]
        .value_counts()
    )

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.bar(
        result_counts.index,
        result_counts.values
    )

    ax.set_xlabel("Predicted Species")
    ax.set_ylabel("Number of Algorithms")
    ax.set_title("Algorithm Prediction Comparison")

    ax.set_ylim(0, 3.5)
    ax.grid(axis="y", alpha=0.3)

    st.pyplot(fig)
    plt.close(fig)


# =====================================
# 10. 예측 결과 전체 출력
# =====================================

def show_results(
    feature_columns,
    input_values,
    graph_type,
    selected_algorithms
):

    results, fitted_models = run_prediction(
        feature_columns,
        input_values
    )

    # ---------------------------------
    # 선택한 알고리즘 결과 비교
    # ---------------------------------

    show_comparison(
        results,
        selected_algorithms
    )

    st.divider()

    # ---------------------------------
    # 대표 예측 결과 선택
    # ---------------------------------

    st.subheader("대표 예측 결과")

    main_algorithm = st.selectbox(
        "대표 예측 결과로 확인할 알고리즘",
        selected_algorithms,
        key="main_" + graph_type
    )

    prediction = results[main_algorithm]

    st.success(
        f"{main_algorithm} 예측 결과: "
        f"{species_names.get(prediction, prediction)}"
    )

    # ---------------------------------
    # 입력값 확인
    # ---------------------------------

    st.subheader("사용자가 입력한 데이터")

    input_df = pd.DataFrame(
        [input_values]
    )

    st.dataframe(
        input_df,
        use_container_width=True,
        hide_index=True
    )

    # ---------------------------------
    # 그래프
    # ---------------------------------

    st.subheader("입력 데이터 시각화")

    if graph_type == "2D":

        draw_2d_graph(input_values)

    else:

        draw_3d_graph(input_values)

    st.info(
        "그래프의 노란색 별은 사용자가 입력한 데이터입니다."
    )

    # ---------------------------------
    # 알고리즘 작동 원리
    # ---------------------------------

    st.divider()

    st.subheader("머신러닝 알고리즘 작동 원리")

    st.write(
        "아래에서 선택한 3개 알고리즘의 "
        "작동 원리를 각각 확인할 수 있습니다."
    )

    for name in selected_algorithms:

        with st.expander(name + " 작동 원리"):

            st.markdown(algorithm_info[name])


# =====================================
# 11. 탭 구성
# =====================================

tab1, tab2 = st.tabs([
    "2가지 속성으로 예측",
    "3가지 속성으로 예측"
])


# =====================================
# 12. 첫 번째 탭
# 꽃잎 길이 + 꽃잎 너비
# =====================================

with tab1:

    st.header("꽃잎 정보로 품종 예측")

    st.write(
        "꽃잎 길이와 꽃잎 너비를 이용하여 "
        "붓꽃의 품종을 예측합니다."
    )

    col1, col2 = st.columns(2)

    with col1:

        petal_length = st.number_input(
            "꽃잎 길이 (cm)",
            min_value=float(df["꽃잎 길이"].min()),
            max_value=float(df["꽃잎 길이"].max()),
            value=3.0,
            step=0.1,
            key="petal_length_2"
        )

    with col2:

        petal_width = st.number_input(
            "꽃잎 너비 (cm)",
            min_value=float(df["꽃잎 너비"].min()),
            max_value=float(df["꽃잎 너비"].max()),
            value=1.0,
            step=0.1,
            key="petal_width_2"
        )

    st.caption(
        f"꽃잎 길이: {df['꽃잎 길이'].min()}~"
        f"{df['꽃잎 길이'].max()}cm | "
        f"꽃잎 너비: {df['꽃잎 너비'].min()}~"
        f"{df['꽃잎 너비'].max()}cm"
    )

    st.divider()

    algorithms_2 = st.multiselect(
        "비교할 알고리즘 3개를 선택하세요.",
        options=list(algorithm_info.keys()),
        default=["KNN", "SVM", "랜덤 포레스트"],
        max_selections=3,
        key="algorithms_2"
    )

    if len(algorithms_2) != 3:

        st.warning("비교를 위해 알고리즘을 정확히 3개 선택해주세요.")

    if st.button(
        "2가지 속성으로 품종 예측하기",
        type="primary",
        key="predict_2"
    ):

        if len(algorithms_2) != 3:

            st.error("알고리즘 3개를 선택해야 합니다.")

        else:

            input_values = {
                "꽃잎 길이": petal_length,
                "꽃잎 너비": petal_width
            }

            show_results(
                ["꽃잎 길이", "꽃잎 너비"],
                input_values,
                "2D",
                algorithms_2
            )


# =====================================
# 13. 두 번째 탭
# 꽃받침 너비 + 꽃잎 길이 + 꽃잎 너비
# =====================================

with tab2:

    st.header("3가지 속성으로 품종 예측")

    st.write(
        "꽃받침 너비를 추가하여 "
        "총 3가지 속성으로 붓꽃 품종을 예측합니다."
    )

    st.info(
        "추가 속성: 꽃받침 너비"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        sepal_width = st.number_input(
            "꽃받침 너비 (cm)",
            min_value=float(df["꽃받침 너비"].min()),
            max_value=float(df["꽃받침 너비"].max()),
            value=3.0,
            step=0.1,
            key="sepal_width_3"
        )

    with col2:

        petal_length_3 = st.number_input(
            "꽃잎 길이 (cm)",
            min_value=float(df["꽃잎 길이"].min()),
            max_value=float(df["꽃잎 길이"].max()),
            value=3.0,
            step=0.1,
            key="petal_length_3"
        )

    with col3:

        petal_width_3 = st.number_input(
            "꽃잎 너비 (cm)",
            min_value=float(df["꽃잎 너비"].min()),
            max_value=float(df["꽃잎 너비"].max()),
            value=1.0,
            step=0.1,
            key="petal_width_3"
        )

    st.caption(
        f"꽃받침 너비: {df['꽃받침 너비'].min()}~"
        f"{df['꽃받침 너비'].max()}cm | "
        f"꽃잎 길이: {df['꽃잎 길이'].min()}~"
        f"{df['꽃잎 길이'].max()}cm | "
        f"꽃잎 너비: {df['꽃잎 너비'].min()}~"
        f"{df['꽃잎 너비'].max()}cm"
    )

    st.divider()

    algorithms_3 = st.multiselect(
        "비교할 알고리즘 3개를 선택하세요.",
        options=list(algorithm_info.keys()),
        default=["KNN", "SVM", "랜덤 포레스트"],
        max_selections=3,
        key="algorithms_3"
    )

    if len(algorithms_3) != 3:

        st.warning("비교를 위해 알고리즘을 정확히 3개 선택해주세요.")

    if st.button(
        "3가지 속성으로 품종 예측하기",
        type="primary",
        key="predict_3"
    ):

        if len(algorithms_3) != 3:

            st.error("알고리즘 3개를 선택해야 합니다.")

        else:

            input_values = {
                "꽃받침 너비": sepal_width,
                "꽃잎 길이": petal_length_3,
                "꽃잎 너비": petal_width_3
            }

            show_results(
                [
                    "꽃받침 너비",
                    "꽃잎 길이",
                    "꽃잎 너비"
                ],
                input_values,
                "3D",
                algorithms_3
            )


# =====================================
# 14. 하단 데이터 정보
# =====================================

st.divider()

st.subheader("데이터 및 알고리즘 정보")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "전체 데이터 수",
        f"{len(df)}개"
    )

    st.write("학습 데이터: Iris.csv")

with col2:

    st.metric(
        "분류 품종 수",
        f"{df['품종'].nunique()}개"
    )

    st.write(
        "분류 대상: Setosa, Versicolor, Virginica"
    )

st.write(
    "사용 알고리즘: KNN, SVM, 랜덤 포레스트, 결정 트리"
)

st.caption(
    "본 프로그램은 Iris 데이터를 활용한 머신러닝 학습용 프로그램입니다."
)
