# 빌드, 검증, 게시 운영

## 현재 운영 상태

Pages 게시 소스는 **GitHub Actions**이며 `PAGES_ACTIONS_ENABLED=true`로 자동 배포가 활성화되어 있습니다(2026-10-16 사용자 제공 상태). `.github/workflows/pages-deploy.yml`은 main push와 수동 실행을 받고, main 및 활성화 변수 조건을 모두 만족할 때 검증·배포합니다. PR에서는 `content-check`만 수행하며 배포하지 않습니다. 사람의 검토·병합 뒤 main 변경이 실제 게시로 이어지므로 공개 여부를 병합 전에 확인합니다.

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

Windows에서 기존 보호 HTML이 CRLF로 체크아웃되어 있으면 Git 변경이 없어도 바이트 해시 검사가 실패할 수 있습니다. 보호 파일·기준 해시·검증 코드를 고치지 말고 줄바꿈 차이를 보고합니다. 검증은 별도 임시 복제본을 `git clone --config core.autocrlf=false <저장소> <임시경로>`로 만들어 Git 원본 바이트로 수행할 수 있습니다. 이때 미커밋 문서 변경도 복사하고 사용한 Python 버전과 실행 위치를 결과에 기록합니다.

빌드는 루트의 고정 `dist/`만 재생성합니다. 원본 HTML·CSS·JS·사이트맵을 덮어쓰지 않습니다. 초안으로 전환한 원고의 이전 출력도 남지 않습니다. 의존성은 버전 고정이며 데이터베이스·서버·OpenAI API가 필요 없습니다.

기존 아티클 5개와 Google·Naver 소유권 확인 파일은 원본 SHA-256, Git 기준 커밋, 배포 결과를 비교합니다. 기준 커밋은 `a5e9b1c67652d5d197e4134328ebfdb7e29d7a2d`입니다. 기존 URL·canonical·JSON-LD를 포함한 파일 전체가 보존됩니다.

공개 Markdown 보호는 `scripts/check_changes.py` 한 곳에서 적용합니다. PR은 이벤트의 base SHA까지, 배포는 체크아웃된 main HEAD까지 기준 커밋 이후의 전체 첫 부모(first-parent) 이력을 검사합니다. 공개 상태가 대상 브랜치에 한 번 반영된 URL은 이후 삭제·변경·초안 전환을 금지합니다. 본문·제목·설명 등은 수정할 수 있고 수정일만 과거로 되돌릴 수 없습니다. 기존 HTML 파일 전체 보존 정책과 신규 Markdown의 내용 수정 정책은 구분됩니다.

`HEAD^`나 마지막 배포 상태에 의존하지 않으므로 최초 수동 배포·반복 수동 배포·merge·squash·여러 rebase 커밋을 한 번에 반영하는 경우에도 같은 정책입니다. 기준 커밋이 첫 부모 이력에 없으면 검사를 실패시키며, CI checkout은 반드시 `fetch-depth: 0`을 사용합니다. 같은 Git blob은 한 번만 읽어 이력 검사 중 중복 처리를 줄입니다. 로컬 기본 검사는 현재 HEAD 이력이며, PR처럼 검사하려면 BASE_SHA를 해당 대상 브랜치의 정확한 SHA로 지정합니다. 배포 모드는 BASE_SHA 환경변수를 무시합니다.

실제 배포 워크플로는 `--require-main-tip`도 지정하여 체크아웃 SHA가 현재 원격 main 끝과 같은지 확인합니다. 예전 성공 실행을 재실행해 이후 공개된 글을 누락시키는 배포는 거부합니다. 이 경우 과거 실행의 Re-run 대신 최신 main에서 새 수동 실행을 시작합니다. 이 확인 뒤에 main이 갱신된 경우 진행 중인 배포는 완료될 수 있고 새 main 실행이 이어서 검증·배포됩니다.

기존 메인 카드·순서는 보존하고 공개 신규 글의 카드만 출력의 `#articles`에 추가합니다. 신규 글은 명시된 관련 글을 먼저, 같은 태그를 가진 글을 다음으로 최대 3개 연결합니다. 기존 아티클의 관련 글 HTML은 변경하지 않습니다. 따라서 **기존 글 본문에 신규 링크를 삽입하지 않습니다.** 신규 글 간 연결과 메인·전체 목록 연결이 자동화 범위입니다. `/articles/index.html`에서 기존·신규 공개 글 전체를 확인할 수 있습니다.

두 사이트맵 파일명과 기존 URL·lastmod를 유지하고 목록 페이지와 공개 신규 글을 추가합니다. 수정일은 원고 메타데이터를 사용하며 빌드 시각을 넣지 않습니다. robots.txt와 검색엔진 확인 파일은 그대로 복사합니다. 외부 링크는 URL 프로토콜만 검사하고 실제 HTTP 응답은 검사하지 않습니다. 외부 서비스 장애가 PR을 막지 않도록 하기 위함입니다. 내부 파일·앵커·이미지·CSS·JS와 모달 대상은 검사합니다.

