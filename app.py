import streamlit as st
from datetime import date, datetime, timedelta, time
from korean_lunar_calendar import KoreanLunarCalendar
from openai import OpenAI
import calendar as cal
import os
import requests

# ==================== 페이지 설정 ====================
st.set_page_config(
    page_title="물때 선상낚시 도우미",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌊 물때 선상낚시 도우미")
st.caption("지역·월별 물때 달력 + 실측 날씨 + ChatGPT 추천 어종 + 낚시 조언")

# ==================== 지역 좌표 (날씨용) ====================
REGION_COORDS = {
    "인천": (37.4563, 126.7052),
    "평택": (36.9921, 127.1129),
    "보령": (36.3334, 126.6128),
    "군산": (35.9677, 126.7369),
    "목포": (34.8118, 126.3922),
    "속초": (38.2070, 128.5918),
    "강릉": (37.7519, 128.8761),
    "울진": (36.9931, 129.4004),
    "포항": (36.0190, 129.3435),
    "울산": (35.5384, 129.3114),
    "통영": (34.8544, 128.4331),
    "거제": (34.8806, 128.6211),
    "여수": (34.7604, 127.6622),
    "완도": (34.3118, 126.7550),
    "제주": (33.4996, 126.5312),
}

# ==================== secrets / OpenAI ====================
def get_openai_client():
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", "")
        if not api_key or str(api_key).startswith("sk-여기에"):
            return None

        # 로컬 SSL 문제가 있을 때만 우회 (클라우드에서는 기본 검증 사용)
        use_insecure = False
        try:
            use_insecure = bool(st.secrets.get("SSL_INSECURE", False))
        except Exception:
            pass

        if use_insecure or os.environ.get("SSL_INSECURE") == "1":
            import httpx
            return OpenAI(api_key=api_key, http_client=httpx.Client(verify=False))
        return OpenAI(api_key=api_key)
    except Exception:
        return None


# ==================== 사이드바 ====================
with st.sidebar:
    st.header("⚙️ 설정")

    today = date.today()
    year = st.number_input("연도", min_value=2024, max_value=2030, value=today.year)
    month = st.number_input("월", min_value=1, max_value=12, value=today.month)

    st.divider()

    sea_area = st.selectbox("해역 선택", ["서해", "동해", "남해"])
    region_options = {
        "서해": ["인천", "평택", "보령", "군산", "목포"],
        "동해": ["속초", "강릉", "울진", "포항", "울산"],
        "남해": ["통영", "거제", "여수", "완도", "제주"],
    }
    region = st.selectbox("세부 지역", region_options[sea_area])

    st.divider()

    client = get_openai_client()
    if client:
        st.success("✅ OpenAI API 키 로드됨")
        if st.button("API 연결 테스트", key="test_api"):
            with st.spinner("테스트 중..."):
                try:
                    models = client.models.list()
                    st.success(f"✅ 연결 성공! (모델 {len(list(models.data))}개)")
                except Exception as e:
                    st.error(f"❌ 연결 실패: {type(e).__name__}: {e}")
                    st.caption("로컬 SSL 문제면 secrets.toml에 SSL_INSECURE = true 추가")
    else:
        st.warning("⚠️ secrets에 OPENAI_API_KEY를 설정해주세요")

    st.info("💡 달력 날짜를 누르면 상세 정보가 나와요!")


# ==================== 물때 계산 ====================
def get_lunar_day(solar_year: int, solar_month: int, solar_day: int):
    calendar = KoreanLunarCalendar()
    if not calendar.setSolarDate(solar_year, solar_month, solar_day):
        return None
    lunar_str = calendar.LunarIsoFormat()
    try:
        parts = lunar_str.replace(" Intercalation", "").split("-")
        return int(parts[2])
    except Exception:
        return None


def get_mul_ttae(lunar_day: int, sea: str) -> str:
    if lunar_day is None:
        return "알 수 없음"
    if sea == "서해":
        mapping = {
            1: "7물", 2: "8물", 3: "9물", 4: "10물", 5: "11물", 6: "12물", 7: "13물",
            8: "조금", 9: "무시", 10: "1물", 11: "2물", 12: "3물", 13: "4물", 14: "5물", 15: "6물",
            16: "7물", 17: "8물", 18: "9물", 19: "10물", 20: "11물", 21: "12물", 22: "13물",
            23: "조금", 24: "무시", 25: "1물", 26: "2물", 27: "3물", 28: "4물", 29: "5물", 30: "6물",
        }
    else:
        mapping = {
            1: "8물", 2: "9물", 3: "10물", 4: "11물", 5: "12물", 6: "13물", 7: "14물",
            8: "조금", 9: "1물", 10: "2물", 11: "3물", 12: "4물", 13: "5물", 14: "6물", 15: "7물",
            16: "8물", 17: "9물", 18: "10물", 19: "11물", 20: "12물", 21: "13물", 22: "14물",
            23: "조금", 24: "1물", 25: "2물", 26: "3물", 27: "4물", 28: "5물", 29: "6물", 30: "7물",
        }
    return mapping.get(lunar_day, "알 수 없음")


def get_mul_type(mul: str) -> str:
    if mul in ["7물", "8물", "9물", "10물"]:
        return "사리"
    if mul in ["조금", "무시"]:
        return "조금"
    return "중간"


def get_tidal_range_cm(mul_type: str, sea: str) -> str:
    base = {
        "사리": {"서해": (350, 550), "동해": (30, 60), "남해": (150, 280)},
        "중간": {"서해": (200, 350), "동해": (20, 45), "남해": (80, 180)},
        "조금": {"서해": (80, 180), "동해": (10, 30), "남해": (40, 100)},
    }
    low, high = base.get(mul_type, {}).get(sea, (50, 150))
    return f"약 {low}~{high} cm"


def estimate_tide_times(mul_type: str) -> dict:
    """음력/물때 유형 기반 대략적인 만조·간조 시각 추정."""
    if mul_type == "사리":
        return {
            "만조": ["05:40", "18:10"],
            "간조": ["00:10", "12:20"],
            "비고": "사리 — 조류가 강한 편",
        }
    if mul_type == "조금":
        return {
            "만조": ["06:30", "18:50"],
            "간조": ["00:50", "13:10"],
            "비고": "조금 — 조류가 약한 편",
        }
    return {
        "만조": ["06:00", "18:30"],
        "간조": ["00:30", "12:50"],
        "비고": "중간 물때",
    }


# ==================== 시즌 참고 데이터 ====================
def get_seasonal_reference(sea: str, month: int) -> str:
    data = {
        "서해": {
            1: "우럭, 광어, 노래미", 2: "우럭, 광어, 노래미", 3: "우럭, 광어, 도다리",
            4: "광어, 우럭, 도다리, 주꾸미", 5: "광어, 우럭, 농어, 주꾸미",
            6: "광어, 우럭, 농어, 갑오징어", 7: "광어, 우럭, 농어, 갑오징어",
            8: "광어, 우럭, 농어, 갑오징어", 9: "주꾸미, 갑오징어, 광어, 우럭",
            10: "주꾸미, 갑오징어, 광어, 우럭", 11: "우럭, 광어, 노래미", 12: "우럭, 광어, 노래미",
        },
        "동해": {
            1: "볼락, 열기, 대구", 2: "볼락, 열기, 대구", 3: "볼락, 열기, 가자미",
            4: "볼락, 열기, 가자미, 방어", 5: "볼락, 열기, 방어, 참돔",
            6: "방어, 참돔, 볼락, 열기", 7: "방어, 부시리, 참돔",
            8: "방어, 부시리, 참돔", 9: "방어, 참돔, 볼락",
            10: "볼락, 열기, 방어", 11: "볼락, 열기, 대구", 12: "볼락, 열기, 대구",
        },
        "남해": {
            1: "볼락, 감성돔, 참돔", 2: "볼락, 감성돔, 참돔", 3: "감성돔, 참돔, 볼락, 도다리",
            4: "감성돔, 참돔, 농어, 한치", 5: "참돔, 감성돔, 농어, 한치",
            6: "한치, 참돔, 농어, 부시리", 7: "한치, 부시리, 참돔, 농어",
            8: "한치, 부시리, 참돔", 9: "참돔, 감성돔, 농어, 갑오징어",
            10: "감성돔, 참돔, 갑오징어, 볼락", 11: "감성돔, 볼락, 참돔", 12: "볼락, 감성돔, 참돔",
        },
    }
    return data.get(sea, {}).get(month, "광어, 우럭, 참돔")


# ==================== ChatGPT 추천 ====================
def recommend_fish_by_gpt(client, date_str: str, region: str, sea: str, mul: str, month: int) -> list:
    seasonal_ref = get_seasonal_reference(sea, month)
    if client is None:
        return [f.strip() for f in seasonal_ref.split(",")][:3]
    try:
        prompt = f"""
당신은 한국 바다 선상낚시 전문 조황 분석가입니다.

[출조 조건]
- 날짜: {date_str}
- 지역: {region} ({sea})
- 물때: {mul}
- 월: {month}월

[시즌 참고 데이터]
{seasonal_ref}

시즌 참고 데이터를 우선 반영하고, 물때·지역 특성을 고려해
선상낚시 대표 어종 3가지만 추천하세요.

형식만 출력:
어종1, 어종2, 어종3
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "한국 바다낚시 조황 전문가. 형식만 정확히 답변."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=50,
            temperature=0.5,
            timeout=30,
        )
        text = response.choices[0].message.content.strip()
        fishes = [f.strip() for f in text.replace("、", ",").split(",") if f.strip()]
        return fishes[:3] if fishes else [f.strip() for f in seasonal_ref.split(",")][:3]
    except Exception as e:
        st.warning(f"어종 추천 API 오류: {type(e).__name__}: {e}")
        return [f.strip() for f in seasonal_ref.split(",")][:3]


def get_llm_advice(client, date_str: str, region: str, sea: str, mul: str, fishes: list) -> str:
    if client is None:
        return "⚠️ secrets에 OpenAI API Key를 설정하면 ChatGPT 조언을 받을 수 있어요."
    try:
        prompt = f"""
한국 바다낚시 전문가로서 초보 조사에게 반말로 조언해.

날짜: {date_str}
지역: {region} ({sea})
물때: {mul}
추천 어종: {', '.join(fishes)}

포함 내용:
1) 이 물때에 이 어종이 좋은 이유
2) 어종별 핵심 기법 1~2가지 (채비·포인트·시간)
3) 출조 시 주의점

