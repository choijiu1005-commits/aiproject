
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import streamlit.components.v1 as components
import time
import html

# --------------------------------
# 1. 기본 페이지 설정
# --------------------------------

st.set_page_config(
    page_title="서울 구움과자 지도",
    page_icon="🍪",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: #FFFDF9;
}
h1, h2, h3 {
    color: #684B38;
}
.store-card {
    background-color: #FFF6EB;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 10px;
}
.small-text {
    color: #806D5D;
    font-size: 14px;
}
div[data-testid="stMetric"] {
    background: #FFF6EB;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------
# 2. 서울 디저트 가게 TOP 10 자료
# --------------------------------

stores = [
    {
        "rank": 1,
        "name": "플러피 베이크샵",
        "english": "Fluffy Bakeshop",
        "area": "공덕",
        "address": "서울특별시 마포구 백범로31길 8 "
                   "2동 상가 1층 106호",
        "geo_address": "2동 106호, 8 Baekbeom-ro 31-gil, "
                       "Mapo-gu, Seoul, South Korea",
        "menu": "휘낭시에, 마들렌, 까눌레",
        "signature": "무화과 휘낭시에, 레몬 마들렌, 바닐라 까눌레",
        "price": "약 3,000~3,600원대",
        "description": "다양한 종류의 마들렌과 휘낭시에, "
                       "까눌레를 판매하는 구움과자 전문점입니다.",
        "hours": "평일 08:00~18:30 / 주말 11:00~16:30",
        "color": "red"
    },
    {
        "rank": 2,
        "name": "연희동오븐",
        "english": "Yeonhui-dong Oven",
        "area": "연희동",
        "address": "서울특별시 서대문구 연희로11나길 7-5 지하 1층",
        "geo_address": "7-5 Yeonhui-ro 11na-gil, "
                       "Seodaemun-gu, Seoul, South Korea",
        "menu": "휘낭시에, 마들렌, 파운드케이크, 티그레",
        "signature": "클래식 휘낭시에, 감태 휘낭시에, "
                     "우지말차 크럼블 마들렌",
        "price": "약 3,400~3,900원대",
        "description": "고메버터를 활용한 휘낭시에와 "
                       "다양한 풍미의 마들렌을 만날 수 있습니다.",
        "hours": "목~토 11:00~19:00",
        "color": "blue"
    },
    {
        "rank": 3,
        "name": "리틀빅토리",
        "english": "Little Victory",
        "area": "연남동",
        "address": "서울특별시 마포구 연희로1길 41",
        "geo_address": "41 Yeonhui-ro 1-gil, "
                       "Mapo-gu, Seoul, South Korea",
        "menu": "마들렌, 휘낭시에, 까눌레, 마카롱",
        "signature": "아몬드 솔티드 카라멜 휘낭시에",
        "price": "매장 확인 필요",
        "description": "프랑스식 파티세리 스타일의 "
                       "작은 구움과자 전문점입니다.",
        "hours": "방문 전 최신 영업시간 확인",
        "color": "green"
    },
    {
        "rank": 4,
        "name": "르솔레이",
        "english": "LE SOLEIL",
        "area": "한남동",
        "address": "서울특별시 용산구 한남동 683-6",
        "geo_address": "683-6 Hannam-dong, "
                       "Yongsan-gu, Seoul, South Korea",
        "menu": "마들렌, 휘낭시에",
        "signature": "로즈 리치 마들렌, 누룽 마들렌",
        "price": "매장 확인 필요",
        "description": "다양한 재료와 조합을 활용한 "
                       "프랑스풍 구움과자를 선보이는 디저트 가게입니다.",
        "hours": "매일 12:00~20:00 (변동 가능)",
        "color": "purple"
    },
    {
        "rank": 5,
        "name": "미드미",
        "english": "Midme",
        "area": "서촌",
        "address": "서울특별시 종로구 자하문로 36",
        "geo_address": "36 Jahamun-ro, "
                       "Jongno-gu, Seoul, South Korea",
        "menu": "마들렌, 까눌레, 휘낭시에",
        "signature": "레몬 마들렌, 감태 휘낭시에",
        "price": "매장 확인 필요",
        "description": "프랑스풍 디저트와 독특한 재료를 "
                       "활용한 구움과자를 판매합니다.",
        "hours": "매일 11:00~20:00 (변동 가능)",
        "color": "orange"
    },
    {
        "rank": 6,
        "name": "구움양과",
        "english": "Guwoomyanggwa",
        "area": "을지로",
        "address": "서울특별시 중구 을지로 157",
        "geo_address": "157 Eulji-ro, Jung-gu, "
                       "Seoul, South Korea",
        "menu": "구움과자",
        "signature": "매장 당일 메뉴 확인",
        "price": "매장 확인 필요",
        "description": "세운상가 인근에 위치한 "
                       "구움과자 전문 디저트 매장입니다.",
        "hours": "매일 11:00~21:00 (변동 가능)",
        "color": "cadetblue"
    },
    {
        "rank": 7,
        "name": "비스퀴테리 산",
        "english": "Biscuiterie San",
        "area": "성산동",
        "address": "서울특별시 마포구 월드컵북로 121-8 "
                   "동산빌딩 1층 101호",
        "geo_address": "121-8 World Cup buk-ro, "
                       "Mapo-gu, Seoul, South Korea",
        "menu": "쿠키, 프랑스식 구움과자",
        "signature": "클래식 쿠키와 구움과자",
        "price": "매장 확인 필요",
        "description": "좋은 재료와 기본에 충실한 "
                       "프랑스풍 구움과자를 만드는 디저트 숍입니다.",
        "hours": "월~일 10:00~16:00 (변동 가능)",
        "color": "darkblue"
    },
    {
        "rank": 8,
        "name": "오흐뒤구떼",
        "english": "Heure du Gouter",
        "area": "연남동",
        "address": "서울특별시 마포구 동교로47길 10",
        "geo_address": "10 Donggyo-ro 47-gil, "
                       "Mapo-gu, Seoul, South Korea",
        "menu": "마들렌, 휘낭시에, 티그레, 파운드",
        "signature": "프렌치 스타일 구움과자",
        "price": "매장 확인 필요",
        "description": "다양한 종류의 프랑스풍 구움과자를 "
                       "선보이는 파티세리입니다.",
        "hours": "방문 전 영업시간 확인",
        "color": "pink"
    },
    {
        "rank": 9,
        "name": "마들마들",
        "english": "Madeul Madeul",
        "area": "압구정",
        "address": "서울특별시 강남구 압구정로42길 36 101호",
        "geo_address": "36 Apgujeong-ro 42-gil, "
                       "Gangnam-gu, Seoul, South Korea",
        "menu": "마들렌, 휘낭시에",
        "signature": "다양한 맛의 마들렌",
        "price": "매장 확인 필요",
        "description": "다양한 맛의 마들렌과 휘낭시에를 "
                       "판매하는 구움과자 매장입니다.",
        "hours": "매일 10:00~20:00 (변동 가능)",
        "color": "darkred"
    },
    {
        "rank": 10,
        "name": "안녕과자점",
        "english": "Hello Cookie Shop",
        "area": "샤로수길",
        "address": "서울특별시 관악구 남부순환로228길 20 1층",
        "geo_address": "20 Nambusunhwan-ro 228-gil, "
                       "Gwanak-gu, Seoul, South Korea",
        "menu": "휘낭시에, 까눌레, 마들렌",
        "signature": "크림치즈 휘낭시에, 무화과 휘낭시에",
        "price": "휘낭시에 약 2,500~2,700원",
        "description": "매일 직접 만드는 다양한 종류의 "
                       "구움과자를 판매하는 테이크아웃 전문점입니다.",
        "hours": "수~일 13:00~21:00",
        "color": "darkgreen"
    }
]


# --------------------------------
# 3. 주소를 위도와 경도로 변환
# --------------------------------

@st.cache_data(ttl=604800, show_spinner=False)
def get_store_locations(addresses):

    geolocator = Nominatim(
        user_agent="seoul_baked_dessert_map_jiwoo"
    )

    results = []

    for address in addresses:

        try:
            location = geolocator.geocode(
                address,
                timeout=15
            )

            if location:
                results.append({
                    "latitude": location.latitude,
                    "longitude": location.longitude
                })
            else:
                results.append(None)

        except (
            GeocoderTimedOut,
            GeocoderUnavailable,
            Exception
        ):
            results.append(None)

        # Nominatim 이용 정책에 맞춰 요청 간격 유지
        time.sleep(1.1)

    return results


# --------------------------------
# 4. 제목 및 소개
# --------------------------------

st.title("서울 구움과자 지도")
st.markdown(
    "서울에서 만날 수 있는 특별한 구움과자 디저트 가게를 찾아보세요."
)

st.markdown("---")

col1, col2, col3 = st.columns(3)

col1.metric("추천 매장", "TOP 10")
col2.metric("지역", "서울")
col3.metric("주요 디저트", "구움과자")

st.markdown("---")


# --------------------------------
# 5. 검색 및 지역 필터
# --------------------------------

st.subheader("디저트 가게 찾기")

search = st.text_input(
    "매장 이름 또는 디저트 메뉴 검색",
    placeholder="예: 휘낭시에, 마들렌, 연희동"
)

areas = ["전체"] + sorted(
    list(set(store["area"] for store in stores))
)

selected_area = st.selectbox(
    "지역 선택",
    areas
)

filtered_stores = []

for store in stores:

    search_text = (
        store["name"]
        + store["area"]
        + store["menu"]
        + store["signature"]
        + store["description"]
    )

    if search.lower() not in search_text.lower():
        continue

    if selected_area != "전체":
        if store["area"] != selected_area:
            continue

    filtered_stores.append(store)


# --------------------------------
# 6. 지도 위치 불러오기
# --------------------------------

st.subheader("서울 구움과자 매장 위치")

addresses = tuple(
    store["geo_address"] for store in stores
)

with st.spinner("서울 디저트 매장의 위치를 검색하고 있어요..."):

    locations = get_store_locations(addresses)

for i, store in enumerate(stores):
    store["latitude"] = (
        locations[i]["latitude"]
        if locations[i] else None
    )

    store["longitude"] = (
        locations[i]["longitude"]
        if locations[i] else None
    )


# --------------------------------
# 7. Folium 지도 만들기
# --------------------------------

m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=11,
    tiles="OpenStreetMap"
)

