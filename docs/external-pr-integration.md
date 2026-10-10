# 외부 시스템의 PR 제출 확장 지점

외부 시스템은 `content/articles/<slug>.md`와 필요한 `/assets/img/` 이미지 파일만 제출합니다. 생성 HTML·sitemap·메인 HTML을 직접 만들 필요가 없습니다. 입력 계약은 [원고 규격](content-authoring.md)이며 검증 진입점은 `python scripts/build.py`입니다. 표준 출력의 PASS와 종료 코드 0이 성공이며, 오류는 비정상 종료 코드로 전달됩니다.

## GitHub API 또는 Git 기반 절차

1. 최신 main SHA를 읽습니다.
2. `content/<slug>` 같은 고유 작업 브랜치를 만듭니다.
3. 규격에 맞는 Markdown과 승인된 이미지 파일만 커밋합니다.
4. main 대상 PR을 생성하고 목적·검증용 초안 여부·근거 출처를 본문에 기록합니다.
5. PR 검사를 확인하고 사람이 검토할 때까지 기다립니다. 승인·병합 API는 호출하지 않습니다.

GitHub 웹을 사용하면 토큰 없이 사람이 이 절차를 수행할 수 있습니다. 자동 외부 시스템은 저장소 범위를 제한한 GitHub App 또는 fine-grained 토큰의 Contents 쓰기·Pull requests 쓰기 권한이 필요합니다. 인증값은 외부 시스템의 보안 저장소에 보관하고 원고·저장소·아티팩트에 넣지 않습니다. Workflow 쓰기나 Pages 배포 권한은 콘텐츠 제출에 필요 없습니다.

외부 시스템이 PR을 제출하는 기능 자체는 이 PR에서 구현하지 않습니다. 입력 파일 경로·원고 규격·PR 대상 브랜치가 확장 지점입니다. 신뢰되지 않은 fork PR은 GitHub의 워크플로 실행 승인이 필요할 수 있습니다. `GITHUB_TOKEN` 기반 자동화로 생성한 PR의 워크플로 실행 정책도 확인해야 합니다. [GitHub 트리거 문서](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)를 참고하세요.

기존 게시 방식에서의 초안 노출을 막기 위해, 이 구조 PR은 별도 Actions 전환 승인 전까지 병합하지 않습니다. 전환 후에는 외부 시스템도 동일한 PR 검증과 수동 승인·병합 절차를 따릅니다.
