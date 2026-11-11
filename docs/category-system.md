# 아티클 카테고리 시스템

대표 분류 `category`는 공개·초안 Markdown 및 `content/legacy-articles.json`의 각 기존 HTML 항목에 필수입니다. 식별자·한국어 표시 이름·표시 순서는 [scripts/categories.py](../scripts/categories.py)의 `CATEGORIES`에서만 관리합니다. 문자열이 아니거나 허용 목록에 없는 값, 누락된 값은 빌드 전에 거부합니다.

`tags`는 한글로 직접 저장하는 세부 주제 목록입니다. [태그 한글화 조사](tag-localization-review.md)의 변환 기록과 보류한 통합 항목을 참고하며, 고정 허용 태그 사전은 아직 없습니다. 현재 관련 글은 [자동 추천 정책](article-recommendations.md)에 따라 직접 주제 연관 → 동일 카테고리 → 연관 카테고리 → 나머지 공개 글 순으로 최대 3개를 선택합니다. 카테고리는 단계별 후보 보충에 사용하고 직접 주제 점수에는 가산하지 않습니다. 기존 `related`는 남겨 두어도 무시합니다. 아래 PR A 검수 기록과 과거 태그 조사 문서의 수동 추천 비교는 당시 동작의 이력이며 현재 정책은 자동 추천 문서를 따릅니다.

## 현재 8개 카테고리

2026-11-11 기준입니다. 기존 7개 식별자의 상대 순서를 보존하고 운동 선택에서 체중 관리로 탐색할 수 있도록 `workout-programs` 다음에 새 `weight-management`를 배치합니다. `workout-programs`는 표시 이름만 **운동 실전 연구소**로 바꾸며 식별자를 유지합니다. 아래 수량은 공개 Markdown 44개·검증용 초안 1개·레거시 HTML 5개의 본문 검토 결과이며 Markdown 수에 초안도 포함됩니다.

| 식별자 | 표시 이름 | Markdown | HTML | 본문의 핵심 질문과 분류 기준 |
| --- | --- | ---: | ---: | --- |
| match-analysis | 경기 분석 | 10 | 0 | 특정 실제 경기의 전개·전술·결과 해설 |
| boxing-technique | 복싱 기술 | 19 | 0 | 개별 펀치·방어·스텝·호흡 등 동작의 수행과 교정 |
| exercise-science | 운동과학 | 10 | 1 | 에너지 소모·생리학·역학·신체 적응과 운동 효과의 과학적 해석 |
| boxing-beginners | 복싱 입문 | 5 | 1 | 첫 수업·장비·체육관 선택·코치와의 소통·입문 준비 |
| combat-culture | 격투기 문화 | 0 | 0 | 격투기와 영화·만화·게임 등 대중문화·문화적 표현의 연결 |
| workout-programs | 운동 실전 연구소 | 1 | 3 | 운동 일정·운동 방식 비교와 선택·챌린지·훈련 전략·실행 계획 |
| weight-management | 다이어트·체중 관리 | 0 | 0 | 체중 감량·유지 전략, 식사·생활습관 선택, 정체기·체성분 관리 |
| combat-history | 격투기 역사 | 0 | 0 | 역사적 인물·사건·기술·제도의 시대적 맥락과 유산 |

제목에 '다이어트'가 있다는 이유만으로 옮기지 않습니다. 같은 운동도 원리 해석이면 운동과학, 조건별 실행 계획이면 운동 실전 연구소, 감량·체성분 관리 의사결정이면 체중 관리입니다. 요일은 편집 주제의 참고이며 실제 글의 중심 질문을 대신하지 않습니다.

### 기존 글 재분류 검토

전체 공개 49개와 초안 1개를 확인한 결과 이번에는 **이동 0개**로 판단했습니다. Markdown과 `content/legacy-articles.json`의 `category`도 그대로 유지합니다. 분류를 채우기 위한 원고 수정이나 새 글 생성은 하지 않습니다.

