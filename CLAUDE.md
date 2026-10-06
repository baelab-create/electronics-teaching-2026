# electronics-teaching-2026 — 전자공학 강의자료 Teaching Edition

이 문서는 다른 기기(연구실 PC / 노트북 / 교수실 PC)의 Claude Code를 위한 유일한
인수인계 문서다. 이전 대화 기록은 볼 수 없다고 가정하고 작성되었다.

## 프로젝트 목적과 현재 상태

배원규 교수(baewongyu@gmail.com, GitHub `baelab-create`)의 "Electronic Devices and
Circuit Theory" Chapter 1 강의용 웹 교재. iPad Safari에서 Apple Pencil로 필기하며
수업하고, 학생들도 같은 링크로 열람·필기한다.

- 공개 URL: https://baelab-create.github.io/electronics-teaching-2026/ (랜딩)
- Chapter 1: https://baelab-create.github.io/electronics-teaching-2026/chapter1.html
- 저장소: https://github.com/baelab-create/electronics-teaching-2026 (**public** — GitHub
  Pages 무료 배포 조건이므로 private으로 바꾸면 안 됨)
- 완성도: Chapter 1은 실수업 투입 중(2026-09 학기). 기능 요청·버그 수정이 수시로 들어오는
  활발한 유지보수 단계. Chapter 2+는 미착수.

## 기술 스택과 폴더 구조

순수 정적 사이트. 빌드 도구·의존성·서버 코드 없음. 배포 = `main`에 push하면 GitHub
Pages가 자동 재배포(빌드 약 30~60초, **CDN 캐시 약 10분** — 배포 직후 검증은
`?v=<커밋해시>` 쿼리로 캐시 우회).

```
index.html            챕터 목록 랜딩 페이지
chapter1.html         Chapter 1(~830KB): 벡터 웹북 뷰어 + 티칭 레이어(아래 참조)
chapter2.html         Chapter 2 · Diode Applications (~1.0MB, 2026-10-06 추가)
assets/page_022.svg ~ page_075.svg   챕터1 54페이지 벡터(총 ~27MB)
assets/ch2/page_001.svg ~ page_074.svg  챕터2 74페이지 벡터(총 ~34MB, PyMuPDF 추출)
assets/share/review11-p{1,2,3}-v2.jpg  공유 탭 자료(수업후기, 1620×2340 선명화본)
tools/build_chapter2.py  PDF→챕터 생성 스크립트(아래 "새 챕터 추가" 참조)
CLAUDE.md             이 문서
```

chapter1.html 내부는 `<script>` 블록 2개다:
1. **뷰어 스크립트**(원본 벡터 웹북 유래, 한 줄로 압축됨): pageTexts/TEXTS 텍스트 레이어,
   setScale/fit/openD 등 전역(sloppy-mode) 함수.
2. **티칭 컨트롤러 IIFE**(이 프로젝트에서 작성): 필기·레이저·공유 탭·ENG 패널·백업 등
   전부. 뷰어 함수는 `window.setScale` 래핑 등으로 후킹한다.

로컬 실행: 그냥 브라우저로 열어도 대부분 동작하지만, 실제 검증은 배포본에서 하는 것을
원칙으로 해 왔다(iPad·Pages 환경과 동일 조건). 로컬 서버가 필요하면 아무 정적 서버나 사용.

## 기능 세트 (2026-09-09 기준)

- GoodNotes식 입력: Apple Pencil/마우스 = 선택한 도구, 손가락 = 스크롤 전용. 팜 리젝션.
- 펜(6색, 굵기 ±0.5, 예측 잉크·곡선 스무딩·필압 테이퍼), 형광펜(한 줄 좌우 고정,
  텍스트 줄 자동 스냅, multiply 블렌드), 지우개, T 텍스트 선택(PC는 Alt+드래그).
- 레이저 포인터: 도구바 맨 앞 빨간 ● 버튼. 혜성형 멀티패스 잔상(같은 경로를 반투명
  6겹으로 겹쳐 그림). **잔상은 펜을 떼도 유지**되고, 다음 획 시작·스크롤·줌에서 지워짐.
- 가반/나반 반별 필기 분리(IndexedDB 키 접두사, localStorage로 마지막 반 기억).
- 📏 범위 마킹(2026-10-06 복원): 도구 패널의 마킹 모드에서 펜으로 문단을 쓸면 수업한
  범위가 텍스트 줄 단위 회색 음영으로 표시, 칠한 곳을 다시 쓸면 지워짐(토글). 페이지별로
  `<chapter>:focus:<page>` 키(annotations store)에 저장되어 백업·복원에 포함. 챕터1의
  정적 399개 마크는 해당 페이지를 처음 수정할 때 편집 가능한 데이터로 승계됨.
