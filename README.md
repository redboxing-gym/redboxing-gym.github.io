# 레드복싱 공식 웹사이트

기존 공개 HTML을 보존하면서 신규 아티클을 Markdown으로 작성하는 GitHub Pages 정적 사이트입니다.

현재 게시 소스는 **GitHub Actions**, 저장소 변수는 **`PAGES_ACTIONS_ENABLED=true`**입니다(2026-10-16 사용자 제공 운영 상태). 사람이 검토한 PR이 main에 병합되면 Pages 워크플로가 검증 후 `dist/`를 자동 배포합니다. PR 검증 자체는 배포하지 않습니다.

- [Codex 프로젝트 지침](AGENTS.md)
- [Markdown 원고·이미지 작성](docs/content-authoring.md)
- [빌드·검증·현재 게시 운영](docs/publishing.md)
- [외부 시스템·로컬 Codex CLI 제출](docs/external-pr-integration.md)
- [아티클 기획·중복 확인](ARTICLE_IDEAS.md)
- [검색 의도별 키워드](SEO_KEYWORDS.md)
- [과거 수정 기록](ARTICLE_FIX_NOTES.md)
- [과거 배포 전환 이력](docs/deployment-transition.md)

Python 3.12 이상으로 로컬 검증합니다. 전체 절차는 게시 운영 문서를 따릅니다.

```powershell
python -m pip install -r requirements-content.txt
python scripts/check_changes.py
python -m unittest discover -s tests -v
python scripts/build.py
python scripts/validate.py
```

생성된 `dist/`는 커밋하지 않습니다. 신규 콘텐츠는 별도 브랜치와 Draft PR로 제출하고 사람이 검토·병합합니다. 검증용 `boxing-first-class.md`는 `draft: true`를 유지합니다.