| 글 | 유지할 분류 | 판단 이유 |
| --- | --- | --- |
| `hangsin-diet-workout` (HTML) | workout-programs | 헬스 외 운동 선택, 몰입·코칭·생활 동선을 통한 지속 가능한 운동 선택이 중심. 식단·감량 속도·체성분 관리 전략을 제공하는 글이 아님 |
| `euljiro-diet-workout` (HTML) | workout-programs | 퇴근 후 접근성·재미·운동 흐름을 통한 지속 가능한 루틴 선택이 중심 |
| `boxing-diet-beginner` (HTML) | boxing-beginners | 처음 시작해도 되는지, 기초 학습 순서와 입문 상담이 중심 |
| `boxing-calorie-burn` (HTML) | exercise-science | 체중·강도·시간에 따른 칼로리·MET 비교와 전신 운동의 에너지 소모 설명이 중심 |
| `stress-relief-boxing` (HTML) | workout-programs | 스트레스 해소 목적에 맞는 샌드백·미트 등 운동 선택이 중심이며 체중 관리 글이 아님 |
| `three-day-weekend-workout` | workout-programs | 금·토·일 운동 일정과 피로를 고려한 복싱·근력 운동 배치가 중심 |
| `boxing-strength-concurrent-training` | exercise-science | AMPK·mTORC1, 병행 훈련과 장기 적응 연구의 해석이 중심. 운동 배치 조언은 원리를 적용하는 보조 내용 |
| 나머지 운동과학 9개 Markdown | exercise-science | 덤벨 토크·신경 적응·젖산 대사·근성장·근육통·반복 속도·에너지 회복·스트레칭·증발 냉각의 작동 원리와 근거가 중심 |
| 복싱 기술 19개·경기 분석 10개 | 기존 분류 | 동작 수행·교정 또는 특정 경기 공방 분석이 중심이며 감량·식단 관리로 바꿀 근거 없음 |
| 복싱 입문 5개 Markdown (초안 포함) | boxing-beginners | 글러브·체육관 선택, 수업 준비, 피드백·스파링 참여 의사소통이 중심 |

신규 체중 관리 글이 없는 현재는 목록에서 이 분류의 빈 결과 안내를 보여 주고 홈에서는 제외합니다. 테스트용 임시 공개 원고를 사용해 향후 글이 들어왔을 때 카드·상세 라벨·홈 탭·필터·관련 글이 생성되는지도 검증합니다. 실제 원고를 검증 목적으로 공개하지 않습니다.

### 러너 카테고리 계약 조사