- 줌: 상단 50%/200% 프리셋 버튼 2개만. **교재 핀치줌은 의도적으로 삭제됨**(아래 이력).
- 📎 공유 탭: 상단 공유 버튼 → `SHARE_FILES` 배열(chapter1.html 내)로 자료 관리.
  이미지 자료는 자체 핀치줌 유지. 필기 동일 지원(키 `sh-<id>-<n>`).
- ENG 패널: 문장 드래그 → 한국어 번역 → Gemini 단어·구문 해설 → TTS(남/여, 반복, 속도).
  Gemini API 키는 사용자가 패널 하단에 입력(localStorage `DrBAE_geminiKey`) — 저장소에는
  키가 전혀 없음. 주 사용처는 PC Chrome.
- 백업: 도구 패널 "💾 백업 HTML 저장" = 필기 전체가 든 자립형 HTML 1개. "📂 불러오기"로
  복원. 기기 교체 시 유일한 이관 수단.
- ♻️ 메모리 비우기 버튼: 필기 저장 완료 대기 → location.reload → 스크롤 복원.

## 필기 데이터 저장 구조

- IndexedDB `DrBAE_TeachingEdition`, store `annotations`(keyPath `key`).
  키: `chapter1:pdf:<N>`(가반) / `chapter1:B:pdf:<N>`(나반) / `sh-<id>-<n>`(공유 탭).
  획 = 정규화 좌표점 {x,y,p} 배열. 기기(브라우저) 로컬에만 존재 — 서버 저장 없음.
- `recordings` store는 남아 있지만 녹음 기능 자체는 제거됨(스키마 버전 유지 목적).
- TTS 캐시: IndexedDB `DrBAE_TTSCache`.

## 주요 설계 결정과 이유 (수정 시 반드시 지킬 것)

1. **인라인 스크립트에 raw `<!--` 나 `<script` 문자열 금지.** HTML 파서 double-escape로
   스크립트 전체가 죽는다(과거 펜 버튼 먹통 원인). `'<scr'+'ipt'` 분리, `<` 이스케이프 사용.
2. **undo 히스토리는 얕은 복사(slice)만.** 전제: 커밋된 획은 절대 제자리 변형하지 않는다
   (지우개는 filter로 새 배열, snapHighlight는 커밋 전 현재 획만 수정). JSON 깊은 복사를
   되돌리면 75분 수업 후반 지연이 재발한다.
3. **펜 커밋은 새 획 하나만 drawStroke.** 전체 redraw는 형광펜·undo·줌 변경 때만.
4. **라이브 프리뷰는 rAF당 1회**(scheduleLivePreview), 고정 오버레이 `inkPreview`(z 115).
5. **savePage는 키별 600ms 디바운스** + pagehide/visibilitychange/beforeunload에서 flush.
6. **캔버스 장당 ~4.2M픽셀(~16MB) 캡**(canvasScaleFor), 화면 밖 캔버스는 IO가 해제(1×1).
   iOS Safari 캔버스 메모리 크래시 방지 — 완화하면 4GB iPad에서 탭이 죽는다.
7. **화면 ±250% 밖 SVG 페이지 이미지는 src 해제**(imgObserver, data-src로 복원).
   디코딩 비트맵이 최대 RAM 소비자였다. 레이아웃 크기는 셸(.page-shell)이 가짐.
8. **교재 핀치줌 삭제됨(2026-09-08, 사용자 요청).** 핀치 미리보기의 GPU 레이어 스파이크가
   4GB iPad "배율 틀어짐"의 유력 원인이었다. 두 손가락 제스처는 Safari 기본 확대로 새지
   않게 차단되어 있다. 되살리려면 커밋 6c27c86 이전 참조.
9. **프로그램 스크롤은 `__instantScroll()` 사용.** html에 scroll-behavior:smooth가 있어
   일반 scrollTo는 애니메이션되어 튄다.
