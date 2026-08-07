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
st.caption("지역·월별 물때 달력 + 실측 날씨 + AI 추천 어종 + 낚시 조언")


# 모바일 대응 CSS
st.markdown("""
<style>
/* 전체 여백 줄이기 */
.block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 900px; }

/* 버튼 텍스트 크기·줄간격 (달력용) */
div.stButton > button {
  white-space: pre-line !important;
  line-height: 1.25 !important;
  font-size: 0.85rem !important;
  padding: 0.45rem 0.35rem !important;
  min-height: 2.8rem !important;
}

/* 사이드바 모바일 */
section[data-testid="stSidebar"] { min-width: 220px; }

@media (max-width: 768px) {
  .block-container { padding-left: 0.6rem; padding-right: 0.6rem; }
  h1 { font-size: 1.35rem !important; }
  h2, h3 { font-size: 1.1rem !important; }
  div.stButton > button { font-size: 0.9rem !important; padding: 0.55rem 0.5rem !important; }
}
</style>
""", unsafe_allow_html=True)



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

# ==================== 국립해양조사원 관측소 코드 ====================
# 조위관측소 (surveyTideLevel)
TIDE_STATIONS = {
    "인천": "DT_0001",
    "평택": "DT_0002",
    "보령": "DT_0024",   # 인근 장항
    "군산": "DT_0024",   # 인근 장항
    "목포": "DT_0007",
    "속초": "DT_0012",
    "강릉": "DT_0012",   # 인근 속초
    "울진": "DT_0012",
    "포항": "DT_0005",   # 인근 부산
    "울산": "DT_0005",
    "통영": "DT_0014",
    "거제": "DT_0014",
    "여수": "DT_0016",
    "완도": "DT_0028",   # 인근 진도
    "제주": "DT_0004",
}

# 파랑 관측소 목록 (코드, 이름, 위도, 경도) - 지역 좌표와 가장 가까운 곳 자동 선택
WAVE_STATION_LIST = [
    ("TW_0080", "우이도", 34.54305, 125.80277),      # 서남해 (목포·완도 쪽)
    ("TW_0081", "생일도", 34.25872, 126.96027),      # 남해 서부
    ("KG_0025", "남해동부", 34.22247, 128.41902),    # 통영·거제 쪽
    ("KG_0024", "대한해협", 34.919, 129.12125),       # 부산·대한해협
    ("TW_0062", "해운대", 35.14897, 129.17016),       # 부산 연안
    ("TW_0075", "중문", 33.2345, 126.40955),          # 제주
    ("KG_0021", "제주남부", 32.09041, 126.96586),     # 제주 남부
]


def nearest_wave_station(lat: float, lon: float):
    """지역 좌표에서 가장 가까운 파랑 관측소 반환"""
    best = None
    best_d = 1e18
    for code, name, slat, slon in WAVE_STATION_LIST:
        d = (lat - slat) ** 2 + (lon - slon) ** 2
        if d < best_d:
            best_d = d
            # 대략 km (위도 1도 ~ 111km)
            km = (d ** 0.5) * 111
            best = (code, name, km)
    return best


def get_data_go_kr_key():
    try:
        return st.secrets.get("DATA_GO_KR_SERVICE_KEY", "") or st.secrets.get("DATA_GO_KR_KEY", "")
    except Exception:
        return ""


