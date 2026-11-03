# 공개 Release 인수의 공개 결과

2026-11-04 WSL2 x86_64, Cline 3.0.74, Windows DART 2.1.0 및 공식 CLI 2.1.0/protocol 2. 설치 출처는 `kalstein00/dart-agent@v0.1.0` GitHub Release이며 소스 commit은 `2e59579f1cc366b1dcae619b996a36830a7a7690`이다. 회사 Linux와 회사 네트워크는 미검증이다. 개인 연결 프로필명·번들·토큰은 포함하지 않는다. [인수 기록](issue-8.md)은 최초 설치와 업데이트, 앞선 중단과 복구의 범위를 설명한다.

단일 여정 요청은 새 합성 SQLite를 가져와 DM·Tag offsets 1–4를 조회하고, SQL 행 수를 준비해 새 Windows CSV로 내보낸 다음 Dataset별 Linux 소스 루트를 등록하고 로그 행 1의 기록 위치를 읽어 비교하도록 지시했다. `cline --provider openai-codex --json --cwd /tmp/dart-agent-implementation-batch/8-release-cwd --timeout 1200 '<합성 통합 여정 요청>' </dev/null` 종료 0. Cline은 글로벌 `dart-control` 스킬을 호출했다. 아래는 자격 증명 없이 보존한 해당 Cline 최종 응답과 실패한 명령 요약이다.

## Synthetic acceptance journey complete

**Compatibility and target:** DART CLI and connected Main both matched **2.1.0 / protocol 2** and the pinned contract fingerprint. The connected app ID matched. The requested window was present, and the supplied session was open for that window.

### Import and Dataset

- Preflight for `synthetic-values.sqlite` → `imported.sqlite` confirmed SQLite input, writable destination, `outputExists=false`, `overwrite=false`, and no catalog impact.
- Import task `3dc296db-4151-4a62-bbbc-d747b46b7673`: **succeeded**; output was published and Dataset was ready.
- Dataset ID: `706fe0ed-0f44-4300-8038-6d3736dd901c`
- SQL alias: `file_5`
- The exact Windows output path was `C:\Users\kalst\dart-agent-issue8-release-final\imported.sqlite`.

### DM and Tag offsets

DM view ID: `b746b71e-4e3b-4b19-b4b8-ae6f30effff1`
Tag view ID: `3e284a37-dc8f-4f90-848e-f6bd193765da`
Both queries returned all four requested rows, with no continuation cursor.

| Offset | DM LineNo | Tag | Tag typed `arg[0]` input | Tag typed `arg[1]` output | Tag typed `arg[3]` serial | DM recorded source |
|---:|---:|---|---:|---:|---:|---|
| 1 | 0 | `VALUE_1` | 21 | 42 | 9007199254740993 | `source/value_demo.c:8` |
| 2 | 1 | `VALUE_2` | 21 | 43 | 9007199254740993 | `source/value_demo.c:8` |
| 3 | 2 | `VALUE_3` | null | 42 | 9007199254740993 | `source/value_demo.c:8` |
| 4 | 3 | `VALUE_4` | 21 | 42 | 9007199254740993 | `source/unavailable.c:8` |

Values in the Tag table are typed integer decimal strings; nulls remain null. DM’s `information` field is derived display text, not the authoritative typed representation.

### SQL result and CSV export

- Saved SQL Builder definition: `62f48649-35d7-45aa-b854-0a4bb5bd5219`
- SQL: `SELECT COUNT(*) AS row_count FROM file_5.log_events`
- Preview task `e8ea62bf-67a0-45b1-ad5c-3768213a3b9c`: **succeeded**
- Prepare task `e83009ad-a9de-4310-ab6f-e412701b4133`: **succeeded**
- Published result ID: `70e035736fb1fe523e1d71bdbaed07e1`
- Typed result: `row_count = 4` (`int64`, decimal encoding); one row, complete and not truncated.
- CSV export task `9359aa73-d751-419f-a6f3-a6a827cee876`: **succeeded**
- Windows output: `C:\Users\kalst\dart-agent-issue8-release-final\row-count.csv`
- Receipt: 1 row, 14 bytes, SHA-256 `eb5a920bb532556176fbf2faa8e031365dcb0a848da9ae948a8531a97238edf0`

The DART receipt confirms completion and reports the path, bytes, row count, and hash. I did not independently read the Windows file contents.

### Source registration and comparison

- Registered and re-inspected Dataset source binding at revision 1:
  - Environment: `Linux`
  - Root: `/tmp/dart-agent-implementation-batch/issue-6-fixture`
- For DM `LineNo=1`, the Dataset records `source/value_demo.c:8`. The resolved file exists under the bound root, is readable, and resolves within it.
- The recorded line contains a `printf` using `convert_value(input)`; nearby line 6 defines `convert_value` as `input * 2`, and line 11 calls `emit_value(21)`. That calculation gives **42**. The corresponding Tag typed cells show input **21** and logged output **43**, so the logged output differs from the source calculation.
- Limitation: the recorded line identifies the logging statement, and the inspected source does not prove which exact source revision or binary produced the Dataset log. Offset 4’s recorded `source/unavailable.c:8` was not resolved or substituted.

The initial `input inspect` attempt was rejected because it lacked required profile/app CLI flags; I checked the command contract and corrected the invocation. No SQLite file was read directly, no credentials were exposed, and no unknown mutation was replayed.

FAILURES:
DART=/home/kalstein/.cline/skills/dart-control/bin/dart; for c in 'import preflight' 'import sqlite' Command exited with code 127
DART=/home/kalstein/.cline/skills/dart-control/bin/dart; "$DART" input inspect --json '{"command":"i Command exited with code 1

## 독립 Windows 파일 검사

Cline은 Windows 파일을 독립적으로 읽지 않았다. 별도 Windows PowerShell `Test-Path`, `Get-Item`, `Get-FileHash`, `ReadAllBytes` 검사 결과는 다음과 같다.

```text
path=C:\Users\kalst\dart-agent-issue8-release-final\row-count.csv
bytes=14
sha256=EB5A920BB532556176FBF2FAA8E031365DCB0A848DA9AE948A8531A97238EDF0
hex=72-6F-77-5F-63-6F-75-6E-74-0D-0A-34-0D-0A
exit=0
```

## 공개 Release 첨부물 SHA256

`gh release download v0.1.0 --repo kalstein00/dart-agent`로 받은 파일을 `sha256sum`으로 검사했다.

```text
9a9cdfa2621908d12756cf3a2dbd6e102fc9e13450518bd3adf15372744ff85b  dart-agent-bundle.zip
d604d107e623882beb689738de1f9bb7fd7685dbc0d3cc1f7a480ebdfb230c05  dart-agent-distribution.json
973a913f26d97ca4015ecb6937b4adea238ba50b582e3a2fb1fcab11c86557c6  dart-agent-manifest.json
f337affaf9b33d2d78c22392f1070abafbc76c0cced7d491af70642a47085899  dart-cli-command-catalog.json
7ba8d9a6ebce309b24368b5e7d9804ce2dbd26893c520248d3caf69d4aff0639  dart-cli-linux-x64
2dd8e422ecc027206fedd4adbd1db0e0cda027fd6ffd9521722ce39b391a2010  dart-cli-manifest.json
3735cb2db803ee0af1c203931f1be0964c7b3459bf645f058e8dc1b69d430137  dart-cli-reference.md
56b417c0c32860d0f1b87db15cac06498d1f4989a5247ed246516c3f6f5f3021  dart-cli-windows-x64.exe
```