10. **파일은 CRLF.** 여러 줄 문자열 치환 시 개행 주의.
11. 녹음 기능은 실수업에서 안 쓰여 제거됨(2026-09-03, 복원은 커밋 b6906d8 이전 참조).
12. 발표 모드(전체화면)는 구현했다가 revert됨(커밋 7d2b92d 참조).
13. **텍스트 오버레이(.text-line)는 data-w + scaleX로 원문 폭에 맞춤(2026-09-14).**
    스팬 자체엔 폭 정보가 없어 브라우저 Times 폭만큼만 선택 하이라이트가 그려져 줄 끝이
    비었다. 각 줄의 정확한 폭을 SVG의 `<use data-text>` matrix 좌표에서 계산해
    `data-w`로 구워 넣었고(스팬 3493/3566), 런타임 init에서 offsetWidth 대비 scaleX 적용.
    스팬 baseline ≈ top + 0.77×font-size 로 SVG 글리프 y와 매칭. 새 챕터 제작 시에도
    같은 베이킹 과정이 필요하다(파이썬 스크립트 방식은 git 히스토리 665471c 참조).

## 작업 관행 (사용자와 합의된 워크플로)

- 요청 패턴: 구현 → main에 push → Pages 빌드 완료 폴링 → **배포본에서 직접 검증** →
  한국어로 결과 보고. 같은 링크 유지가 절대 조건.
- Pages 빌드 확인: `GET api.github.com/repos/baelab-create/electronics-teaching-2026/pages/builds/latest`
  (토큰은 `git credential fill`로 획득) → status가 built + 커밋 일치까지 폴링.
- 새 공유 자료 추가: 파일을 고해상도 JPG로 변환(필요 시 선명화) → `assets/share/` →
  `SHARE_FILES` 배열에 항목 추가.
- 새 챕터 추가(2026-10-06부터 PDF 직통 파이프라인): 소스 PDF는 학생용 저장소
  `C:\Users\user\Downloads\electronics-study\pdfs\chapterN.pdf`. `tools/build_chapter2.py`를
  복사해 상단 상수(PDF 경로, BOOK_OFF=인쇄쪽번호 오프셋, TITLE, SECS 절 목록)만 바꿔 실행하면
  chapter1.html을 템플릿 삼아 chapterN.html을 통째로 생성한다 — PyMuPDF로 페이지별 벡터 SVG
  추출(assets/chN/), 텍스트 레이어 스팬은 PDF 좌표에서 left/top/data-w를 정확히 계산(베이킹
  불필요), TEXTS(번역 서랍용 페이지 텍스트)·SECS(목차)·북페이지 오프셋·IndexedDB 키 접두사
  `chapterN:`까지 치환. 생성 후 index.html "준비 중" 카드 교체. 절 목록은 PDF에서 12pt 번호
  스팬으로 감지해 교차 확인할 것(스크립트 주석 참조).

## 알려진 이슈 / 다음 작업 후보

- 4GB iPad Pro 3세대에서 150분 연속 수업 시 메모리 빠듯 — 2026-09-04 최적화(이미지 해제,
  핀치 삭제, ♻️ 버튼)의 실전 검증 대기 중. 재발 시 당시 배율·공유 탭 사용 여부 확인.
- 사용자의 Gemini API 키가 텍스트 생성 모델에서 404 — 키 자체 제한으로 추정, 미해결.
  ENG 패널의 "🔧 연결 테스트"와 실패 메시지의 [키 진단] 출력이 진단용으로 들어 있다.
- Chapter 2 이후 제작 예정(벡터 웹북 번들은 교수가 제공).
- 기기 업그레이드(M1 iPad) 검토 중 — 이관은 백업 HTML로.

## git에 없는 로컬 파일과 조달 방법

| 파일 | 위치(원본 PC) | 용도 / 조달 |
|---|---|---|
| chapter1_vector_webbook_bundle.zip | Downloads | 챕터1 원본 번들. 새 챕터는 교수가 새 번들 제공 |
| Chapter1_Teaching_Edition_GitHub.html | Downloads | 구판(래스터) 아카이브. 참고용, 없어도 됨 |
| laser-pointer.html | Downloads | 레이저 잔상 데모(이미 반영됨). 없어도 됨 |
| 수업후기11.pdf 원본 | 저장소 히스토리 커밋 2ffa113 | raw URL로 받을 수 있음 |
| 필기 데이터 | 각 기기 브라우저 IndexedDB | git과 무관. 이관은 "백업 HTML 저장/불러오기" |

## 다른 기기 최초 세팅

```
git clone https://github.com/baelab-create/electronics-teaching-2026.git
```
- 읽기/작업은 클론만으로 충분(의존성 없음).
- **push하려면** 그 기기의 Git 자격증명 관리자에 `baelab-create` 계정 인증이 필요
  (HTTPS push 시 브라우저 로그인 또는 PAT). 커밋 identity는 저장소 로컬로
  `git config user.name baelab-create && git config user.email baewongyu@gmail.com` 설정.
