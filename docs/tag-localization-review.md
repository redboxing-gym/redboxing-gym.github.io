# 태그·kicker 한글화 조사 및 이행 기록

## 조사 범위와 보존 원칙

기준은 Draft PR #93의 `8c64790e73d40b655ee50855ee9d6e06117bfa35` (`8c64790`)입니다. 공개 Markdown 44개와 검증용 초안 1개, 합계 45개를 전수 조사했습니다. 아래 사용 건수는 **초안 포함 원고 수**이며 태그 중복 출현 횟수가 아닙니다. 태그/kicker별 원고 링크로 실제 용례를 확인할 수 있습니다. 별도의 보호 HTML 5개는 manifest 데이터와 원본 내부 문구를 구분했습니다.

이 문서의 변환표는 **이번 데이터 이행의 기록**이며 최종 표준 태그 사전·고정 허용 목록·영문 ID 저장소가 아닙니다. 런타임 번역 계층이나 태그별 영문 ID를 추가하지 않았습니다. Markdown 원본과 manifest에 한글 문자열을 직접 저장합니다.

- Markdown 고유 태그: **16종 → 15종**. 변환 전 영문 14종·한글 2종이며, 변환 후 15종 모두 한글입니다.
- 원고 단위 태그 언어: 변환 전 영문만 44개·한글만 1개·한 배열 안 한영 혼용 0개. 사이트 전체로는 두 언어가 혼재했습니다. 변환 후 45개 모두 한글입니다.
- Markdown 고유 kicker: **26종 → 25종**. 변환 전 영문 4종(원고 5개)·한글 22종(원고 40개). 변환 후 25종 모두 한글이며 이미 한글인 40개 kicker는 유지합니다. `BOXING BASICS`의 번역이 기존 `복싱 기초`와 같아져 고유 값이 한 개 줄었습니다.
- 변경한 Markdown은 44개입니다. 이미 한글 태그·kicker를 쓰던 `light-heavy-load-muscle-growth.md`는 수정하지 않았습니다. 태그의 순서·본문·그 밖의 frontmatter는 보존했습니다.
- `exercise-science`가 직역하면 기존 `운동과학`과 같은 문자열이 됩니다. 이 한 곳을 제외하고 서로 다른 기존 태그를 하나로 합치지 않았습니다. 한 원고 안에 두 별칭이 함께 있던 사례는 없어 원고별 태그 개수는 유지됩니다.

## 변환 전 전체 고유 태그와 사용 원고