400자 이내, 핵심만.
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "친절하고 실용적인 한국 바다낚시 전문가."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=600,
            temperature=0.7,
            timeout=30,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ LLM 오류: {type(e).__name__}: {e}"


# ==================== 날씨 (Open-Meteo, 키 불필요) ====================
@st.cache_data(ttl=1800)
def fetch_weather(lat: float, lon: float, target_date: str) -> dict:
    """Open-Meteo 일별 예보 + 해양(파고) 정보"""
    result = {"ok": False, "msg": "", "out_of_range": False}
    try:
        # 예보 가능 범위 체크 (Open-Meteo는 대략 16일)
        try:
            target = date.fromisoformat(target_date)
        except Exception:
            target = None
        if target is not None:
            delta_days = (target - date.today()).days
            if delta_days > 16:
                result["out_of_range"] = True
                result["msg"] = "날씨 예보는 오늘 기준 최대 16일까지 지원됩니다. 더 가까운 날짜를 선택해 주세요."
                return result
            if delta_days < -5:
                # 너무 과거도 예보 API 범위 밖
                result["out_of_range"] = True
                result["msg"] = "선택한 날짜는 예보 범위를 벗어났습니다. 오늘부터 16일 이내 날짜를 선택해 주세요."
                return result

        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
            "windspeed_10m_max,winddirection_10m_dominant,weathercode"
            "&timezone=Asia%2FSeoul"
            f"&start_date={target_date}&end_date={target_date}"
        )
        r = requests.get(url, timeout=10)
        if r.status_code == 400:
            result["out_of_range"] = True
            result["msg"] = "날씨 예보는 오늘 기준 최대 16일까지 지원됩니다. 더 가까운 날짜를 선택해 주세요."
            return result
        r.raise_for_status()
        daily = r.json().get("daily", {})

        marine_url = (
            "https://marine-api.open-meteo.com/v1/marine"
            f"?latitude={lat}&longitude={lon}"
            "&daily=wave_height_max,wave_direction_dominant,wave_period_max"
            "&timezone=Asia%2FSeoul"
            f"&start_date={target_date}&end_date={target_date}"
        )
        mr = requests.get(marine_url, timeout=10)
        marine = {}
        if mr.status_code == 200:
            marine = mr.json().get("daily", {})

        weather_codes = {
            0: "맑음", 1: "대체로 맑음", 2: "구름 조금", 3: "흐림",
            45: "안개", 48: "서리 안개",
            51: "이슬비", 61: "비", 63: "비", 65: "강한 비",
            71: "눈", 80: "소나기", 95: "뇌우",
        }
        code = (daily.get("weathercode") or [0])[0]
        result.update({
            "ok": True,
            "tmax": (daily.get("temperature_2m_max") or [None])[0],
            "tmin": (daily.get("temperature_2m_min") or [None])[0],
            "rain": (daily.get("precipitation_sum") or [0])[0],
            "wind": (daily.get("windspeed_10m_max") or [None])[0],
            "wind_dir": (daily.get("winddirection_10m_dominant") or [None])[0],
            "sky": weather_codes.get(code, f"코드 {code}"),
            "wave": (marine.get("wave_height_max") or [None])[0],
            "wave_period": (marine.get("wave_period_max") or [None])[0],
        })
        return result
    except Exception as e:
        err = str(e)
        if "400" in err or "Bad Request" in err:
            result["out_of_range"] = True
            result["msg"] = "날씨 예보는 오늘 기준 최대 16일까지 지원됩니다. 더 가까운 날짜를 선택해 주세요."
        else:
            result["msg"] = err
        return result


