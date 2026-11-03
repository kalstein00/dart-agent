# DART 2.1.0 Release 자산 준비

`tools/prepare_release.py`는 유지보수 담당자가 공식 `kalstein00/DART`의 `v2.1.0` 배포를 검증하고 이 저장소의 Release에 첨부할 파일을 준비하는 Linux x64 도구다. Python 표준 라이브러리와 `uv`, 다운로드에는 인증된 `gh`가 필요하다. Bun/Node, DART 소스 checkout, 이미 게시된 dart-agent Release는 필요하지 않다.

```bash
uv run --no-project python tools/prepare_release.py --output /tmp/dart-agent-release-0.1.0
```

출력은 새 디렉터리여야 한다. 내려받기·크기·SHA256·버전·계약·실제 실행 중 하나라도 실패하면 종료 코드 1을 반환하고 출력 후보를 게시하지 않는다. 기존 출력은 덮어쓰지 않는다. 먼저 받아 둔 **공식 자산만** 사용할 때는 `--source-dir /path/to/official-assets`를 추가한다. 이 모드에도 동일한 해시·실행 검사가 적용된다. 소스 디렉터리의 다른 파일은 복사하지 않는다.

`release/dart-2.1.0.lock.json`은 신뢰 기준이다. 공식 Release API의 자산 ID·공개 이름·bytes·SHA256과 agent manifest의 version/protocol/contract를 고정했다. 해시는 손상 검출 수단이며 배포처 인증을 대신하지 않는다. `--lock`은 명시적으로 검토한 다른 신뢰 파일이나 테스트 fixture를 사용할 때만 지정한다. 공급자가 같은 태그의 파일을 교체하면 기존 lock으로 성공하지 않으며, 변경 검토·해시 재확인·Linux 실행·별도 업무 인수 후 명시적으로 갱신해야 한다. `latest`로 자동 이동하지 않는다.

## 출력과 배포 정보

다음 8개 파일을 개별 Release 첨부물로 사용한다. 도구는 게시하지 않으며 별도 통합 ZIP을 만들지 않는다. upstream의 `dart-agent-bundle.zip`은 공식 참조 자료 원본이므로 그대로 첨부한다.

| 파일 | 내용 |
| --- | --- |
| `dart-cli-linux-x64` | 공식 Linux x64/glibc 실행 파일 |
| `dart-cli-windows-x64.exe` | 공식 Windows x64 실행 파일 |
| `dart-cli-manifest.json` | CLI target·해시·공개 계약 |
| `dart-agent-manifest.json` | 공식 6개 다운로드의 크기·해시·공개 계약 |
| `dart-cli-command-catalog.json` | 공식 기계 판독 명령 계약 |
| `dart-cli-reference.md` | 공식 명령 참조 |
| `dart-agent-bundle.zip` | 가이드·예제·참조·파일별 manifest |
| `dart-agent-distribution.json` | 이 저장소의 설치 도구가 사용할 버전·플랫폼·해시·Linux 검증 결과 |

배포 정보 `schemaVersion: 1`은 `skillVersion: 0.1.0`과 `dartVersion: 2.1.0`을 별도 필드로 제공한다. `protocolVersion: 2`, `contract`의 format/fingerprint, `upstream`의 repository/tag, `platforms`의 `linux-x64`/`windows-x64`별 공개 `file`·os·cpu·libc, `assets`의 7개 공식 파일별 bytes/SHA256를 제공한다. 설치 도구는 호환 버전·플랫폼을 먼저 확인하고 고정된 Release 태그의 해당 파일을 검증해야 한다. 스킬 버전 변경이 DART 버전 자동 변경을 의미하지 않는다. 출력의 `verification`은 실제 Linux 실행 결과와 Windows의 무결성 검사 한계를 구분한다.

실제 Release 이름은 agent manifest의 `downloads[].file`을 따른다. 현재 CLI manifest의 `artifacts[].file`에는 `dart-linux-x64` 등 과거 이름이 남아 있으므로, os/cpu/libc와 동일 bytes/SHA256로 공개 다운로드를 연결한다. 오래된 문서의 이름으로 다운로드하지 않는다. 내부 ZIP은 정확한 파일 목록·파일별 해시·identity·standalone manifest를 검사하고, bundled Reference/catalog가 외부 공개 파일과 같은지 확인한다. transport와 명령 registry는 공식 CLI를 그대로 소비한다.

준비 디렉터리는 검증된 공식 파일과 생성한 배포 정보만 포함한다. 개인 연결 번들·토큰·profile·회사 Dataset·회사 소스는 입력받거나 복사하지 않는다. 공식 번들에는 upstream이 공개한 `investigation-example/synthetic-values.sqlite`와 합성 예제 소스가 들어 있다. 실행 파일과 ZIP, 큰 참조 파일은 Git에 커밋하지 않는다.

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