| 기존 태그 | 원고 수 | 언어 | 사용 원고 |
| --- | ---: | --- | --- |
| `boxing` | 37 | 영문 | [boxing-body-jab-level-change](../content/articles/boxing-body-jab-level-change.md), [boxing-breathing-basics](../content/articles/boxing-breathing-basics.md), [boxing-combination-memory](../content/articles/boxing-combination-memory.md), [boxing-feedback-one-at-a-time](../content/articles/boxing-feedback-one-at-a-time.md), [boxing-first-class](../content/articles/boxing-first-class.md), [boxing-footwork-feet-crossing](../content/articles/boxing-footwork-feet-crossing.md), [boxing-guard-return](../content/articles/boxing-guard-return.md), [boxing-heavy-bag-distance](../content/articles/boxing-heavy-bag-distance.md), [boxing-jab-feint-response](../content/articles/boxing-jab-feint-response.md), [boxing-jab-without-pullback](../content/articles/boxing-jab-without-pullback.md), [boxing-jump-rope-troubleshooting](../content/articles/boxing-jump-rope-troubleshooting.md), [boxing-lead-hook-body-rotation](../content/articles/boxing-lead-hook-body-rotation.md), [boxing-mirror-gaze](../content/articles/boxing-mirror-gaze.md), [boxing-mitt-start-signal](../content/articles/boxing-mitt-start-signal.md), [boxing-parry-small-movement](../content/articles/boxing-parry-small-movement.md), [boxing-pivot-lead-foot-turn](../content/articles/boxing-pivot-lead-foot-turn.md), [boxing-rear-uppercut-short-path](../content/articles/boxing-rear-uppercut-short-path.md), [boxing-shadow-punch-endpoint](../content/articles/boxing-shadow-punch-endpoint.md), [boxing-slip-balance](../content/articles/boxing-slip-balance.md), [boxing-sparring-participation](../content/articles/boxing-sparring-participation.md), [boxing-stance-front-foot](../content/articles/boxing-stance-front-foot.md), [boxing-strength-concurrent-training](../content/articles/boxing-strength-concurrent-training.md), [boxing-weave-keep-opponent-in-view](../content/articles/boxing-weave-keep-opponent-in-view.md), [canelo-mbilli-pressure-combinations](../content/articles/canelo-mbilli-pressure-combinations.md), [dubois-wardley-rematch-result](../content/articles/dubois-wardley-rematch-result.md), [exercise-lactate-fuel-shuttle](../content/articles/exercise-lactate-fuel-shuttle.md), [foster-navarrete-final-round](../content/articles/foster-navarrete-final-round.md), [gonzalez-vazquez-body-shot-finish](../content/articles/gonzalez-vazquez-body-shot-finish.md), [hangsin-boxing-gym-guide](../content/articles/hangsin-boxing-gym-guide.md), [kavanagh-moreno-leg-kicks-clinch](../content/articles/kavanagh-moreno-leg-kicks-clinch.md), [osuna-cangelosi-fifth-round-response](../content/articles/osuna-cangelosi-fifth-round-response.md), [resendiz-mazoudier-late-rally](../content/articles/resendiz-mazoudier-late-rally.md), [rest-between-sets-energy-recovery](../content/articles/rest-between-sets-energy-recovery.md), [romero-ferreira-body-head](../content/articles/romero-ferreira-body-head.md), [smith-puello-southpaw-jab](../content/articles/smith-puello-southpaw-jab.md), [sweat-evaporation-exercise-cooling](../content/articles/sweat-evaporation-exercise-cooling.md), [three-day-weekend-workout](../content/articles/three-day-weekend-workout.md) |
| `beginner` | 27 | 영문 | [boxing-body-jab-level-change](../content/articles/boxing-body-jab-level-change.md), [boxing-breathing-basics](../content/articles/boxing-breathing-basics.md), [boxing-combination-memory](../content/articles/boxing-combination-memory.md), [boxing-feedback-one-at-a-time](../content/articles/boxing-feedback-one-at-a-time.md), [boxing-first-class](../content/articles/boxing-first-class.md), [boxing-footwork-feet-crossing](../content/articles/boxing-footwork-feet-crossing.md), [boxing-guard-return](../content/articles/boxing-guard-return.md), [boxing-heavy-bag-distance](../content/articles/boxing-heavy-bag-distance.md), [boxing-jab-feint-response](../content/articles/boxing-jab-feint-response.md), [boxing-jab-without-pullback](../content/articles/boxing-jab-without-pullback.md), [boxing-jump-rope-troubleshooting](../content/articles/boxing-jump-rope-troubleshooting.md), [boxing-lead-hook-body-rotation](../content/articles/boxing-lead-hook-body-rotation.md), [boxing-mirror-gaze](../content/articles/boxing-mirror-gaze.md), [boxing-mitt-start-signal](../content/articles/boxing-mitt-start-signal.md), [boxing-parry-small-movement](../content/articles/boxing-parry-small-movement.md), [boxing-pivot-lead-foot-turn](../content/articles/boxing-pivot-lead-foot-turn.md), [boxing-rear-uppercut-short-path](../content/articles/boxing-rear-uppercut-short-path.md), [boxing-shadow-punch-endpoint](../content/articles/boxing-shadow-punch-endpoint.md), [boxing-slip-balance](../content/articles/boxing-slip-balance.md), [boxing-sparring-participation](../content/articles/boxing-sparring-participation.md), [boxing-stance-front-foot](../content/articles/boxing-stance-front-foot.md), [boxing-weave-keep-opponent-in-view](../content/articles/boxing-weave-keep-opponent-in-view.md), [early-strength-neural-adaptation](../content/articles/early-strength-neural-adaptation.md), [hangsin-boxing-gym-guide](../content/articles/hangsin-boxing-gym-guide.md), [muscle-soreness-repeated-bout](../content/articles/muscle-soreness-repeated-bout.md), [stretching-range-of-motion-tolerance](../content/articles/stretching-range-of-motion-tolerance.md), [sweat-evaporation-exercise-cooling](../content/articles/sweat-evaporation-exercise-cooling.md) |
| `technique` | 10 | 영문 | [boxing-body-jab-level-change](../content/articles/boxing-body-jab-level-change.md), [boxing-breathing-basics](../content/articles/boxing-breathing-basics.md), [boxing-guard-return](../content/articles/boxing-guard-return.md), [boxing-jab-feint-response](../content/articles/boxing-jab-feint-response.md), [boxing-jab-without-pullback](../content/articles/boxing-jab-without-pullback.md), [boxing-lead-hook-body-rotation](../content/articles/boxing-lead-hook-body-rotation.md), [boxing-parry-small-movement](../content/articles/boxing-parry-small-movement.md), [boxing-rear-uppercut-short-path](../content/articles/boxing-rear-uppercut-short-path.md), [boxing-shadow-punch-endpoint](../content/articles/boxing-shadow-punch-endpoint.md), [boxing-slip-balance](../content/articles/boxing-slip-balance.md) |
| `practice` | 1 | 영문 | [boxing-combination-memory](../content/articles/boxing-combination-memory.md) |
| `footwork` | 2 | 영문 | [boxing-footwork-feet-crossing](../content/articles/boxing-footwork-feet-crossing.md), [boxing-pivot-lead-foot-turn](../content/articles/boxing-pivot-lead-foot-turn.md) |
| `equipment` | 1 | 영문 | [boxing-glove-ounce-label](../content/articles/boxing-glove-ounce-label.md) |
| `exercise-science` | 8 | 영문 | [boxing-strength-concurrent-training](../content/articles/boxing-strength-concurrent-training.md), [dumbbell-curl-angle-torque](../content/articles/dumbbell-curl-angle-torque.md), [early-strength-neural-adaptation](../content/articles/early-strength-neural-adaptation.md), [exercise-lactate-fuel-shuttle](../content/articles/exercise-lactate-fuel-shuttle.md), [muscle-soreness-repeated-bout](../content/articles/muscle-soreness-repeated-bout.md), [resistance-training-repetition-tempo](../content/articles/resistance-training-repetition-tempo.md), [rest-between-sets-energy-recovery](../content/articles/rest-between-sets-energy-recovery.md), [sweat-evaporation-exercise-cooling](../content/articles/sweat-evaporation-exercise-cooling.md) |
| `strength` | 5 | 영문 | [boxing-strength-concurrent-training](../content/articles/boxing-strength-concurrent-training.md), [dumbbell-curl-angle-torque](../content/articles/dumbbell-curl-angle-torque.md), [early-strength-neural-adaptation](../content/articles/early-strength-neural-adaptation.md), [muscle-soreness-repeated-bout](../content/articles/muscle-soreness-repeated-bout.md), [resistance-training-repetition-tempo](../content/articles/resistance-training-repetition-tempo.md) |
| `defense` | 1 | 영문 | [boxing-weave-keep-opponent-in-view](../content/articles/boxing-weave-keep-opponent-in-view.md) |
| `fight-review` | 6 | 영문 | [canelo-mbilli-pressure-combinations](../content/articles/canelo-mbilli-pressure-combinations.md), [dubois-wardley-rematch-result](../content/articles/dubois-wardley-rematch-result.md), [gonzalez-vazquez-body-shot-finish](../content/articles/gonzalez-vazquez-body-shot-finish.md), [kavanagh-moreno-leg-kicks-clinch](../content/articles/kavanagh-moreno-leg-kicks-clinch.md), [romero-ferreira-body-head](../content/articles/romero-ferreira-body-head.md), [smith-puello-southpaw-jab](../content/articles/smith-puello-southpaw-jab.md) |
| `review` | 4 | 영문 | [foster-navarrete-final-round](../content/articles/foster-navarrete-final-round.md), [khizriev-braga-split-decision](../content/articles/khizriev-braga-split-decision.md), [osuna-cangelosi-fifth-round-response](../content/articles/osuna-cangelosi-fifth-round-response.md), [resendiz-mazoudier-late-rally](../content/articles/resendiz-mazoudier-late-rally.md) |
| `mma` | 2 | 영문 | [kavanagh-moreno-leg-kicks-clinch](../content/articles/kavanagh-moreno-leg-kicks-clinch.md), [khizriev-braga-split-decision](../content/articles/khizriev-braga-split-decision.md) |
| `운동과학` | 1 | 한글 | [light-heavy-load-muscle-growth](../content/articles/light-heavy-load-muscle-growth.md) |
| `근력운동` | 1 | 한글 | [light-heavy-load-muscle-growth](../content/articles/light-heavy-load-muscle-growth.md) |
| `workout` | 2 | 영문 | [rest-between-sets-energy-recovery](../content/articles/rest-between-sets-energy-recovery.md), [three-day-weekend-workout](../content/articles/three-day-weekend-workout.md) |
| `science` | 1 | 영문 | [stretching-range-of-motion-tolerance](../content/articles/stretching-range-of-motion-tolerance.md) |