def wind_dir_text(deg) -> str:
    if deg is None:
        return "-"
    dirs = ["북", "북동", "동", "남동", "남", "남서", "서", "북서"]
    return dirs[int((deg + 22.5) // 45) % 8]


# ==================== 선상24 링크 ====================
def sunsang24_link(region: str, fish: str = "") -> str:
    """선상24는 공개 검색 API가 없어 메인으로 연결."""
    return "https://www.sunsang24.com/"


# ==================== 메인 달력 ====================
month_days = cal.monthcalendar(year, month)
month_name = f"{year}년 {month}월"
weekday_names = ["월", "화", "수", "목", "금", "토", "일"]

st.subheader(f"📅 {month_name} 물때 달력  ({sea_area} · {region})")

cols = st.columns(7)
for i, day_name in enumerate(weekday_names):
    cols[i].markdown(
        f"<div style='text-align:center;font-weight:700;padding:4px 0;color:#555;'>{day_name}</div>",
        unsafe_allow_html=True,
    )

selected_day = st.session_state.get("selected_day")

for week in month_days:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day == 0:
                st.write("")
                continue

            lunar_day = get_lunar_day(year, month, day)
            mul = get_mul_ttae(lunar_day, sea_area)
            mul_type = get_mul_type(mul)
            range_cm = get_tidal_range_cm(mul_type, sea_area)
            d = date(year, month, day)
            wd = weekday_names[d.weekday()]
            is_selected = selected_day == day

            # 카드 정보 전부 버튼 라벨에 (한 번 클릭)
            label = f"{day}일({wd})\n{mul}\n{range_cm}"
            if st.button(label, key=f"day_{year}_{month}_{day}", use_container_width=True):
                st.session_state["selected_day"] = day
                st.session_state["selected_mul"] = mul
                st.session_state["selected_mul_type"] = mul_type
                st.session_state["selected_range"] = range_cm
                st.session_state["selected_date_str"] = f"{year}-{month:02d}-{day:02d}"
                st.session_state.pop("selected_fishes", None)
                st.session_state.pop("last_advice", None)
                st.rerun()

            color_bar = {
                "사리": "#e85d4c",
                "중간": "#43a047",
                "조금": "#1e88e5",
            }.get(mul_type, "#9e9e9e")
            st.markdown(
                f"<div style='height:4px;border-radius:2px;background:{color_bar};margin-top:-6px;margin-bottom:8px;'></div>",
                unsafe_allow_html=True,
            )


# ==================== 상세 ====================
if st.session_state.get("selected_day"):
    st.divider()
    day = st.session_state["selected_day"]
    mul = st.session_state.get("selected_mul", "")
    mul_type = st.session_state.get("selected_mul_type", "")
    range_cm = st.session_state.get("selected_range", "")
    date_str = st.session_state.get("selected_date_str", "")

    st.subheader(f"📌 {date_str} 상세 정보")

    tide_est = estimate_tide_times(mul_type)
    c1, c2, c3 = st.columns(3)
    c1.metric("물때", f"{mul} ({mul_type})")
    c2.metric("고저차(조차)", range_cm)
    note = tide_est["비고"].split("—")[-1].strip() if "—" in tide_est["비고"] else tide_est["비고"]
    c3.metric("조류 경향", note)

    st.markdown(
        f"**추정 만조**: {', '.join(tide_est['만조'])} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"**추정 간조**: {', '.join(tide_est['간조'])}"
    )
    st.caption("※ 만조·간조 시각은 물때 유형 기반 추정값입니다. 정확한 값은 국립해양조사원 조위 API 연동 시 대체됩니다.")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 🐟 추천 어종")
        if "selected_fishes" not in st.session_state:
            with st.spinner("시즌 데이터 + ChatGPT 추천 중..."):
                fishes = recommend_fish_by_gpt(client, date_str, region, sea_area, mul, month)
                st.session_state["selected_fishes"] = fishes
        else:
            fishes = st.session_state["selected_fishes"]

        if st.button("🔄 다시 추천받기", key="refresh_fish"):
            with st.spinner("다시 추천 중..."):
                fishes = recommend_fish_by_gpt(client, date_str, region, sea_area, mul, month)
                st.session_state["selected_fishes"] = fishes
                st.rerun()

        fish_icons = {
            "광어": "🐟", "우럭": "🐠", "참돔": "🐡", "농어": "🎣",
            "주꾸미": "🐙", "갑오징어": "🦑", "한치": "🦑", "볼락": "🐟",
            "감성돔": "🐡", "방어": "🐟", "부시리": "🐟", "돌돔": "🐡",
            "열기": "🐠", "가자미": "🐟", "노래미": "🐠", "도다리": "🐟", "대구": "🐟",
        }
        for fish in fishes:
            icon = fish_icons.get(fish, "🐟")
            link = sunsang24_link(region, fish)
            st.markdown(
                f"""
                <a href="{link}" target="_blank" style="text-decoration:none;">
                  <div style="
                    display:flex;align-items:center;gap:10px;
                    background:linear-gradient(145deg,#f0f7ff,#fff);
                    border:1.5px solid #90caf9;border-radius:10px;
                    padding:10px 14px;margin-bottom:8px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.08);
                    color:#1565c0;font-weight:600;font-size:15px;">
                    <span style="font-size:22px;">{icon}</span>
                    <span>{fish}</span>
                    <span style="margin-left:auto;font-size:12px;color:#888;">선상24 →</span>
                  </div>
                </a>
                """,
                unsafe_allow_html=True,
            )

        st.link_button("선상24 전체 예약 페이지", sunsang24_link(region), use_container_width=True)

    with col2:
        st.markdown("### 🤖 ChatGPT 낚시 조언")
        if st.button("상세 조언 받기", type="primary"):
            with st.spinner("조언 생성 중..."):
                st.session_state["last_advice"] = get_llm_advice(
                    client, date_str, region, sea_area, mul, fishes
                )
        if "last_advice" in st.session_state:
            st.markdown(st.session_state["last_advice"])
        else:
            st.info("버튼을 누르면 이 날짜·물때에 맞는 낚시 기법을 알려줘요.")

    # ==================== 날씨 ====================
    st.divider()
    st.markdown("### 🌤️ 해당일 날씨 / 해상 정보")

    lat, lon = REGION_COORDS.get(region, (37.5, 127.0))
    weather = fetch_weather(lat, lon, date_str)

    if weather.get("ok"):
        w1, w2, w3, w4 = st.columns(4)
        w1.metric("하늘", weather.get("sky", "-"))
        tmax, tmin = weather.get("tmax"), weather.get("tmin")
        w2.metric("기온", f"{tmin:.0f}~{tmax:.0f}°C" if tmax is not None and tmin is not None else "-")
        rain = weather.get("rain") or 0
        w3.metric("강수", f"{rain:.1f} mm")
        wind = weather.get("wind")
        w4.metric(
            "최대풍속",
            f"{wind:.1f} m/s ({wind_dir_text(weather.get('wind_dir'))})" if wind is not None else "-",
        )

        wave = weather.get("wave")
        if wave is not None:
            period = weather.get("wave_period")
            extra = f" / 주기 {period:.0f}초" if period else ""
            st.markdown(f"**파고(최대)**: 약 **{wave:.1f} m**{extra}")
        st.caption(f"출처: Open-Meteo · 기준 좌표 {region} ({lat:.2f}, {lon:.2f})")
    else:
        msg = weather.get("msg") or "날씨 정보를 불러오지 못했어요."
        if weather.get("out_of_range"):
            st.info(f"ℹ️ {msg}")
        else:
            st.warning(f"날씨 정보를 불러오지 못했어요. ({msg})")

    st.markdown(f"[🗺️ Windy에서 {region} 해상 날씨 보기](https://www.windy.com/{lat}/{lon})")


# ==================== 하단 ====================
st.divider()
st.markdown("""
**참고**
- OpenAI 키: Streamlit secrets (`OPENAI_API_KEY`)
- 로컬에서 SSL 오류 시 secrets에 `SSL_INSECURE = true` 추가
- 물때·조차·만조/간조 시각은 음력·유형 기반 추정 (추후 국립해양조사원 API로 교체 가능)
- 날씨·파고: Open-Meteo (무료, 키 불필요)
- 선상24: 공식 공개 API 없음 → 사이트 연결
""")
