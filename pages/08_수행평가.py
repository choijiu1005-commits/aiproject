
import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import time
import html

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="서울 디저트 지도 TOP 10",
    page_icon="🥐",
    layout="wide"
)

# ==========================================
# 2. 전체 디자인
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #fffaf3;
}

.block-container {
    max-width: 1600px;
    padding-top: 2rem;
}

h1, h2, h3 {
    color: #68452f;
}

.hero {
    background: linear-gradient(120deg, #f4d9bc, #fff0df);
    padding: 30px;
    border-radius: 22px;
    margin-bottom: 20px;
    border: 1px solid #ead2b8;
}

.dessert-card {
    background: white;
    border: 1px solid #ead9c8;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 12px;
}

div[data-testid="stMetric"] {
    background: white;
    border-radius: 15px;
    padding: 15px;
    border: 1px solid #ead9c8;
}

/* 빵 이모티콘 애니메이션 */
.falling-food {
    position: fixed !important;
    top: -100px;
    z-index: 999999 !important;
    pointer-events: none !important;
    user-select: none;
    display: block;
    opacity: 0.42;
    animation-name: food-fall;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
}

@keyframes food-fall {
    0% {
        transform: translateY(-100px) rotate(0deg);
    }

    100% {
        transform: translateY(115vh) rotate(360deg);
    }
}

/* 지도 마커 디자인 */
.map-marker {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    background: #a96c45;
    color: white;
    border: 3px solid white;
    box-shadow: 0 3px 10px rgba(0,0,0,0.35);
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 19px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. 빵 이모티콘 낙하 효과
# ==========================================

st.markdown("""
<div class="falling-food"
style="left:3%;font-size:42px;animation-duration:14s;animation-delay:-4s;">
🥐
</div>

<div class="falling-food"
style="left:12%;font-size:35px;animation-duration:19s;animation-delay:-12s;">
🍞
</div>

<div class="falling-food"
style="left:22%;font-size:40px;animation-duration:16s;animation-delay:-8s;">
🍪
</div>

<div class="falling-food"
style="left:32%;font-size:34px;animation-duration:21s;animation-delay:-15s;">
🥨
</div>

<div class="falling-food"
style="left:42%;font-size:43px;animation-duration:17s;animation-delay:-5s;">
🥯
</div>

<div class="falling-food"
style="left:53%;font-size:36px;animation-duration:20s;animation-delay:-11s;">
🧁
</div>

<div class="falling-food"
style="left:63%;font-size:42px;animation-duration:15s;animation-delay:-7s;">
🥐
</div>

<div class="falling-food"
style="left:73%;font-size:38px;animation-duration:22s;animation-delay:-17s;">
🍩
</div>

<div class="falling-food"
style="left:83%;font-size:40px;animation-duration:18s;animation-delay:-9s;">
🍪
</div>

<div class="falling-food"
style="left:94%;font-size:35px;animation-duration:20s;animation-delay:-13s;">
🍞
</div>
""", unsafe_allow_html=True)


# ==========================================
# 4. 디저트 매장 TOP 10
# ==========================================

stores = [
    {
        "rank": 1,
        "name": "플러피 베이크샵",
        "area": "마포구 공덕동",
        "address": "서울특별시 마포구 백범로31길 8",
        "search": "8 Baekbeom-ro 31-gil, Mapo-gu, Seoul, South Korea",
        "menu": "마들렌, 휘낭시에, 까눌레",
        "description": "다양한 마들렌과 휘낭시에를 즐길 수 있는 구움과자 중심 매장입니다.",
        "price": "약 3,000원대부터 (변동 가능)"
    },
    {
        "rank": 2,
        "name": "르솔레이",
        "area": "용산구 한남동",
        "address": "서울특별시 용산구 한남동 683-6",
        "search": "683-6 Hannam-dong, Yongsan-gu, Seoul, South Korea",
        "menu": "마들렌, 휘낭시에, 까눌레",
        "description": "프랑스풍 구움과자와 다양한 디저트를 선보이는 매장입니다.",
        "price": "매장 메뉴 확인"
    },
    {
        "rank": 3,
        "name": "리틀빅토리",
        "area": "마포구 연남동",
        "address": "서울특별시 마포구 연희로1길 41",
        "search": "41 Yeonhui-ro 1-gil, Mapo-gu, Seoul, South Korea",
        "menu": "마들렌, 휘낭시에, 까눌레, 마카롱",
        "description": "프랑스풍 구움과자를 중심으로 디저트를 선보이는 파티세리입니다.",
        "price": "매장 메뉴 확인"
    },
    {
        "rank": 4,
        "name": "패션5",
        "area": "용산구 한남동",
        "address": "서울특별시 용산구 이태원로 272",
        "search": "272 Itaewon-ro, Yongsan-gu, Seoul, South Korea",
        "menu": "케이크, 타르트, 페이스트리",
        "description": "다양한 프리미엄 디저트와 파티세리 메뉴를 만날 수 있는 디저트 명소입니다.",
        "price": "메뉴별 상이"
    },
    {
        "rank": 5,
        "name": "청수당 베이커리",
        "area": "종로구 익선동",
        "address": "서울특별시 종로구 돈화문로11나길 31-9",
        "search": "31-9 Donhwamun-ro 11na-gil, Jongno-gu, Seoul, South Korea",
        "menu": "카스텔라, 약과, 구움 디저트",
        "description": "한옥 분위기에서 한국식 디저트와 베이커리 메뉴를 즐길 수 있습니다.",
        "price": "메뉴별 상이"
    },
    {
        "rank": 6,
        "name": "카페 레이어드 북촌",
        "area": "종로구 북촌",
        "address": "서울특별시 종로구 북촌로2길 2-3",
        "search": "2-3 Bukchon-ro 2-gil, Jongno-gu, Seoul, South Korea",
        "menu": "스콘, 케이크, 구움 디저트",
        "description": "다양한 맛의 스콘과 케이크를 즐길 수 있는 디저트 카페입니다.",
        "price": "메뉴별 상이"
    },
    {
        "rank": 7,
        "name": "블렌디 스튜디오",
        "area": "강남구 역삼동",
        "address": "서울특별시 강남구 강남대로48길 25",
        "search": "25 Gangnam-daero 48-gil, Gangnam-gu, Seoul, South Korea",
        "menu": "파르 브르통, 까눌레",
        "description": "프랑스식 구움 디저트 메뉴를 찾아볼 수 있는 디저트 스튜디오입니다.",
        "price": "메뉴별 상이"
    },
    {
        "rank": 8,
        "name": "소나",
        "area": "강남구 신사동",
        "address": "서울특별시 강남구 강남대로162길 40",
        "search": "40 Gangnam-daero 162-gil, Gangnam-gu, Seoul, South Korea",
        "menu": "프렌치 디저트",
        "description": "섬세한 플레이팅과 프렌치 스타일 디저트로 알려진 공간입니다.",
        "price": "메뉴별 상이"
    },
    {
        "rank": 9,
        "name": "마얘",
        "area": "서초구 서래마을",
        "address": "서울특별시 서초구 사평대로22길 14",
        "search": "14 Sapyeong-daero 22-gil, Seocho-gu, Seoul, South Korea",
        "menu": "프렌치 케이크, 타르트, 마카롱",
        "description": "프랑스풍 파티세리 디저트를 즐길 수 있는 디저트 숍입니다.",
        "price": "메뉴별 상이"
    },
    {
        "rank": 10,
        "name": "카페 노티드 청담",
        "area": "강남구 청담동",
        "address": "서울특별시 강남구 도산대로53길 15",
        "search": "15 Dosan-daero 53-gil, Gangnam-gu, Seoul, South Korea",
        "menu": "크림 도넛, 베이커리 디저트",
        "description": "다양한 크림 도넛과 달콤한 베이커리 디저트로 유명한 브랜드입니다.",
        "price": "메뉴별 상이"
    }
]


# ==========================================
# 5. 주소를 위도와 경도로 변환
# ==========================================

@st.cache_data(ttl=604800, show_spinner=False)
def get_locations(addresses):

    geolocator = Nominatim(
        user_agent="seoul_dessert_map_app"
    )

    results = []

    for address in addresses:

        try:
            location = geolocator.geocode(
                address,
                timeout=15
            )

            if location:
                results.append((
                    location.latitude,
                    location.longitude
                ))
            else:
                results.append(None)

        except Exception:
            results.append(None)

        time.sleep(1.1)

    return results


# ==========================================
# 6. 메인 제목
# ==========================================

st.markdown("""
<div class="hero">

<h1>서울 디저트 지도 TOP 10</h1>

<h3>Seoul Dessert Map</h3>

<p>
서울에서 인기 있는 디저트 매장을 지도에서 찾아보세요!
</p>

<p>
지도 마커를 누르면 매장 정보를 확인할 수 있어요.
</p>

</div>
""", unsafe_allow_html=True)


col1, col2, col3 = st.columns(3)

col1.metric("추천 매장", "10곳")
col2.metric("지역", "서울")
col3.metric("지도", "Folium")


st.info(
    "TOP 10은 공식 매출 순위가 아닌 추천 목록입니다. "
    "주소, 메뉴 및 영업 정보는 방문 전 확인해 주세요."
)


# ==========================================
# 7. 검색 기능
# ==========================================

st.subheader("디저트 매장 검색")

col1, col2 = st.columns([2, 1])

with col1:

    keyword = st.text_input(
        "매장 이름 또는 메뉴 검색",
        placeholder="예: 마들렌, 휘낭시에, 노티드"
    )

with col2:

    areas = ["전체"] + sorted(
        list(set(item["area"] for item in stores))
    )

    selected_area = st.selectbox(
        "지역 선택",
        areas
    )


filtered = []

for item in stores:

    search_text = (
        item["name"]
        + item["area"]
        + item["menu"]
        + item["description"]
    )

    if keyword.lower() not in search_text.lower():
        continue

    if selected_area != "전체":
        if item["area"] != selected_area:
            continue

    filtered.append(item)


# ==========================================
# 8. 매장 좌표 불러오기
# ==========================================

st.markdown("---")

st.header("서울 디저트 매장 위치")

st.write(
    "아래 지도에서 숫자가 적힌 큰 마커를 클릭해 보세요."
)

with st.spinner("매장 위치를 불러오는 중입니다..."):

    locations = get_locations(
        tuple(item["search"] for item in stores)
    )


for item, location in zip(stores, locations):

    if location:

        item["lat"] = location[0]
        item["lon"] = location[1]

    else:

        item["lat"] = None
        item["lon"] = None


# ==========================================
# 9. 큰 Folium 지도 만들기
# ==========================================

m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=11,
    tiles="OpenStreetMap",
    control_scale=True
)

valid_locations = []

for item in filtered:

    if item["lat"] is None:
        continue

    valid_locations.append([
        item["lat"],
        item["lon"]
    ])

    name = html.escape(item["name"])
    area = html.escape(item["area"])
    menu = html.escape(item["menu"])
    description = html.escape(item["description"])
    address = html.escape(item["address"])

    # 큰 번호 마커
    marker_html = f"""
    <div class="map-marker">
        {item['rank']}
    </div>
    """

    icon = folium.DivIcon(
        html=marker_html,
        icon_size=(46, 46),
        icon_anchor=(23, 23)
    )

    # 마커를 클릭했을 때 나타나는 정보
    popup_html = f"""
    <div style="
        width:280px;
        font-family:sans-serif;
        line-height:1.6;
        padding:5px;
    ">

        <h2 style="color:#805B40;">
        TOP {item['rank']}
        </h2>

        <h3>{name}</h3>

        <hr>

        <b>지역</b><br>
        {area}

        <br><br>

        <b>대표 메뉴</b><br>
        {menu}

        <br><br>

        <b>주소</b><br>
        {address}

        <br><br>

        <b>매장 소개</b><br>
        {description}

    </div>
    """

    folium.Marker(
        location=[
            item["lat"],
            item["lon"]
        ],
        tooltip=f"TOP {item['rank']} · {item['name']}",
        popup=folium.Popup(
            popup_html,
            max_width=350
        ),
        icon=icon
    ).add_to(m)


# 매장 위치가 화면 안에 들어오도록 자동 확대
if valid_locations:

    m.fit_bounds(
        valid_locations,
        padding=(55, 55)
    )


# ==========================================
# 10. 지도 크게 출력
# ==========================================

st_folium(
    m,
    width=1400,
    height=850,
    returned_objects=[],
    use_container_width=True
)

st.caption(
    f"현재 지도에 표시된 매장: {len(valid_locations)}곳"
)

if len(valid_locations) < len(filtered):

    st.warning(
        "일부 매장의 주소를 찾지 못했습니다. "
        "주소 검색 서비스의 응답을 확인해 주세요."
    )


# ==========================================
# 11. 지도 아래 디저트 매장 설명
# ==========================================

st.markdown("---")

st.header("서울 디저트 매장 TOP 10")

st.write(
    "각 매장을 눌러 대표 메뉴와 매장 특징을 확인해 보세요."
)


for item in filtered:

    with st.expander(
        f"TOP {item['rank']} | {item['name']} · {item['area']}"
    ):

        st.markdown(
            f"### {item['name']}"
        )

        st.write(
            "**대표 메뉴:**",
            item["menu"]
        )

        st.write(
            "**매장 소개:**",
            item["description"]
        )

        st.write(
            "**주소:**",
            item["address"]
        )

        st.write(
            "**가격:**",
            item["price"]
        )

        if item["lat"] is not None:

            map_url = (
                "https://www.google.com/maps/search/?api=1&query="
                + str(item["lat"])
                + ","
                + str(item["lon"])
            )

            st.link_button(
                "구글 지도에서 위치 확인",
                map_url
            )


# ==========================================
# 12. 하단 안내
# ==========================================

st.markdown("---")

st.markdown("""
<div style="
    text-align:center;
    color:#927963;
    padding:25px;
">

<h2>SEOUL DESSERT MAP</h2>

<p>
달콤한 디저트와 함께하는 서울 탐방
</p>

<p>
지도: OpenStreetMap / Folium
</p>

</div>
""", unsafe_allow_html=True)