`boxing`과 `beginner`에는 초안 `boxing-first-class`도 포함됩니다. 공개 원고만 세면 각각 36개·26개입니다.

## 변환 전 전체 고유 kicker와 사용 원고

| 기존 kicker | 원고 수 | 언어 | 사용 원고 |
| --- | ---: | --- | --- |
| 복싱 기술 연습 | 3 | 한글 | [boxing-body-jab-level-change](../content/articles/boxing-body-jab-level-change.md), [boxing-jab-feint-response](../content/articles/boxing-jab-feint-response.md), [boxing-weave-keep-opponent-in-view](../content/articles/boxing-weave-keep-opponent-in-view.md) |
| BEGINNER BOXING | 2 | 영문 | [boxing-breathing-basics](../content/articles/boxing-breathing-basics.md), [boxing-first-class](../content/articles/boxing-first-class.md) |
| 복싱 기초 | 1 | 한글 | [boxing-combination-memory](../content/articles/boxing-combination-memory.md) |
| 하나씩 배우는 복싱 | 1 | 한글 | [boxing-feedback-one-at-a-time](../content/articles/boxing-feedback-one-at-a-time.md) |
| 초보 복싱 스텝 | 1 | 한글 | [boxing-footwork-feet-crossing](../content/articles/boxing-footwork-feet-crossing.md) |
| 복싱 장비 가이드 | 1 | 한글 | [boxing-glove-ounce-label](../content/articles/boxing-glove-ounce-label.md) |
| 복싱 기술과 교정 | 8 | 한글 | [boxing-guard-return](../content/articles/boxing-guard-return.md), [boxing-jab-without-pullback](../content/articles/boxing-jab-without-pullback.md), [boxing-lead-hook-body-rotation](../content/articles/boxing-lead-hook-body-rotation.md), [boxing-parry-small-movement](../content/articles/boxing-parry-small-movement.md), [boxing-rear-uppercut-short-path](../content/articles/boxing-rear-uppercut-short-path.md), [boxing-shadow-punch-endpoint](../content/articles/boxing-shadow-punch-endpoint.md), [boxing-slip-balance](../content/articles/boxing-slip-balance.md), [boxing-stance-front-foot](../content/articles/boxing-stance-front-foot.md) |
| BOXING BASICS | 1 | 영문 | [boxing-heavy-bag-distance](../content/articles/boxing-heavy-bag-distance.md) |
| 줄넘기 기초 | 1 | 한글 | [boxing-jump-rope-troubleshooting](../content/articles/boxing-jump-rope-troubleshooting.md) |
| 처음 배우는 복싱 | 1 | 한글 | [boxing-mirror-gaze](../content/articles/boxing-mirror-gaze.md) |
| 생활체육 복싱 입문 | 1 | 한글 | [boxing-mitt-start-signal](../content/articles/boxing-mitt-start-signal.md) |
| 복싱 방향 전환 | 1 | 한글 | [boxing-pivot-lead-foot-turn](../content/articles/boxing-pivot-lead-foot-turn.md) |
| 복싱 수업 대화 | 1 | 한글 | [boxing-sparring-participation](../content/articles/boxing-sparring-participation.md) |
| 운동과학 | 4 | 한글 | [boxing-strength-concurrent-training](../content/articles/boxing-strength-concurrent-training.md), [exercise-lactate-fuel-shuttle](../content/articles/exercise-lactate-fuel-shuttle.md), [light-heavy-load-muscle-growth](../content/articles/light-heavy-load-muscle-growth.md), [sweat-evaporation-exercise-cooling](../content/articles/sweat-evaporation-exercise-cooling.md) |
| 복싱 경기 리뷰 | 2 | 한글 | [canelo-mbilli-pressure-combinations](../content/articles/canelo-mbilli-pressure-combinations.md), [smith-puello-southpaw-jab](../content/articles/smith-puello-southpaw-jab.md) |
| 복싱 경기 돌아보기 | 4 | 한글 | [dubois-wardley-rematch-result](../content/articles/dubois-wardley-rematch-result.md), [foster-navarrete-final-round](../content/articles/foster-navarrete-final-round.md), [gonzalez-vazquez-body-shot-finish](../content/articles/gonzalez-vazquez-body-shot-finish.md), [resendiz-mazoudier-late-rally](../content/articles/resendiz-mazoudier-late-rally.md) |
| 쉽게 풀어 보는 운동과학 | 1 | 한글 | [dumbbell-curl-angle-torque](../content/articles/dumbbell-curl-angle-torque.md) |
| 쉽게 이해하는 운동과학 | 1 | 한글 | [early-strength-neural-adaptation](../content/articles/early-strength-neural-adaptation.md) |
| BEGINNER'S GUIDE | 1 | 영문 | [hangsin-boxing-gym-guide](../content/articles/hangsin-boxing-gym-guide.md) |
| 격투 스포츠 다시 보기 | 1 | 한글 | [kavanagh-moreno-leg-kicks-clinch](../content/articles/kavanagh-moreno-leg-kicks-clinch.md) |
| 격투 스포츠 경기 돌아보기 | 1 | 한글 | [khizriev-braga-split-decision](../content/articles/khizriev-braga-split-decision.md) |
| 몸으로 이해하는 운동과학 | 1 | 한글 | [muscle-soreness-repeated-bout](../content/articles/muscle-soreness-repeated-bout.md) |
| 경기로 배우는 복싱 | 2 | 한글 | [osuna-cangelosi-fifth-round-response](../content/articles/osuna-cangelosi-fifth-round-response.md), [romero-ferreira-body-head](../content/articles/romero-ferreira-body-head.md) |
| 쉽게 읽는 운동과학 | 2 | 한글 | [resistance-training-repetition-tempo](../content/articles/resistance-training-repetition-tempo.md), [stretching-range-of-motion-tolerance](../content/articles/stretching-range-of-motion-tolerance.md) |
| 운동과학 쉽게 읽기 | 1 | 한글 | [rest-between-sets-energy-recovery](../content/articles/rest-between-sets-energy-recovery.md) |
| WEEKEND WORKOUT | 1 | 영문 | [three-day-weekend-workout](../content/articles/three-day-weekend-workout.md) |

