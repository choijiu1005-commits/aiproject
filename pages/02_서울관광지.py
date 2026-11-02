

import pandas as pd
import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(
    page_title="서울 인기 관광지 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

st.title("서울 인기 관광지 TOP 10")
st.write(
    "외국인 관광객들이 즐겨 찾는 서울의 대표 관광지를 지도에서 확인해 보세요!"
)

# 관광지 데이터
spots = [
    {
        "rank": 1,
        "name": "명동",
        "lat": 37.5636,
        "lon": 126.9869,
        "category": "쇼핑 · 먹거리",
        "description": "화장품 쇼핑과 길거리 음식, 다양한 브랜드 매장이 모여 있는 서울의 대표 관광지입니다."
    },
    {
        "rank": 2,
        "name": "N서울타워",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "전망 · 랜드마크",
        "description": "남산 정상 부근에서 서울의 아름다운 전경을 감상할 수 있는 대표 랜드마크입니다."
    },
    {
        "rank": 3,
        "name": "코엑스 · 별마당도서관",
        "lat": 37.5116,
        "lon": 127.0594,
        "category": "쇼핑 · 문화",
        "description": "대형 쇼핑몰과 전시 공간이 있으며, 높은 책장으로 유명한 별마당도서관도 있습니다."
    },
    {
        "rank": 4,
        "name": "강남역",
        "lat": 37.4979,
        "lon": 127.0276,
        "category": "쇼핑 · 도심",
        "description": "패션 매장과 맛집, 카페가 밀집한 서울의 대표적인 번화가입니다."
    },
    {
        "rank": 5,
        "name": "홍대 거리",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "K-컬처 · 공연",
        "description": "개성 있는 상점과 카페, 거리 공연 등 젊은 문화와 K-컬처를 즐길 수 있습니다."
    },
    {
        "rank": 6,
        "name": "경복궁",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "역사 · 문화",
        "description": "조선 시대의 대표 궁궐로 한국의 전통 건축과 역사를 경험할 수 있습니다."
    },
    {
        "rank": 7,
        "name": "동대문디자인플라자",
        "lat": 37.5671,
        "lon": 127.0095,
        "category": "건축 · 전시",
        "description": "독특한 곡선형 건축물로 유명하며 전시와 디자인 행사를 즐길 수 있습니다."
    },
    {
        "rank": 8,
        "name": "광장시장",
        "lat": 37.5700,
        "lon": 126.9997,
        "category": "전통시장 · 먹거리",
        "description": "빈대떡과 다양한 한국 길거리 음식을 맛볼 수 있는 서울의 대표 전통시장입니다."
    },
    {
        "rank": 9,
        "name": "북촌한옥마을",
        "lat": 37.5826,
        "lon": 126.9830,
        "category": "전통 · 문화",
        "description": "전통 한옥이 모여 있는 동네로 한국의 옛 주거 문화를 느낄 수 있습니다."
    },
    {
        "rank": 10,
        "name": "성수동",
        "lat": 37.5445,
        "lon": 127.0560,
        "category": "카페 · 팝업스토어",
        "description": "개성 있는 카페와 편집숍, 팝업스토어가 많아 트렌디한 서울을 경험하기 좋습니다."
    }
]

# 데이터프레임 생성
df = pd.DataFrame(spots)

# 지도 만들기
st.subheader("서울 관광지 지도")

seoul_map = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# 지도에 관광지 표시
for spot in spots:

    popup_text = f"""
    <div style="width:220px">
        <h4>TOP {spot['rank']}. {spot['name']}</h4>
        <p>{spot['category']}</p>
        <p>{spot['description']}</p>
    </div>
    """

    folium.Marker(
        location=[spot["lat"], spot["lon"]],
        tooltip=f"TOP {spot['rank']} · {spot['name']}",
        popup=folium.Popup(popup_text, max_width=280),
        icon=folium.Icon(
            color="red" if spot["rank"] <= 3 else "blue",
            icon="info-sign"
        )
    ).add_to(seoul_map)

# 지도 화면 출력
st_folium(
    seoul_map,
    width=None,
    height=570,
    use_container_width=True
)

# 관광지 설명
st.divider()
st.subheader("서울 관광지 TOP 10 소개")

for start in range(0, len(spots), 2):

    columns = st.columns(2)

    for column, spot in zip(columns, spots[start:start + 2]):

        with column:

            st.markdown(
                f"### {spot['rank']}. {spot['name']}"
            )

            st.caption(spot["category"])

            st.write(spot["description"])

            st.divider()

# 자료 안내
st.subheader("자료 참고")

st.write(
    "서울시 외국인 관광객 방문 분석과 서울의 대표 관광 명소를 "
    "참고하여 구성한 소개용 관광지 목록입니다. "
    "공식 단일 관광지 순위는 아닙니다."
)

st.markdown(
    "[서울시 외국인 관광객 분석 자료 바로가기]"
    "(https://english.seoul.go.kr/from-k-culture-to-k-hiking-foreign-tourists-venture-beyond-seouls-top-attractions/)"
)

st.caption(
    "※ 지도는 인터넷 연결이 필요하며, 관광지 좌표는 대표 위치입니다."
)
