---
name: dart-agent-release
description: Release kalstein00/dart-agent against an official kalstein00/DART app release. Use when asked to prepare, update, or publish the dart-agent release; optional DART tag or release URL, defaulting to the latest stable release. Excludes controlling the running DART app and creating or editing this skill.
---

# DART Agent Release

`kalstein00/dart-agent`의 DART 제어 스킬·번들·설치 도구를 공식 `kalstein00/DART` 릴리즈에 맞추고, 요청된 범위까지 검증·발행한다. Python은 항상 `uv run --no-project python`으로 실행한다.

## 입력과 기본값

- `$dart-agent-release`: 실행 시 DART 앱의 최신 정식 릴리즈를 조회해 dart-agent 릴리즈를 진행한다.
- `$dart-agent-release v2.1.1`: 지정한 DART 태그를 사용한다.
- `$dart-agent-release https://github.com/kalstein00/DART/releases/tag/v2.1.1`: URL에서 정확한 저장소와 태그를 확인해 사용한다.
- 사용자가 준비만·검토만·초안만 요청하면 그 범위를 지킨다. 스킬 작성·설치 요청 자체는 릴리즈 실행 요청이 아니다.

선택값은 자연어 요청이나 스킬 이름 뒤의 태그/URL에서 읽는다. 필수 인자는 없다. DART 앱 태그와 dart-agent 태그는 별개의 버전이다.

## 1. 대상 릴리즈를 고정한다

현재 체크아웃의 `AGENTS.md`, 도메인 문서와 `docs/release-preparation.md`, `docs/installation.md`, 기존 도구·테스트를 읽는다. remote가 `kalstein00/dart-agent`인지 확인하고 작업 트리와 진행 중인 릴리즈를 확인한다. 관련 없는 사용자 변경을 보존한다. 해당 체크아웃이 없으면 위치를 확인한다.

인자가 없으면 인증된 `gh`로 아래 API를 조회한다. 날짜나 태그 문자열 정렬, 로컬 lock, 이전 채팅의 버전으로 최신값을 추측하지 않는다.

```bash
gh api repos/kalstein00/DART/releases/latest
```

태그를 지정하면 해당 태그를 URL 인코딩해 아래 API를 사용한다. URL은 `https://github.com/kalstein00/DART/releases/tag/` 경로만 이 저장소의 릴리즈로 해석한다.

```text
gh api repos/kalstein00/DART/releases/tags/ENCODED_TAG
```

기본 선택은 GitHub가 latest로 지정한 정식 릴리즈이며 draft/prerelease를 제외한다. 명시된 prerelease 태그/URL은 해당 시험판 대상 요청으로 해석한다. Draft upstream 릴리즈는 발행된 공식 자산 기준이 아니므로 입력으로 사용하지 않고 상태를 보고한다. 조회 실패·인증 실패·없는 태그는 원인을 보고하고 중단한다. 다른 태그나 개발 후보로 자동 대체하지 않는다.

선택한 응답 전체를 작업용 `dist/` 하위 새 디렉터리에 저장하고 tag, Release ID, URL, published_at, 본문, 자산 ID·이름·크기·digest를 고정한다. 같은 실행 중 latest를 다시 선택하지 않는다. annotated tag는 실제 commit까지 역참조하고 tree도 조회한다. `target_commitish`는 브랜치명일 수 있으므로 실제 태그 commit을 기준으로 한다.

현재 compatibility, 기본 lock, 원격 dart-agent 최신 릴리즈와 첨부물도 대조한다. 같은 upstream 태그·계약·자산 해시가 이미 정식 배포됐고, 현재의 스킬·도구 등 릴리즈 대상 변경까지 그 dart-agent 태그에 포함되며 사용자가 별도 새 버전을 요청하지 않았다면 기존 릴리즈 링크와 함께 완료한다. 같은 upstream을 사용하더라도 미발행 변경이 있으면 그 변경을 포함한 새 dart-agent 릴리즈를 진행한다. 같은 태그의 자산이 바뀌었다면 차이를 조사하고 기존 lock·공개 태그를 덮어쓰지 않는다. 초안이나 일부만 발행된 작업은 일치하는 commit과 자산을 확인한 뒤 이어간다.