## 영문 태그 전체 변환표

| 변환 전 | 원본에 저장한 한글 | 기존 사용 원고 수 | 의미 보존·검토 메모 |
| --- | --- | ---: | --- |
| `boxing` | 복싱 | 37 | 복싱 일반 주제를 보존. 지나치게 포괄적인지 추후 검토. |
| `beginner` | 초보자 | 27 | 운동과학 글에도 사용되므로 복싱 입문으로 범위를 좁히지 않고 초보자라는 대상 의미를 보존. |
| `technique` | 복싱 기술 | 10 | 현 용례는 모두 복싱 동작 기술. |
| `practice` | 기술 연습 | 1 | 콤비네이션 익히기 용례. technique과 통합하지 않음. |
| `footwork` | 풋워크 | 2 | 복싱 발 움직임을 뜻하는 통용 표기. |
| `equipment` | 복싱 장비 | 1 | 현재 글러브 용례의 장비 의미. |
| `exercise-science` | 운동과학 | 8 | 기존 한글 운동과학과 동일한 번역. 문자열 충돌과 추천 영향을 아래에 기록. |
| `strength` | 근력 | 5 | 힘을 내는 능력이라는 근력으로 직역. 활동을 뜻하는 기존 근력운동과 구별. |
| `defense` | 방어 | 1 | 위빙 글에서의 방어 의미. 기술 또는 풋워크와 합치지 않음. |
| `fight-review` | 경기 리뷰 | 6 | 경기를 돌아보는 의미. 일반 review와 구분해 유지. |
| `review` | 리뷰 | 4 | 범위를 임의로 경기 분석으로 확정하지 않고 리뷰로만 표기. fight-review와 통합 보류. |
| `mma` | 종합격투기 | 2 | 종합격투기라는 종목명. |
| `workout` | 운동 프로그램 | 2 | 현재의 주말 일정·세트 간 휴식 구성 용례를 운동 프로그램으로 표기. 세부 기준은 추후 검토. |
| `science` | 과학 | 1 | 과학으로만 직역. 운동과학으로 좁히거나 해당 태그와 합치지 않음. |