@st.cache_data(ttl=900)
def fetch_khoa_tide(obs_code: str, yyyymmdd: str, key: str) -> dict:
    """국립해양조사원 조위관측소 실측·예측 조위"""
    if not key or not obs_code:
        return {"ok": False, "msg": "조위 API 키가 없습니다. secrets에 DATA_GO_KR_SERVICE_KEY를 넣으세요."}
    try:
        url = "https://apis.data.go.kr/1192136/surveyTideLevel/GetSurveyTideLevelApiService"
        params = {
            "serviceKey": key,
            "type": "json",
            "obsCode": obs_code,
            "reqDate": yyyymmdd,
            "numOfRows": 300,
            "pageNo": 1,
            "min": 10,  # 10분 간격
        }
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        header = data.get("header") or {}
        if str(header.get("resultCode")) not in ("00", "0"):
            return {"ok": False, "msg": header.get("resultMsg", "조위 API 오류")}
        body = data.get("body") or {}
        items = (body.get("items") or {}).get("item") or []
        if isinstance(items, dict):
            items = [items]
        if not items:
            return {"ok": False, "msg": "해당일 조위 데이터 없음"}

        # 실측(tdlvHgt) 기준 최고/최저 → 만조/간조 근사
        valid = [it for it in items if it.get("tdlvHgt") is not None]
        if not valid:
            valid = items
        hi = max(valid, key=lambda x: float(x.get("tdlvHgt") or x.get("bscTdlvHgt") or 0))
        lo = min(valid, key=lambda x: float(x.get("tdlvHgt") or x.get("bscTdlvHgt") or 0))
        hi_v = float(hi.get("tdlvHgt") or hi.get("bscTdlvHgt") or 0)
        lo_v = float(lo.get("tdlvHgt") or lo.get("bscTdlvHgt") or 0)
        # 최근 값
        last = valid[-1]
        last_v = float(last.get("tdlvHgt") or last.get("bscTdlvHgt") or 0)
        return {
            "ok": True,
            "station": hi.get("obsvtrNm", obs_code),
            "high_time": str(hi.get("obsrvnDt", ""))[-5:] if hi.get("obsrvnDt") else "-",
            "high_cm": round(hi_v, 1),
            "low_time": str(lo.get("obsrvnDt", ""))[-5:] if lo.get("obsrvnDt") else "-",
            "low_cm": round(lo_v, 1),
            "range_cm": round(hi_v - lo_v, 1),
            "last_cm": round(last_v, 1),
            "last_time": str(last.get("obsrvnDt", "")),
            "count": len(valid),
        }
    except Exception as e:
        return {"ok": False, "msg": f"{type(e).__name__}: {e}"}