## 2. 공식 자산과 소비자 계약을 함께 갱신한다

릴리즈 본문과 공식 agent/CLI manifest, versioned manifest, catalog, Reference를 읽고 releaseVersion, protocolVersion, formatVersion, contractVersion과 전체 fingerprint를 확인한다. 이번에 추가·삭제·변경된 명령과 연결 UI 위치를 스킬 지침에 반영한다. 특히 구버전 CSV 명령을 새 file export 계약으로 오인하지 않는다.

공식 자산은 인증된 `gh api -H 'Accept: application/octet-stream' repos/kalstein00/DART/releases/assets/ASSET_ID`로 받는다. 비공개 upstream의 브라우저 URL 404를 릴리즈 부재로 해석하지 않는다. 바이너리는 `subprocess.run(..., stdout=opened_binary_file, check=True, timeout=...)`처럼 바이트 그대로 저장한다. 다운로드가 정체되면 제한된 재시도나 범위 다운로드 후 전체 크기·SHA256으로 최종 파일을 확인한다. 실패한 파일은 실행하거나 패키징하지 않는다.

원본 manifest에 `status: candidate` 또는 source `status: declared`가 있어도 공개 Release에 첨부된 사실과 구분해 원본 그대로 보존한다. 선언된 source와 실제 태그 commit/tree의 차이는 조사한다. 파일 hash 일치로 소스 빌드 재현이나 Main 연결 성공을 주장하지 않는다.

기존 `tools/prepare_release.py`, `tools/package_release.py`, `tools/install.py`와 `skills/dart-control/compatibility.json`을 기준으로 변경한다.

- 새 `release/dart-VERSION.lock.json`에 실제 Release 출처와 필요한 공식 자산 ID·크기·SHA256, 기존·버전된 계약, 후보 ID/source를 고정한다. 이전 lock은 이력으로 보존한다. 자산 목록·개수는 현재 manifest와 소비 도구로 결정하며 이전 릴리즈의 개수를 복사하지 않는다.
- 기본 lock과 compatibility를 새 기준으로 맞추고, 버전·protocol·manifest 형식의 고정 검사 및 관련 테스트를 조정한다. 새로운 protocol을 단순 허용하는 대신 실제 identity/export와 catalog가 정확히 일치해야 한다.
- dart-agent 버전은 기존 태그와 변경 성격에서 정한다. 사용자 지정 버전을 우선한다. 호환성을 깨는 protocol/contract 변경은 0.x에서 minor, 1.x 이상에서 major를 올리고, 그 외 기능은 minor·수정은 patch로 정한다. DART 앱 버전을 그대로 복사하지 않는다.
- `skills/dart-control/SKILL.md`, `references/connection.md`, `references/analysis.md`, README와 설치·릴리즈 문서 중 영향을 받는 부분을 갱신한다. CLI와 connected Main을 각각 배포 기준과 비교하는 절차를 유지한다. 과거 검증 기록은 당시의 관측으로 보존한다.

## 3. 준비·설치·업데이트를 검증한다

`prepare_release.py --source-dir ASSETS --output FRESH_PREPARED_DIR`로 새 디렉터리에 준비하고 `package_release.py --source-dir FRESH_PREPARED_DIR --output FRESH_ZIP`으로 패키징한다. 검증된 ZIP만 저장소의 `release/dart-agent-release-assets.zip`으로 반영한다. 기존 출력 경로를 쓰는 도구는 임시 출력부터 만든다.