marker_cluster = MarkerCluster().add_to(m)

mapped_count = 0

for store in filtered_stores:

    if store["latitude"] is None:
        continue

    # HTML에 삽입되는 문자열 안전 처리
    name = html.escape(store["name"])
    menu = html.escape(store["menu"])
    signature = html.escape(store["signature"])
    area = html.escape(store["area"])
    address = html.escape(store["address"])
    description = html.escape(store["description"])

    popup_html = f"""
    <div style="width:270px; font-family:sans-serif;">

        <h3 style="color:#805B40;">
            {name}
        </h3>

        <hr>

        <b>추천 번호</b> : TOP {store["rank"]}<br>
        <b>지역</b> : {area}<br>
        <b>대표 메뉴</b> : {menu}<br>
        <b>추천 메뉴</b> : {signature}<br>

        <hr>

        <b>매장 소개</b><br>
        {description}

        <hr>

        <b>주소</b><br>
        {address}

        <br><br>

        <a href="https://www.google.com/maps/search/?api=1&query="
        target="_blank">
        </a>

        <a href="https://map.naver.com/p/search/{store['name']}"
        target="_blank">
        네이버 지도에서 보기
        </a>

    </div>
    """

    folium.Marker(
        location=[
            store["latitude"],
            store["longitude"]
        ],
        tooltip=store["name"],
        popup=folium.Popup(
            popup_html,
            max_width=350
        ),
        icon=folium.Icon(
            color=store["color"],
            icon="gift",
            prefix="fa"
        )
    ).add_to(marker_cluster)

    mapped_count += 1


