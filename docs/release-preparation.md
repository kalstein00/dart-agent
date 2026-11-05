# DART CLI 자산 준비

## 현재 개발 후보 — 2026-11-05

기본 lock `release/dart-2.1.0.lock.json`과 저장소 ZIP은 DART 소스 커밋 `14a85e60d8ce69098bfba04e708abf409d5d2ff8`의 개발 후보이며 공개 릴리스가 아니다. 해당 후보의 계약 fingerprint는 `4f523920d4db114df90df3e46ea828de0d08bc7a52514d8d36b2035ad09418d5`다. 공개 `v2.1.0`의 원래 lock은 `release/dart-2.1.0-release.lock.json`에 보존한다. 동일 버전 문자열은 동일 계약을 보장하지 않는다.

DART의 Bun 1.4.3 `buildStandalone.mjs` 산출물과 `acceptanceBundle.mjs generate`, `generateAgentBundle` 산출물에서 Linux/Windows CLI, manifest, reference, catalog와 bundle을 구성했다. 후보 ZIP은 7개 파일의 크기와 SHA256을 lock에 고정한다. 설치는 이 ZIP을 풀고 내부 manifest·번들·플랫폼·계약·실제 실행 CLI와 catalog를 검증한 다음 교체한다. `installation.json`과 배포 정보의 upstream은 `development-candidate`와 소스 커밋을 표시하고 릴리스로 주장하지 않는다. 해시는 동일성 검사이며 게시자 인증이 아니다.

후보는 공개 Release API에서 다운로드하지 않는다. 별도 준비된 같은 파일을 검증하려면 다음 명령을 사용한다. 기존 출력은 덮어쓰지 않는다.

```bash
uv run --no-project python tools/prepare_release.py --source-dir /path/to/candidate-assets --output /tmp/dart-agent-candidate
uv run --no-project python tools/package_release.py --source-dir /tmp/dart-agent-candidate --output /tmp/dart-agent-candidate.zip
```

공개 릴리스 다운로드를 별도로 재현할 때는 명시적으로 `--lock release/dart-2.1.0-release.lock.json`을 선택한다. 과거 공개 릴리스와 현재 스킬/앱의 호환성을 뜻하지 않는다. 후보 생성이나 오프라인 확인만으로 설치된 앱·회사 Linux·회사 네트워크 인수를 주장하지 않는다. 개인 연결 정보는 자산과 증거에 포함하지 않는다.

2026-11-05 WSL에서 준비 도구는 최종 Linux 실행 파일의 version, contract identity 및 전체 export와 catalog 일치를 확인했다. Windows에서는 같은 후보의 exe version과 identity를 별도 확인했다. 사용자가 설치된 Linux 후보 CLI로 PIN 페어링을 완료한 후 `app inspect`는 개발 앱의 connected-main identity와 같은 fingerprint를 확인했다. 회사 환경과 설치된 Windows 앱은 검증하지 않았다. 새 Cline 대화에서 설치 스킬의 PIN 지침이 로드됐고 사용자의 대화형 PIN 입력과 Main 확인을 안내했다. 참조 파일을 찾기 위한 전체 파일 시스템 검색이 관측되어 빠른 경로 선택은 보장되지 않는다. 전역 skills 안의 같은 이름을 가진 기존 백업은 `~/.cline/skill-backups/`로 보존해 중복 발견을 막았다.

## 검증 기록 — 2026-11-03

최종 도구의 인증된 `gh api` 다운로드 경로로 준비한 자산에서 검증했다. 환경은 현재 개발 PC의 WSL2 Linux x86_64, kernel 6.18.54.1, Ubuntu glibc 2.39다. 회사 Linux 환경의 호환성·네트워크 접근성 검증을 대신하지 않는다. Windows exe는 크기·SHA256와 공식 manifest의 플랫폼 identity를 확인했으며 Windows 네이티브 실행은 수행하지 않았다.

- `uv run --no-project python tools/prepare_release.py --output /tmp/dart-agent-implementation-batch/prepared-2`: 종료 0, 공식 7개 자산 검증 및 배포 정보 생성.
- 준비된 **최종** `dart-cli-linux-x64 version`: 종료 0, `ok: true`, version `2.1.0`, protocol `2`, mode `installed`.
- 같은 파일의 `contract identity`: 종료 0, contract format `2`, projection `1`, SHA256 fingerprint `6fc2f2381407bc3b1193293dae8a78dbfec6412ca1e8619d061a957dbb597042`.
- 같은 파일의 `contract export full`: 종료 0, 응답 `data`가 공식 command catalog와 정확히 일치.
- Linux CLI SHA256: `7ba8d9a6ebce309b24368b5e7d9804ce2dbd26893c520248d3caf69d4aff0639` (91,641,824 bytes).
- Windows CLI SHA256: `56b417c0c32860d0f1b87db15cac06498d1f4989a5247ed246516c3f6f5f3021` (97,225,216 bytes).
- agent manifest SHA256: `973a913f26d97ca4015ecb6937b4adea238ba50b582e3a2fb1fcab11c86557c6`.

준비 도구의 공개 CLI 경계에서 성공·체크섬 불일치·누락 파일·다운로드 실패·고정 버전 불일치·manifest 버전 불일치·실행 파일 버전 불일치·기존 출력 보존을 검사한다.

```bash
uv run --no-project python -m unittest discover -s tests -p test_prepare_release.py -v
```

실제 준비 디렉터리와 상세 로그는 이번 작업의 `/tmp/dart-agent-implementation-batch/`에 보관했다. 재현할 때는 위 명령으로 새 디렉터리를 준비한다. CLI의 오프라인 identity는 Windows DART 앱의 identity나 연결·업무 실행 성공을 증명하지 않는다. 이 작업에서는 Release 게시와 회사망·Windows 앱 업무 인수를 수행하지 않았다.
