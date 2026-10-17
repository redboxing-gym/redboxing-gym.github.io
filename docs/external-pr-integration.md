# 외부 시스템의 PR 제출 확장 지점

정기 콘텐츠 자동화의 제출 범위는 신규 `content/articles/<slug>.md` 1개와 해당 글에 실제 사용되는 신규 `assets/img/` WebP 이미지들로 구성합니다. 파일 개수에 고정 제한은 없습니다. 기존 사이트 코드·아티클·이미지·스크립트·워크플로·기획 문서는 변경하지 않습니다. `ARTICLE_IDEAS.md`는 주제 선정 참고자료로만 사용하고 정기 콘텐츠 PR에서 수정하지 않습니다. 생성 HTML·sitemap·메인 HTML을 직접 만들 필요가 없습니다. 입력 계약은 [원고 규격](content-authoring.md)입니다. [게시 운영](publishing.md)의 보호 검사·테스트·빌드·최종 검증을 모두 수행하고 이미지의 실제 디코딩 검사도 별도로 완료합니다. 각 명령의 종료 코드 0과 성공 결과를 확인하며 `python scripts/build.py`의 PASS만으로 제출 가능하다고 판단하지 않습니다.

## GitHub API 또는 Git 기반 절차

1. 최신 main SHA를 읽습니다.
2. `content/<slug>` 같은 고유 작업 브랜치를 만듭니다.
3. `draft: false`인 신규 Markdown 1개와 `image_gen`으로 생성해 WebP로 저장하고 실제 디코딩 검증을 마친 해당 글의 신규 이미지들만 커밋합니다. 대표 이미지·초반 4컷 요약 만화·필요한 본문 설명 이미지의 제작은 [이미지 정책](content-authoring.md#이미지-제작과-검증)을 따릅니다.
4. main 대상 Draft PR을 생성하고 목적·Markdown `draft: false` 상태·근거 출처·이미지 디코딩 검증 결과를 본문에 기록합니다.
5. PR 검사를 확인하고 사람이 검토할 때까지 기다립니다. 승인·병합 API는 호출하지 않습니다.

GitHub 웹을 사용하면 토큰 없이 사람이 이 절차를 수행할 수 있습니다. 자동 외부 시스템은 저장소 범위를 제한한 GitHub App 또는 fine-grained 토큰의 Contents 쓰기·Pull requests 쓰기 권한이 필요합니다. 인증값은 외부 시스템의 보안 저장소에 보관하고 원고·저장소·아티팩트에 넣지 않습니다. Workflow 쓰기나 Pages 배포 권한은 콘텐츠 제출에 필요 없습니다.

외부 시스템이 PR을 제출하는 기능 자체는 이 PR에서 구현하지 않습니다. 입력 파일 경로·원고 규격·PR 대상 브랜치가 확장 지점입니다. 신뢰되지 않은 fork PR은 GitHub의 워크플로 실행 승인이 필요할 수 있습니다. `GITHUB_TOKEN` 기반 자동화로 생성한 PR의 워크플로 실행 정책도 확인해야 합니다. [GitHub 트리거 문서](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)를 참고하세요.

## 로컬 Codex CLI 제출 절차

이 절차는 향후 콘텐츠 제출용입니다. 문서 정리만 요청된 작업에서는 커밋·푸시·PR 생성을 실행하지 않습니다. 기본 규칙은 [AGENTS.md](../AGENTS.md)를 따릅니다.

1. 작업 트리가 깨끗한지 확인하고 `git fetch origin` 후 최신 `origin/main`에서 `git switch -c content/<slug>-<date> origin/main`으로 고유 브랜치를 만듭니다. 기존 로컬 변경은 덮어쓰지 말고 보고합니다.
2. [원고·이미지 작성](content-authoring.md)에 따라 공개 글과 초안을 모두 읽고 중복을 확인합니다. 기획 단계에서 본문과 시각자료를 함께 설계하고 신규 `content/articles/<slug>.md`를 `draft: false`로 완성합니다. 내장 `image_gen`으로 대표 이미지, 완성 본문에 근거한 초반 4컷 요약 만화, 이해에 필요한 본문 설명 이미지를 제작하고 모두 신규 WebP 파일로 저장합니다. 개수·비율에 고정 제한을 두지 않으며 장식성 이미지는 만들지 않습니다. 대표 이미지의 해상도·비율은 실제 표시 영역에 맞춰 선택합니다. `ARTICLE_IDEAS.md`와 기존 검증용 초안(`draft: true`)은 수정하지 않습니다. 각 이미지를 실제 디코딩해 WebP 형식·픽셀 크기를 기록하고 경로·대체 텍스트·본문 일치·실제 사용 여부를 확인합니다. 모바일 만화 가독성과 본문 이미지의 반응형 한계도 검토하며 기존 빌드 검사만으로 충분하다고 간주하지 않습니다.
3. [로컬 검증](publishing.md)을 모두 통과시키고 main 대비 PR diff가 신규 Markdown 1개와 해당 글에서 실제 사용하는 신규 WebP 이미지들의 추가만 포함하는지 확인합니다. 경로가 이미 존재하거나 다른 파일의 추가·수정·삭제가 있으면 제출하지 않고 보고합니다. 원고와 실제 사용 이미지 경로만 명시적으로 stage하고 staged diff도 확인합니다. `git add .`는 피합니다.
4. 콘텐츠 제출이 승인된 작업에서만 해당 파일을 커밋하고 `git push -u origin <작업브랜치>`로 제출합니다. `gh auth status`로 인증을 확인하되 토큰을 출력하거나 저장소에 기록하지 않습니다.
5. PR 설명 파일에 검색 의도와 중복 확인 결과, 출처·확인일, 이미지별 역할·경로·생성 방식·실제 디코딩 도구·형식·크기·모바일 표시 검토 결과, Markdown `draft: false` 상태, 검증 결과를 기록합니다. `gh pr create --draft --base main --head <작업브랜치> --title "<제목>" --body-file <설명파일>`로 Draft PR을 생성합니다. 설명 파일은 저장소 밖에 두고 비밀정보를 넣지 않습니다.
6. PR의 `content-check`와 검토 아티팩트를 확인한 뒤 사람에게 전달합니다. 자동 승인·자동 병합·main 직접 push는 하지 않습니다. GitHub Draft PR 상태와 Markdown `draft` 값은 별개입니다. 원고는 이미 `draft: false`이지만 PR 병합 전에는 실제 게시되지 않습니다. 사람의 PR 병합 승인이 게시 승인이며, 사람이 GitHub Draft PR을 검토 가능한 상태로 전환해 병합하면 GitHub Actions가 검증·자동 배포합니다. Pages 설정이나 변수를 바꿀 필요가 없습니다.

Codex CLI 정기 실행, 스케줄러, 인증 보관, PR 생성 코드는 아직 이 저장소에 구현하지 않습니다. 별도 유료 OpenAI API나 추가 과금 서비스로 자동 전환하지 않습니다.
