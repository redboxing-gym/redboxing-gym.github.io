# GitHub Pages 전환과 장애 복구

이 문서는 실행 계획입니다. 현재 Pages 설정·main·배포 활성화 변수는 변경하지 않았습니다. 콘텐츠 PR #15와 별도 배포 PR은 모두 승인 전에는 병합하지 않습니다.

## 브랜치와 배포 안전장치

- 콘텐츠: `feature/markdown-content-system` → main, PR #15.
- 배포: `feature/pages-actions-deployment` → `feature/markdown-content-system`을 대상으로 한 별도 초안 PR. PR #15 위에 쌓은 변경이므로 현재 diff에는 배포 전용 파일만 표시됩니다.
- 배포 PR을 콘텐츠 브랜치로 병합하지 않습니다. PR #15가 main에 병합된 **후**, 배포 PR의 base를 main으로 변경하고 필요하면 최신 main 위로 rebase하여 다시 검사합니다.
- 배포 워크플로는 main push 또는 main에서의 수동 실행만 받습니다. PR에서는 실행되지 않습니다.
- 저장소 변수 `PAGES_ACTIONS_ENABLED`가 정확히 `true`인 경우에만 빌드·배포합니다. 기본은 미설정이며 비활성 상태입니다. 별도 승인 없이 설정하지 않습니다.
- 배포 환경은 `github-pages`, 배포 가능 브랜치는 main으로 제한합니다. 배포 job에만 `pages: write`와 `id-token: write` 권한을 부여합니다.
- 업로드 경로는 `dist/` 하나입니다. 원고·스크립트·템플릿·테스트·문서와 심볼릭 링크가 섞이면 검증이 실패합니다.
- 최초 수동 실행과 이후 main push는 모두 `python scripts/check_changes.py --mode deployment --require-main-tip`로 전체 main 첫 부모 이력을 검사합니다. `HEAD^` 비교는 사용하지 않습니다. 원본 기준 커밋이 누락된 shallow checkout이나 이력이 재작성된 저장소는 실패합니다. 오래된 SHA의 실행 재시도도 거부하므로 최신 main에서 새 수동 실행을 시작합니다.
- main에 공개 상태로 반영된 Markdown의 URL·canonical·작성일은 고정입니다. 본문 등은 수정 가능하고 `updated`는 이력의 최대 수정일 이상이어야 합니다. 배포가 비활성인 기간에도 이 보호는 유지됩니다.

## 승인 후 정확한 전환 순서

1. **두 PR과 아래 전환 작업에 대한 명시적 승인을 받습니다.** 자동 병합은 끕니다. content-check를 필수 검사로 지정하고 main 직접 push를 제한합니다. 리뷰 조건은 실제 리뷰어 구성에 맞춥니다.
2. 현재 Settings → Pages 게시 소스(브랜치·폴더), 사용자 도메인 설정, 마지막 성공 배포 SHA와 URL을 기록합니다. 워크플로 실행·배포 큐가 모두 종료되었는지 확인합니다. 다른 PR 병합을 잠시 중지합니다.
3. 마지막 성공한 **정적 사이트 커밋**에서 복구 브랜치 `backup/pages-before-actions`를 만듭니다. 이 브랜치에는 `content/`, `scripts/`, `templates/`, `tests/`가 없어야 합니다. 사이트 결과를 확인하고 백업 브랜치와 SHA를 기록합니다. 현재 알려진 기존 정적 기준은 `a5e9b1c67652d5d197e4134328ebfdb7e29d7a2d`이며, 실제 마지막 성공 배포와 일치하는지 먼저 확인합니다. 복구 브랜치는 수정하지 않습니다.
4. `PAGES_ACTIONS_ENABLED`가 미설정 또는 `false`인지 확인하고 github-pages 환경의 허용 브랜치를 main으로 제한합니다.
5. **PR #15 병합 전에** Settings → Pages → Source를 GitHub Actions로 변경합니다. 원고가 있는 main을 기존 Jekyll 게시가 먼저 처리하지 않도록 하는 순서입니다. 이 시점에는 main에 사용자 배포 워크플로가 없으며 기존 게시 페이지가 계속 열리는지 확인합니다. 사이트가 유지되지 않거나 설정 전환이 실패하면 PR을 병합하지 말고 기존 소스로 복원합니다.
6. 승인된 PR #15를 main에 병합합니다. 현재 게시 소스는 이미 Actions이며 PR #15에는 배포 워크플로가 없으므로 콘텐츠가 게시되지 않습니다. 원고는 `draft: true`로 유지합니다.
7. 별도 배포 PR의 base를 main으로 바꿉니다. squash/rebase 병합으로 PR #15의 커밋이 달라졌다면 배포 전용 커밋만 최신 main 위로 rebase하고 push합니다. diff에 배포 워크플로와 그 검증 테스트만 남았는지 확인하고 PR 검사를 다시 통과시킵니다. 변경 내용이 달라지면 다시 리뷰합니다.
8. 승인된 배포 PR을 main에 병합합니다. 활성화 변수가 false이므로 이 push의 배포 워크플로는 건너뜁니다. Pages 소스가 Actions인지 다시 확인합니다.
9. 승인 범위에 따라 `PAGES_ACTIONS_ENABLED=true`를 설정하고 **main을 선택해** Pages 워크플로를 수동 실행합니다. 파일이나 main을 직접 수정할 필요가 없습니다. 기준 커밋부터 main HEAD까지 전체 첫 부모 이력·원본 보존 검사·회귀 테스트·독립 검증·dist 전용 업로드가 모두 성공해야 배포 job이 실행됩니다. 최초 실행도 HEAD의 직전 커밋만 비교하지 않습니다.
10. 배포 성공 후 루트, 기존 아티클 5개, 두 사이트맵, robots, Google/Naver 확인 파일이 정상 응답하는지 확인합니다. 신규 목록 화면과 모바일 문의 바도 확인합니다. 테스트 원고의 HTML URL은 404여야 합니다. 마지막 성공 배포 SHA와 실행 URL을 기록하고 PR 병합 중지를 해제합니다.

