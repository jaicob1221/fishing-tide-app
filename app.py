Ctrl+K
Ctrl+J




1m 10s동안 작업함
Windy API 연동까지 반영했어.

적용 내용
secrets의 WINDY_API_KEY 사용
상세 화면 날씨 아래에 해상 지도 표시
키 있음 → Map Forecast API (바람 레이어 + 지역 마커)
키 없음 → 공개 embed
사이드바에 Windy API 키 로드됨 표시
secrets.toml 추가
WINDY_API_KEY = "발급받은_맵_Forecast_키"
예:

OPENAI_API_KEY = "sk-...."
DATA_GO_KR_SERVICE_KEY = "...."
NAVER_CLIENT_ID = "...."
NAVER_CLIENT_SECRET = "...."
WINDY_API_KEY = "...."
SSL_INSECURE = true
로컬: run.bat 재실행
Cloud: Secrets에도 같은 키 추가 후 재배포

전체 app.py

날짜를 누르면 날씨 카드 아래 Windy 지도가 보여야 해.



다음 내용을 참조하세요:


41s동안 작업함
원인은 API 키 도메인 제한이야.

Cannot use Windy API, key is used from unauthorized domain. (403)
Map Forecast 키는 등록한 웹 주소에서만 동작해.
localhost:2424 / xxx.streamlit.app 이 키 설정에 없으면 막힌다.

코드 수정
지도는 공개 embed로 바꿨어.

키·도메인 등록 없이 동작
바람 레이어·지역 좌표 표시는 동일
Streamlit에 가장 안정적
app.py

Map Forecast 키를 꼭 쓰려면
api.windy.com/keys 에서 키 설정
Allowed domains에 추가:
localhost
127.0.0.1
본인앱이름.streamlit.app
저장 후 수 분 기다렸다가 새로고침
그래도 Streamlit components.html + 외부 스크립트 조합은 환경에 따라 까다로워서, 지금은 embed가 더 낫다.

run.bat 다시 실행한 뒤 날짜를 누르면, 빨간 403 없이 지도가 보여야 해.

Domain restrictions 과 Project identification 에는 어떤 내용을 넣어야해?


16s동안 작업함
Windy 키 설정에 넣을 내용을 정리하면 아래와 같아.

1. Project identification (프로젝트 이름)
앱/서비스를 구분하는 이름이면 된다. 도메인 주소가 아니라 라벨.

예시:

물때 선상낚시 도우미
또는

fishing-tide-app
영문·한글 모두 가능. 본인만 알아보면 됨.

2. Domain restrictions (도메인 제한)
이 키를 쓸 수 있는 웹 주소를 넣는 칸이야.
여기에 없는 주소에서 키를 쓰면 unauthorized domain (403) 이 난다.

로컬 테스트만 할 때
Windy 스태프 안내 기준:

방법	내용
추천	도메인 칸을 비워 두기 → localhost에서 사용 가능
또는	localhost 명시
localhost
http:// / 포트(:2424)는 보통 넣지 않음.

Streamlit Cloud도 쓸 때
Cloud 주소의 호스트명을 추가한다.

예:

localhost
your-app-name.streamlit.app
실제 주소가
https://fishing-tide-app.streamlit.app 이면:

fishing-tide-app.streamlit.app
Premium 쪽 안내는 2단계 도메인 최대 5개 정도.

넣으면 안 되는 예
http://localhost:2424          ← 스키마·포트 포함
https://xxx.streamlit.app/page ← 경로 포함
3. 우리 앱 기준으로 추천 입력
항목	값
Project identification	물때 선상낚시 도우미
Domain restrictions	로컬만 → 비움 또는 localhost
Cloud도 → localhost + 본인앱.streamlit.app
API 종류	Map Forecast API
4. 참고
지금 코드는 공개 embed를 쓰므로, 위 설정을 안 맞춰도 지도는 이미 동작해.
Map Forecast 키를 Streamlit에 다시 붙이려면 도메인을 꼭 맞춰야 하고, embed만 쓸 거면 Domain 설정은 필수는 아니야.




14 sources


이렇게 채워넣었는데 맞게 넣은걸까?


5s동안 작업함
지금 입력은 칸이 서로 바뀌어 있어. 아래처럼 바꾸면 돼.

올바른 입력
항목	넣을 내용	예시
Domain restrictions	도메인만 (선택)	localhost, streamlit.app
Project identification	앱/사이트 이름 또는 URL (필수)	물때 선상낚시 도우미
추천 입력값
Domain restrictions (선택)

localhost, streamlit.app
로컬만 쓰려면 localhost 만, 또는 비워 두기
Cloud도 쓰려면 Streamlit 주소의 도메인 추가
예: 앱 URL이 https://fishing-tide-app-xxxx.streamlit.app 이면
localhost, fishing-tide-app-xxxx.streamlit.app
또는 넓게 localhost, streamlit.app
Project identification (필수)

물때 선상낚시 도우미
또는