기존 한글 `운동과학`(1개), `근력운동`(1개)은 그대로 유지했습니다. 의미 범위가 불분명한 `science`, `review`, `strength`는 각각 과학·리뷰·근력이라는 직역을 보존했으며, 다른 개념과의 동치 관계나 최종 명칭을 결정하지 않았습니다.

## 변환 후 고유 태그와 사용 수

아래 역시 초안 포함 Markdown 기준입니다. manifest의 복싱 태그 5개는 별도이며 고유 태그 수에는 영향을 주지 않습니다.

| 저장된 태그 | 원고 수 |
| --- | ---: |
| 복싱 | 37 |
| 초보자 | 27 |
| 복싱 기술 | 10 |
| 기술 연습 | 1 |
| 풋워크 | 2 |
| 복싱 장비 | 1 |
| 운동과학 | 9 |
| 근력 | 5 |
| 방어 | 1 |
| 경기 리뷰 | 6 |
| 리뷰 | 4 |
| 종합격투기 | 2 |
| 운동 프로그램 | 2 |
| 과학 | 1 |
| 근력운동 | 1 |

## 변경한 kicker

카테고리 이름으로 일괄 치환하지 않았습니다. 기존 글 성격과 의미에 맞춰 다음 네 종류만 바꾸고 이미 한글인 표현은 유지했습니다.

