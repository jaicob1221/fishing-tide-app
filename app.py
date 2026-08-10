import streamlit as st
from datetime import date, datetime, timedelta, time
from korean_lunar_calendar import KoreanLunarCalendar
from openai import OpenAI
import calendar as cal
import os
import requests
import re

# ==================== 페이지 설정 ====================
st.set_page_config(
    page_title="물때 선상낚시 도우미",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 모바일·제목 잘림 대응 CSS
st.markdown("""
<style>
.block-container {
  padding-top: 1rem;
  padding-bottom: 2rem;
  max-width: 900px;
  overflow: visible !important;
}
/* 기본 타이틀 숨기고 커스텀 헤더 사용 */
h1 { display: none !important; }

.app-header {
  margin: 0 0 0.4rem 0;
  padding: 0;
  overflow: visible;
  word-break: keep-all;
  overflow-wrap: break-word;
}
.app-header .title {
  font-size: 1.55rem;
  font-weight: 700;
  line-height: 1.35;
  color: inherit;
  margin: 0;
}
.app-header .subtitle {
  font-size: 0.88rem;
  color: #666;
  margin-top: 0.25rem;
  line-height: 1.4;
  word-break: keep-all;
}

div.stButton > button {
  white-space: pre-line !important;
  line-height: 1.25 !important;
  font-size: 0.85rem !important;
  padding: 0.45rem 0.35rem !important;
  min-height: 2.8rem !important;
}
/* 달력 날짜 버튼: 카드 안에서도 잘 보이게 */
div.stButton > button[kind="secondary"] {
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
  text-align: left !important;
  justify-content: flex-start !important;
  font-weight: 600 !important;
  color: #222 !important;
}
div.stButton > button[kind="primary"] {
  text-align: left !important;
  justify-content: flex-start !important;
}
section[data-testid="stSidebar"] { min-width: 220px; }

@media (max-width: 768px) {
  .block-container { padding-left: 0.6rem; padding-right: 0.6rem; }
  .app-header .title { font-size: 1.25rem; }
  .app-header .subtitle { font-size: 0.8rem; }
  h2, h3 { font-size: 1.1rem !important; }
  div.stButton > button { font-size: 0.9rem !important; padding: 0.55rem 0.5rem !important; }
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    """
<div class="app-header">
  <p class="title">🌊 물때 선상낚시 도우미</p>
  <p class="subtitle">지역·월별 물때 달력 · 실측 날씨 · AI 추천 어종 · 낚시 조언</p>
</div>
""",
    unsafe_allow_html=True,
)

# 사이드바 하단 임시 진단
if st.sidebar.button("네트워크 진단"):
    import socket, time, requests
    for host in ["apis.data.go.kr", "api.open-meteo.com", "api.openai.com"]:
        t0 = time.time()
        try:
            socket.create_connection((host, 443), timeout=5).close()
            st.sidebar.success(f"{host} TCP OK ({time.time()-t0:.1f}s)")
        except Exception as e:
            st.sidebar.error(f"{host} TCP FAIL: {type(e).__name__}")
    t0 = time.time()
    try:
        r = requests.get("https://apis.data.go.kr", timeout=8)
        st.sidebar.info(f"data.go.kr HTTP {r.status_code} ({time.time()-t0:.1f}s)")
    except Exception as e:
        st.sidebar.error(f"data.go.kr HTTP FAIL: {type(e).__name__}")

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


def _sanitize_api_error(err: Exception) -> str:
    """에러 메시지에서 serviceKey 등 민감정보 제거"""
    import re as _re
    msg = f"{type(err).__name__}: {err}"
    msg = _re.sub(r"serviceKey=[^&\s]+", "serviceKey=***", msg)
    msg = _re.sub(r"[0-9a-f]{40,}", "***", msg, flags=_re.I)
    if "ConnectTimeout" in type(err).__name__ or "timed out" in msg.lower():
        return "공공데이터 서버 연결 시간 초과 (잠시 후 다시 시도해 주세요)"
    if "ConnectionError" in type(err).__name__ or "Max retries" in msg:
        return "공공데이터 서버에 연결할 수 없습니다 (네트워크·서버 상태 확인)"
    return msg[:180]


def _requests_get_retry(url: str, params: dict, timeout: int = 30, retries: int = 3):
    """data.go.kr 호출용 재시도"""
    import time
    last_err = None
    for i in range(retries):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            return r
        except Exception as e:
            last_err = e
            if i < retries - 1:
                time.sleep(1.2 * (i + 1))
    raise last_err




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
        r = _requests_get_retry(url, params, timeout=30, retries=3)
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
        return {"ok": False, "msg": _sanitize_api_error(e)}


@st.cache_data(ttl=1800)
def fetch_fishing_index(req_date: str, region: str, key: str, gubun: str = "선상") -> dict:
    """국립해양조사원 바다낚시지수 (fcstFishingv2)
    req_date: YYYYMMDD, gubun: 선상|갯바위
    """
    if not key:
        return {"ok": False, "msg": "DATA_GO_KR_SERVICE_KEY 없음"}
    try:
        url = "https://apis.data.go.kr/1192136/fcstFishingv2/GetFcstFishingApiServicev2"
        params = {
            "serviceKey": key,
            "type": "json",
            "reqDate": req_date,
            "gubun": gubun,
            "pageNo": 1,
            "numOfRows": 300,
        }
        r = _requests_get_retry(url, params, timeout=35, retries=3)
        if r.status_code != 200:
            return {"ok": False, "msg": f"HTTP {r.status_code}"}
        data = r.json()
        header = data.get("header") or {}
        if str(header.get("resultCode", "")) not in ("00", "0"):
            return {"ok": False, "msg": header.get("resultMsg", "API 오류")}

        body = data.get("body") or {}
        items = (body.get("items") or {}).get("item") or []
        if isinstance(items, dict):
            items = [items]
        if not items:
            return {"ok": False, "msg": "해당일 낚시지수 없음"}

        lat0, lon0 = REGION_COORDS.get(region, (None, None))

        def dist2(it):
            try:
                la = float(it.get("lat"))
                lo = float(it.get("lot") or it.get("lon") or 0)
                if lat0 is None:
                    return 999
                return (la - lat0) ** 2 + (lo - lon0) ** 2
            except Exception:
                return 999

        # 지역 좌표에 가까운 포인트 우선
        items_sorted = sorted(items, key=dist2)
        near = [it for it in items_sorted if dist2(it) < (1.5 ** 2)]  # 대략 1.5도 이내
        use = near if near else items_sorted[:20]

        rows = []
        for it in use[:12]:
            rows.append({
                "place": it.get("seafsPstnNm") or "-",
                "species": it.get("seafsTgfshNm") or "-",
                "index": it.get("totalIndex") or "-",
                "score": "-",  # 이 API는 totalIndex(등급) 중심
                "wave": (
                    f"{it.get('minWvhgt')}~{it.get('maxWvhgt')} m"
                    if it.get("minWvhgt") is not None else "-"
                ),
                "wtmp": (
                    f"{it.get('minWtem')}~{it.get('maxWtem')} ℃"
                    if it.get("minWtem") is not None else "-"
                ),
                "time": it.get("predcNoonSeCd") or "-",
                "tide": it.get("tdlvHrCn") or "-",
                "wind": (
                    f"{it.get('minWspd')}~{it.get('maxWspd')} m/s"
                    if it.get("minWspd") is not None else "-"
                ),
                "date": it.get("predcYmd") or req_date,
            })

        # 대표: 가장 가까운 포인트의 오전/오후 중 첫 행
        return {
            "ok": True,
            "rows": rows,
            "count": len(items),
            "near_count": len(near),
            "gubun": gubun,
            "date": req_date,
        }
    except Exception as e:
        return {"ok": False, "msg": _sanitize_api_error(e)}


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


def get_naver_credentials():
    try:
        cid = st.secrets.get("NAVER_CLIENT_ID", "") or ""
        csec = st.secrets.get("NAVER_CLIENT_SECRET", "") or ""
        if cid and csec and not str(cid).startswith("여기에"):
            return str(cid).strip(), str(csec).strip()
    except Exception:
        pass
    return "", ""


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

    nid, nsec = get_naver_credentials()
    if nid and nsec:
        st.success("✅ 네이버 검색 API 키 로드됨")
    else:
        st.warning("⚠️ NAVER_CLIENT_ID / SECRET 미설정")

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

# ==================== 어종별 실전 공략 (현장 주류 방식) ====================
# 조행기·카페에서 실제로 많이 쓰는 방법. AI가 생미끼 등 비주류로 빗나가지 않게 고정.
SPECIES_METHODS = {
    "주꾸미": {
        "주력": "에기(루어) — 선상은 봉돌+에기 수직 탐색이 조행기 주류",
        "금지/비주류": "생미끼를 주 공법으로 안내 금지. 에기에 '3.0호·3.5호' 같은 호수 표기를 임의로 붙이지 말 것(주꾸미 에기는 조행기에서 호수로 거의 안 씀)",
        "채비": "쭈갑대(또는 가벼운 낚싯대)+베이트릴, 봉돌 12~16호(조류·수심에 따라), 에기, 애자. 조류에 따라 2단 채비(단차·가지줄 조절)가 조행기에 자주 등장",
        "에기표현": "조행기·카페 원문에 나온 그대로: '에기', '수평에기', '왕눈이(에기)', 구체 상품명 등. 검색 결과에 없는 호수·스펙을 지어내지 말 것",
        "포인트": "바닥 주꾸미 — 모래·자갈·패류 지대. 밑걸림 방지 위해 바닥을 지속 터치. 서해는 조수 간만·물때 확인",
        "시즌팁": "서해는 조수 간만 차가 커 물때 선택이 중요. 조금 물때가 유리하다는 조행기가 많음",
        "액션": "에기를 바닥에 두고 짧게 들어 올렸다 내리며 탐색. 바닥 감각 유지. 반응 좋은 에기는 그날 조행기에 언급된 종류·상품명 위주로 교체",
        "필수장비목록": "쭈갑대, 베이트릴, 봉돌 12~16호+, 에기(여러 종류·컬러), 애자, 합사·쇼크리더",
    },
"갑오징어": {
        "주력": "에깅(에기 루어)",
        "금지/비주류": "생미끼 중심 안내 지양. 에기 호수(3.0호 등)를 검색 결과 없이 임의로 쓰지 말 것",
        "채비": "에깅 로드·릴, 에기, 필요 시 샤로/딥 타입은 조행기 원문 표현을 따름",
        "에기표현": "조행기 원문 그대로: '에기', '수평에기', '왕눈이', 구체 상품명 등. 검색에 없는 호수·스펙 금지",
        "포인트": "암초·골 주변, 수심은 조행기에 나온 표현을 우선",
        "시즌팁": "가을 시즌 피크. 침강·타입은 조행기 언급을 따름",
        "액션": "바닥 찍고 저킹 후 폴링 구간 입질이 조행기에 자주 등장",
    },
"한치": {
        "주력": "한치 채비(이카메탈·오모리그·수평) 또는 에기",
        "금지/비주류": "바닥 생미끼 전용 안내 지양",
        "채비": "이카메탈/한치 스페셜, 야간 케미·라이트 활용",
        "포인트": "야간 선상, 수심층 탐색",
        "시즌팁": "여름~초가을 야간이 주력",
        "액션": "수심층 바꾸며 고패질, 입질 수심 고정",
    },
    "광어": {
        "주력": "다운샷(웜) + 생미끼 외바늘/타이라바 등 지역·선사에 따라 병행",
        "금지/비주류": "생미끼만 안내하지 말 것. 웜 다운샷도 반드시 포함",
        "채비": "① 다운샷: 지그헤드/싱커+웜(직선·컬테일 등 조행기 명칭). ② 생미끼: 외바늘+청갯지렁이·미꾸라지 등. ③ 타이라바는 조행기/선사에 언급될 때",
        "에기표현": "",
        "포인트": "모래·펄 바닥, 수심은 조행기 표현 우선",
        "시즌팁": "서해 사리 전후 조류 받는 곳. 웜 컬러·크기는 조행기 원문 인용",
        "액션": "다운샷은 바닥 유지하며 끌거나 톡톡 액션. 생미끼는 고패질·흘림. 조행기에 나온 방식 우선",
    },
"우럭": {
        "주력": "외바늘·카드채비 생미끼, 일부 지그헤드",
        "금지/비주류": "",
        "채비": "우럭 카드·외바늘, 미끼 청갯지렁이·크릴",
        "포인트": "암초·침선 주변",
        "시즌팁": "사리 물때 조류 셀 때 유리한 경우 많음",
        "액션": "바닥~약간 띄워 고패질",
    },
    "농어": {
        "주력": "루어(미노우·바이브) 또는 생미끼",
        "금지/비주류": "",
        "채비": "미노우 12~16cm, 또는 외바늘 생미끼",
        "포인트": "조류 소용돌이, 수중턱, 연안 가까운 뱃길",
        "시즌팁": "아침·해질녘 피딩",
        "액션": "릴링 속도 변화, 수면~중층",
    },
    "참돔": {
        "주력": "타이라바·참돔지깅·일부 생미끼",
        "금지/비주류": "",
        "채비": "타이라바 60~150g, 훅 세트",
        "포인트": "수중여·골, 조류 받는 곳",
        "시즌팁": "물돌이 전후 입질 집중되는 조행기 많음",
        "액션": "폴링 바이트 노리며 천천히",
    },
    "볼락": {
        "주력": "볼락 루어(지그헤드+웜) 또는 카드채비",
        "금지/비주류": "",
        "채비": "지그헤드 1~3g, 아징/볼락 로드",
        "포인트": "연안 암초·해초, 야간",
        "시즌팁": "동·남해 야간 시즌",
        "액션": "슬로우 리트리브, 수심층 탐색",
    },
    "열기": {
        "주력": "카드채비 생미끼(크릴 등)",
        "금지/비주류": "",
        "채비": "열기 카드, 작은 바늘",
        "포인트": "암초 지대, 수심 다양",
        "시즌팁": "동해 시즌 물때에 맞춰 이동",
        "액션": "고패질, 입질 수심 고정",
    },
    "방어": {
        "주력": "지깅·라이브베이트",
        "금지/비주류": "",
        "채비": "메탈지그 100~250g, 또는 생미끼",
        "포인트": "조류 빠른 곳, 어군 탐색",
        "시즌팁": "가을 피크 동·남해",
        "액션": "저킹 후 폴링, 어탐 연동",
    },
    "부시리": {
        "주력": "지깅",
        "금지/비주류": "",
        "채비": "메탈지그, 강화 채비",
        "포인트": "수중여·조류목",
        "시즌팁": "여름~가을",
        "액션": "빠른 액션과 폴링 병행",
    },
}



def get_species_method_guide(fishes: list) -> str:
    lines = []
    for f in fishes or []:
        info = SPECIES_METHODS.get(f)
        if not info:
            lines.append(f"- {f}: 해당 지역 조행기에서 가장 많이 쓰는 선상 주력 채비를 따를 것")
            continue
        extra = info.get("필수장비목록", "")
        egi = info.get("에기표현", "")
        parts = [
            f"- {f}",
            f"  · 주력 공법: {info['주력']}",
            f"  · 채비: {info['채비']}",
        ]
        if egi:
            parts.append(f"  · 에기 명칭 규칙: {egi}")
        parts.extend([
            f"  · 포인트: {info['포인트']}",
            f"  · 시즌팁: {info['시즌팁']}",
            f"  · 액션: {info['액션']}",
            f"  · 주의: {info['금지/비주류'] or '조행기 주류 방식만 안내'}",
        ])
        if extra:
            parts.append(f"  · 필수장비: {extra}")
        lines.append("\n".join(parts))
    return "\n".join(lines) if lines else "(어종 공략 데이터 없음)"



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


def recommend_fish_by_naver(region: str, sea: str, month: int) -> list:
    """네이버 검색 빈도 기반 추천 어종 3종
    단계: 선상낚시 → 지역 → (어종 후보 카운트) → 검색월 반영
    """
    client_id, client_secret = get_naver_credentials()
    seasonal_fallback = [f.strip() for f in get_seasonal_reference(sea, month).split(",")][:3]

    if not client_id or not client_secret:
        return seasonal_fallback

    # 알려진 대상 어종 목록 (매칭용, 긴 이름 우선)
    known = [
        "주꾸미", "갑오징어", "한치", "광어", "우럭", "농어", "참돔", "감성돔",
        "볼락", "열기", "방어", "부시리", "돌돔", "노래미", "도다리", "가자미",
        "대구", "학꽁치", "붕장어", "삼치", "고등어",
    ]

    queries_stage = [
        # 1) 선상낚시 조행기
        f"선상낚시 조행기",
        f"선상 조행기 {sea}",
        # 2) 지역
        f"{region} 선상 조행기",
        f"{region} 선상낚시 조행기",
        # 3) 검색월
        f"{month}월 {region} 선상 조행기",
        f"{month}월 선상낚시 조행기 {sea}",
        f"{month}월 {region} 조행기",
    ]

    counts = {k: 0 for k in known}
    month_counts = {k: 0 for k in known}
    seen_titles = set()

    for qi, q in enumerate(queries_stage):
        for kind in ("blog", "cafe"):
            try:
                items = naver_search(q, client_id, client_secret, kind=kind, display=20)
            except Exception:
                items = []
            for it in items:
                title = it.get("title") or ""
                if title[:40] in seen_titles:
                    continue
                seen_titles.add(title[:40])
                blob = f"{title} {it.get('description') or ''}"
                # 선상 관련 글만 약하게 가점 대상 (제목에 내륙만 있으면 스킵하지 않되 가중치)
                weight = 1
                if "선상" in blob:
                    weight += 1
                if region and region in blob:
                    weight += 1
                if f"{month}월" in blob:
                    weight += 2
                # 월 단계 쿼리면 월 카운트에도 반영
                is_month_q = qi >= 4
                for fish in known:
                    if fish in blob:
                        counts[fish] += weight
                        if is_month_q or f"{month}월" in blob:
                            month_counts[fish] += weight

    # 월 매칭 빈도에 가중을 더해 최종 점수
    final = {}
    for fish in known:
        final[fish] = counts[fish] + month_counts[fish] * 1.5

    ranked = sorted(final.items(), key=lambda x: x[1], reverse=True)
    top = [name for name, sc in ranked if sc > 0][:3]

    if len(top) < 3:
        for f in seasonal_fallback:
            if f not in top:
                top.append(f)
            if len(top) >= 3:
                break
    return top[:3]


def recommend_fish_by_gpt(client, date_str: str, region: str, sea: str, mul: str, month: int) -> list:
    """하위 호환: 네이버 빈도 추천을 우선 사용"""
    return recommend_fish_by_naver(region, sea, month)


def naver_search(query: str, client_id: str, client_secret: str, kind: str = "blog", display: int = 15) -> list:
    """네이버 검색 API (blog / cafearticle)"""
    import re
    endpoints = {
        "blog": "https://openapi.naver.com/v1/search/blog.json",
        "cafe": "https://openapi.naver.com/v1/search/cafearticle.json",
    }
    url = endpoints.get(kind, endpoints["blog"])
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    params = {"query": query, "display": display, "sort": "sim"}
    r = requests.get(url, headers=headers, params=params, timeout=10)
    if r.status_code != 200:
        return []
    items = r.json().get("items") or []
    results = []
    for it in items:
        title = re.sub(r"<[^>]+>", "", it.get("title") or "").strip()
        desc = re.sub(r"<[^>]+>", "", it.get("description") or "").strip()
        link = it.get("link") or ""
        source = it.get("bloggername") or it.get("cafename") or kind
        postdate = str(it.get("postdate") or "")
        if title:
            results.append({
                "title": title,
                "description": desc[:200],
                "link": link,
                "source": source,
                "kind": kind,
                "postdate": postdate,
                "query": query,
            })
    return results


def _item_text(it: dict) -> str:
    return f"{it.get('title', '')} {it.get('description', '')}"


def _filter_contains(items: list, keywords: list, mode: str = "any") -> list:
    """제목+요약에 키워드 포함 필터. mode=any|all"""
    out = []
    for it in items:
        t = _item_text(it)
        hits = [kw for kw in keywords if kw and kw in t]
        if mode == "all" and len(hits) == len([k for k in keywords if k]):
            out.append(it)
        elif mode == "any" and hits:
            out.append(it)
    return out


def _recency_score(postdate: str) -> float:
    if not postdate or len(postdate) != 8 or not postdate.isdigit():
        return 0.0
    try:
        from datetime import datetime as _dt
        d = _dt.strptime(postdate, "%Y%m%d").date()
        age = (date.today() - d).days
        if age <= 45:
            return 20.0
        if age <= 90:
            return 12.0
        if age <= 180:
            return 5.0
        if age > 400:
            return -8.0
    except Exception:
        return 0.0
    return 0.0


def _final_score(it: dict, month: int, fishes: list, region: str) -> float:
    t = _item_text(it)
    score = 0.0
    for i, fish in enumerate(fishes or []):
        if fish and fish in t:
            score += 15.0 if i == 0 else 8.0
    if "조행기" in t:
        score += 8.0
    if "선상" in t:
        score += 6.0
    if f"{month}월" in t:
        score += 10.0
    if region and region in t:
        score += 8.0
    score += _recency_score(it.get("postdate") or "")
    for kw in ("수평에기", "왕눈이", "에기", "다운샷", "웜"):
        if kw in t:
            score += 2.0
    return score


def fetch_johwang_snippets(region: str, sea: str, fishes: list, month: int) -> str:
    """순차 필터: 어종 조행기 → 선상 → 월 → 지역 → 점수 선정
    각 단계 결과가 부족하면 해당 단계만 완화(스킵)
    """
    client_id, client_secret = get_naver_credentials()
    if not client_id or not client_secret:
        return (
            "(네이버 API 키 없음 — secrets에 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 설정 필요. "
            "현장 주류 공법 데이터로 보완)"
        )

    primary = (fishes or ["광어"])[0]
    secondary = fishes[1] if fishes and len(fishes) > 1 else None
    MIN_KEEP = 5  # 이 미만이면 해당 필터 완화

    # ----- 1) 어종 조행기 검색 (기반 풀) -----
    base_queries = [
        f"{primary} 조행기",
        f"{primary} 선상 조행기",
        f"{month}월 {primary} 조행기",
    ]
    if secondary:
        base_queries.append(f"{secondary} 조행기")

    pool = []
    errors = []
    for q in base_queries:
        for kind in ("blog", "cafe"):
            try:
                for it in naver_search(q, client_id, client_secret, kind=kind, display=15):
                    it["query"] = q
                    pool.append(it)
            except Exception as e:
                errors.append(f"{kind}:{type(e).__name__}")

    # 제목 중복 제거
    uniq = {}
    for it in pool:
        key = (it.get("title") or "")[:48]
        if key and key not in uniq:
            uniq[key] = it
    stage = list(uniq.values())
    trace = [f"1) 어종 조행기 검색 풀: {len(stage)}건"]

    if not stage:
        msg = f"(네이버 조행기 검색 결과 없음 — '{primary} 조행기' 및 현장 주류 공법으로 보완)"
        if errors:
            msg += f" [오류: {', '.join(errors[:3])}]"
        return msg

    # 어종 키워드 포함 강제 (1순위 필터)
    species_kw = [primary] + ([secondary] if secondary else [])
    filtered = _filter_contains(stage, species_kw, mode="any")
    if len(filtered) >= MIN_KEEP:
        stage = filtered
        trace.append(f"1-b) 어종명 포함 필터: {len(stage)}건")
    else:
        trace.append(f"1-b) 어종명 필터 완화(유지 {len(stage)}건)")

    # ----- 2) 선상 필터 -----
    filtered = _filter_contains(stage, ["선상"], mode="any")
    if len(filtered) >= MIN_KEEP:
        stage = filtered
        trace.append(f"2) 선상 필터: {len(stage)}건")
    else:
        trace.append(f"2) 선상 필터 완화(후보 부족 {len(filtered)}건)")

    # ----- 3) 검색월 필터 -----
    month_kw = [f"{month}월", f"{month} 월"]
    # 시즌 보조 키워드
    season_extra = {
        8: ["초가을", "여름"], 9: ["가을", "초가을"], 10: ["가을"],
        11: ["늦가을", "초겨울"], 12: ["겨울"], 1: ["겨울"], 2: ["겨울"],
        3: ["봄", "초봄"], 4: ["봄"], 5: ["봄", "초여름"], 6: ["여름"], 7: ["여름"],
    }
    month_kw += season_extra.get(month, [])
    filtered = _filter_contains(stage, month_kw, mode="any")
    if len(filtered) >= MIN_KEEP:
        stage = filtered
        trace.append(f"3) {month}월·시즌 필터: {len(stage)}건")
    else:
        # ±1개월 완화
        near = [f"{month}월"]
        if month > 1:
            near.append(f"{month-1}월")
        if month < 12:
            near.append(f"{month+1}월")
        filtered2 = _filter_contains(stage, near, mode="any")
        if len(filtered2) >= 3:
            stage = filtered2
            trace.append(f"3) 월 필터 완화(±1개월): {len(stage)}건")
        else:
            trace.append(f"3) 월 필터 완화(유지 {len(stage)}건)")

    # ----- 4) 지역 필터 -----
    region_kw = [region] if region else []
    if sea:
        region_kw.append(sea)
    filtered = _filter_contains(stage, region_kw, mode="any")
    if len(filtered) >= 3:
        stage = filtered
        trace.append(f"4) 지역·해역 필터: {len(stage)}건")
    else:
        trace.append(f"4) 지역 필터 완화(후보 부족 {len(filtered)}건)")

    # ----- 5) 점수 정렬 최종 N건 -----
    for it in stage:
        it["_score"] = _final_score(it, month, fishes or [], region or "")
    ranked = sorted(stage, key=lambda x: x.get("_score", 0), reverse=True)[:12]
    trace.append(f"5) 점수 상위: {len(ranked)}건")

    lines = ["[네이버 순차필터] " + " → ".join(trace)]
    for it in ranked:
        kind_label = "블로그" if it["kind"] == "blog" else "카페"
        pd = it.get("postdate") or ""
        pd_s = f"{pd[:4]}-{pd[4:6]}-{pd[6:]}" if len(pd) == 8 else ""
        head = f"- [{kind_label}/{it['source']}"
        if pd_s:
            head += f"/{pd_s}"
        head += f"] {it['title']}"
        if it.get("description"):
            head += f": {it['description']}"
        lines.append(head)

    return "\n".join(lines)



def get_llm_advice(client, date_str, region, sea, mul, fishes, month=None):
    if client is None:
        return "⚠️ secrets에 OpenAI API Key를 설정하면 AI 낚시조언을 받을 수 있어요."
    try:
        if month is None:
            try:
                month = int(date_str.split("-")[1])
            except Exception:
                month = date.today().month
        with st.spinner("조행기 글을 검색·수집하는 중..."):
            web_refs = fetch_johwang_snippets(region, sea, fishes, month)
        seasonal = get_seasonal_reference(sea, month)
        method_guide = get_species_method_guide(fishes)
        prompt = f"""
너는 네이버 조행기 글을 요약하는 실전 분석가다.
일반 AI 잔소리 금지. 조행기·카페에서 반복되는 현장 내용만 말한다.

[조건] 날짜 {date_str} / {region}({sea}) / 물때 {mul} / 선상만
[추천 어종] {', '.join(fishes)}
→ 이 어종은 네이버 선상 조행기 검색에서 지역·시기에 많이 등장한 순으로 고른 것이다.
→ 가이드는 반드시 이 추천 어종만 다룬다. 다른 어종을 추가하지 말 것.

[시즌 참고] {seasonal}

[현장 주류 공법 — 추천 어종 기준]
{method_guide}

[네이버 조행기 검색 결과 — 어종→선상→월→지역 순차필터 후 선정. 최우선 반영]
{web_refs}

규칙:
1) 주꾸미=에기+봉돌(12~16호)·애자·2단채비 주류. 생미끼 주력 금지.
2) 갑오징어·주꾸미 에기 이름은 네이버 검색 원문 그대로만 사용.
   - 허용: "에기", "수평에기", "왕눈이", 상품명 등 글에 실제로 적힌 말
   - 금지: 검색에 없는 "에기 3.0호/3.5호/4.0호" 등 호수 추론