https://fishing-tide-app-fvlfcpazego5dqt8jcxz.streamlit.app
따옴표(")와 or 문구는 넣지 마세요.

지금 화면에서 잘못된 점
칸	현재 값	문제
Domain restrictions	물때 선상낚시 도우미	도메인이 아님 → 프로젝트 이름
Project identification	"localhost" or "fishing-..."	따옴표·or 포함, 형식 불일치
다시 채운 예
Domain restrictions:
localhost, streamlit.app

Project identification:
물때 선상낚시 도우미
Save 누른 뒤 1~2분 기다렸다가 앱을 새로고침해 봐.

참고: 지금 앱은 공개 embed로 지도를 보여 주므로, 이 설정을 안 맞춰도 지도는 동작해. Map Forecast 키를 다시 쓸 때만 위 도메인 설정이 중요해.



다음 내용을 참조하세요:


17s동안 작업함
지금 올려둔 최신 코드는 이미 공개 embed만 쓰고, API 키를 안 넣어요.
화면에 403이 나온다는 건 예전 버전(Map Forecast + 키) 이 아직 실행 중이라는 뜻이야.

해야 할 일
아래 app.py로 덮어쓰기
로컬: C:\fishing_tide_app\app.py 교체
Cloud: GitHub에 같은 파일 push 후 재배포
앱 완전 재시작
로컬: 실행 창 끄고 run.bat 다시
Cloud: 배포 완료 후 브라우저 강력 새로고침 (Ctrl+Shift+R)
(선택) secrets의 WINDY_API_KEY는 지워도 됨
embed는 키가 필요 없음
app.py

확인 방법
지도 아래 캡션이 이렇게 나오면 최신판이야.

Windy embed · 인천 (37.46, 126.71)
빨간 403 + unauthorized domain 이면 아직 구버전.

교체·재실행 후에도 같으면, 로컬인지 Cloud인지 알려줘.

임베드 방식과 API 방식의 차이는 무엇이야?


3s동안 작업함
Windy 임베드와 API(Map Forecast) 차이는 이렇게 보면 돼.

한 줄 요약
임베드 (embed)	API (Map Forecast)
방식	Windy 지도를 그대로 가져와 보여 줌	우리 페이지 안에 Windy 엔진을 심어 제어
키	불필요	필요 + 도메인 등록
커스터마이즈	적음 (URL 파라미터 정도)	많음 (레이어·마커·이벤트 등)
1. 임베드 방식 (지금 앱)
https://embed.windy.com/embed2.html?lat=...&lon=...&overlay=wind
Windy 사이트의 미리 만든 지도 화면을 iframe으로 넣음
바람·파고 등 레이어는 Windy가 제공
API 키·도메인 제한 없음
Streamlit / 로컬 / Cloud 모두 잘 됨
장점: 설정 간단, 403 없음, 유지보수 적음
단점: 지도 UI·기능을 Windy가 정함, 세밀한 조작 어려움

2. API 방식 (Map Forecast)
windyInit({ key: "발급키", lat, lon, overlay: "wind" }, ...)
Leaflet + Windy 라이브러리로 우리 HTML 안에 지도 생성
키로 인증하고, 허용된 도메인에서만 동작
마커, 레이어 전환, 클릭 이벤트 등 코드로 제어 가능
장점: 출조 포인트 표시, 레이어 자동 전환, 앱 UI와 일체감
단점: 키·도메인 설정, Streamlit에서 스크립트/도메인 이슈 많음, 상용은 유료

→ 예전에 본 unauthorized domain 403이 이 방식의 제한이야.

비교 표
항목	임베드	API
API 키	없음	필요
도메인 등록	없음	필요 (localhost, xxx.streamlit.app)
바람/파고 지도	가능	가능
위치 지정	URL로 가능	코드로 가능
마커·커스텀 UI	제한적	자유로움
Streamlit 호환	좋음	까다로움
비용	무료	테스트 무료 / 상용 유료
우리 앱에선
지금은 임베드 → 안정적으로 해상 날씨 지도 표시
API는 나중에 “출조 포인트 여러 개 표시”, “파고 레이어 자동 전환” 같이 지도와 앱을 깊게 연동할 때 다시 검토하면 됨
일상적인 “이 지역 바람·파고 보기”에는 임베드로 충분해.

난 API 방식으로 하고 싶어


6s동안 작업함
사용자에 의해 요청이 중단되었습니다.

그런데 아직도 403 오류창이 떠


55s동안 작업함
403이 계속 뜨는 이유와 선택지를 정리했어.

왜 Streamlit에서 API가 403인가
Map Forecast API는 허용된 도메인에서만 키를 쓸 수 있어.

Streamlit 지도는 components.html iframe 안에 그려지는데, 이때 주소(origin)가 종종:

null 이거나
등록한 localhost / xxx.streamlit.app 과 다르게 잡힘
그래서 키·도메인을 맞춰도 앱 안에서는 403이 날 수 있어.
(Windy 쪽 보안 정책 + Streamlit 구조 한계)

지금 코드
모드	동작
공개 embed (권장)	키 없이 지도 표시, 403 없음
Map Forecast API (실험)	키 사용 시도 — 도메인 맞으면 성공, 아니면 403
상세 화면 지도 위에서 라디오로 방식 선택 가능.

app.py

파일 덮어쓰기 → 앱 재시작
지도 위 「공개 embed (권장)」 선택 → 403 없어야 함
API를 쓰려면 「Map Forecast API」 선택 + 키 도메인 설정
API를 꼭 쓰고 싶을 때
api.windy.com/keys
Domain restrictions
로컬 테스트: 비워 두기 또는 localhost
Cloud: 본인앱.streamlit.app 또는 streamlit.app
Project identification: 물때 선상낚시 도우미
Save 후 수 분 대기 → 앱에서 API 모드 다시 시도
그래도 403이면 Streamlit iframe 한계일 가능성이 큼.
그때는 공개 embed로 지도 표시 + 필요 시 Windy.com 새 탭이 현실적인 방법이야.

먼저 embed 모드로 지도가 정상인지 확인해 줘.



다음 내용을 참조하세요:


22s동안 작업함
지금 화면 캡션이 Windy Map Forecast 이라서, 아직 예전 app.py가 돌아가고 있어.
최신 파일은 캡션이 Windy 공개 embed 로 나와.

반드시 할 일
아래 app.py 다운로드 후
로컬: C:\fishing_tide_app\app.py 완전히 교체
Cloud: GitHub에 올린 뒤 Redeploy
실행 중인 Streamlit 종료 후 다시 실행
run.bat
브라우저 강력 새로고침 (Ctrl + Shift + R)
날짜 다시 선택 → 지도 아래 글자 확인
캡션	의미
Windy 공개 embed · 인천 ...	✅ 최신 (403 없음)
Windy Map Forecast · ... · wind	❌ 구버전 (403 남)
app.py

이 버전은 API 키를 전혀 쓰지 않고 embed만 쓰므로, 파일이 제대로 바뀌면 빨간 403 창은 사라져야 해.

조위 정보와 낚시 지수 해결방법은?


3s동안 작업함
조위·낚시지수는 코드 버그보다 apis.data.go.kr 연결 문제에 가깝다. 해결 방향을 정리하면 아래와 같아.

원인
환경	증상
Streamlit Cloud	ConnectTimeout 자주 발생 (해외 서버 → 한국 공공망)
로컬	될 때도 있고, 서버 상태에 따라 타임아웃
앱은 실패 시 추정 만조/간조로 넘어가게 되어 있음.

해결 방법 (우선순위)
1. 로컬에서 쓰기 (가장 확실)
한국 PC에서 실행하면 Cloud보다 잘 되는 경우가 많음.

cd C:\fishing_tide_app
run.bat
→ http://localhost:2424

2. 공공데이터 포털 상태 확인
data.go.kr / API 활용신청 상태
브라우저에서 https://apis.data.go.kr 접속 여부
조위·바다낚시지수 각각 활용신청·승인 여부
키가 조위용만 되고 낚시지수 미신청이면 한쪽만 실패할 수 있음.

3. secrets 키 확인
DATA_GO_KR_SERVICE_KEY = "발급받은_일반인증키"
디코딩된 키 / 인코딩 키 혼동 주의
포털에서 서비스별 활용신청 필요 여부 확인
4. Cloud에서 쓸 때 현실적 대응
항목	Cloud
물때 달력	✅ 동작
추정 만조/간조	✅ 동작
실측 조위 API	❌ 불안정 → 추정값 사용
낚시지수 API	❌ 불안정
날씨·Windy embed·AI	✅ 대체로 동작
Cloud는 추정 조위 + 물때로 두고, 실측이 필요할 때만 로컬을 쓰는 구성이 현실적이다.

5. 근본 해결 (선택)
한국 리전 서버에 배포하면 공공 API가 안정적임.

Naver Cloud, AWS 서울, 가비아 등 VPS
여기에 Streamlit 실행
비용·관리가 들어감.

지금 앱 동작
조위 API 시도 (짧게 대기)
  → 성공: 관측소 실측 표시
  → 실패: "추정 만조/간조" 표시 후 다음 항목 진행
낚시지수도 동일하게, 실패해도 날씨·추천·AI는 계속 나옴.

체크리스트
로컬에서 조위가 되는지 확인
되면 → Cloud 네트워크 문제로 확정
로컬도 안 되면 → 키·활용신청·data.go.kr 장애 확인
Cloud만 쓸 거면 → 추정 조위로 운영해도 출조 참고용으로는 충분
원하면 조위 실패 시 문구를 더 짧게, 또는 재시도 버튼만 넣는 수정도 가능해요.

로컬로 운영하면서 모바일로 접근하고 싶은데?


8s동안 작업함
로컬 PC에서 실행한 앱을 같은 Wi-Fi의 휴대폰으로 보는 방법이야.

1. 조건
PC와 휴대폰이 같은 Wi-Fi
PC에서 Streamlit 실행 중
공유기 게스트 네트워크 분리·AP 격리가 꺼져 있는 것이 좋음
2. Streamlit을 외부(폰)에서 받게 실행
run.bat 대신 아래처럼 실행하거나, bat를 수정한다.

cd C:\fishing_tide_app
venv\Scripts\activate
python -m streamlit run app.py --server.port 2424 --server.address 0.0.0.0
0.0.0.0 → 같은 네트워크 기기에서 접속 가능
localhost만 쓰면 폰에서는 안 열림
3. PC IP 확인 (Windows)
cmd:

ipconfig
무선 LAN 어댑터의 IPv4 주소 예:

192.168.0.15
4. 휴대폰 브라우저에서
http://192.168.0.15:2424
(본인 PC IP + 포트)

5. 안 열릴 때
원인	해결
Windows 방화벽	인바운드에 포트 2424 허용
address 미설정	--server.address 0.0.0.0 확인
다른 Wi-Fi	PC·폰 같은 네트워크인지 확인
모바일 데이터	Wi-Fi로 전환
방화벽 빠른 허용 (관리자 cmd):

netsh advfirewall firewall add rule name="Streamlit 2424" dir=in action=allow protocol=TCP localport=2424
6. run.bat 수정 예
@echo off
cd /d "%~dp0"
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
echo.
echo  폰에서 접속: http://PC의IPv4:2424
echo  (ipconfig 로 IPv4 확인)
echo.
python -m streamlit run app.py --server.port 2424 --server.address 0.0.0.0
pause
7. 홈 화면에 아이콘 (선택)
아이폰

Safari로 위 주소 접속
공유 → 홈 화면에 추가
안드로이드

Chrome으로 접속
메뉴 → 홈 화면에 추가 / 앱 설치
참고
방식	범위
같은 Wi-Fi + 0.0.0.0	집/사무실 안 폰만
집 밖·다른 망	Cloud 배포 또는 터널(ngrok 등) 필요
집 안·같은 Wi-Fi 기준이면 IP:2424 로 충분해.
run.bat을 위 내용으로 바꿔 줄까?

서로 다른 네트워크일 경우는?


5s동안 작업함
다른 네트워크(집 밖, LTE, 다른 Wi-Fi)에서는 집 PC의 192.168.x.x 주소로 접속할 수 없어.
밖에서 쓰려면 아래 중 하나를 써야 해.

선택지 비교
방법	난이도	비용	조위 API	추천
1. Streamlit Cloud	쉬움	무료	불안정할 수 있음	외부 공유에 가장 무난
2. 터널 (ngrok 등)	중간	무료~	로컬과 동일(한국망)	잠깐 테스트·지인 공유
3. 공유기 포트포워드	중~상	무료	로컬과 동일	보안·설정 부담
4. 한국 VPS	상	유료	비교적 안정	장기 운영
1. Streamlit Cloud (이미 해본 방식)
GitHub에 코드 올리고 Cloud 배포
주소 예: https://xxx.streamlit.app
어디서든 폰·PC 접속 가능
조위/낚시지수는 Cloud ↔ data.go.kr 때문에 가끔 타임아웃 가능
→ 외부에서 쓰기엔 제일 단순

2. 터널 (로컬 앱을 밖으로 잠깐 열기)
PC에서 앱 실행 + 터널 프로그램이 임시 공개 URL을 만들어 줌.

Cloudflare Tunnel (무료 추천) 또는 ngrok

예: ngrok

ngrok http 2424
나오면 예:

https://abcd-12-34-56-78.ngrok-free.app
이 주소를 폰(다른 망)에서 열면 됨.

장점	단점
로컬과 같은 환경 (조위 API도 로컬처럼)	PC 켜 두고 터널도 실행 중이어야 함
설정이 비교적 쉬움	무료는 URL이 바뀔 수 있음
3. 공유기 포트 포워드
공유기에서 외부 포트 → PC 2424 연결
휴대폰에서 http://공인IP:2424
보안·동적 IP·통신사 차단 이슈가 있어 비추천 (초보·개인용).

4. 한국 VPS에 올리기
NCP, AWS 서울 등에 Streamlit 상시 실행
→ 고정 URL + 공공 API도 상대적으로 안정.

상황별 추천
목적	추천
밖에 나가서 폰으로 보기	Streamlit Cloud
조위 API까지 꼭 로컬처럼	터널(ngrok/Cloudflare) + PC 켜 두기
지인에게 잠깐만 링크	ngrok
오래 안정적으로	Cloud 또는 한국 VPS
정리:
다른 네트워크에서는 같은 Wi-Fi 방식이 안 되고,
Cloud 배포 또는 터널이 현실적인 답이야.

원하면 ngrok / Cloudflare Tunnel 중 하나로 단계별 설정만 골라서 적어 줄게.

Cloudflare Tunnel (무료 추천) 으로 방법 안내해줘


4s동안 작업함
Cloudflare Tunnel(무료) 로 집 PC Streamlit을 다른 네트워크·폰에서 쓰는 방법이야.

전체 흐름
폰(LTE 등) → Cloudflare → 터널 → 집 PC:2424 Streamlit
PC가 켜져 있고, Streamlit + 터널이 실행 중이어야 해.

1. Cloudflare 계정
https://dash.cloudflare.com/sign-up 가입
이메일 인증
도메인이 없어도 Quick Tunnel로 바로 쓸 수 있음. (아래 3-A)

2. cloudflared 설치 (Windows)
다운로드:
https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
→ Windows (amd64)
또는 직접:
https://github.com/cloudflare/cloudflared/releases 에서 cloudflared-windows-amd64.exe
예: C:\cloudflared\cloudflared.exe 에 저장
(이름만 cloudflared.exe 로)
확인 (cmd):
cd C:\cloudflared
cloudflared.exe --version
3. 터널 실행
방법 A — Quick Tunnel (가장 간단, 도메인 불필요)
1) Streamlit 먼저 실행