원고·템플릿·스크립트·내부 문서는 배포 아티팩트에 복사하지 않습니다. 기존 정적 자산 디렉터리는 그대로 복사합니다. `dist/`는 커밋하지 않습니다.

## PR 워크플로

`.github/workflows/content-check.yml`은 main 또는 `feature/markdown-content-system` 대상 `pull_request`와 수동 검증만 실행합니다. 후자는 전환 당시의 호환 대상이며 신규 콘텐츠 PR의 대상은 main입니다. 파일 필터가 없으므로 필수 검증이 파일 필터 때문에 Pending에 머물지 않습니다. `contents: read` 권한만 사용하며 배포·커밋·승인·병합·댓글 작성 권한을 요청하지 않습니다. `pull_request_target`도 사용하지 않습니다.

무료 표준 `ubuntu-latest` 러너 1개, 최대 10분, 동시 실행 취소, 아티팩트 3일 보존으로 사용량을 제한합니다. 공개 저장소의 표준 GitHub-hosted 러너 정책을 활용합니다. 아티팩트 저장공간과 GitHub 계정 정책은 관리자가 확인해야 하며 유료 러너나 유료 서비스는 도입하지 않습니다.

## 배포 안전장치와 사람의 검토

`.github/workflows/pages-deploy.yml`은 검증된 `dist/`만 업로드합니다. 빌드 job은 `contents: read`, `pages: read`를 사용하고 배포 job에만 `pages: write`, `id-token: write`를 부여합니다. `github-pages` 환경을 사용하며 배포 동시 실행은 취소하지 않습니다. main·활성화 변수 조건, 전체 이력 검사, 최신 main 확인, 테스트 및 SEO·리소스 검증을 우회하지 않습니다.

정기 콘텐츠는 신규 Markdown 아티클 1개와 해당 글에 실제 사용되는 신규 WebP 이미지들만 GitHub Draft PR로 제출합니다. 파일 개수의 고정 제한은 없으며 기존 사이트 코드·아티클·이미지·스크립트·워크플로·기획 문서는 변경하지 않습니다. `ARTICLE_IDEAS.md`는 참고자료로만 사용하고 수정하지 않습니다. 원고는 `draft: false`로 제출하며 GitHub Draft PR 상태와 Markdown `draft` 값은 별개입니다. PR 병합 전에는 실제 게시되지 않습니다. 사람은 원고·근거·이미지·검증 결과를 확인하고 Draft PR을 검토 가능한 상태로 전환해 병합하며, 이 병합 승인이 게시 승인입니다. 병합 후 GitHub Actions가 검증에 성공하면 자동 배포합니다. 기존 `draft: true` 검증용 초안은 유지합니다. 기획 단계에서 본문과 시각자료를 함께 설계합니다. 신규 이미지는 내장 `image_gen`으로 생성하고 모두 WebP로 저장합니다. 대표 이미지는 실제 표시 영역에 적합한 해상도·비율을 선택하며 고정 필수 규격은 없습니다. 완성 본문을 기준으로 제작한 세로형 단일 이미지의 4컷 요약 만화를 글 초반에 넣고, 본문 설명 이미지는 이해에 필요한 만큼 개수·비율 제한 없이 생성합니다. 장식성 이미지는 만들지 않습니다. 모든 최종 이미지를 실제 디코딩해 형식·픽셀 크기를 기록하고 경로·대체 텍스트·본문 일치·실제 사용을 확인합니다. 기존 이미지를 신규 생성물로 취급하지 않습니다. 기존 빌드 검사 통과만으로 이미지 검증이 충분하다고 간주하지 않습니다. 대표/카드 잘림과 모바일 만화 가독성·가로 넘침을 검토하며 [레이아웃 분석과 현재 본문 이미지의 반응형 한계](content-authoring.md#실제-표시-영역과-권장-규격)를 따릅니다. main 직접 push, 자동 승인·자동 병합은 금지합니다. 브랜치 보호 및 필수 검사·리뷰 조건의 실제 설정 여부는 코드만으로 확인할 수 없으며 변경이 필요하면 관리자에게 별도로 요청합니다. Codex가 Pages 설정이나 저장소 변수를 임의로 변경하지 않습니다.

## 복구

실패한 출력을 강제 게시하지 않고 로그를 확인한 뒤 수정 PR을 검증·검토·병합합니다. 공개 Markdown의 URL·작성일을 유지하고 `updated`를 과거로 되돌리지 않습니다. 오래된 실행의 재실행 대신 최신 main에서 새 실행을 사용합니다. 배포 중단이나 설정 변경은 관리자가 별도로 판단합니다.

과거 전환 순서와 장애별 복구 표는 [전환 이력](deployment-transition.md)에 보존했습니다. 당시 브랜치·PR·백업 정보는 실행 전 실제 존재와 상태를 확인해야 하며 현재 작업 지시로 사용하지 않습니다. Markdown이 포함된 main을 Jekyll 게시로 되돌리거나 생성 결과를 main에 강제 push하지 않습니다.

공식 문서: [Pages 게시 소스](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site), [Actions 과금](https://docs.github.com/en/billing/concepts/product-billing/github-actions), [워크플로 트리거](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).