# 지도 출력

st_folium(
    m,
    width=1200,
    height=650,
    returned_objects=[]
)

st.caption(
    f"현재 검색 조건에 해당하는 매장 중 "
    f"{mapped_count}곳의 위치를 지도에 표시했습니다."
)

if mapped_count < len(filtered_stores):
    st.warning(
        "일부 매장의 주소를 지도에서 찾지 못했습니다. "
        "주소를 확인하거나 잠시 후 다시 시도해 주세요."
    )


# --------------------------------
# 8. 디저트 가게 상세 정보
# --------------------------------

st.markdown("---")

st.subheader("디저트 가게 상세 정보")

if filtered_stores:

    selected_store_name = st.selectbox(
        "상세 정보를 확인할 매장",
        [store["name"] for store in filtered_stores]
    )

    selected_store = next(
        store for store in filtered_stores
        if store["name"] == selected_store_name
    )

    st.markdown(
        f"""
        <div class="store-card">

        <h2>{selected_store['name']}</h2>

        <p class="small-text">
        {selected_store['english']}
        </p>

        <h4>TOP {selected_store['rank']}</h4>

        <p>
        <b>지역:</b> {selected_store['area']}
        </p>

        <p>
        <b>주소:</b> {selected_store['address']}
        </p>

        <p>
        <b>대표 메뉴:</b> {selected_store['menu']}
        </p>

        <p>
        <b>추천 메뉴:</b> {selected_store['signature']}
        </p>

        <p>
        <b>가격 정보:</b> {selected_store['price']}
        </p>

        <p>
        <b>영업시간:</b> {selected_store['hours']}
        </p>

        <hr>

        <p>
        <b>매장 소개</b><br>
        {selected_store['description']}
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    if selected_store["latitude"] is not None:

        map_url = (
            "https://www.google.com/maps/search/?api=1&query="
            + str(selected_store["latitude"])
            + ","
            + str(selected_store["longitude"])
        )

        st.link_button(
            "구글 지도로 위치 확인하기",
            map_url
        )

else:

    st.info("검색 조건에 해당하는 매장이 없습니다.")


# --------------------------------
# 9. 전체 매장 목록
# --------------------------------

st.markdown("---")

st.subheader("서울 구움과자 매장 TOP 10 목록")

for store in filtered_stores:

    with st.expander(
        f"TOP {store['rank']} | {store['name']} ({store['area']})"
    ):

        st.write("**대표 메뉴:**", store["menu"])
        st.write("**추천 메뉴:**", store["signature"])
        st.write("**주소:**", store["address"])
        st.write("**특징:**", store["description"])

        if store["latitude"] is not None:

            st.write(
                "**지도 좌표:**",
                store["latitude"],
                store["longitude"]
            )


# --------------------------------
# 10. 하단 안내
# --------------------------------

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#8B735F;">

    <h4>SEOUL BAKED DESSERT MAP</h4>

    서울의 다양한 구움과자를 만나보세요.

    <p>본 앱은 디저트 가게 정보 탐색을 위한 추천 지도입니다.</p>

    <p>메뉴, 가격, 영업시간은 매장 사정에 따라 달라질 수 있습니다.</p>

    </div>
    """,
    unsafe_allow_html=True
)