cd C:\fishing_tide_app
venv\Scripts\activate
python -m streamlit run app.py --server.port 2424 --server.address 0.0.0.0
2) 새 cmd 창에서:

cd C:\cloudflared
cloudflared.exe tunnel --url http://127.0.0.1:2424
3) 출력 예:

https://random-words-1234.trycloudflare.com
이 https 주소를 폰·다른 PC에서 열면 됨.

장점	단점
가입 직후 바로 사용	실행할 때마다 URL이 바뀜
도메인·설정 거의 없음	PC+터널이 켜져 있어야 함
방법 B — Named Tunnel (고정에 가까움, 도메인 있을 때)
본인 도메인을 Cloudflare에 연결한 경우:

cloudflared.exe tunnel login
cloudflared.exe tunnel create fishing-tide
cloudflared.exe tunnel route dns fishing-tide tide.내도메인.com
cloudflared.exe tunnel run --url http://127.0.0.1:2424 fishing-tide
도메인이 없으면 방법 A만 쓰면 된다.

4. 한 번에 켜는 bat 예
C:\fishing_tide_app\run_tunnel.bat 예시:

@echo off
cd /d C:\fishing_tide_app
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat

echo [1/2] Streamlit 시작 (포트 2424)...
start "Streamlit" cmd /k "python -m streamlit run app.py --server.port 2424 --server.address 0.0.0.0"

timeout /t 5 /nobreak >nul

echo [2/2] Cloudflare Tunnel 시작...
cd /d C:\cloudflared
cloudflared.exe tunnel --url http://127.0.0.1:2424

pause
Streamlit 창 + 터널 창이 뜸
터널 창에 나온 https://….trycloudflare.com 을 복사해 폰에서 접속
5. 사용 시 주의
항목	내용
PC	절전/종료하면 접속 끊김
두 프로그램	Streamlit + cloudflared 둘 다 실행
URL	Quick Tunnel은 재실행 시 주소 변경
secrets	로컬 .streamlit/secrets.toml 그대로 사용 (조위 API도 로컬망 기준)
보안	링크 아는 사람만 접속 가능에 가깝지만, 공개 URL이므로 지인 공유 수준으로
6. 접속 확인 순서
PC에서 Streamlit localhost:2424 정상인지
cloudflared tunnel --url http://127.0.0.1:2424 실행
나온 https://….trycloudflare.com 을 PC 브라우저로 한 번 열기
같은 주소를 휴대폰 LTE로 열기
정리: 도메인 없이 쓰려면 Quick Tunnel이 맞고,
cloudflared tunnel --url http://127.0.0.1:2424 한 줄이 핵심이야.

설치 중 버전·경로에서 막히면 그때 메시지를 그대로 보내 줘.

윈디 임베드에서 날짜 이동을 해도 시뮬레이션 이미지가 변경안되는데 방법이 없어?


43s동안 작업함
결론부터: 공개 embed만으로는 앱에서 고른 날짜로 시뮬레이션이 잘 안 바뀌는 경우가 많아. Windy 쪽 제한에 가깝다.

