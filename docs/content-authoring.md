# Markdown 원고 작성과 제출

이 구조는 GitHub Pages와 무료 오픈소스 도구만 사용합니다. ChatGPT는 API 호출 없이 원고를 작성하고, 사용자는 GitHub 웹에서 파일을 추가해 PR을 제출할 수 있습니다.

## 먼저 알아둘 운영 상태

현재 단계는 PR 검증용입니다. Pages 게시 소스는 변경하지 않았습니다. **Actions 전환을 별도 승인받기 전에는 이 PR을 병합하지 마세요.** 현재 브랜치 기반 게시의 Jekyll이 원고 Markdown을 HTML로 처리할 수 있기 때문에, 현재 게시 방식에 이 구조를 그대로 병합하면 초안 제외를 보장할 수 없습니다. 검토 아티팩트 `dist/`는 초안 HTML을 생성하지 않습니다.

## 파일 형식

`content/articles/<slug>.md`에 UTF-8 파일을 추가합니다. 실제 예제는 [검증용 초안](../content/articles/boxing-first-class.md)입니다.

```markdown
---
title: "복싱 첫 수업 준비 안내"
description: "처음 복싱을 시작하는 분을 위한 수업 준비 안내."
slug: "boxing-first-class"
published: "2026-10-10"
updated: "2026-10-10"
keywords: ["초보 복싱", "복싱 입문"]
canonical: "https://redboxing-gym.github.io/articles/boxing-first-class.html"
kicker: "BEGINNER BOXING"
lead: "첫 수업을 준비할 때 확인할 사항입니다."
hero_image: "/assets/img/freetime.webp"
hero_alt: "레드복싱 운동 공간"
tags: ["beginner", "boxing"]
related: ["/articles/boxing-diet-beginner.html"]
draft: true
---

## 첫 수업 준비

본문을 작성합니다.
```

## 메타데이터 규칙

| 필드 | 규칙 |
| --- | --- |
| title / description | 비어 있지 않은 문자열. 검색 결과에 적합한 자연스러운 한국어 |
| slug | 영문 소문자·숫자·단어 사이 하이픈. 파일명과 일치 |
| published / updated | 따옴표로 감싼 YYYY-MM-DD. 수정일은 작성일 이후 또는 같은 날 |
| keywords | 한 개 이상 문자열 목록 |
| canonical | `https://redboxing-gym.github.io/articles/<slug>.html`과 정확히 일치 |
| kicker / lead | 카드·대표 영역 문구 |
| hero_image / hero_alt | 기존 `/assets/img/` 파일의 경로와 대체 텍스트 |
| tags | 선택 문자열 목록. 관련 글 우선순위에 사용 |
| related | 선택 문자열 목록. 공개된 기존·신규 글의 `/articles/...html` 경로 |
| draft | 따옴표 없는 `true` 또는 `false`, 반드시 명시 |

제목은 템플릿이 H1으로 만듭니다. 본문은 `##`부터 사용합니다. 문단, 목록, 강조, 링크, 이미지, 표, 코드 블록을 지원합니다. 원시 HTML·스크립트·iframe·HTML 자동 링크는 지원하지 않습니다. 링크는 `[문구](URL)`로 작성합니다. 문의 CTA·지점 전화·카카오톡은 템플릿에서 제공합니다.

파일의 공개 URL은 slug로 결정되며 기존 HTML URL과 충돌하면 실패합니다. `draft: false`가 main 이력에 반영되면 배포가 아직 비활성 상태여도 공개 URL을 예약·보호합니다. 이후 slug·canonical·작성일을 바꾸거나 원고를 삭제하거나 초안으로 되돌릴 수 없습니다. 제목·설명·본문·키워드·이미지·관련 글 등의 수정은 허용합니다. `updated`는 해당 글의 main 이력에 기록된 가장 최근 수정일보다 앞설 수 없습니다. 같은 날 여러 번 수정하는 것은 허용합니다.

기존 HTML 아티클 5개는 별도 정책으로 파일 전체를 보존합니다. 신규 Markdown 글의 본문 수정 허용과 충돌하지 않습니다. PR 작업 브랜치에서만 잠시 `draft: false`였다가 최종 원고를 초안으로 되돌린 상태는 main에 공개 상태가 반영되지 않았다면 URL을 잠그지 않습니다. 빌드 검토용 임시 공개 상태를 main에 커밋하지 마세요.

공개 글의 내용을 복구할 때도 URL과 작성일을 유지하고 수정일이 뒤로 돌아가지 않도록 합니다. 예전 커밋을 그대로 revert하여 수정일을 과거로 되돌리지 말고, 복구할 본문과 현재 정책에 맞는 `updated`를 담은 PR을 제출하세요.

`draft: true`도 메타데이터·본문 형식·본문 내부 링크를 검사하지만 HTML 파일을 만들지 않습니다. 공개 목록·관련 글·사이트맵에도 포함되지 않습니다. 초안 URL로 링크하면 검증이 실패합니다. 전체 생성 페이지의 SEO 검사는 공개 원고에 적용됩니다.

## ChatGPT에 전달할 지시문

> 레드복싱의 Markdown 원고 규격을 따라 UTF-8 Markdown 파일 하나를 작성해줘. YAML 필드를 모두 채우고 draft는 true로 설정해줘. 본문은 H2부터 작성하고 HTML은 쓰지 마. 존재하는 이미지와 공개 URL만 사용해줘. 건강 효과, 통계, 비용, 운영시간 등 확인되지 않은 사실은 만들어내지 마. 코드 수정이나 API 호출은 필요 없어.

작성 시 이 문서와 사용할 기존 글 URL·이미지 목록을 함께 제공하세요. ChatGPT가 원고를 작성하는 것과 GitHub에 제출하는 것은 별개입니다. GitHub 웹에서 작업 브랜치에 파일을 추가하고 main 대상 PR을 생성하세요.

## 검토와 게시

1. PR의 `content-check` 성공 여부와 원고를 확인합니다.
2. Actions 실행에서 `site-review-<run_id>`를 다운로드합니다.
3. 압축을 풀어 `python -m http.server 8000`으로 실행하고 `http://localhost:8000/`를 확인합니다. 루트 상대 경로 때문에 파일을 직접 더블클릭하는 방식은 권장하지 않습니다.
4. 초안 HTML이 없는지 확인합니다. 테스트 초안은 계속 `draft: true`로 유지합니다.
5. Actions 전환 승인 후에만 실제 게시 원고를 `draft: false`로 바꾸는 PR을 검토·승인·병합합니다.

PR 검사 성공만으로 승인이나 병합이 이루어지지 않습니다.