3) 광어는 반드시 (A) 웜 다운샷 과 (B) 생미끼 를 함께 안내. 생미끼만 쓰지 말 것.
   - 웜/다운샷 명칭도 검색 원문 우선, 없으면 '다운샷+웜' 수준만.
4) 봉돌 호수 등 숫자는 검색·주류 공법에 있을 때만.
5) 반말, 800~1300자.

### 조황 분위기
### 주력 공법 (어종별) — 에기·웜 명칭은 원문 인용
### 물때·운영
### 바로 체크할 것
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "조행기 요약 전문가. 주꾸미·갑오징어 에기 호수 임의 생성 금지, 검색 원문 명칭만. 광어는 웜 다운샷+생미끼 함께. 반말."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1400, temperature=0.5, timeout=60,
        )
        body = response.choices[0].message.content
        return body + f"\n\n---\n*참고: 네이버 블로그·카페 '{month}월 어종 조행기' 검색 + 현장 주류 공법 기반. 당일 현장과 다를 수 있습니다.*"
    except Exception as e:
        return f"⚠️ LLM 오류: {type(e).__name__}: {e}"


def render_stat_row(items, accent="#1e88e5"):
    cells = []
    for label, value, sub in items:
        sub_html = f'<div style="font-size:11px;color:#888;margin-top:2px;">{sub}</div>' if sub else ""
        cells.append(
            '<div style="flex:1;min-width:90px;background:linear-gradient(145deg,#fafbfc,#fff);'
            f'border:1px solid #e0e0e0;border-left:3px solid {accent};border-radius:8px;padding:8px 10px;'
            'box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
            f'<div style="font-size:11px;color:#666;margin-bottom:2px;">{label}</div>'
            f'<div style="font-size:14px;font-weight:600;color:#222;line-height:1.3;">{value}</div>'
            f"{sub_html}</div>"
        )
    st.markdown(
        '<div style="display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 10px 0;">'
        + "".join(cells) + "</div>",
        unsafe_allow_html=True,
    )