| 기존 Markdown kicker | 저장한 한글 | 원고 수 | 대상 |
| --- | --- | ---: | --- |
| BEGINNER BOXING | 복싱 입문 가이드 | 2 | [boxing-breathing-basics](../content/articles/boxing-breathing-basics.md), [boxing-first-class](../content/articles/boxing-first-class.md) |
| BOXING BASICS | 복싱 기초 | 1 | [boxing-heavy-bag-distance](../content/articles/boxing-heavy-bag-distance.md) |
| BEGINNER'S GUIDE | 복싱장 선택 가이드 | 1 | [hangsin-boxing-gym-guide](../content/articles/hangsin-boxing-gym-guide.md) |
| WEEKEND WORKOUT | 주말 운동 루틴 | 1 | [three-day-weekend-workout](../content/articles/three-day-weekend-workout.md) |

### 보호 HTML과 manifest

아래 HTML 5개는 원본 바이트·보호 해시·본문·내부 영문 kicker를 그대로 두었습니다. manifest의 `boxing` 태그만 복싱으로 바꾸고, 목록/메인 카드에서 사용하는 별도 kicker도 한글로 저장했습니다. 그러므로 **보호 상세 페이지 내부에는 영문 문구가 남습니다.** 이는 이번 작업의 명시적 제외 범위입니다.

| 보호 HTML | 원본 내부/기존 manifest kicker | 새 manifest 카드 kicker |
| --- | --- | --- |
| [hangsin-diet-workout.html](../articles/hangsin-diet-workout.html) | HANGSIN DIET WORKOUT | 행신동 다이어트 운동 |
| [euljiro-diet-workout.html](../articles/euljiro-diet-workout.html) | EULJIRO DIET WORKOUT | 을지로 다이어트 운동 |
| [boxing-diet-beginner.html](../articles/boxing-diet-beginner.html) | BEGINNER BOXING DIET | 초보 복싱 다이어트 |
| [boxing-calorie-burn.html](../articles/boxing-calorie-burn.html) | BOXING CALORIE BURN | 복싱 칼로리 소모 |
| [stress-relief-boxing.html](../articles/stress-relief-boxing.html) | STRESS RELIEF BOXING | 스트레스 해소 복싱 |

## 최종 사전 확정 전 검토 대상

| 후보·문제 | 현재 처리 | 후속 검토 질문 |
| --- | --- | --- |
| boxing / 복싱 | 37개 원고에서 의미 보존 | 대부분 글에 붙는 종목 태그가 분류·추천에 유용한가? 기본값과 선택값을 구별할 것인가? |
| beginner / 초보자 | 대상 독자라는 의미 보존 | 복싱 입문 카테고리와 독자 수준 태그를 구별할 것인가? 운동과학 입문에도 공통 사용 가능한가? |
| review / fight-review | 리뷰 / 경기 리뷰로 구분 | 현재 용례는 모두 경기 글이지만 같은 뜻으로 의도했는가? 최종 통합 승인 전에는 두 그룹을 합치지 않음. |
| science / exercise-science / 운동과학 | 과학 / 운동과학으로 보존 | science 용례가 운동과학만을 의도했는가? 그 범위를 확정한 뒤 동의어 여부를 정할 것. |
| strength / 근력운동 | 근력 / 근력운동으로 구분 | 능력과 훈련 활동을 별개 주제로 유지할 것인가? 명칭 통합 시 추천 연결이 달라짐. |
| technique / practice / footwork / defense | 복싱 기술 / 기술 연습 / 풋워크 / 방어 | 넓은 기술 태그와 세부 기술·연습 방식의 상하위 관계를 어떻게 표현할 것인가? |
| workout / 운동 프로그램 | 두 원고 용례를 유지 | 운동 일정과 세트 구성·회복을 같은 태그로 묶을지, 범위를 더 구체화할지 검토. |
| 운동과학 계열 kicker 여러 표현 | 기존 한글 표현 유지 | kicker는 태그가 아니므로 굳이 하나로 통일할 필요가 있는가? 글별 문체를 허용할 것인가? |

위 항목은 조사·검토 목록이며 이번 PR에서 삭제·분할·최종 통합 정책을 적용하지 않았습니다.

## 관련 글 추천 전후 비교