준비·설치 시 파일 크기·SHA256, manifest·bundle 내부 결합, 플랫폼, 기존·버전된 catalog를 검증한다. 현재 OS의 최종 공식 CLI로 version, identity, full export, versioned identity/export를 실행하고 응답 protocol·계약·전체 export를 lock/catalog와 대조한다. upstream이 이 명령 체계를 바꿨다면 새 공식 계약을 확인해 도구를 조정한다.

설치는 `--skills-dir`로 지정한 임시 경로에서 최초 설치와 같은 명령의 업데이트를 확인한다. 설치된 CLI의 versioned identity를 재확인하고, 잘못된 계약·변조·누락 자산이 기존 설치와 개인 프로필을 보존하는지 관련 테스트로 확인한다. 사용자의 실제 전역 스킬이나 연결 프로필은 릴리즈 검증용으로 교체하지 않는다.

```bash
uv run --no-project python -m unittest discover -s tests -v
```

실제 통과·실패·skip 개수와 검증 OS를 기록한다. 문서 링크와 스킬이 명시한 명령을 새 catalog에 대조한다. Windows 실행·Linux 파일 무결성·Linux 실행·실제 Cline/Main/PIN/업무·회사 환경을 구분한다. 수행하지 않은 앱 연결 인수는 미검증으로 명시한다. 필수 자산·오프라인 계약·설치 검증이 실패하면 발행 전에 해결한다.

## 4. 요청된 릴리즈를 발행하고 공개 경로를 확인한다

실제 변경·신규 lock·번들·문서·검증 결과를 검토하고 대상 파일만 Conventional Commit으로 커밋한다. 릴리즈 진행 요청은 필요한 commit/push/tag/Release 발행을 포함한다. 준비·검토·초안 요청은 해당 경계에서 끝낸다. 이미 받은 권한을 다시 확인하지 않는다.

전체 commit SHA로 대상 remote branch에 정상 push하고 원격 SHA를 확인한다. force push나 기존 공개 태그 이동 없이 새 dart-agent 태그를 사용한다. 새 ZIP, lock, 민감 경로를 제거한 distribution manifest와 그 첨부물들의 `SHA256SUMS`를 준비한다. 검증 로그의 개인 경로·프로필·PIN·인증 정보를 첨부하지 않는다.

정확한 릴리즈 노트를 파일로 작성해 `--notes-file`로 전달한다. upstream 링크, 앱/CLI/protocol/contract 요구사항, 변경된 스킬 동작, 고정 태그 clone 설치·업데이트 명령, 검증 범위와 미검증 항목을 포함한다.

1. `gh release create AGENT_TAG ... --target FULL_COMMIT_SHA --draft`로 파일을 올린다. 전체 SHA를 사용한다.
2. 초안의 대상 commit·첨부물 목록·크기·상태와 GitHub digest를 로컬 SHA256에 대조한다. digest가 없으면 해당 첨부물을 다시 내려받아 검증한다. 기존 초안은 같은 대상인지 확인한 뒤 재사용한다.
3. 검증 후 `gh release edit AGENT_TAG --draft=false`로 공개한다. 정식 릴리즈는 `--latest`, 요청된 시험판은 `--prerelease`를 적용하고 정식 latest를 바꾸지 않는다.
4. 공개 태그를 새 디렉터리에 clone하고 commit과 ZIP hash를 확인한다. 그 clone의 설치 도구로 임시 경로 최초 설치·동일 명령 업데이트와 설치된 CLI identity를 확인한다. 실패하면 게시 후 검증 실패를 보고하고 조사하며, 기존 태그나 릴리즈를 자동 삭제·이동하지 않는다.
5. 최종 Release가 draft가 아닌지, tag/commit/첨부물이 의도와 같은지 재조회한다. 공개 clone 검증 결과를 릴리즈 노트에 보충하고 작업 트리 상태를 확인한다.

완료 보고에는 릴리즈 링크, commit, 앱/protocol/contract 기준, 핵심 검증 결과와 미검증 환경을 간결하게 제시한다. 이미 최신인 경우에는 재발행하지 않았다는 결과와 기존 링크를 제시한다.