def sunsang24_link(region: str, fish: str = "") -> str:
    # 선상 예약 목록 페이지
    return "https://www.sunsang24.com/ship/list/"


@st.cache_data(ttl=1800)
def fetch_weather(lat: float, lon: float, target_date: str) -> dict:
    result = {"ok": False, "msg": "", "out_of_range": False}
    try:
        try:
            target = date.fromisoformat(target_date)
        except Exception:
            target = None
        if target is not None:
            delta = (target - date.today()).days
            if delta > 16:
                result["out_of_range"] = True
                result["msg"] = "날씨 예보는 오늘 기준 최대 16일까지 지원됩니다. 더 가까운 날짜를 선택해 주세요."
                return result
            if delta < -5:
                result["out_of_range"] = True
                result["msg"] = "선택한 날짜는 예보 범위를 벗어났습니다."
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
        marine = {}
        try:
            mr = requests.get(
                "https://marine-api.open-meteo.com/v1/marine"
                f"?latitude={lat}&longitude={lon}"
                "&daily=wave_height_max,wave_period_max&timezone=Asia%2FSeoul"
                f"&start_date={target_date}&end_date={target_date}",
                timeout=10,
            )
            if mr.status_code == 200:
                marine = mr.json().get("daily", {})
        except Exception:
            pass
        codes = {0: "맑음", 1: "대체로 맑음", 2: "구름 조금", 3: "흐림", 61: "비", 63: "비", 80: "소나기", 95: "뇌우"}
        code = (daily.get("weathercode") or [0])[0]
        result.update({
            "ok": True,
            "tmax": (daily.get("temperature_2m_max") or [None])[0],
            "tmin": (daily.get("temperature_2m_min") or [None])[0],
            "rain": (daily.get("precipitation_sum") or [0])[0],
            "wind": (daily.get("windspeed_10m_max") or [None])[0],
            "wind_dir": (daily.get("winddirection_10m_dominant") or [None])[0],
            "sky": codes.get(code, f"코드 {code}"),
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


# ==================== 메인 달력 ====================
month_days = cal.monthcalendar(year, month)
weekday_names = ["월", "화", "수", "목", "금", "토", "일"]
st.subheader(f"📅 {year}년 {month}월 물때 달력")
st.caption(f"{sea_area} · {region}  ·  날짜를 누르면 상세 정보")
st.markdown(
    '<div style="display:flex;gap:10px;flex-wrap:wrap;font-size:0.8rem;margin-bottom:0.5rem;">'
    '<span><span style="color:#e85d4c;">●</span> 사리</span>'
    '<span><span style="color:#43a047;">●</span> 중간</span>'
    '<span><span style="color:#1e88e5;">●</span> 조금</span></div>',
    unsafe_allow_html=True,
)
selected_day = st.session_state.get("selected_day")
week_num = 0
for week in month_days:
    days_in_week = [d for d in week if d != 0]
    if not days_in_week:
        continue
    week_num += 1
    first, last = days_in_week[0], days_in_week[-1]
    # 현재일이 속한 주차만 기본 펼침 (다른 달은 선택일 우선, 없으면 접힘)
    today = date.today()
    contains_today = (
        year == today.year and month == today.month and today.day in days_in_week
    )
    contains_selected = selected_day in days_in_week if selected_day else False
    with st.expander(
        f"{week_num}주차  ({first}일 ~ {last}일)",
        expanded=(contains_today or contains_selected),
    ):
        for day in days_in_week:
            lunar_day = get_lunar_day(year, month, day)
            mul = get_mul_ttae(lunar_day, sea_area)
            mul_type = get_mul_type(mul)
            range_cm = get_tidal_range_cm(mul_type, sea_area)
            d = date(year, month, day)
            wd = weekday_names[d.weekday()]
            is_selected = selected_day == day
            color = {"사리": "#e85d4c", "중간": "#43a047", "조금": "#1e88e5"}.get(mul_type, "#9e9e9e")
            bg = {"사리": "#fdecea", "중간": "#e8f5e9", "조금": "#e3f2fd"}.get(mul_type, "#f5f5f5")
            mark = "▶ " if is_selected else ""
            label = f"{mark}{day}일({wd}) · {mul} · {range_cm}"
            # 물때색 = 날짜 블록 배경 (닫힌 HTML 한 덩어리 + 버튼)
            ring = f"box-shadow:0 0 0 2px {color};" if is_selected else ""
            card = (
                f'<div style="background-color:{bg};border-left:6px solid {color};'
                f'border-radius:10px;padding:10px 12px;margin:6px 0;{ring}">'
                f'<div style="font-weight:600;color:#222;font-size:0.95rem;">{label}</div>'
                f"</div>"
            )
            st.markdown(card, unsafe_allow_html=True)
            if st.button(
                f"{day}일 선택",
                key=f"day_{year}_{month}_{day}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
            ):
                st.session_state["selected_day"] = day
                st.session_state["selected_mul"] = mul
                st.session_state["selected_mul_type"] = mul_type
                st.session_state["selected_range"] = range_cm
                st.session_state["selected_date_str"] = f"{year}-{month:02d}-{day:02d}"
                st.session_state.pop("selected_fishes", None)
                st.session_state.pop("last_advice", None)
                st.rerun()

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
    note = tide_est["비고"].split("—")[-1].strip() if "—" in tide_est["비고"] else tide_est["비고"]
    render_stat_row([
        ("물때", f"{mul} ({mul_type})", ""),
        ("고저차(추정)", range_cm, ""),
        ("조류 경향", note, ""),
    ], accent="#546e7a")

    st.markdown("##### 🌊 국립해양조사원 조위")
    ymd = date_str.replace("-", "")
    tide_code = TIDE_STATIONS.get(region, "")
    khoa_tide = fetch_khoa_tide(tide_code, ymd, get_data_go_kr_key()) if tide_code else {"ok": False, "msg": "관측소 미매핑"}
    if khoa_tide.get("ok"):
        render_stat_row([
            ("관측소", khoa_tide["station"], ""),
            ("최고조위", f"{khoa_tide['high_cm']} cm", khoa_tide.get("high_time", "")),
            ("최저조위", f"{khoa_tide['low_cm']} cm", khoa_tide.get("low_time", "")),
            ("조차", f"{khoa_tide['range_cm']} cm", ""),
        ], accent="#0277bd")
        st.caption(f"최근 {khoa_tide['last_cm']} cm · {khoa_tide['last_time']} · {khoa_tide['count']}건(10분)")
    else:
        st.caption(f"조위: {khoa_tide.get('msg')} · 추정 만조 {', '.join(tide_est['만조'])} / 간조 {', '.join(tide_est['간조'])}")

    st.markdown("##### 🎣 바다낚시지수 (선상)")
    ymd_idx = date_str.replace("-", "")
    fidx = fetch_fishing_index(ymd_idx, region, get_data_go_kr_key(), gubun="선상")
    if fidx.get("ok") and fidx.get("rows"):
        r0 = fidx["rows"][0]
        render_stat_row([
            ("구분", "선상", fidx.get("date", "")),
            ("가까운 포인트", str(r0.get("place") or "-"), str(r0.get("time") or "")),
            ("낚시지수", str(r0.get("index") or "-"), str(r0.get("tide") or "")),
            ("수온", str(r0.get("wtmp") or "-"), ""),
            ("파고", str(r0.get("wave") or "-"), str(r0.get("wind") or "")),
        ], accent="#2e7d32")
        lines = []
        for row in fidx["rows"][:8]:
            lines.append(
                f"- **{row.get('place','-')}** · {row.get('species','-')} · "
                f"**{row.get('index','-')}** ({row.get('time','-')})"
            )
        st.markdown("\n".join(lines))
        st.caption(
            f"국립해양조사원 바다낚시지수 · 전체 {fidx.get('count')}건 중 "
            f"{region} 인근 {fidx.get('near_count', 0)}건 우선 표시"
        )
    else:
        st.caption(f"낚시지수: {fidx.get('msg', '조회 실패')} · gubun=선상")

    st.markdown("##### 🌤️ 해당일 날씨 / 해상 정보")

    lat, lon = REGION_COORDS.get(region, (37.5, 127.0))
    weather = fetch_weather(lat, lon, date_str)
    if weather.get("ok"):
        tmax, tmin = weather.get("tmax"), weather.get("tmin")
        rain = weather.get("rain") or 0
        wind = weather.get("wind")
        temp_s = f"{tmin:.0f}~{tmax:.0f}°C" if tmax is not None and tmin is not None else "-"
        wind_s = f"{wind:.1f} m/s ({wind_dir_text(weather.get('wind_dir'))})" if wind is not None else "-"
        wave = weather.get("wave")
        period = weather.get("wave_period")
        wave_s = f"{wave:.1f} m" if wave is not None else "-"
        period_s = f"주기 {period:.0f}초" if period else ""
        render_stat_row([
            ("하늘", weather.get("sky", "-"), ""),
            ("기온", temp_s, ""),
            ("강수", f"{rain:.1f} mm", ""),
            ("풍속", wind_s, ""),
            ("파고(예보)", wave_s, period_s),
        ], accent="#6a1b9a")
        st.caption(f"Open-Meteo · {region} ({lat:.2f}, {lon:.2f})")
    else:
        msg = weather.get("msg") or "날씨 정보를 불러오지 못했어요."
        if weather.get("out_of_range"):
            st.info(f"ℹ️ {msg}")
        else:
            st.warning(f"날씨: {msg}")
    st.markdown(f"[🗺️ Windy에서 {region} 해상 날씨 보기](https://www.windy.com/{lat}/{lon})")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 🐟 추천 어종")
        st.caption("네이버 선상 조행기 검색 빈도 기준 (지역·월 반영)")
        if "selected_fishes" not in st.session_state:
            with st.spinner("네이버 조행기 검색으로 어종 집계 중..."):
                st.session_state["selected_fishes"] = recommend_fish_by_gpt(
                    client, date_str, region, sea_area, mul, month
                )
        fishes = st.session_state["selected_fishes"]
        if st.button("🔄 다시 추천받기", key="refresh_fish"):
            st.session_state["selected_fishes"] = recommend_fish_by_gpt(
                client, date_str, region, sea_area, mul, month
            )
            st.rerun()
        icons = {
            "광어": "🐟", "우럭": "🐠", "참돔": "🐡", "농어": "🎣", "주꾸미": "🐙",
            "갑오징어": "🦑", "한치": "🦑", "볼락": "🐟", "감성돔": "🐡", "방어": "🐟",
            "부시리": "🐟", "열기": "🐠", "노래미": "🐠", "도다리": "🐟", "대구": "🐟",
        }
        for fish in fishes:
            icon = icons.get(fish, "🐟")
            st.markdown(
                f'<a href="{sunsang24_link(region, fish)}" target="_blank" style="text-decoration:none;">'
                f'<div style="display:flex;align-items:center;gap:10px;background:linear-gradient(145deg,#f0f7ff,#fff);'
                f'border:1.5px solid #90caf9;border-radius:10px;padding:10px 14px;margin-bottom:8px;'
                f'color:#1565c0;font-weight:600;font-size:15px;">'
                f'<span style="font-size:22px;">{icon}</span><span>{fish}</span>'
                f'<span style="margin-left:auto;font-size:12px;color:#888;">선상24 →</span></div></a>',
                unsafe_allow_html=True,
            )
        st.link_button("선상24 전체 예약 페이지", sunsang24_link(region), use_container_width=True)

    with col2:
        st.markdown("### 🤖 AI 낚시조언")
        if st.button("AI 상세 조언 받기", type="primary"):
            with st.spinner("조행기 검색 + 조언 생성 중..."):
                st.session_state["last_advice"] = get_llm_advice(
                    client, date_str, region, sea_area, mul, fishes, month
                )
        if "last_advice" in st.session_state:
            st.markdown(st.session_state["last_advice"])
        else:
            st.info("버튼을 누르면 'N월 어종 조행기' 검색을 반영한 실전 조언을 생성합니다.")