왜 안 바뀌나
방식	날짜 지정
embed (embed.windy.com)	calendar=now 중심. 선택일을 URL로 넘기는 공식 지원이 약함
Windy 본문 (windy.com/?날짜-시,위도,경도,줌)	예보 시각 지정 가능
Map Forecast API	timestamp로 가능 (도메인 403 이슈)
그래서 앱 달력 날짜를 바꿔도 iframe 안 바람 애니메이션이 그대로인 것처럼 보일 수 있어.

쓸 수 있는 방법
embed 안 하단 타임라인
직접 스크롤해서 날짜·시간 이동 (가장 확실)
「선택일 기준 Windy 전체 화면」 링크 (코드에 반영함)
예: https://www.windy.com/?2026-08-15-12,37.45,126.71,8
→ 선택일 정오 예보로 본문 지도 오픈
Map Forecast API
시각 제어는 되지만 Streamlit에서 도메인 403이 자주 남
코드 변경
선택 날짜가 오늘 이후이면
「선택일(YYYY-MM-DD) 기준으로 Windy 전체 화면 열기」 링크 표시
embed는 위치·바람 레이어 유지, 날짜는 전체화면/타임라인 이용
app.py

덮어쓴 뒤 재실행 → 날짜 선택 → 지도 아래 선택일 기준 전체 화면 링크로 확인해 봐.




16 sources
로컬에서 윈디API로 테스트 해보고 싶어. app.py 파일 만들어줘


56s동안 작업함
로컬에서 Windy Map Forecast API로 시험할 수 있게 준비해 뒀어.

1. secrets 설정
C:\fishing_tide_app\.streamlit\secrets.toml

WINDY_API_KEY = "발급받은_Map_Forecast_키"
2. 키 도메인 (중요)
api.windy.com/keys

항목	값
Domain restrictions	비움 또는 localhost
Project identification	물때 선상낚시 도우미
저장 후 1~2분 대기.

3. 방법 A — 메인 앱에서 테스트
app.py (키 있으면 API 모드)

cd C:\fishing_tide_app
python -m streamlit run app.py --server.port 2424 --server.address localhost
날짜 선택 → 지도에 「Map Forecast API 모드」 가 보이면 성공.
403이면 Domain을 비웠는지 다시 확인.

4. 방법 B — HTML 단독 테스트 (더 확실)
Streamlit iframe origin 문제를 피하려면 일반 브라우저 + localhost 서버가 낫다.

windy_api_local.html

cd C:\fishing_tide_app
python -m http.server 8080
브라우저에서:

http://localhost:8080/windy_api_local.html
API 키 붙여넣기
지도 로드 클릭
여기서 OK면 키·도메인은 정상이야.

정리
결과	의미
HTML(8080) OK, Streamlit 403	Streamlit iframe origin 문제 → 앱은 embed, API는 HTML로 테스트
둘 다 403	Domain restrictions / 키 종류(Map Forecast인지) 확인
둘 다 OK	로컬 API 연동 성공
먼저 방법 B(HTML) 로 키 동작을 확인하는 걸 추천해.



우선 맵이 안뜨는데?


32s동안 작업함
화면이 「Windy에서 인천 해상 날씨 보기」 링크만 있는 건 구버전 app.py야.
최신 파일에는 지도 iframe이 들어 있어.

할 일
아래 app.py 다운로드 후
C:\fishing_tide_app\app.py 덮어쓰기
Streamlit 완전 종료 후 다시 실행
run.bat
브라우저 Ctrl+Shift+R
날짜 다시 선택
정상일 때 날씨 카드 아래에:

제목: 해상 지도 (Windy)
지도(바람 레이어) 가 보여야 함
캡션: Windy 공개 embed · 인천 ...
app.py

링크만 보이면 아직 예전 파일이 실행 중인 거야.
덮어쓴 뒤에도 같으면, 실행 중인 폴더 경로가 C:\fishing_tide_app 이 맞는지 확인해 줘.



다음 내용을 참조하세요:


21s동안 작업함
HTML 테스트에서도 403이면 키 도메인 설정 또는 파일 여는 방식 문제야.

1. 주소 확인 (가장 흔함)
file:// 로 열면 origin이 없어서 항상 403이 난다.

잘못된 예	올바른 예
file:///C:/fishing_tide_app/windy_api_local.html	http://localhost:8080/windy_api_local.html
올바른 실행:

cd C:\fishing_tide_app
python -m http.server 8080
브라우저 주소창에 직접:

http://localhost:8080/windy_api_local.html
탭에 localhost:8080 이 보여야 해. (windy_api_local.html만 보이면 파일로 연 것일 수 있음)

2. 키 Domain 설정 다시 확인
api.windy.com/keys → 해당 키 수정

항목	넣을 값
Domain restrictions	비워 두기 (로컬 테스트에 가장 좋음)
또는 정확히 localhost 만	
Project identification	물때 선상낚시 도우미
넣으면 안 되는 예:

물때 선상낚시 도우미 ← Domain 칸에 넣음 (잘못)
streamlit.app 만 있고 localhost 없음
http://localhost:8080 (스키마·포트 포함)
Save 후 2~3분 기다렸다가 다시 지도 로드.

3. 키 종류
Map Forecast 키여야 해.
Point Forecast / Webcams 키는 지도 API에 쓸 수 없음.

4. 그래도 403이면
Domain을 완전히 비운 새 키를 하나 더 발급
새 키로 HTML에서 다시 테스트
콘솔에 더 이상 Failed to authorize 가 없는지 확인
앱 지도는
메인 app.py는 공개 embed(키 없음)로 지도를 보여 주도록 되어 있어.
API 403과 별개로, 최신 app.py를 쓰면 앱 안에서는 지도가 떠야 해.

지금은:

http://localhost:8080/... 로 여는지
Domain 비움 또는 localhost 만 있는지
이 두 가지만 다시 확인해 줘.



다음 내용을 참조하세요:


10s동안 작업함
404는 서버는 떴는데 그 폴더에 HTML 파일이 없다는 뜻이야.

우리가 만든 windy_api_local.html은 아직 PC에 없을 수 있어. 파일을 받아서 서버를 같은 폴더에서 실행해야 해.

1. 파일 받기
아래 파일을 다운로드해서 저장:

경로 예: C:\fishing_tide_app\windy_api_local.html

2. 서버 실행 (파일 있는 폴더에서)
cd C:\fishing_tide_app
dir windy_api_local.html
python -m http.server 8080
dir 결과에 windy_api_local.html 이 보여야 해.
없으면 파일이 다른 곳에 저장된 것.

3. 브라우저 주소
http://localhost:8080/windy_api_local.html
http://localhost:8080/ 만 열면 파일 목록이 보임 → 목록에서 windy_api_local.html 클릭해도 됨
file:///C:/... 로 열면 안 됨 (API 403 원인)
4. 체크
확인	내용
파일 위치	C:\fishing_tide_app\windy_api_local.html
cmd 현재 폴더	C:\fishing_tide_app
URL	http://localhost:8080/windy_api_local.html
Domain	키 설정에서 비움 또는 localhost
파일 저장 위치와 cd 한 폴더가 같으면 404는 사라져.

로컬호스트에서 API로 데이터 수신이 됨을 확인했어. 이제 위의 app.py에 윈디 API를 적용한 버전으로 app를 다운로드 받을 수 있게 해줘


32s동안 작업함
Windy Map Forecast API가 적용된 app.py야.

동작
조건	지도
WINDY_API_KEY 있음	Map Forecast API (바람 레이어 + 지역 마커, 선택일 timestamp)
키 없음	공개 embed
secrets.toml
WINDY_API_KEY = "로컬에서 확인한_Map_Forecast_키"
Domain은 로컬 테스트와 같이 비움 또는 localhost.

실행
cd C:\fishing_tide_app
python -m streamlit run app.py --server.port 2424 --server.address localhost
사이드바에 ✅ Windy Map Forecast API 키 로드됨 → 날짜 선택 → 해상 지도 확인.

app.py

덮어쓴 뒤 앱을 재시작하고 날짜를 눌러 봐.