기준 커밋의 실제 빌드 HTML에서 관련 글 패널을 추출하고 한글화 후 공개 Markdown 44개 패널을 같은 순서로 비교했습니다. **43개 동일, 1개 변경**입니다. `related` frontmatter와 추천 알고리즘의 명시적 연결 우선순위·태그 중복 수·URL 정렬·최대 3개 규칙은 수정하지 않았습니다.

변경 대상: [가벼운 무게로도 근육이 자랄까?](../content/articles/light-heavy-load-muscle-growth.md)

| 순서 | 변환 전 추천 URL | 변환 후 추천 URL |
| --- | --- | --- |
| 1 | `/articles/boxing-body-jab-level-change.html` | `/articles/boxing-strength-concurrent-training.html` |
| 2 | `/articles/boxing-breathing-basics.html` | `/articles/dumbbell-curl-angle-torque.html` |
| 3 | `/articles/boxing-calorie-burn.html` | `/articles/early-strength-neural-adaptation.html` |

이 원고의 원래 한글 태그는 운동과학·근력운동이었고, 다른 글의 exercise-science·strength와 문자열이 달라 태그 일치가 없었습니다. exercise-science 8개가 운동과학으로 번역되어 이제 공통 태그 1개가 생겼습니다. 기존 URL 동률 정렬에 따라 운동과학 글 3개가 선택됩니다. strength는 근력으로 번역했으므로 근력운동과는 여전히 별개입니다. 이 원고 자체의 태그·본문·관련 글 명시값은 바꾸지 않았습니다. 다른 43개 결과와 모든 명시적 related 값은 유지됩니다.

## 사이트 형식과 향후 러너 규칙

### 현재 사이트가 허용하는 형식

- UTF-8 YAML의 `tags`는 비어 있지 않은 문자열 원소로 이루어진 목록입니다. 선택 필드이므로 생략/빈 목록도 기존 계약상 허용됩니다. 각 원소에 `.strip()` 후 내용이 있는지 검사하며 원문 문자열끼리 정확히 비교합니다. 한글·영문을 특정 문자 집합으로 제한하거나 태그를 enum으로 제한하는 검증은 없습니다.
- `kicker`는 내용이 있는 필수 문자열입니다. 한글을 그대로 파싱하고 Jinja2 자동 이스케이프를 거쳐 출력합니다. 태그/kicker를 별도 ID로 바꾸거나 출력 시 번역하지 않습니다.
- 태그는 관련 글의 문자열 일치에 사용됩니다. 공백·맞춤법·유니코드 정규화가 다른 별칭을 자동 합치지 않습니다. 이번 데이터는 NFC 한글이며 기존 태그 순서와 원고별 개수를 유지합니다.
- 카테고리의 영문 ID/한글 표시명, URL·날짜·SEO 키워드/설명·본문·이미지·JSON-LD·사이트맵·메뉴·필터·자동 전환 계약은 유지합니다.

### 러너가 앞으로 생성할 원고

1. 한글 태그를 `tags: ["초보자", "복싱", "복싱 기술"]`처럼 YAML 원문에 직접 저장합니다. 영문 식별자/번역명 쌍을 만들지 않습니다.
2. 태그는 글의 종목·주제·대상·기술을 정확히 표현하도록 고르고, 최종 사전 미확정 상태에서는 이번 표를 고정 허용 목록으로 취급하지 않습니다. 뜻이 같은 표현의 오탈자·공백 변형과 원고 안의 중복은 피합니다. NFC 정규화와 앞뒤 공백 제거를 권장합니다.
3. `beginner`를 무조건 복싱 입문으로 좁히는 등 문맥과 다른 해석을 피합니다. 의미가 애매하면 후보·근거와 함께 사람 검토로 넘기고 무리하게 기존 태그와 합치지 않습니다.
4. kicker는 해당 글을 설명하는 짧고 자연스러운 한국어 문구로 작성합니다. 카테고리명으로 강제하거나 SEO 키워드를 나열하지 않습니다. 한글 줄바꿈과 실제 카드·모바일 표시를 확인합니다.
5. 기존 메타데이터 계약과 보호 검사·빌드·SEO 검증을 그대로 실행하고, 태그 변경 시 명시적 연결과 자동 추천 전후를 비교합니다.

### 러너를 바꾸기 전의 호환성

사이트 파서는 영문 문자열도 읽을 수 있으므로 옛 러너가 작성한 영문 태그/kicker가 곧바로 YAML 또는 빌드를 깨뜨리지는 않습니다. 다만 영문 boxing과 한글 복싱은 다른 문자열이므로 추천 연결이 분리되고, 영문 kicker가 화면에 다시 나타납니다. 현재 원고 한글화 회귀 검사도 만족하지 못할 수 있습니다. 따라서 러너 프롬프트/원고 예시/출력 검토 규칙을 별도 변경하기 전에는 생성 원고를 사람 검토 후 제출해야 합니다. 이 PR은 사이트 저장소만 수정하며 러너·프리뷰 저장소는 수정하지 않습니다.

