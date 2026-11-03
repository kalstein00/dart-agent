# #3 설치·연결 검증

2026-11-03, 개발 PC의 WSL2 Linux x86_64 (kernel 6.18.54.1, glibc 2.39), Cline CLI 3.0.74. 회사의 WSL 없는 Linux 배포판과 회사 네트워크는 별도 검증 대상이다.

## 설치 출처

`tools/prepare_release.py`가 #2에서 실제 공식 DART v2.1.0 자산을 내려받아 검증한 준비 출력으로 `tools/install.py --prepared-dir ...`를 실행했다. 전역 `~/.cline/skills/dart-control` 설치 및 명시적 `--update`가 성공했다. 설치된 Linux CLI 실제 `version`, `contract identity`가 2.1.0, protocol 2, format 2, fingerprint `6fc2f2381407bc3b1193293dae8a78dbfec6412ca1e8619d061a957dbb597042`를 보고했다.

이 실행은 `development-prepared-assets` 설치다. dart-agent `v0.1.0` Release는 아직 없으며, 기본 공개 설치 명령은 실패하고 사용 가능한 스킬을 게시하지 않았다. 발행된 Release 설치 성공 증거는 #8 최종 게이트에 남긴다. Release 발행·push는 수행하지 않았다.

## 실제 Cline 및 연결

첫 실제 Cline 요청에서 `skills` 도구가 `dart-control`을 로드하고 설치된 공식 CLI의 version/contract identity를 성공적으로 호출했다. 연결 프로필이 없을 때 Windows 앱 실행·Remote Access·새 번들 조치를 보고했다.

Windows 담당자가 발급한 새 번들을 파일 stdin으로 공식 CLI에 등록했다. 목적별 인수 프로필 `dart-agent-acceptance-3`을 생성했으며 번들·토큰·개인 프로필 내용을 출력하거나 배포물에 넣지 않았다. 연결된 Windows Main의 독립적인 `app inspect`가 installed 2.1.0, protocol 2, 동일 계약 fingerprint와 `observation.source=connected-main`을 보고했다.

실제 Cline 요청이 `dart-control`을 로드한 뒤 설치된 CLI로 version → contract identity → app inspect → window list → session create → session inspect를 수행했다. 창은 하나였고, 반환된 제어 세션과 창은 모두 open이었다. 후속 상태 확인에서 같은 app/window/session으로 session inspect를 한 번 더 호출해 두 번째로 모두 open임을 확인했다. 이 Cline 요청은 exit 0으로 끝났고 모든 CLI 응답이 ok=true였다. 공개 대상 식별자는 다음과 같다.

- appId: `2d6a2777-871b-4006-849e-740b134a37ba`
- windowId: `8babf7ad-4464-4fbe-b779-4ee8339c9ea0`
- sessionId: `4d1c6ca5-cf47-4789-9359-b794f35e90fc`

Cline의 실제 호출은 JSON 이벤트의 `skills(dart-control)` 및 `run_commands` 결과로 확인했다. 이 ID는 현재 앱 실행에 한정되며 재시작 후 재사용하지 않는다.

## 집중 검사

`uv run --no-project python -m unittest discover -s tests -p test_install.py -v`: 4 tests, 성공, skip/retry 없음. 설치 성공·명시적 업데이트·개인 프로필 보존·깨진 자산과 Release 실패 시 기존 설치 보존을 공개 설치 진입점에서 검사했다. 최초 RED는 설치 진입점 부재로 실패했고 구현 후 GREEN을 확인했다.

전체 테스트와 공통 최종 검사는 배치 상위 작업이 최종 통합 후보에서 실행한다.