html 테스트에선 잘되었으나 앱에 코드로 적용했을때는 윈디 API가 잘안되는데?


1m 47s동안 작업함
원인은 이거야.

환경	origin	결과
http://localhost:8080/windy_api_local.html	localhost	✅ OK
Streamlit components.html	null	❌ 403
앱 안에서는 HTML을 localhost 서버로 연 뒤 iframe으로 넣도록 바꿨어. (HTML 테스트와 같은 방식)

변경 내용
앱이 windy_runtime.html 생성
백그라운드에서 http://127.0.0.1:8765 로 앱 폴더 서빙
지도를 그 주소 iframe으로 표시 → origin=localhost → API 허용
app.py

사용
파일 덮어쓰기
Streamlit 재시작 (run.bat)
날짜 선택 → 해상 지도
캡션 예: Windy Map Forecast API · localhost:8765 · 인천 ...

방화벽이 8765를 막으면, 앱 폴더에서 수동으로:

python -m http.server 8765
를 한 번 더 실행하면 돼.

steamlit도 iframe 방식으로 윈디API를 넣을 순 없나?


2s동안 작업함
가능해. 그게 지금 최신 app.py가 쓰는 방식이야.

Streamlit + Windy API = iframe이 맞는 이유
방식	origin	Windy API
st.components.v1.html(...) (코드 직접 삽입)	null	❌ 403
st.components.v1.iframe("http://localhost:...")	localhost	✅
HTML 테스트가 된 이유와 같고, Streamlit도 iframe으로 localhost HTML을 띄우면 API를 쓸 수 있어.

지금 앱 구조
[Streamlit 화면]
    └── iframe → http://127.0.0.1:8765/windy_runtime.html
                      ↑
              앱이 만든 HTML (키·좌표·마커 포함)
              로컬 static 서버가 서빙 (origin = localhost)
WINDY_API_KEY로 windy_runtime.html 생성
127.0.0.1:8765 에서 폴더 서빙
st.components.v1.iframe(...) 으로 표시
사용 시
최신 app.py 덮어쓰기
secrets에 WINDY_API_KEY
Domain: 비움 또는 localhost
run.bat 재실행 → 날짜 선택
캡션에 localhost:8765 가 보이면 iframe 방식으로 동작 중인 거야.

정리: Streamlit도 iframe으로 Windy API 가능하고, 직접 html()에 스크립트를 넣는 방식만 피하면 돼. 최신 코드가 이미 그 구조야.



다음 내용을 참조하세요:


54s동안 작업함
Cloud에서 회색 깨진 그림이 나온 이유야.

캡션에 localhost:8765 가 보이는데,
Streamlit Cloud 화면은 사용자 폰/PC 브라우저에서 열리므로 localhost = 그 기기의 PC야.
Cloud 서버가 아니어서 iframe이 비어 보인다.

수정
환경	Windy
로컬 (localhost:2424) + API 키	Map Forecast API (localhost iframe)
Streamlit Cloud	공개 embed (항상 지도 표시)
app.py

로컬: 파일 덮어쓰기 후 재실행 → API 지도
Cloud: GitHub에 올린 뒤 Redeploy → embed 지도
Cloud 캡션 예: Windy 공개 embed · 인천 ...
(더 이상 localhost:8765 가 아니어야 함)

정리: Windy API는 로컬, Cloud는 embed가 맞다.

지금까지 만든 서비스에서 CHATGPT API 연계가 유료서비스다 보니 부담이 되서 AI 가이드 기능을 제외하고 싶어. AI 가이드를 제외하고 그 영역에 블로그나 카페글 링크를 올리는건 어떨까?


1m 13s동안 작업함
좋은 방향이야. 유료 ChatGPT 조언은 빼고, 그 자리에 네이버 블로그·카페 조행기 링크를 넣었어.

변경 요약
이전	이후
🤖 AI 낚시조언 버튼 + GPT 생성	📰 조행기 · 카페 글 링크 목록
OpenAI API 호출 (유료)	네이버 검색 API만 사용
추천 어종	그대로 (네이버 빈도 기반)
조행기 영역
추천 어종 + 지역 + 월로 블로그/카페 검색
제목 · 출처 · 날짜 · 요약 + 클릭 링크
「조행기 다시 검색」으로 새로고침
OpenAI
사이드바에서 더 이상 필수로 안 씀
OPENAI_API_KEY는 secrets에서 지워도 됨 (비용 절감)
app.py

덮어쓴 뒤 재실행 → 날짜 선택 → 오른쪽에 조행기 링크가 보이면 정상이야.
네이버 키가 있어야 링크가 채워져.



조행기의 검색조건이 너무 빡빡한것 같아. 아래처럼 설계하면 어떨까?
1단계 추천어종 조행기 -> 2단계 해당 지역 조행기 -> 3단계 해당 월 조행기
이런순으로 진행하되 각 단계에서 해당되는 결과가 없을 경우 전단계의 결과를 출력하는 것으로


1m동안 작업함
좋은 방향이야. AI 가이드(유료 GPT)는 제외하고, 그 자리를 네이버 블로그·카페 조행기 링크로 바꿨어.

변경 요약
이전	이후
🤖 AI 낚시조언 버튼 + GPT 생성	📰 조행기 · 카페 글 링크 목록
OpenAI API 호출 (유료)	네이버 검색만 사용 (무료 할당량)
추천 어종	그대로 (네이버 빈도 기반)
조행기 영역
추천 어종 + 지역 + 월로 블로그/카페 검색
제목 · 출처 · 날짜 · 요약 + 클릭 링크
「조행기 다시 검색」으로 새로고침
OpenAI
사이드바에서 더 이상 필수로 안 씀
OPENAI_API_KEY는 secrets에서 지워도 됨 (비용 절감)
app.py

덮어쓴 뒤 재실행 → 날짜 선택 → 오른쪽에 조행기 링크가 보이면 정상이야.
네이버 키가 있어야 링크가 채워져.



깃허브에 변경승인이 안눌러지고 비활성화 되었어 이유가 뭐야?


21s동안 작업함
GitHub 웹 편집기에서 Commit changes가 비활성화되는 흔한 이유는 아래와 같아.

1. 커밋 메시지가 비어 있음 (가장 흔함)
버튼을 누르기 전에 아래로 스크롤해서:

Commit message 칸에 내용을 입력해야 함
예: AI 제거, 조행기 링크로 변경
메시지 없이 저장하려고 하면 버튼이 안 눌리거나 비활성으로 보여.

2. 변경 내용이 없다고 판단된 경우
이미 같은 내용이 main에 있으면 커밋할 게 없음
또는 붙여넣기가 제대로 안 돼서 파일이 이전과 동일
에디터에서 글자 하나라도 수정해 보거나, 커밋 메시지 칸을 눌러 봐.

3. 파일 크기 / 웹 편집 한계
app.py가 길면 웹 편집기가 불안정하거나 커밋이 막힐 수 있어.
이때는 웹에서 붙여넣기 대신:

로컬에서 파일 수정
GitHub 웹 → Add file → Upload files 로 app.py 업로드
커밋 메시지 입력 후 커밋
또는 GitHub Desktop 사용.

4. 권한 / 브랜치 보호
본인 저장소가 아니거나
main에 직접 커밋이 막혀 있으면
버튼이 비활성일 수 있어.
본인 계정 jaicob1221/fishing-tide-app 이고 collaborator면 보통은 가능.

추천 진행 순서
아래로 스크롤 → 커밋 메시지 입력 (AI 제거, 조행기 링크 추가)
그래도 안 되면 → Upload files로 app.py 통째로 업로드
Cloud 앱 Manage app → Reboot 또는 재배포
로컬에서 이미 API 지도가 되면, Cloud에는 이 버전을 올린 뒤 embed로 지도가 보이게 하면 돼.



조행기 가페글에 검색된 내용이 없는 상태야. 다시 수정해줘


24m 5s동안 작업함
조행기 검색이 비어 나오던 원인을 고쳤어.