### 향후 표준 사전 확정 시 변경 지점

러너 프롬프트와 출력 스키마/예시, 작성 문서, 기존 Markdown 및 legacy manifest의 태그 데이터, 회귀 테스트가 검토 대상입니다. 사이트에 사전을 도입한다면 허용값/동의어/정규화/폐기 태그 이행 방식과 추천 변화에 대한 승인을 먼저 정해야 합니다. `scripts/build.py`의 자유 문자열 검증과 추천 문자열 비교를 바꾸는 작업은 별도 정책 변경으로 다루며 가중치·정렬을 임의로 바꾸지 않습니다. 현재 카테고리 정의를 태그 사전으로 재사용하거나 화면 번역 계층을 추가할 이유는 없습니다.

## 검증 기록

보호 HTML의 Windows CRLF 차이를 피하려고 `core.autocrlf=false`인 별도 임시 복제본에서 검증했습니다. 실행 위치는 `C:/Users/hsg/AppData/Local/Temp/redboxing-localization-_s8cnbmp/repo`, Python은 3.14.6이며 기존 고정 의존성과 Playwright Chromium을 사용했습니다. 기준 스냅샷·추천 비교 자료는 저장소 밖에 두었으며, production에 영문 태그 별칭 데이터를 추가하지 않았습니다.

```powershell
python scripts/check_changes.py
$env:RUN_BROWSER_TESTS = '1'
python -m unittest discover -s tests -v
python scripts/build.py
python scripts/validate.py
```

- 보호 검사 통과: 첫 부모 커밋 56개에 걸친 공개 URL 44개 잠금 및 원본 보호 파일을 확인했습니다.
- 전체 테스트 **62개 모두 통과**, 제외 없음. 일반 48개와 브라우저 14개입니다. 한글 YAML/Jinja 이스케이프·NFC 원문·사전 밖의 임의 태그·영문 문자열 파싱 하위 호환·한글 태그 추천 및 명시적 연결 우선순위를 검증했습니다.
- 기존 자동 전환 테스트의 고정 100ms 대기를 실제 브라우저 미디어 변경 이벤트를 기다리도록 보완했습니다. 앱의 타이머·동작 줄이기 처리 코드는 수정하지 않았으며 해당 검사를 별도로도 통과했습니다.
- 새 태그 화면 검사는 원고에서 태그 집합과 검수 대상을 자동 선정하므로 고정 허용 목록을 강제하지 않습니다. 검수 대상 자동 선정으로 보완한 뒤 해당 브라우저 검사를 별도로 다시 실행했습니다.
- 빌드 및 독립 SEO 검증 통과: HTML 53개, 기존 HTML 5개·공개 Markdown 44개·초안 1개 제외. 두 사이트맵과 리소스·앵커 검사 정상입니다.
- 기준 커밋의 별도 빌드와 비교해 HTML 53개의 title/canonical/meta/JSON-LD가 동일했습니다. Markdown 45개의 본문 및 tags/kicker 이외 메타데이터, 렌더링 본문 44개, legacy manifest의 보호 해시 및 tags/kicker 이외 필드, 보호 HTML 바이트·사이트맵·robots.txt도 동일합니다.
- 관련 글은 위에 기록한 1개만 변경됐으며 나머지 43개는 동일했습니다. 알고리즘·가중치·정렬·명시적 related는 유지합니다.
- 360/390/1440px에서 새 kicker 네 종류와 한글 태그 표시를 실제 렌더링했습니다. 현재 태그 15종을 모두 검사했으며 가로 넘침과 kicker 영역 넘침이 없었습니다. 목록 카드 49개의 kicker도 한글이고 기존 7개 카테고리 필터를 유지합니다.
- `C:/Users/hsg/AppData/Local/Temp/redboxing-localization-_s8cnbmp/qa`의 모바일·PC 스크린샷을 직접 열어 글자 크기·줄바꿈·간격을 확인했습니다. 이는 로컬 증거 경로이며 공유 프리뷰 URL은 아닙니다. CSS·템플릿·사이트 JavaScript 수정은 필요하지 않았습니다.

GitHub Python 3.12 `content-check` 및 최신 `site-review` 링크는 PR #93 설명에서 확인합니다. 러너·프리뷰 저장소, main, 배포 설정은 변경하지 않았으며 병합·배포하지 않습니다.
