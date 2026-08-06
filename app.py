import streamlit as st
from datetime import date, datetime, timedelta
from korean_lunar_calendar import KoreanLunarCalendar
from openai import OpenAI
import calendar as cal
import os

# ==================== 페이지 설정 ====================
st.set_page_config(
    page_title="물때 선상낚시 도우미",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌊 물때 선상낚시 도우미")
st.caption("지역·월별 물때 달력 + ChatGPT 추천 어종 + 낚시 조언")

# ==================== secrets에서 API 키 가져오기 ====================
def get_openai_client():
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
        if not api_key or api_key.startswith("sk-여기에"):
            return None
        
        # SSL 인증서 문제 우회 (이전에 다른 도구에서 했던 방식과 동일)
        import httpx
        http_client = httpx.Client(verify=False)
        return OpenAI(api_key=api_key, http_client=http_client)
    except Exception:
        return None

# ==================== 사이드바 ====================
with st.sidebar:
    st.header("⚙️ 설정")
    
    # 연월 선택
    today = date.today()
    year = st.number_input("연도", min_value=2024, max_value=2030, value=today.year)
    month = st.number_input("월", min_value=1, max_value=12, value=today.month)
    
    st.divider()
    
    # 해역 / 지역 선택
    sea_area = st.selectbox("해역 선택", ["서해", "동해", "남해"])
    
    region_options = {
        "서해": ["인천", "평택", "보령", "군산", "목포"],
        "동해": ["속초", "강릉", "울진", "포항", "울산"],
        "남해": ["통영", "거제", "여수", "완도", "제주"]
    }
    region = st.selectbox("세부 지역", region_options[sea_area])
    
    st.divider()
    
    # secrets 상태 표시
    client = get_openai_client()
    if client:
        st.success("✅ OpenAI API 키 로드됨 (secrets.toml)")
        if st.button("API 연결 테스트", key="test_api"):
            with st.spinner("테스트 중..."):
                try:
                    models = client.models.list()
                    st.success(f"✅ 연결 성공! (모델 수: {len(list(models.data))})")
                except Exception as e:
                    st.error(f"❌ 연결 실패: {type(e).__name__}: {e}")
    else:
        st.warning("⚠️ secrets.toml에 OPENAI_API_KEY를 설정해주세요")
        st.caption("`.streamlit/secrets.toml` 파일에 키를 넣으면 됩니다.")
    
    st.info("💡 달력에서 날짜를 클릭하면 상세 정보가 나와요!")

# ==================== 물때 계산 함수 ====================
def get_lunar_day(solar_year: int, solar_month: int, solar_day: int):
    calendar = KoreanLunarCalendar()
    success = calendar.setSolarDate(solar_year, solar_month, solar_day)
    if not success:
        return None
    lunar_str = calendar.LunarIsoFormat()
    try:
        parts = lunar_str.replace(" Intercalation", "").split("-")
        return int(parts[2])
    except:
        return None


def get_mul_ttae(lunar_day: int, sea: str) -> str:
    if lunar_day is None:
        return "알 수 없음"
    
    if sea == "서해":
        mapping = {
            1: "7물", 2: "8물", 3: "9물", 4: "10물", 5: "11물", 6: "12물", 7: "13물",
            8: "조금", 9: "무시", 10: "1물", 11: "2물", 12: "3물", 13: "4물", 14: "5물", 15: "6물",
            16: "7물", 17: "8물", 18: "9물", 19: "10물", 20: "11물", 21: "12물", 22: "13물",
            23: "조금", 24: "무시", 25: "1물", 26: "2물", 27: "3물", 28: "4물", 29: "5물", 30: "6물"
        }
    else:
        mapping = {
            1: "8물", 2: "9물", 3: "10물", 4: "11물", 5: "12물", 6: "13물", 7: "14물",
            8: "조금", 9: "1물", 10: "2물", 11: "3물", 12: "4물", 13: "5물", 14: "6물", 15: "7물",
            16: "8물", 17: "9물", 18: "10물", 19: "11물", 20: "12물", 21: "13물", 22: "14물",
            23: "조금", 24: "1물", 25: "2물", 26: "3물", 27: "4물", 28: "5물", 29: "6물", 30: "7물"
        }
    return mapping.get(lunar_day, "알 수 없음")


def get_mul_type(mul: str) -> str:
    if mul in ["7물", "8물", "9물", "10물"]:
        return "사리"
    elif mul in ["조금", "무시"]:
        return "조금"
    else:
        return "중간"


def get_tidal_range_cm(mul_type: str, sea: str) -> str:
    """
    물때 유형에 따른 대략적인 조차(고저차) 추정 (cm)
    실제 값은 국립해양조사원 조위 데이터가 필요함
    """
    # 서해가 조차 큼
    base = {
        "사리": {"서해": (350, 550), "동해": (30, 60), "남해": (150, 280)},
        "중간": {"서해": (200, 350), "동해": (20, 45), "남해": (80, 180)},
        "조금": {"서해": (80, 180), "동해": (10, 30), "남해": (40, 100)},
    }
    low, high = base.get(mul_type, {}).get(sea, (50, 150))
    return f"약 {low}~{high} cm"


# ==================== 시즌별 대표 출조 어종 참고 데이터 ====================
def get_seasonal_reference(sea: str, month: int) -> str:
    """월별·해역별 실제 많이 나가는 선상 어종 참고 정보"""
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


# ==================== ChatGPT 어종 추천 ====================
def recommend_fish_by_gpt(client, date_str: str, region: str, sea: str, mul: str, month: int) -> list:
    if client is None:
        ref = get_seasonal_reference(sea, month)
        return [f.strip() for f in ref.split(",")][:3]
    
    try:
        seasonal_ref = get_seasonal_reference(sea, month)
        
        prompt = f"""
당신은 한국 바다 선상낚시 전문 조황 분석가입니다.

[출조 조건]
- 날짜: {date_str}
- 지역: {region} ({sea})
- 물때: {mul}
- 월: {month}월

[시즌 참고 데이터 - 이 시기에 실제로 많이 출조되고 조황이 좋은 어종]
{seasonal_ref}

위 시즌 참고 데이터를 우선적으로 반영하고, 물때 특성(사리/중간/조금)과 지역 특성을 고려해서
지금 가장 기대할 수 있는 선상낚시 대표 어종 3가지만 추천하세요.

답변은 반드시 아래 형식으로만 하세요. 다른 설명 금지:

어종1, 어종2, 어종3
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 한국 바다낚시 조황 전문가입니다. 시즌 데이터를 반영해 형식에 맞춰 정확히 답변하세요."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.5,
            timeout=30
        )
        text = response.choices[0].message.content.strip()
        fishes = [f.strip() for f in text.replace("、", ",").split(",") if f.strip()]
        return fishes[:3] if fishes else [f.strip() for f in seasonal_ref.split(",")][:3]
    except Exception as e:
        st.warning(f"어종 추천 API 오류: {type(e).__name__}: {e}")
        ref = get_seasonal_reference(sea, month)
        return [f.strip() for f in ref.split(",")][:3]


# ==================== ChatGPT 상세 조언 ====================
def get_llm_advice(client, date_str: str, region: str, sea: str, mul: str, fishes: list) -> str:
    if client is None:
        return "⚠️ secrets.toml에 OpenAI API Key를 설정하면 ChatGPT 조언을 받을 수 있어요."
    
    try:
        prompt = f"""
당신은 한국 바다낚시 전문가입니다. 초보 조사님께 친절하고 실용적으로 조언해주세요. (반말 톤)

날짜: {date_str}
지역: {region} ({sea})
물때: {mul}
추천 선상 어종: {', '.join(fishes)}

다음 내용을 포함해서 답변해주세요:
1. 이 물때에 왜 이 어종들이 좋은지 간단히
2. 각 어종별 핵심 낚시 기법 1~2가지 (채비, 포인트, 시간대 등)
3. 그날 출조 시 주의할 점

답변은 너무 길지 않게 핵심만 400자 이내로 작성해주세요.
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 친절하고 실용적인 한국 바다낚시 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7,
            timeout=30
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ LLM 호출 중 오류: {type(e).__name__}: {e}"


# ==================== 메인 화면 - 달력 ====================
month_days = cal.monthcalendar(year, month)
month_name = f"{year}년 {month}월"
weekday_names = ["월", "화", "수", "목", "금", "토", "일"]

st.subheader(f"📅 {month_name} 물때 달력  ({sea_area} · {region})")

# 요일 헤더
cols = st.columns(7)
for i, day_name in enumerate(weekday_names):
    cols[i].markdown(
        f"<div style='text-align:center; font-weight:700; padding:6px 0; color:#555;'>{day_name}</div>",
        unsafe_allow_html=True
    )

# 물때 유형별 색상
def get_card_style(mul_type: str, is_selected: bool = False) -> str:
    colors = {
        "사리": ("#ffe8e0", "#e85d4c", "#c0392b"),   # 배경, 테두리, 강조
        "중간": ("#e8f5e9", "#43a047", "#2e7d32"),
        "조금": ("#e3f2fd", "#1e88e5", "#1565c0"),
    }
    bg, border, accent = colors.get(mul_type, ("#f5f5f5", "#9e9e9e", "#616161"))
    shadow = "0 4px 12px rgba(0,0,0,0.15)" if is_selected else "0 2px 6px rgba(0,0,0,0.08)"
    border_w = "2.5px" if is_selected else "1.5px"
    return f"""
        background: linear-gradient(145deg, {bg}, #ffffff);
        border: {border_w} solid {border};
        border-radius: 12px;
        box-shadow: {shadow};
        padding: 10px 6px;
        text-align: center;
        margin-bottom: 8px;
        min-height: 90px;
        transition: all 0.15s ease;
    """

# 달력 그리드
selected_day = st.session_state.get("selected_day", None)

for week in month_days:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day == 0:
                st.write("")
            else:
                lunar_day = get_lunar_day(year, month, day)
                mul = get_mul_ttae(lunar_day, sea_area)
                mul_type = get_mul_type(mul)
                range_cm = get_tidal_range_cm(mul_type, sea_area)
                
                # 요일 구하기
                d = date(year, month, day)
                wd = weekday_names[d.weekday()]
                
                is_selected = (selected_day == day)
                style = get_card_style(mul_type, is_selected)
                
                # 카드 형태의 날짜 블록
                card_html = f"""
                <div style="{style}">
                    <div style="font-size:15px; font-weight:700; color:#222; margin-bottom:4px;">
                        {day}일({wd})
                    </div>
                    <div style="font-size:13px; font-weight:600; color:#444; margin-bottom:3px;">
                        {mul}
                    </div>
                    <div style="font-size:11px; color:#666;">
                        {range_cm}
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
                # 클릭용 버튼 (투명하게 겹치거나 아래에)
                if st.button("선택", key=f"day_{year}_{month}_{day}", use_container_width=True):
                    st.session_state["selected_day"] = day
                    st.session_state["selected_mul"] = mul
                    st.session_state["selected_mul_type"] = mul_type
                    st.session_state["selected_range"] = range_cm
                    st.session_state["selected_date_str"] = f"{year}-{month:02d}-{day:02d}"
                    st.session_state.pop("selected_fishes", None)
                    st.session_state.pop("last_advice", None)
                    st.rerun()

# ==================== 선택된 날짜 상세 ====================
if "selected_day" in st.session_state and st.session_state["selected_day"]:
    st.divider()
    day = st.session_state["selected_day"]
    mul = st.session_state.get("selected_mul", "")
    mul_type = st.session_state.get("selected_mul_type", "")
    range_cm = st.session_state.get("selected_range", "")
    date_str = st.session_state.get("selected_date_str", "")
    
    st.subheader(f"📌 {date_str} 상세 정보")
    
    # 물때 + 조차
    st.markdown(f"**물때**: {mul}  ({mul_type})")
    st.markdown(f"**해수면 고저차(조차)**: {range_cm}")
    st.caption("※ 위 조차는 물때 유형에 따른 대략적인 추정값입니다. 실제 값은 국립해양조사원 조위 데이터를 참고하세요.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🐟 ChatGPT 추천 어종")
        
        # 날짜 변경 시마다 새로 추천 (강제)
        if "selected_fishes" not in st.session_state:
            with st.spinner("시즌 데이터 + ChatGPT가 어종을 추천하는 중..."):
                fishes = recommend_fish_by_gpt(client, date_str, region, sea_area, mul, month)
                st.session_state["selected_fishes"] = fishes
        else:
            fishes = st.session_state["selected_fishes"]
        
        if st.button("🔄 다시 추천받기", key="refresh_fish"):
            with st.spinner("다시 추천 중..."):
                fishes = recommend_fish_by_gpt(client, date_str, region, sea_area, mul, month)
                st.session_state["selected_fishes"] = fishes
                st.rerun()
        
        # 어종별 아이콘 매핑
        fish_icons = {
            "광어": "🐟", "우럭": "🐠", "참돔": "🐡", "농어": "🎣",
            "주꾸미": "🐙", "갑오징어": "🦑", "한치": "🦑", "볼락": "🐟",
            "감성돔": "🐡", "방어": "🐟", "부시리": "🐟", "돌돔": "🐡",
            "열기": "🐠", "가자미": "🐟"
        }
        
        for fish in fishes:
            icon = fish_icons.get(fish, "🐟")
            link = "https://www.sunsang24.com"
            st.markdown(
                f"""
                <a href="{link}" target="_blank" style="text-decoration:none;">
                    <div style="
                        display:flex; align-items:center; gap:10px;
                        background:linear-gradient(145deg,#f0f7ff,#ffffff);
                        border:1.5px solid #90caf9; border-radius:10px;
                        padding:10px 14px; margin-bottom:8px;
                        box-shadow:0 2px 6px rgba(0,0,0,0.08);
                        color:#1565c0; font-weight:600; font-size:15px;
                    ">
                        <span style="font-size:22px;">{icon}</span>
                        <span>{fish}</span>
                        <span style="margin-left:auto; font-size:12px; color:#888;">선상24 →</span>
                    </div>
                </a>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        st.link_button("선상24 전체 예약 페이지 열기", "https://www.sunsang24.com", use_container_width=True)
    
    with col2:
        st.markdown("### 🤖 ChatGPT 낚시 조언")
        
        if st.button("상세 조언 받기", type="primary"):
            with st.spinner("ChatGPT가 조언을 생성하는 중..."):
                advice = get_llm_advice(client, date_str, region, sea_area, mul, fishes)
                st.session_state["last_advice"] = advice
        
        if "last_advice" in st.session_state:
            st.markdown(st.session_state["last_advice"])
        else:
            st.info("버튼을 누르면 이 날짜·물때에 맞는 낚시 기법을 알려줘요.")
    
    # ==================== 날씨 영역 ====================
    st.divider()
    st.markdown("### 🌤️ 해당일 날씨 / 해상 정보")
    
    st.info("""
    **현재 상태**: 날씨·파고·바람 정보는 아직 실제 API가 연동되지 않았습니다.
    
    다음 단계에서 추가할 수 있는 것들:
    - 기상청 해양기상부이 / 등표 관측 데이터
    - Open-Meteo 또는 Windy 임베드
    - 국립해양조사원 해상예보
    
    원하시면 바로 다음으로 날씨 연동을 진행할게요.
    """)

# ==================== 하단 안내 ====================
st.divider()
st.markdown("""
**참고 사항**
- OpenAI API Key는 `.streamlit/secrets.toml` 파일에 저장해서 사용합니다. (화면에는 노출되지 않음)
- 물때와 조차는 음력 기반 전통 방식 + 대략 추정값입니다.
- 어종 추천은 ChatGPT가 실시간으로 생성합니다.
- 선상24는 공식 API가 공개되지 않아 현재는 사이트로 연결만 지원합니다.
""")