수정 내용
fetch_joghaengi_links를 단계적 캐스케이드로 다시 짬

1단계 – 추천어종 중심
광어 선상 조행기, 인천 광어 조행기, 8월 광어 조행기 등
2단계 – 지역 중심
인천 선상 조행기, 인천 조행기 등
3단계 – 월/일반
8월 선상 조행기, 선상 조행기 등
결과가 부족하면 다음 단계로 넘어가고, 필터도 훨씬 느슨하게 바꿨어.
그래도 비면 필터 없이 한 번 더 검색해서라도 링크를 채우도록 했음.

추가로:

네이버 검색을 sort=date(최신순) 기본으로 변경
_requests_get_retry + SSL 대응 적용
관련성 점수 높은 글이 위로 오도록 정렬
사용 방법
app.py 저장 후 앱 재실행 (또는 그냥 「🔄 조행기 다시 검색」 버튼 클릭)
캐시가 비워지면서 새로 검색됨
이제 인천 + 8월 기준으로도 링크가 나올 거야.
다시 확인해 보고, 아직도 비면 알려줘.

1단계 – 추천어종 중심 광어 선상 조행기, 인천 광어 조행기, 8월 광어 조행기 등
2단계 – 1단계의 검색 결과내에서 선택 지역으로 필터
3단계 – 2단계의 검색 결과에서 선택월과 인접한 게시글 필터
 
위 처럼 단계적 스케이드를 적용하고 3단계에서 필터된 결과가 없을시 2단계로 하향, 2단계에서 검색결과가 없을시 1단계로 하향하여 게시글의 제목을 표시하고 해당 제목을 클릭시 iframe으로 게시글 본문을 볼 수 있도록 연계


2m 6s동안 작업함
요청한 대로 조행기 검색 로직을 바꿨어.

변경된 캐스케이드
1단계 – 추천어종 중심 검색
광어 선상 조행기, 광어 조행기, 인천 광어 조행기, 8월 광어 조행기 등으로 풀을 모음
2단계 – 1단계 결과 안에서 선택 지역 필터
제목/요약에 인천(또는 영종·강화 등)이 들어간 글만 남김
3단계 – 2단계 결과 안에서 선택월 ± 인접월(±1) 게시일 필터
예: 8월 선택 → 7·8·9월 글만
3단계 결과 없음 → 2단계로 하향
2단계 결과 없음 → 1단계로 하향
화면에 지금 몇 단계 결과가 보이는지도 표시해 둠.

본문 보기 (iframe)
각 글 옆에 「보기」 버튼 추가
누르면 아래에 iframe으로 본문 시도 + 「원문 새 탭에서 열기」 버튼
네이버 블로그/카페는 X-Frame-Options로 iframe을 막는 경우가 많아서, 안 보이면 새 탭 버튼으로 열면 됨
사용법
app.py 저장 후 앱 재실행
「🔄 조행기 다시 검색」 클릭해서 캐시 비우기
글 목록에서 보기 눌러서 본문 확인
다시 테스트해 보고 결과 알려줘.

app 파일 다운로드 할 수 있게 해줘


8s동안 작업함
app.py 파일 다운로드할 수 있게 준비했어.

위 파일에서 다운로드하면 돼.

1단계 검색을 광어 선상 낚시, 농어 선상 낚시, 우럭 출조, 광어 선상 출조 등으로 좀 포괄적 검색을 해줘


48s동안 작업함
1단계 검색어를 더 포괄적으로 바꿨어.

바뀐 1단계 검색어 예시 (어종당)
광어 선상 조행기
광어 선상 낚시
광어 선상 출조
광어 출조
광어 조행기
광어 선상
인천 광어 선상
인천 광어 출조
8월 광어 선상
8월 광어 출조
조행기뿐 아니라 낚시·출조 표현까지 넣어서 풀을 넓게 모으고,
필터 키워드에도 출조를 추가했어.

풀이 50건 정도 모이면 추가 검색은 중단해서 API 호출도 과하게 안 나가게 해 둠.

앱 다시 실행하거나 「🔄 조행기 다시 검색」 눌러서 확인해 봐.

app 다운 할 수 있게 해줘


7s동안 작업함
app.py 다운로드할 수 있게 준비했어.




app.py
import streamlit as st
from datetime import date, datetime, timedelta, time
from korean_lunar_calendar import KoreanLunarCalendar
from openai import OpenAI
import calendar as cal
import os
from pathlib import Path
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
  <p class="subtitle">지역·월별 물때 달력 · 실측 날씨 · 추천 어종 · 조행기 링크</p>
</div>
""",
    unsafe_allow_html=True,
)



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


def _ssl_verify() -> bool:
    """로컬 인증서 문제 시 secrets SSL_INSECURE=true → verify 끄기"""
    try:
        if bool(st.secrets.get("SSL_INSECURE", False)):
            return False
    except Exception:
        pass
    if os.environ.get("SSL_INSECURE") == "1":
        return False
    return True


def _requests_get_retry(url: str, params: dict = None, timeout: int = 10, retries: int = 2, **kwargs):
    """외부 API 호출용 재시도 (SSL_INSECURE 지원)
    timeout/retries 기본값을 짧게 둬서 실패 시 화면이 오래 멈추지 않게 함.
    """
    import time
    last_err = None
    verify = kwargs.pop("verify", _ssl_verify())
    params = params or {}
    # connect timeout을 짧게 (tuple: connect, read)
    to = (min(6, timeout), timeout) if not isinstance(timeout, tuple) else timeout
    for i in range(retries):
        try:
            r = requests.get(url, params=params, timeout=to, verify=verify, **kwargs)
            return r
        except Exception as e:
            last_err = e
            if verify and ("SSL" in type(e).__name__ or "CERTIFICATE" in str(e).upper() or "SSLError" in str(type(e))):
                try:
                    r = requests.get(url, params=params, timeout=to, verify=False, **kwargs)
                    return r
                except Exception as e2:
                    last_err = e2
            if i < retries - 1:
                time.sleep(0.4)
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
        r = _requests_get_retry(url, params, timeout=8, retries=1)
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
        r = _requests_get_retry(url, params, timeout=8, retries=1)
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

        use_insecure = False
        try:
            use_insecure = bool(st.secrets.get("SSL_INSECURE", False))
        except Exception:
            pass
        if os.environ.get("SSL_INSECURE") == "1":
            use_insecure = True

        import httpx
        # 로컬 SSL/프록시 환경 대응: timeout 넉넉히
        http_client = httpx.Client(
            verify=not use_insecure,
            timeout=httpx.Timeout(60.0, connect=30.0),
        )
        return OpenAI(api_key=api_key, http_client=http_client)
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


def get_windy_api_key() -> str:
    try:
        k = st.secrets.get("WINDY_API_KEY", "") or ""
        if k and not str(k).startswith("여기에"):
            return str(k).strip()
    except Exception:
        pass
    return ""



def _is_streamlit_cloud() -> bool:
    """Streamlit Community Cloud 여부"""
    if Path("/mount/src").exists():
        return True
    if os.environ.get("STREAMLIT_SHARING_MODE"):
        return True
    host = (os.environ.get("HOSTNAME") or "") + (os.environ.get("SERVER_NAME") or "")
    if "streamlit" in host.lower():
        return True
    return False


def _ensure_local_static_server(port: int = 8765) -> bool:
    """앱 폴더를 localhost 로 서빙 (로컬 전용). Cloud 에서는 사용 안 함."""
    if _is_streamlit_cloud():
        return False
    if st.session_state.get("_windy_static_ok"):
        return True
    import threading
    from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

    app_dir = Path(__file__).resolve().parent

    class _Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(app_dir), **kwargs)

        def log_message(self, format, *args):
            pass

    try:
        import urllib.request
        urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=0.4)
        st.session_state["_windy_static_ok"] = True
        st.session_state["_windy_static_port"] = port
        return True
    except Exception:
        pass

    try:
        httpd = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        st.session_state["_windy_static_ok"] = True
        st.session_state["_windy_static_port"] = port
        return True
    except OSError:
        try:
            import urllib.request
            urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=0.4)
            st.session_state["_windy_static_ok"] = True
            st.session_state["_windy_static_port"] = port
            return True
        except Exception:
            return False


def _write_windy_runtime_html(key: str, lat: float, lon: float, region: str, ts_ms) -> Path:
    app_dir = Path(__file__).resolve().parent
    out = app_dir / "windy_runtime.html"
    ts_line = f"opts.timestamp = {int(ts_ms)};" if ts_ms else ""
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Windy</title>
<style>html,body,#windy{{margin:0;height:100%;width:100%;background:#0d1b2a}}</style>
</head>
<body>
<div id="windy"></div>
<script src="https://unpkg.com/leaflet@1.4.0/dist/leaflet.js"></script>
<script src="https://api.windy.com/assets/map-forecast/libBoot.js"></script>
<script>
var opts = {{
  key: {repr(key)},
  lat: {lat},
  lon: {lon},
  zoom: 8,
  overlay: "wind",
  level: "surface",
  detail: true,
  hourFormat: "24h"
}};
{ts_line}
windyInit(opts, function(api) {{
  L.marker([{lat}, {lon}]).addTo(api.map)
    .bindPopup({repr(str(region) + " 출조 해역")}).openPopup();
}});
</script>
</body>
</html>
"""
    out.write_text(html, encoding="utf-8")
    return out


