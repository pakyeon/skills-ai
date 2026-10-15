# 종합 방법론 설계와 출처

이 방법론은 사용자 프로젝트의 문서 저장·유지 관리에 맞춘 독자적인 종합 설계다. 모든 분야에서 검증된 공식 표준이나 완전무결한 시스템이라고 주장하지 않는다. 지침, 실제 구현된 점검 기능, 향후 선택적인 도구를 구분한다.

## 사용한 여섯 후보

모두 2026-10-13 GitHub API 조회 시 1,000 stars 이상이었다. 아래 커밋과 해당 문서를 검토했으며 원문이나 프로그램을 그대로 복제하지 않았다.

| 저장소 | Stars | 검토 버전 | 채택한 원칙 |
| --- | ---: | --- | --- |
| [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) | 15,482 | [32ac5a02](https://github.com/AgriciDaniel/claude-obsidian/commit/32ac5a02c4e082e4a5628ca810776375e134708e) | 원자료·주장·처리 장부 분리, 출처 독립성, 복구 가능한 변경 |
| [SamurAIGPT/llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent) | 3,616 | [a17ab5df](https://github.com/SamurAIGPT/llm-wiki-agent/commit/a17ab5df66da9b74a0eaeb664a67d662d0fb166d) | 연결된 개념·자료·종합 문서, 빠른 구조 점검과 의미 검토 분리 |
| [sdyckjq-lab/llm-wiki-skill](https://github.com/sdyckjq-lab/llm-wiki-skill) | 2,535 | [efa2294d](https://github.com/sdyckjq-lab/llm-wiki-skill/commit/efa2294dd7c00479f7d8463fef88812d2fd5d1bc) | 추출·추론·미확인 구분, 대화의 지식 정리, 변경 감지와 연결 복구 |
| [Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki) | 2,474 | [eafcc770](https://github.com/Astro-Han/karpathy-llm-wiki/commit/eafcc77001e496cc43499e4923b663aec722c813) | 작성 전 신규·갱신·충돌 분류, 근거 위치 확인, 관련 문서 갱신과 과거 기록 보존 |
| [atomicstrata/llm-wiki-compiler](https://github.com/atomicstrata/llm-wiki-compiler) | 2,181 | [a3eb4473](https://github.com/atomicstrata/llm-wiki-compiler/commit/a3eb4473b0b2d2aa747d2f4a7f683d35efe16521) | 분석 후 생성, 출처 간 중복 통합, 입력 해시와 반영 문서의 증분 처리 |
| [nvk/llm-wiki](https://github.com/nvk/llm-wiki) | 1,408 | [95a042c6](https://github.com/nvk/llm-wiki/commit/95a042c68998559305bc69ac8c482c4e1a415ad3) | 프로젝트·주제의 경계, 파생 색인, 점진적 적용, 조용한 아카이브 |

## 확인한 운영 문서

- [AgriciDaniel: 근거 계약](https://github.com/AgriciDaniel/claude-obsidian/blob/32ac5a02c4e082e4a5628ca810776375e134708e/skills/wiki/references/provenance.md), [변경·복구 계약](https://github.com/AgriciDaniel/claude-obsidian/blob/32ac5a02c4e082e4a5628ca810776375e134708e/skills/wiki/references/operation-transactions.md).
- [SamurAIGPT: 운영 스키마](https://github.com/SamurAIGPT/llm-wiki-agent/blob/a17ab5df66da9b74a0eaeb664a67d662d0fb166d/AGENTS.md).
- [sdyckjq-lab: 스킬 운영 규칙](https://github.com/sdyckjq-lab/llm-wiki-skill/blob/efa2294dd7c00479f7d8463fef88812d2fd5d1bc/SKILL.md), [기능과 이름 변경·복구 설명](https://github.com/sdyckjq-lab/llm-wiki-skill/blob/efa2294dd7c00479f7d8463fef88812d2fd5d1bc/README.md).
- [Astro-Han: 통합·근거·갱신 규칙](https://github.com/Astro-Han/karpathy-llm-wiki/blob/eafcc77001e496cc43499e4923b663aec722c813/SKILL.md).
- [atomicstrata: 두 단계 처리](https://github.com/atomicstrata/llm-wiki-compiler/blob/a3eb4473b0b2d2aa747d2f4a7f683d35efe16521/docs/concepts/how-it-works.mdx), [문서·처리 상태 모델](https://github.com/atomicstrata/llm-wiki-compiler/blob/a3eb4473b0b2d2aa747d2f4a7f683d35efe16521/docs/concepts/wiki-model.mdx).
- [nvk: 위키 운영 원칙](https://github.com/nvk/llm-wiki/blob/95a042c68998559305bc69ac8c482c4e1a415ad3/claude-plugin/skills/wiki-manager/SKILL.md), [파생 색인](https://github.com/nvk/llm-wiki/blob/95a042c68998559305bc69ac8c482c4e1a415ad3/claude-plugin/skills/wiki-manager/references/indexing.md).

## 충돌을 해결한 기준

| 후보 사이의 차이 | 이 프로젝트용 설계 |
| --- | --- |
| 개념·개체별 문서와 종류별 폴더 | 사용자 요구에 따라 문서 종류가 주 분류다. 별칭·관계로 교차 주제를 연결한다. |
| 수집마다 새 요약 생성과 중복 통합 | 새 정보와 별도 재사용 목적이 있을 때만 생성하고 기존 대표 문서를 먼저 갱신한다. |
| 출처 표기와 사실 검증의 혼용 | 출처에 있는지, 내용이 맞는지, 지금도 유효한지를 별도로 검토한다. |
| 오래된 정보 자동 감쇠 | 오래됐다는 이유로 폐기하지 않는다. 변경·적용 범위·재확인 필요를 점검한다. |
| 전체 자동 수정과 검토 중심 처리 | 명확한 연결·색인 오류 및 허용된 통합은 수정하고 근거 없는 판단은 미해결로 남긴다. |
| 위키 링크와 Markdown 링크 | 상대 Markdown을 기본으로 하고 Obsidian 연결은 필요할 때 명확한 경로로 추가한다. |
| 고정 문서 길이·링크 수·폴더 깊이 | 문서 목적과 재사용 가치를 기준으로 분리·통합한다. |
| 원자적 일괄 변경과 일반 파일 도구 | 변경 전 버전·작업 기록·충돌 확인을 적용한다. 도구가 지원하는 원자성 범위만 주장한다. |
| 구조 검사 성공과 신뢰도 상승 | 형식·해시 검사로 사실 검증이나 결정 승인을 대신하지 않는다. |

사용자 요구에서 온 `docs/`, 종류별 역할, 작업일지·진행 기록, 통합과 `legacy/` 결정 보존은 유지한다. 이전에 도입했던 특정 계획·진행·결정 파일의 고정 세트, 같은 파일명 강제, 별도 작업 결정 폴더와 전용 탐색·증상 표 강제는 제거했다.

## 운영 규모와 갱신

작은 프로젝트는 Markdown·색인·근거 링크로 시작한다. 실제 출처와 중요한 주장이 생기면 장부를 만들고, 반복 구조 점검에는 포함된 스크립트를 쓴다. 자료량 때문에 조회가 어려워지면 종류별 색인·검색·선택적 그래프를 추가한다. 별도 검색·임베딩 프로그램은 자동 설치하지 않는다.

변경된 규칙은 해결하려는 문제, 출처 버전, 기존 문서에 대한 영향을 확인해 `schema.md`에 반영한다. 별 수는 출처 선정 기준이며 개별 기능의 정확성을 보장하는 증거가 아니다. 새로운 방법론을 조사했다고 기존 구조를 자동 이전하지 않는다.
