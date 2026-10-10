# 빌드, 검증, 게시 전환

## 현재 단계

작업 브랜치와 PR에서 빌드·검증만 수행합니다. 배포 워크플로, 자동 병합, Pages 설정 변경은 포함하지 않았습니다. 현재 GitHub의 `pages-build-deployment`와 main 게시 방식은 유지됩니다. **이 PR은 전환 승인을 받을 때까지 병합하지 않습니다.** 브랜치 기반 Jekyll에 Markdown 원고가 노출되는 것을 막으려면 Actions 전환이 병합 전에 조율되어야 합니다.

## 로컬 검증

Python 3.12 이상을 사용합니다. CI 기준은 3.12입니다.

```powershell
python -m pip install -r requirements-content.txt
python scripts/check_changes.py
python -m unittest discover -s tests -v
python scripts/build.py
python scripts/validate.py
python -m http.server 8000 --directory dist
```

빌드는 루트의 고정 `dist/`만 재생성합니다. 원본 HTML·CSS·JS·사이트맵을 덮어쓰지 않습니다. 초안으로 전환한 원고의 이전 출력도 남지 않습니다. 의존성은 버전 고정이며 데이터베이스·서버·OpenAI API가 필요 없습니다.

기존 아티클 5개와 Google·Naver 소유권 확인 파일은 원본 SHA-256, Git 기준 커밋, 배포 결과를 비교합니다. 기준 커밋은 `a5e9b1c67652d5d197e4134328ebfdb7e29d7a2d`입니다. 기존 URL·canonical·JSON-LD를 포함한 파일 전체가 보존됩니다.

공개 Markdown 보호는 `scripts/check_changes.py` 한 곳에서 적용합니다. PR은 이벤트의 base SHA까지, 배포는 체크아웃된 main HEAD까지 기준 커밋 이후의 전체 첫 부모(first-parent) 이력을 검사합니다. 공개 상태가 대상 브랜치에 한 번 반영된 URL은 이후 삭제·변경·초안 전환을 금지합니다. 본문·제목·설명 등은 수정할 수 있고 수정일만 과거로 되돌릴 수 없습니다. 기존 HTML 파일 전체 보존 정책과 신규 Markdown의 내용 수정 정책은 구분됩니다.

`HEAD^`나 마지막 배포 상태에 의존하지 않으므로 최초 수동 배포·반복 수동 배포·merge·squash·여러 rebase 커밋을 한 번에 반영하는 경우에도 같은 정책입니다. 기준 커밋이 첫 부모 이력에 없으면 검사를 실패시키며, CI checkout은 반드시 `fetch-depth: 0`을 사용합니다. 같은 Git blob은 한 번만 읽어 이력 검사 중 중복 처리를 줄입니다. 로컬 기본 검사는 현재 HEAD 이력이며, PR처럼 검사하려면 BASE_SHA를 해당 대상 브랜치의 정확한 SHA로 지정합니다. 배포 모드는 BASE_SHA 환경변수를 무시합니다.

실제 배포 워크플로는 `--require-main-tip`도 지정하여 체크아웃 SHA가 현재 원격 main 끝과 같은지 확인합니다. 예전 성공 실행을 재실행해 이후 공개된 글을 누락시키는 배포는 거부합니다. 이 경우 과거 실행의 Re-run 대신 최신 main에서 새 수동 실행을 시작합니다. 이 확인 뒤에 main이 갱신된 경우 진행 중인 배포는 완료될 수 있고 새 main 실행이 이어서 검증·배포됩니다.

기존 메인 카드·순서는 보존하고 공개 신규 글의 카드만 출력의 `#articles`에 추가합니다. 신규 글은 명시된 관련 글을 먼저, 같은 태그를 가진 글을 다음으로 최대 3개 연결합니다. 기존 아티클의 관련 글 HTML은 변경하지 않습니다. 따라서 **기존 글 본문에 신규 링크를 삽입하지 않습니다.** 신규 글 간 연결과 메인·전체 목록 연결이 자동화 범위입니다. `/articles/index.html`에서 기존·신규 공개 글 전체를 확인할 수 있습니다.

두 사이트맵 파일명과 기존 URL·lastmod를 유지하고 목록 페이지와 공개 신규 글을 추가합니다. 수정일은 원고 메타데이터를 사용하며 빌드 시각을 넣지 않습니다. robots.txt와 검색엔진 확인 파일은 그대로 복사합니다. 외부 링크는 URL 프로토콜만 검사하고 실제 HTTP 응답은 검사하지 않습니다. 외부 서비스 장애가 PR을 막지 않도록 하기 위함입니다. 내부 파일·앵커·이미지·CSS·JS와 모달 대상은 검사합니다.

원고·템플릿·스크립트·내부 문서는 배포 아티팩트에 복사하지 않습니다. 기존 정적 자산 디렉터리는 그대로 복사합니다. `dist/`는 커밋하지 않습니다.

## PR 워크플로

`.github/workflows/content-check.yml`은 main 또는 `feature/markdown-content-system` 대상 `pull_request`와 수동 검증만 실행합니다. 후자는 콘텐츠 PR 위에 쌓은 별도 배포 PR의 검증 대상입니다. 파일 필터가 없으므로 필수 검증이 파일 필터 때문에 Pending에 머물지 않습니다. `contents: read` 권한만 사용하며 배포·커밋·승인·병합·댓글 작성 권한을 요청하지 않습니다. `pull_request_target`도 사용하지 않습니다.

무료 표준 `ubuntu-latest` 러너 1개, 최대 10분, 동시 실행 취소, 아티팩트 3일 보존으로 사용량을 제한합니다. 공개 저장소의 표준 GitHub-hosted 러너 정책을 활용합니다. 아티팩트 저장공간과 GitHub 계정 정책은 관리자가 확인해야 하며 유료 러너나 유료 서비스는 도입하지 않습니다.

## 별도 승인 후 필요한 수동 설정

정확한 승인·병합·게시 소스 전환 순서와 단계별 장애 복구는 [전환 절차](deployment-transition.md)를 따릅니다. 배포 구현은 `feature/pages-actions-deployment`의 별도 미병합 PR에서 검토합니다. 이 콘텐츠 PR에는 배포 워크플로가 없습니다.

main 직접 push 제한, PR 및 `content-check` 필수 검사, 리뷰 조건을 설정해야 합니다. 본인 PR을 스스로 승인할 수 없으므로 실제 리뷰어 구성에 맞게 승인 수를 정합니다. 자동 병합은 활성화하지 않습니다. 배포 전용 활성화 변수는 별도 승인 전에는 설정하지 않습니다.

Actions 배포 전환이 완료되기 전에는 Markdown만 추가해 **PR 빌드·SEO 검사**까지 자동화됩니다. 자동 실제 게시까지 연결하는 것은 후속 승인 범위입니다.

## 복구

실패 단계에 따라 복구 방법이 달라집니다. [전환 절차의 복구 표](deployment-transition.md)를 확인하세요. Markdown이 포함된 main을 Jekyll 게시로 되돌리거나 생성 결과를 main에 강제 push하지 않습니다.

공식 문서: [Pages 게시 소스](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site), [Actions 과금](https://docs.github.com/en/billing/concepts/product-billing/github-actions), [워크플로 트리거](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).