읽기 전용 참조 기준: [SGHwang/redboxing-runner main `547e6caa`](https://github.com/SGHwang/redboxing-runner/tree/547e6caa6e70b860de87a6508daf6d5599c9dce7). 웹사이트 기준 main은 `1e7d7d3`(관련 글 자동화 PR #95 병합)입니다.

- [`article_runner.py`](https://github.com/SGHwang/redboxing-runner/blob/547e6caa6e70b860de87a6508daf6d5599c9dce7/article_runner.py#L76)는 실행 시 웹사이트 `origin/main`을 fetch하고 해당 SHA로 실행별 작업 트리를 만듭니다. `article.txt` + 공통 편집 원칙 + 요일 문서 + 과거 주제 맥락을 합쳐 그 작업 트리에서 Codex를 실행합니다. 카테고리 목록이나 요일→카테고리 식별자 매핑을 코드에 고정하지 않습니다.
- [`prompts/article.txt` 6행](https://github.com/SGHwang/redboxing-runner/blob/547e6caa6e70b860de87a6508daf6d5599c9dce7/prompts/article.txt#L6)은 실제 웹사이트 `AGENTS.md`, 작성·게시 문서를 읽고 해당 규칙을 우선 적용하도록 합니다. 러너가 웹사이트 `CATEGORIES`를 직접 import하는 방식은 아니며, 생성 담당 Codex가 웹사이트 작성 가이드에서 허용 식별자와 분류 경계를 확인합니다.
- [`목요일 편집 지침`](https://github.com/SGHwang/redboxing-runner/blob/547e6caa6e70b860de87a6508daf6d5599c9dce7/prompts/weekdays/thursday.md)은 다이어트·체중 관리, [`토요일 지침`](https://github.com/SGHwang/redboxing-runner/blob/547e6caa6e70b860de87a6508daf6d5599c9dce7/prompts/weekdays/saturday.md)은 운동 실전 연구소를 정의합니다. 금요일은 격투기·대중문화, 일요일은 역사·인물·유산으로 기존 식별자 범위와 맞습니다.
- [`publish_article.py`](https://github.com/SGHwang/redboxing-runner/blob/547e6caa6e70b860de87a6508daf6d5599c9dce7/publish_article.py#L61)는 해당 웹사이트 작업 트리의 테스트·빌드·보호 검사를 실행합니다. 허용 카테고리는 최종적으로 웹사이트 빌더가 `scripts/categories.py`로 검사합니다. `topic_guard.py`·`run_state.py`에도 카테고리 허용 목록은 없습니다.

따라서 **웹사이트 변경만으로 새 실행의 카테고리 계약을 수용할 수 있으며, 러너 수정은 필수가 아닙니다.** 이 웹사이트 PR이 병합된 main을 새 실행이 가져온 뒤부터 적용됩니다. 이미 생성되어 보존 중인 실행별 작업 트리는 당시 기준 SHA의 기존 분류를 사용하므로 자동 소급 적용되지 않습니다. 러너를 수정하거나 기존 실행을 임의로 이전하지 않습니다. 실제 원고 생성·이미지 제작·러너 실행은 이번 검증 범위가 아니며, 정적 코드·프롬프트 조사와 웹사이트 빌드/브라우저 검증에 근거한 판단입니다.

러너 수요일 지침의 토요일 설명에는 이전 표시 이름인 '운동 프로그램'이 남아 있습니다. 안정 식별자 `workout-programs`와 최신 토요일 본문은 호환되므로 기능상 필수 수정은 아니며, 향후 러너 문구 정리 시 반영할 수 있습니다.

### 개편 검증 — 2026-11-11

Python 3.14.6, 고정 빌드 의존성 및 Playwright Chromium으로 검증했습니다. 기존 작업 폴더의 무관한 JPG 삭제 변경 6개를 유지하고, 보호 HTML의 CRLF 변환을 피하기 위해 `core.autocrlf=false`인 저장소 밖 별도 복제본을 사용했습니다.

- 보호 검사: 보호 파일 원본과 공개 URL 44개, 첫 부모 커밋 55개 이력 통과.
- 전체 테스트: 81개 중 일반 66개 통과, 선택 브라우저 15개 제외. 브라우저 별도 실행은 15개 모두 통과.
- 빌드·독립 검증: 기존 HTML 5개·공개 Markdown 44개·초안 1개 제외, HTML 53개 통과.
- 기준 main과 배포 파일 169개 비교: 홈·목록·주말 운동 상세 3개에서 표시 이름과 신규 필터만 변경. 그 변경을 제외한 출력 바이트 동일. 원고·레거시 메타데이터·본문·이미지·URL·canonical·작성/수정일·기존 추천 목록·사이트맵·robots·소유권 확인 파일 보존.
- 실제 화면: 360/390/1440px의 필터·카드·상세·홈을 검사하고 캡처를 직접 확인. 체중 관리 빈 상태와 임시 테스트 원고가 있는 상태 모두 가로 넘침 없음. 기존 키보드·10초 순환·터치·초안 비공개 검사도 통과.

스크린샷은 저장소 밖 `C:/Users/hsg/AppData/Local/Temp/redboxing-category-qa`에 보관합니다. 임시 원고는 테스트 종료 시 제거하며 실제 사이트에 추가하지 않습니다. GitHub Python 3.12 검사는 Draft PR의 `content-check`에서 별도 확인하며, 검토용 실제 사이트는 그 실행의 `site-review-<run_id>` 아티팩트를 사용합니다.

## 최초 분류 기준 — PR A 당시 이력

PR A의 기준 main은 `d559484dc16bf156b07d09d90cd83a346689774c`입니다. 제목뿐 아니라 도입부와 본문의 주된 질문을 기준으로 대표 주제를 하나 부여했습니다. 아래 수량에는 초안 1개가 포함됩니다.

| 대표 주제 | Markdown | 기존 HTML | 기준 |
| --- | ---: | ---: | --- |
| 경기 분석 | 10 | 0 | 특정 경기의 공방·전술·결과를 해설하는 글. 복싱 및 MMA 경기 리뷰 포함 |
| 복싱 기술 | 19 | 0 | 잽·훅·어퍼컷·방어·스텝·스탠스·샌드백 거리·호흡·미트·거울·줄넘기 등 동작과 연습 방법 |
| 운동과학 | 10 | 1 | 에너지·신경 적응·근육 성장·근육통·열 조절·스트레칭·운동 강도 등 생리·역학 원리 |
| 복싱 입문 | 5 | 1 | 첫 수업·체육관 선택·글러브 선택·코치 피드백·스파링 참여 의사 등 입문자의 선택과 소통 |
| 격투기 문화 | 0 | 0 | 현재 주된 검색 의도가 일치하는 글 없음 |
| 운동 프로그램 | 1 | 3 | 주간 운동 일정·지역별 다이어트 운동 선택·스트레스 해소 목적의 운동 구성 |
| 격투기 역사 | 0 | 0 | 현재 주된 검색 의도가 일치하는 글 없음 |

기존 HTML은 행신·을지로 다이어트 및 스트레스 해소 글을 운동 프로그램, 초보 복싱 다이어트를 복싱 입문, 칼로리 소모 글을 운동과학으로 분류했습니다. `boxing-first-class.md`는 복싱 입문에 속하며 `draft: true`를 유지합니다. 기존 Markdown에는 `category` 한 줄만 추가하며 본문·다른 메타데이터·이미지를 변경하지 않습니다.

## 화면 동작과 출력 계약

- `/articles/index.html`은 전체 49개 공개 글을 처음부터 HTML 링크로 출력합니다. 전체 보기와 8개 카테고리 순서는 분류 정의를 따릅니다.
- JavaScript가 준비되면 필터를 표시합니다. 버튼은 Tab으로 이동하고 Enter/Space로 선택하며, `aria-pressed`와 상태 알림으로 선택·결과 수를 제공합니다. 빈 카테고리에는 준비 중 안내를 표시합니다. URL·canonical을 바꾸거나 새로고침하지 않습니다.
- JavaScript를 끄거나 필터 스크립트를 불러오지 못해도 전체 글·링크가 표시됩니다. 사용 불가능한 필터는 숨깁니다.
- 홈과 목록 카드에 대표 카테고리를 표시합니다. 홈은 [카테고리별 최신 글 순환](home-article-rotation.md)으로 표시 수를 제한하고, 목록은 전체 공개 글을 유지합니다. 빌드는 루트 `index.html`을 덮어쓰지 않으며 보호 HTML 원본을 보존합니다.
- Markdown 상세 페이지에는 대표 카테고리·기존 태그·전체 목록 링크를 표시합니다. 기존 HTML 상세 페이지는 원본 그대로 배포합니다.
- 생성 결과는 기존과 동일한 `dist/`에만 작성합니다. 글 URL·canonical·작성/수정일·사이트맵 계약과 초안 비공개 정책을 유지합니다. 분류별 URL이나 별도 사이트맵 항목은 생성하지 않습니다.

## 검증 명령

```powershell
python scripts/check_changes.py
python -m unittest discover -s tests -v
python scripts/build.py
python scripts/validate.py
```

Windows의 보호 파일이 CRLF로 체크아웃된 경우 [게시 운영](publishing.md)의 임시 LF 복제본 절차를 사용합니다. 보호 파일과 해시는 수정하지 않습니다.

화면 회귀 검사는 선택 의존성인 Playwright·Chromium 설치 환경에서 실행합니다. 필수 빌드 의존성이나 워크플로는 추가하지 않습니다.

```powershell
$env:RUN_BROWSER_TESTS = '1'
# 필요하면 저장소 밖 경로에 실제 화면 스크린샷을 보관합니다.
$env:QA_OUTPUT_DIR = '<저장소 밖 QA 폴더>'
python -m unittest discover -s tests -p '*browser.py' -v
```

기존 이미지 반응형 검사에 더해 실제 빌드 결과의 8개 필터·빈 결과·키보드·선택 상태·새로고침 없음·JavaScript 비활성 목록을 검증합니다. 홈·목록·상세는 360/390/1440px에서 가로 넘침과 이미지 로드를 검사합니다. 체중 관리 분류는 실제 빈 상태와 테스트 원고가 있는 상태를 모두 확인합니다. 기존 이미지 테스트의 과거 CSS 비교에는 새 카테고리 UI 스타일을 양쪽에 동일 적용하여, 라벨 추가에 따른 카드 자연 높이와 기존 이미지 크기 규칙을 구분합니다.

### PR A 로컬 검증 기록 — 2026-11-06

아래는 최초 카테고리 구현 커밋 `7ac0b61` 당시 기록입니다. 이후 메인 영역 추가 작업의 검증 범위와 결과는 [메인 카테고리 순환](home-article-rotation.md)에 별도로 기록합니다.

Python 3.14.6, 고정 의존성 및 Playwright Chromium으로 검증했습니다. 기존 작업 폴더의 보호 HTML은 CRLF이므로 원본 폴더를 수정하지 않고 `core.autocrlf=false`인 별도 임시 Git 복제본에 PR 변경 파일을 복사하여 실행했습니다. 실행 위치는 `C:/Users/hsg/AppData/Local/Temp/redboxing-categories-z8xue_ra/repo`입니다. CI의 Python 3.12 검증은 PR의 `content-check` 결과로 별도 확인합니다.

- 보호 검사: 기존 보호 파일 및 첫 부모 커밋 53개에 걸친 공개 URL 44개 잠금 통과.
- 전체 테스트: 45개 중 일반 테스트 40개 통과, 선택 브라우저 검사 5개 제외.
- 브라우저 별도 실행: 기존 이미지 검사 2개와 새 카테고리 검사 3개 모두 통과.
- 빌드 및 독립 검증: HTML 53개, 기존 HTML 글 5개·공개 Markdown 44개·초안 1개 제외. SEO·구조화 데이터·내부 리소스·앵커·사이트맵 통과.
- 기준 main 빌드와 비교: Markdown 45개의 본문 및 category 이외 메타데이터 동일, 공개 Markdown 44개의 렌더링 본문·관련 글 패널 동일, 기존 HTML 글 5개와 두 사이트맵·robots.txt의 출력 바이트 동일.
- 실제 화면: 360/390/1440px에서 홈·목록·상세의 가로 넘침 없음, 깨진 이미지 없음. PC·390px 모바일 스크린샷을 직접 열어 필터 줄바꿈·선택 표시·카드·본문 분류 표시를 확인. 390px JavaScript 비활성 목록도 검증.

스크린샷은 저장소 밖 `C:/Users/hsg/AppData/Local/Temp/redboxing-categories-z8xue_ra/qa`에 보관했습니다. 이는 로컬 검증 증거 경로이며 다른 검토자의 컴퓨터나 프리뷰 서비스에서 접근할 수 있는 URL이 아닙니다. 원고 본문·이미지·운영 설정은 변경하지 않았으며 배포는 실행하지 않았습니다.

## 여러 Markdown 변경 PR의 검수 대안

사용자가 확인한 기존 프리뷰 시스템은 여러 Markdown 파일을 바꾸는 PR을 지원하지 않습니다. 이 PR은 45개 Markdown과 빌더·템플릿·자산을 함께 변경하므로 해당 프리뷰의 검수 범위를 벗어납니다. 프리뷰 및 러너 저장소는 수정하지 않습니다.

이번 PR은 기존 `content-check`가 만드는 `site-review-<run_id>` 아티팩트로 검수합니다. 이는 PR 브랜치의 전체 소스에서 실제 `dist/`를 빌드하므로 여러 원고와 코드 변경을 함께 포함합니다.

1. Draft PR의 `content-check` 성공을 확인하고 해당 실행의 검토 아티팩트를 다운로드합니다.
2. 새 폴더에 압축을 풀고 그 폴더에서 `python -m http.server 8000`을 실행합니다. 원고가 있는 저장소 루트가 아니라 압축을 푼 배포 결과 루트를 제공합니다.
3. `http://localhost:8000/articles/index.html`에서 전체·각 카테고리·빈 카테고리·키보드를 확인합니다. JavaScript를 끈 상태에서도 전체 링크를 확인합니다.
4. 홈 `/` 및 Markdown 상세 `/articles/boxing-breathing-basics.html`의 카테고리·태그를 PC·모바일에서 확인합니다. 기존 HTML 상세가 유지되고 `/articles/boxing-first-class.html`은 404인지 확인합니다.

이 방법은 배포·운영 main 병합·프리뷰 저장소 변경 없이 검토할 수 있습니다. 아티팩트 보존 기간은 기존 정책상 3일입니다. 만료 시 최신 PR 커밋에 대한 검증을 다시 실행하거나 PR 브랜치를 로컬에서 빌드합니다.

프리뷰 시스템의 후속 변경은 별도 작업으로 검토해야 합니다. 단일 원고 선택 가정을 제거하고 PR의 전체 트리에서 같은 빌더·의존성·메타데이터 검증을 사용해야 합니다. 다중 원고·템플릿·분류 정의·CSS·JS 변경을 함께 반영하고, `dist/` 전체를 제공하며, 초안 제외·원본 보호·기존 URL·필터 자산 로드에 대한 통합 테스트가 필요합니다. 이번 PR에서 실제 프리뷰 서비스와의 통합 성공을 주장하지 않습니다.