이후 main에 승인된 콘텐츠 PR이 병합되면 같은 검증 후 자동 배포됩니다. PR 검사 통과만으로 자동 병합되지는 않습니다.

## 장애별 복구

| 상황 | 복구 절차 |
| --- | --- |
| Source 전환 실패 또는 기존 페이지 유지 실패, PR #15 미병합 | 두 PR을 그대로 둡니다. 활성화 변수는 false로 유지합니다. Source를 기록한 기존 브랜치·폴더로 복원하고 기존 URL을 확인합니다. |
| PR #15만 병합되고 배포 PR 준비가 지연됨 | Pages Source는 Actions로 유지하고 마지막 성공 사이트를 확인합니다. 원고가 포함된 main을 브랜치 게시로 전환하지 않습니다. 필요하면 다음 행의 백업 게시로 복구합니다. |
| 첫 빌드·업로드·배포 실패 | 활성화 변수를 false로 바꾸고 추가 배포를 막습니다. 마지막 성공 페이지가 유지되는지 확인합니다. 실패 로그를 검토하여 수정 PR을 검증·리뷰·병합한 후 승인받아 변수를 켜고 main 수동 실행을 재시도합니다. 실패한 빌드 결과를 강제 게시하지 않습니다. |
| 성공 배포 후 콘텐츠·레이아웃 회귀 | 변수를 false로 바꾸고 진행 중인 Pages 워크플로가 끝났거나 취소되었는지 확인합니다. 잘못된 내용을 복구하는 PR을 검증·리뷰·병합합니다. 공개 Markdown의 URL·작성일을 유지하고 updated는 이력의 최대 수정일 이상으로 유지합니다. 과거 원고 전체를 그대로 revert하여 수정일을 되돌리지 않습니다. 수정 후 변수를 켜고 main 수동 실행으로 다시 게시합니다. |
| 즉시 기존 정적 사이트로 복구해야 함 | 변수를 false로 바꾸고 진행 중인 Pages 워크플로를 취소한 뒤 완료를 확인합니다. Settings → Pages에서 브랜치 게시로 전환하되 **main이 아니라 3단계의 `backup/pages-before-actions`와 기록한 폴더**를 선택합니다. 원고가 없는 백업에서 기존 사이트를 게시하고 URL을 확인합니다. main을 reset·force-push하지 않습니다. |
| 백업 게시 후 Actions 재전환 | 수정 PR과 검사·리뷰를 완료하고 변수는 false로 유지합니다. Source를 Actions로 바꾸고 기존 사이트 유지 여부를 확인한 다음, 승인 후 변수를 켜고 main에서 수동 실행합니다. |

Pages 배포 자체를 실행해 보는 검증은 전환 승인 이후에만 수행합니다. 미병합 브랜치에서의 테스트는 빌드와 워크플로 구조 검사까지이며 실제 Pages 환경·OIDC 권한은 최초 승인된 실행에서 확인합니다.

## 최종 전환 체크리스트

- [ ] PR #15와 #16의 최신 커밋·diff·CI 결과를 검토하고 병합과 전환을 별도 승인했다.
- [ ] 기존 아티클 5개와 소유권 확인 파일의 원본·출력 보존 검사가 통과했다.
- [ ] 실제 Git 이력 테스트로 merge·squash·다중 커밋·최초/반복 수동 실행·공개 원고 수정 및 금지 변경을 확인했다.
- [ ] 테스트 원고는 draft:true이며 dist에 HTML·목록 링크·사이트맵 항목이 없다.
- [ ] 전체 이력 checkout, 공통 보호 검사, dist 전용 업로드, main/활성화 변수 제한을 확인했다.
- [ ] 마지막 성공 SHA·게시 소스·도메인과 원고 없는 복구 브랜치를 기록했다.
- [ ] 활성화 변수는 false 상태로 유지하고, Source 전환 → PR #15 병합 → PR #16 main 재지정·재검증 → PR #16 병합 순서로 진행한다.
- [ ] 승인 후에만 변수를 true로 설정하고 main 수동 첫 배포를 실행한다.
- [ ] 최초 배포의 실제 Pages/OIDC 권한, 기존 URL·사이트맵·robots·확인 파일과 초안 URL 404를 확인한다.
- [ ] 장애 복구 시 공개 URL·작성일·수정일 보호를 유지하고, 필요하면 원고 없는 백업 브랜치로 게시한다.

공식 근거: [사용자 정의 Pages 워크플로](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages), [게시 소스 설정](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