def _render_windy_embed(lat, lon, region, date_str, height):
    embed_url = (
        "https://embed.windy.com/embed2.html?"
        f"lat={lat}&lon={lon}&detailLat={lat}&detailLon={lon}"
        "&zoom=8&level=surface&overlay=wind"
        "&menu=&message=true&marker=true&calendar=now"
        "&pressure=&type=map&location=coordinates&detail=true"
        "&metricWind=m/s&metricTemp=%C2%B0C&radarRange=-1"
    )
    if date_str:
        embed_url += f"&_appdate={date_str}"
    st.components.v1.iframe(embed_url, height=height, scrolling=False)
    st.caption(f"Windy 공개 embed · {region} ({lat:.2f}, {lon:.2f})")


def render_windy_map(lat: float, lon: float, region: str, date_str: str = None, height: int = 450):
    """Windy 지도
    - 로컬 + API 키 → localhost iframe (Map Forecast API)
    - Cloud / 키 없음 → 공개 embed
    """
    key = get_windy_api_key()
    on_cloud = _is_streamlit_cloud()

    time_token = None
    ts_ms = None
    if date_str:
        try:
            d = date.fromisoformat(date_str)
            if d >= date.today():
                time_token = d.strftime("%Y-%m-%d") + "-12"
                from datetime import timezone
                dt = datetime(d.year, d.month, d.day, 3, 0, 0, tzinfo=timezone.utc)
                ts_ms = int(dt.timestamp() * 1000)
        except Exception:
            pass

    # Cloud 에서는 localhost iframe 불가 → embed
    if key and not on_cloud:
        port = 8765
        ok = _ensure_local_static_server(port)
        _write_windy_runtime_html(key, lat, lon, region, ts_ms)
        if ok:
            bust = date_str or "now"
            map_url = f"http://127.0.0.1:{port}/windy_runtime.html?v={bust}-{lat}-{lon}"
            st.components.v1.iframe(map_url, height=height, scrolling=False)
            st.caption(f"Windy Map Forecast API · localhost:{port} · {region}")
        else:
            st.info("로컬 지도 서버를 쓰지 못해 공개 embed로 표시합니다.")
            _render_windy_embed(lat, lon, region, date_str, height)
    else:
        if on_cloud and key:
            st.caption("Cloud 환경: Windy는 공개 embed 사용 (API는 로컬 전용)")
        _render_windy_embed(lat, lon, region, date_str, height)

    if time_token:
        st.markdown(
            f"[🗺️ 선택일({date_str}) Windy 전체 화면](https://www.windy.com/?{time_token},{lat},{lon},8)"
        )
    else:
        st.markdown(f"[🗺️ Windy 전체 화면](https://www.windy.com/{lat}/{lon})")


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

    client = None  # AI 조언 기능 비활성화 (비용 절감). 조행기 링크 사용
    st.caption("AI 조언 기능 제외됨 · 조행기 링크 사용")

    nid, nsec = get_naver_credentials()
    if nid and nsec:
        st.success("✅ 네이버 검색 API 키 로드됨")
    else:
        st.warning("⚠️ NAVER_CLIENT_ID / SECRET 미설정")

    if get_windy_api_key():
        st.success("✅ Windy Map Forecast API 키 로드됨")
    else:
        st.caption("Windy: secrets에 WINDY_API_KEY 없으면 공개 embed 사용")

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
                items = naver_search(q, client_id, client_secret, kind=kind, display=20, sort="sim")
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


def naver_search(query: str, client_id: str, client_secret: str, kind: str = "blog", display: int = 15, sort: str = "date") -> list:
    """네이버 검색 API (blog / cafearticle). sort=date(최신) 또는 sim(유사도)"""
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
    params = {"query": query, "display": min(display, 30), "sort": sort if sort in ("date", "sim") else "date"}
    try:
        r = _requests_get_retry(url, params=params, timeout=10, retries=2, headers=headers)
        if r is None or r.status_code != 200:
            return []
        items = r.json().get("items") or []
    except Exception:
        return []
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



def _post_month(postdate: str) -> int | None:
    """YYYYMMDD → 월(1~12). 파싱 실패 시 None"""
    if not postdate or len(postdate) != 8 or not postdate.isdigit():
        return None
    try:
        m = int(postdate[4:6])
        return m if 1 <= m <= 12 else None
    except Exception:
        return None


