# redboxing-gym.github.io

레드복싱 공식 정적 웹사이트입니다. 기존 공개 HTML과 SEO 자산을 보존하며 신규 원고의 Markdown 빌드와 PR 검증을 준비합니다.

- [Markdown 원고 작성](docs/content-authoring.md)
- [빌드·검증·배포 전환](docs/publishing.md)
- [외부 시스템 PR 연동](docs/external-pr-integration.md)

현재 PR 단계에서는 배포 설정을 변경하지 않습니다. **Actions 전환 승인 전에는 콘텐츠 관리 구조 PR을 병합하지 않습니다.** 테스트 원고는 `draft: true`이며 빌드 결과에 HTML 파일이 생성되지 않습니다.

```powershell
python -m pip install -r requirements-content.txt
python -m unittest discover -s tests -v
python scripts/build.py
```