@st.cache_data(ttl=900)
def fetch_khoa_wave(obs_code: str, key: str) -> dict:
    """국립해양조사원 국가해양관측망 실측 파랑"""
    if not key or not obs_code:
        return {"ok": False, "msg": "파랑 API 키가 없습니다. secrets에 DATA_GO_KR_SERVICE_KEY를 넣으세요."}
    try:
        url = "https://apis.data.go.kr/1192136/noonWave/GetNoonWaveApiService"
        params = {
            "serviceKey": key,
            "type": "json",
            "obsCode": obs_code,
            "numOfRows": 12,
            "pageNo": 1,
        }
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        header = data.get("header") or {}
        if str(header.get("resultCode")) not in ("00", "0"):
            return {"ok": False, "msg": header.get("resultMsg", "파랑 API 오류")}
        body = data.get("body") or {}
        items = (body.get("items") or {}).get("item") or []
        if isinstance(items, dict):
            items = [items]
        if not items:
            return {"ok": False, "msg": "파랑 데이터 없음"}
        last = items[-1]
        return {
            "ok": True,
            "station": last.get("obsvtrNm", obs_code),
            "time": last.get("obsrvnDt", ""),
            "wvhgt": last.get("wvhgt"),
            "max_wvhgt": last.get("maxWvhgt"),
            "wvpd": last.get("wvpd"),
            "wvdrct": last.get("wvdrct"),
        }
    except Exception as e:
        return {"ok": False, "msg": f"{type(e).__name__}: {e}"}


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
    return f"{low}~{high} cm"


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
        return "⚠️ secrets에 OpenAI API Key를 설정하면 AI 낚시조언을 받을 수 있어요."
    try:
        prompt = f"""
당신은 한국 바다 **선상낚시(보트/선박 출조)** 실전 경력 20년 이상의 전문 가이드다.
절대 갯바위·방파제·워킹·도보 낚시 내용은 넣지 마라. 전부 선상(배 위) 기준으로만 조언한다.
중급~고급 조사도 바로 선내에서 적용할 수 있는 수준의 디테일로 반말 톤으로 작성한다.

[조건]
- 날짜: {date_str}
- 지역: {region} ({sea})
- 물때: {mul}
- 대상 어종: {', '.join(fishes)}
- 낚시 형태: 선상낚시 전용

아래 구조를 지켜 작성하되, 각 항목을 구체적으로 써라. (총 800~1200자 수준)

1) 물때·조류 해석 (선상 기준)
- 이 물때의 조류 세기·방향 변화 타이밍
- 만조/간조 전후 몇 시간이 핵심인지, 배가 어느 쪽으로 붙는지

2) 어종별 선상 실전 공략 (어종마다 구분)
- 추천 채비 (바늘 호수, 목줄 길이·호수, 봉돌 무게, 카드채비/외바늘/다운샷 등)
- 미끼·집어제 운용 (배에서 하는 방식)
- 포인트 (수심대, 골·턱·암초·조류받이, 배가 붙는 위치)
- 액션·템포 (고패질 간격, 슬랙 관리, 입질 패턴, 드랍/리프팅)

3) 시간대별 선상 대응
- 출항~오전까지 / 정오 전후 / 오후~철수 각각 수심·채비·포인트 전환

4) 현장 변수 대응 (선내)
- 바람·파고·탁도에 따른 채비·앵커/드리프트 전략
- 입질 없을 때 우선 바꿔볼 순서 (수심→채비→미끼→포인트)

갯바위·캐스팅·도보 포인트 언급 금지. 숫자·호수·수심·시간 위주로 구체적으로.
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "한국 바다 선상낚시 실전 전문가. 고급 조사 수준의 구체적 조언을 반말로 제공한다."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1200,
            temperature=0.65,
            timeout=45,
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


# ==================== 메인 달력 (모바일 우선: 세로 리스트) ====================
month_days = cal.monthcalendar(year, month)
month_name = f"{year}년 {month}월"
weekday_names = ["월", "화", "수", "목", "금", "토", "일"]

st.subheader(f"📅 {month_name} 물때 달력")
st.caption(f"{sea_area} · {region}  ·  날짜를 누르면 상세 정보")

# 범례
st.markdown(
    """
    <div style="display:flex;gap:10px;flex-wrap:wrap;font-size:0.8rem;margin-bottom:0.5rem;">
      <span><span style="color:#e85d4c;">●</span> 사리</span>
      <span><span style="color:#43a047;">●</span> 중간</span>
      <span><span style="color:#1e88e5;">●</span> 조금</span>
    </div>
    """,
    unsafe_allow_html=True,
)

selected_day = st.session_state.get("selected_day")

# 주 단위로 묶어 세로 배치 (폰에서도 깨지지 않음)
week_num = 0
for week in month_days:
    days_in_week = [d for d in week if d != 0]
    if not days_in_week:
        continue
    week_num += 1
    first = days_in_week[0]
    last = days_in_week[-1]
    with st.expander(f"{week_num}주차  ({first}일 ~ {last}일)", expanded=(week_num <= 2 or (selected_day in days_in_week if selected_day else False))):
        for day in days_in_week:
            lunar_day = get_lunar_day(year, month, day)
            mul = get_mul_ttae(lunar_day, sea_area)
            mul_type = get_mul_type(mul)
            range_cm = get_tidal_range_cm(mul_type, sea_area)
            d = date(year, month, day)
            wd = weekday_names[d.weekday()]
            is_selected = selected_day == day

            color = {"사리": "#e85d4c", "중간": "#43a047", "조금": "#1e88e5"}.get(mul_type, "#9e9e9e")
            mark = "▶ " if is_selected else ""
            label = f"{mark}{day}일({wd})  ·  {mul}  ·  {range_cm}"

            bcol1, bcol2 = st.columns([6, 1])
            with bcol1:
                if st.button(label, key=f"day_{year}_{month}_{day}", use_container_width=True):
                    st.session_state["selected_day"] = day
                    st.session_state["selected_mul"] = mul
                    st.session_state["selected_mul_type"] = mul_type
                    st.session_state["selected_range"] = range_cm
                    st.session_state["selected_date_str"] = f"{year}-{month:02d}-{day:02d}"
                    st.session_state.pop("selected_fishes", None)
                    st.session_state.pop("last_advice", None)
                    st.rerun()
            with bcol2:
                st.markdown(
                    f"<div style='height:38px;border-radius:6px;background:{color};margin-top:4px;'></div>",
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
    c2.metric("고저차(추정)", range_cm)
    note = tide_est["비고"].split("—")[-1].strip() if "—" in tide_est["비고"] else tide_est["비고"]
    c3.metric("조류 경향", note)

    # ---- 국립해양조사원 실측·예측 조위 ----
    st.markdown("#### 🌊 국립해양조사원 조위 정보")
    ymd = date_str.replace("-", "")
    tide_code = TIDE_STATIONS.get(region, "")
    khoa_tide = fetch_khoa_tide(tide_code, ymd, get_data_go_kr_key()) if tide_code else {"ok": False, "msg": "관측소 미매핑"}
    if khoa_tide.get("ok"):
        t1, t2, t3, t4 = st.columns(4)
        t1.metric("관측소", khoa_tide["station"])
        t2.metric("최고조위(근사 만조)", f"{khoa_tide['high_cm']} cm", delta=khoa_tide.get("high_time"))
        t3.metric("최저조위(근사 간조)", f"{khoa_tide['low_cm']} cm", delta=khoa_tide.get("low_time"))
        t4.metric("조차(실측 범위)", f"{khoa_tide['range_cm']} cm")
        st.caption(f"최근 조위 {khoa_tide['last_cm']} cm · {khoa_tide['last_time']} · 자료 {khoa_tide['count']}건 (10분 간격)")
    else:
        st.info(f"조위 API: {khoa_tide.get('msg', '조회 실패')} — 추정 만조 {', '.join(tide_est['만조'])} / 간조 {', '.join(tide_est['간조'])}")

    # ---- 국립해양조사원 실측 파랑 (가장 가까운 관측소) ----
    st.markdown("#### 🌊 국립해양조사원 파랑 정보")
    rlat, rlon = REGION_COORDS.get(region, (37.5, 127.0))
    nearest = nearest_wave_station(rlat, rlon)
    if nearest:
        wave_code, wave_name, dist_km = nearest
        khoa_wave = fetch_khoa_wave(wave_code, get_data_go_kr_key())
        if khoa_wave.get("ok"):
            w1, w2, w3, w4 = st.columns(4)
            w1.metric("관측소", f"{khoa_wave['station']}")
            wh = khoa_wave.get("wvhgt")
            w2.metric("유의파고", f"{wh} m" if wh is not None else "-")
            mwh = khoa_wave.get("max_wvhgt")
            w3.metric("최대파고", f"{mwh} m" if mwh is not None else "-")
            pd_ = khoa_wave.get("wvpd")
            w4.metric("파주기", f"{pd_} 초" if pd_ is not None else "-")
            st.caption(
                f"관측시각: {khoa_wave.get('time', '-')} · "
                f"{region}에서 약 {dist_km:.0f} km 거리의 최근접 파랑 관측소"
            )
            if dist_km > 150:
                st.caption("⚠️ 선택한 지역과 관측소 거리가 멉니다. 아래 Open-Meteo 파고를 함께 참고하세요.")
        else:
            st.info(f"파랑 API: {khoa_wave.get('msg', '조회 실패')}")
    else:
        st.info("가까운 파랑 관측소를 찾지 못했습니다.")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 🐟 추천 어종")
        if "selected_fishes" not in st.session_state:
            with st.spinner("시즌 데이터 + AI 어종 추천 중..."):
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
        st.markdown("### 🤖 AI 낚시조언")
        if st.button("AI 상세 조언 받기", type="primary"):
            with st.spinner("조언 생성 중..."):
                st.session_state["last_advice"] = get_llm_advice(
                    client, date_str, region, sea_area, mul, fishes
                )
        if "last_advice" in st.session_state:
            st.markdown(st.session_state["last_advice"])
        else:
            st.info("버튼을 누르면 이 날짜·물때에 맞는 고급 실전 공략을 알려줘요.")

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