def fetch_joghaengi_links(region: str, sea: str, month: int, fishes: list, max_links: int = 8) -> list:
    """조행기 링크 단계적 필터 캐스케이드

    1단계: 추천어종 중심 검색으로 풀 수집
    2단계: 1단계 결과 중 선택 지역이 제목/요약에 포함된 것만
    3단계: 2단계 결과 중 선택월 ± 인접월(±1) 게시일만

    3단계 결과 없으면 → 2단계로 하향
    2단계 결과 없으면 → 1단계로 하향
    """
    client_id, client_secret = get_naver_credentials()
    if not client_id or not client_secret:
        return []
    if not fishes:
        fishes = ["광어", "우럭"]

    # ---------- 1단계: 추천어종 중심 포괄 검색 풀 ----------
    # 조행기 / 낚시 / 출조 등 실제 많이 쓰는 표현을 폭넓게 검색
    queries = []
    for fish in fishes[:3]:
        queries.extend([
            f"{fish} 선상 조행기",
            f"{fish} 선상 낚시",
            f"{fish} 선상 출조",
            f"{fish} 출조",
            f"{fish} 조행기",
            f"{fish} 선상",
            f"{region} {fish} 선상",
            f"{region} {fish} 출조",
            f"{month}월 {fish} 선상",
            f"{month}월 {fish} 출조",
        ])
    # 중복 쿼리 제거 (순서 유지)
    seen_q = set()
    queries = [q for q in queries if not (q in seen_q or seen_q.add(q))]

    keywords = ("조행", "선상", "낚시", "출조", "포인트", "입질", "채비", "낚시터") + tuple(fishes)
    seen_link = set()
    stage1 = []
    MAX_POOL = 50  # 풀이 충분히 모이면 추가 API 호출 중단

    for q in queries:
        if len(stage1) >= MAX_POOL:
            break
        for kind in ("blog", "cafe"):
            if len(stage1) >= MAX_POOL:
                break
            try:
                items = naver_search(q, client_id, client_secret, kind=kind, display=15, sort="date")
            except Exception:
                items = []
            for it in items:
                link = (it.get("link") or "").strip()
                title = (it.get("title") or "").strip()
                if not link or not title:
                    continue
                key = link.split("?")[0]
                if key in seen_link:
                    continue
                blob = f"{title} {it.get('description') or ''}"
                if not any(x in blob for x in keywords):
                    continue
                seen_link.add(key)
                it["query"] = q
                stage1.append(it)
                if len(stage1) >= MAX_POOL:
                    break

    if not stage1:
        return []

    # ---------- 2단계: 1단계 결과에서 선택 지역 필터 ----------
    region_kw = [region]
    # 간단한 지역 변형 (필요 시 확장)
    if region == "인천":
        region_kw += ["인천항", "영종", "강화", "월미"]
    elif region == "서해":
        region_kw += ["군산", "보령", "태안", "대천"]
    stage2 = []
    for it in stage1:
        blob = _item_text(it)
        if any(kw in blob for kw in region_kw if kw):
            stage2.append(it)

    # ---------- 3단계: 2단계 결과에서 선택월 ± 인접월 필터 ----------
    adj_months = set()
    for d in (-1, 0, 1):
        m = month + d
        if m < 1:
            m = 12
        elif m > 12:
            m = 1
        adj_months.add(m)

    stage3 = []
    for it in stage2:
        pm = _post_month(it.get("postdate") or "")
        # postdate가 있고 선택월±1에 해당하는 경우만 Stage3 통과
        if pm is not None and pm in adj_months:
            stage3.append(it)

    # ---------- 하향 선택 ----------
    if stage3:
        chosen = stage3
        stage_used = 3
    elif stage2:
        chosen = stage2
        stage_used = 2
    else:
        chosen = stage1
        stage_used = 1

    # 관련성 점수 정렬
    try:
        chosen = sorted(chosen, key=lambda it: _final_score(it, month, fishes, region), reverse=True)
    except Exception:
        pass

    # 메타 정보 기록 (UI에서 단계 표시용)
    for it in chosen:
        it["cascade_stage"] = stage_used

    return chosen[:max_links]


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
        err_name = type(e).__name__
        err_s = str(e)
        if "Connection" in err_name or "connection" in err_s.lower() or "SSL" in err_s:
            return (
                "⚠️ OpenAI 연결 실패\n\n"
                "1) secrets.toml 에 `SSL_INSECURE = true` 가 있는지 확인\n"
                "2) 앱을 완전히 종료 후 run.bat 으로 다시 실행\n"
                "3) 방화벽/백신이 openai.com 을 막는지 확인\n"
                "4) 같은 키로 이전에 만든 도구가 되면 키는 정상 → 네트워크/SSL 문제"
            )
        return f"⚠️ LLM 오류: {err_name}: {err_s[:200]}"


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
        r = _requests_get_retry(url, params=None, timeout=15, retries=2)
        if r.status_code == 400:
            result["out_of_range"] = True
            result["msg"] = "날씨 예보는 오늘 기준 최대 16일까지 지원됩니다. 더 가까운 날짜를 선택해 주세요."
            return result
        r.raise_for_status()
        daily = r.json().get("daily", {})
        marine = {}
        try:
            mr = _requests_get_retry(
                "https://marine-api.open-meteo.com/v1/marine"
                f"?latitude={lat}&longitude={lon}"
                "&daily=wave_height_max,wave_period_max&timezone=Asia%2FSeoul"
                f"&start_date={target_date}&end_date={target_date}",
                params=None,
                timeout=15,
                retries=2,
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
        elif "SSL" in err or "CERTIFICATE" in err.upper():
            result["msg"] = "SSL 인증서 오류 — secrets.toml에 SSL_INSECURE = true 를 넣고 재실행해 주세요."
        else:
            result["msg"] = _sanitize_api_error(e)
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
    st.markdown("###### 🗺️ 해상 지도 (Windy)")
    render_windy_map(lat, lon, region, date_str=date_str, height=400)

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

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 🐟 추천 어종")
        st.caption("네이버 선상 조행기 검색 빈도 기준 (지역·월 반영)")
        if "selected_fishes" not in st.session_state:
            with st.spinner("네이버 조행기 검색으로 어종 집계 중..."):
                st.session_state["selected_fishes"] = recommend_fish_by_naver(region, sea_area, month)
        fishes = st.session_state["selected_fishes"]
        if st.button("🔄 다시 추천받기", key="refresh_fish"):
            st.session_state["selected_fishes"] = recommend_fish_by_naver(region, sea_area, month)
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
        st.markdown("### 📰 조행기 · 카페 글")
        st.caption("1단계 어종검색 → 2단계 지역필터 → 3단계 월(인접)필터 · 결과 없으면 이전 단계로 하향")
        cache_key = f"jog_links_{date_str}_{region}_{'-'.join(fishes)}"
        if st.button("🔄 조행기 다시 검색", key="refresh_jog"):
            st.session_state.pop(cache_key, None)
            st.session_state.pop("selected_jog_idx", None)
            st.rerun()
        if cache_key not in st.session_state:
            with st.spinner("네이버 블로그·카페 조행기 검색 중..."):
                st.session_state[cache_key] = fetch_joghaengi_links(
                    region, sea_area, month, fishes, max_links=8
                )
        links = st.session_state.get(cache_key) or []
        if not links:
            st.info(
                "검색된 출조 후기 링크가 없습니다. 네이버 API 키를 확인하거나 "
                f"[네이버에서 '{month}월 {region} 선상 출조' 검색](https://search.naver.com/search.naver?query={month}월+{region}+선상+출조)을 이용해 보세요."
            )
        else:
            stage_used = links[0].get("cascade_stage", 1)
            stage_label = {1: "1단계(어종)", 2: "2단계(지역)", 3: "3단계(월)"}.get(stage_used, "")
            st.caption(f"현재 표시: **{stage_label}** 결과 · {len(links)}건")

            for i, it in enumerate(links):
                kind_label = "블로그" if it.get("kind") == "blog" else "카페"
                src = it.get("source") or kind_label
                pd = it.get("postdate") or ""
                if len(pd) == 8 and pd.isdigit():
                    pd = f"{pd[:4]}-{pd[4:6]}-{pd[6:]}"
                meta = f"{kind_label} · {src}" + (f" · {pd}" if pd else "")
                title = it.get("title") or "제목 없음"
                desc = (it.get("description") or "")[:100]

                # 제목 클릭 → 선택
                col_t, col_b = st.columns([5, 1])
                with col_t:
                    st.markdown(
                        f'<div style="border:1px solid #e0e0e0;border-radius:10px;padding:8px 12px;margin-bottom:4px;background:#fafafa;">'
                        f'<div style="font-weight:600;color:#1565c0;font-size:14px;">{title}</div>'
                        f'<div style="font-size:12px;color:#888;margin-top:3px;">{meta}</div>'
                        f'<div style="font-size:12px;color:#555;margin-top:3px;">{desc}</div>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with col_b:
                    if st.button("보기", key=f"jog_view_{i}", use_container_width=True):
                        st.session_state["selected_jog_idx"] = i
                        st.rerun()

            # 선택된 글 iframe + 원문 링크
            sel_idx = st.session_state.get("selected_jog_idx")
            if sel_idx is not None and 0 <= sel_idx < len(links):
                sel = links[sel_idx]
                st.markdown("---")
                st.markdown(f"**📖 {sel.get('title') or '본문'}**")
                link = sel.get("link") or "#"
                st.caption("일부 네이버 블로그/카페는 iframe 차단으로 본문이 안 보일 수 있어요. 그때는 아래 버튼으로 새 탭에서 열어주세요.")
                try:
                    import streamlit.components.v1 as components
                    components.iframe(link, height=480, scrolling=True)
                except Exception:
                    st.warning("iframe을 불러오지 못했습니다.")
                st.link_button("🔗 원문 새 탭에서 열기", link, use_container_width=True)
                if st.button("닫기", key="jog_close"):
                    st.session_state.pop("selected_jog_idx", None)
                    st.rerun()

Fishing Tide Calendar App MVP - Grok #TS4MP:1:https:grok.com::c/ac5bfbf3-5047-4a90-a638-d57988b19d23:TS4MP#
