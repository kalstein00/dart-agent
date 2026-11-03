# Dataset 가져오기와 DM·Tag 조회 인수

공식 DART v2.1.0 `dart-agent-bundle.zip`의 `investigation-example/synthetic-values.sqlite`는 합성 입력이다. SHA256은 `1c322713ef445d47cfdb64ed7746b0d64f01bdc7226f6e85282f139db52fd805`. 동일 번들의 `investigation-example/logs.json`은 로그 행 0–3의 기대값을 기록한다: 각각 input/output은 21/42, 21/43, null/42, 21/42다. Tag 정의 offset은 문자열 `1`, `2`, `3`, `4`다. signed int64 `9007199254740993`은 decimal 문자열 그대로 유지한다. 로그 행 번호는 소스 줄 번호가 아니다.

## 재현

1. [준비 도구](../release-preparation.md)로 공식 자산을 검증하고, bundle에서 위 합성 SQLite를 Windows DART가 접근할 새 경로에 복사한다. Windows 경로는 현장에 맞게 선택한다. 회사 DB를 사용하지 않는다.
2. [설치·연결](../installation.md)에 따라 설치하고 Windows 앱 및 선택한 창의 세션을 확인한다. 개발 준비 자산 설치는 공개 Release 설치와 구분한다.
3. Cline에서 설치된 `dart-control`을 호출하여 해당 Windows 절대 경로를 가져오고 준비 완료 후 DM과 Tag offset 1–4의 값과 로그 행 번호를 요청한다. 명시적 profile/app/window/session은 실제 조회 결과로 제공한다. CLI 계약의 preflight, task 상태, Dataset readiness, 각 view와 rows 공개 결과를 보존한다. 개인정보와 연결 비밀은 증거에서 제외한다.
4. 실제 반환된 DM·Tag 행을 위 기대값 및 bundle의 `logs.json`과 비교하고 task의 성공과 Dataset의 readiness를 따로 확인한다. 파일 provenance와 DM의 `file`/`source_line`을 구분한다. 실행 환경·설치 출처와 실패/미검증 범위도 기록한다.

## 오류 경계 관측

Windows DART 2.1.0과 Linux 공식 CLI 2.1.0의 연결된 세션에서 존재하지 않는 합성 Windows 경로에 대한 `import preflight`는 종료 코드 1, `INPUT_NOT_FOUND`/`preflight`를 반환했다. 존재하지 않는 Dataset ID에 대한 `dataset inspect`도 종료 코드 1, `TARGET_NOT_FOUND`/`target`을 반환했다. 실제 import task 실패·취소 사례는 이 두 결과로 검증된 것이 아니다.

## 실제 Cline 결과 (2026-11-03)

Cline CLI 3.0.74, WSL2 Linux x86_64, 공식 Linux CLI와 Windows DART 2.1.0/protocol 2에서 실행했다. `tools/install.py --prepared-dir /tmp/dart-agent-implementation-batch/prepared-2 --update`로 검증된 개발 준비 자산과 후보 스킬을 설치했다. 공개 Release 설치 및 회사 Linux/네트워크 검증은 아니다. 실제 요청은 위 합성 Windows 경로를 가져와 완료까지 기다리고 DM·Tag offset 1–4 값과 로그 행 번호를 보고하도록 지시했다. `cline --provider openai-codex --json --cwd /tmp/dart-agent-implementation-batch --timeout 600 '<요청>' </dev/null` 종료 코드 0. Cline은 설치 스킬을 호출하고 공식 계약만 필요한 명령별로 조회했다.

App `2d6a2777-871b-4006-849e-740b134a37ba`, Window `8babf7ad-4464-4fbe-b779-4ee8339c9ea0`, Session `4d1c6ca5-cf47-4789-9359-b794f35e90fc`을 사용했다. Windows 입력은 `C:\Users\kalst\dart-agent-synthetic\synthetic-values.sqlite`. `import preflight` 후 `import sqlite`는 task `ac8dd477-2df1-4185-af29-3194d01f06c0`을 접수했고, 같은 task의 `task wait`은 `succeeded`, `catalogCommitted:true`, `status:ready`를 반환했다. 별도 `dataset inspect`는 Dataset `a471d89a-288f-46ff-865e-99f481ad3f6c`의 readiness `ready`, schema 5와 입력 `sourceFiles` 경로를 확인했다. Source binding은 미등록이다. 출력은 원본 경로이고 `outputPublished:false`, `overwrite:false`였다.

공개 `view source inspect`와 `view open`으로 DM `4b6ad4cc-37a1-4a36-82ea-ed526f8080ae`, Tag `ddf74188-e5b4-458a-8f5f-2a263eb37d66`를 열고 각각 `dm rows`, `tag rows`를 호출했다. 두 결과는 각각 4행, `nextCursor:null`이었다. DM의 표시 정보와 Tag typed cells를 공식 `logs.json`과 비교했다.

| 로그 행 | DM tag | DM input/output 표시 | Tag typed input/output/nullable/serial |
| --- | --- | --- | --- |
| 0 | VALUE_1 | 21 / 42 | 21 / 42 / null / 9007199254740993 |
| 1 | VALUE_2 | 21 / 43 | 21 / 43 / null / 9007199254740993 |
| 2 | VALUE_3 | 빈 표시 / 42 | null / 42 / null / 9007199254740993 |
| 3 | VALUE_4 | 21 / 42 | 21 / 42 / null / 9007199254740993 |

DM `information`의 serial 표시 문자열은 `9007199254740992`로 반올림되어 있으므로 Tag의 원래 typed cell과 구분한다. DM `file`/`source_line`은 행 0–2에서 `source/value_demo.c:8`, 행 3에서 `source/unavailable.c:8`이며 입력 SQLite provenance와 다르다. 소스 파일은 읽지 않았다. Cline이 처음 두 source inspect에서 실행 파일 경로를 잘못 입력해 로컬 종료 코드 127을 받았고, 정확한 경로로 읽기 요청을 재시도했다. 최초 `--version`도 실패 후 공식 `version`으로 확인했다. 이 재시도는 import 재실행이 아니다.

같은 후보에 대한 별도 실제 Cline 잘못된 입력 요청도 종료 코드 0으로 대화를 마쳤고, Cline은 `INPUT_NOT_FOUND`/`preflight`와 Windows에서 파일을 준비하거나 올바른 경로를 제공하라는 조치를 보고했다. 가져오기 task는 제출하지 않았다. 이는 오류 처리가 성공한 관측이며 실패한 RED 시험은 아니다.

## 원본 스킬 기준선

별도 Cline 설정과 workspace에 시작 커밋 `034231a`의 스킬 및 같은 검증 자산을 설치했다. 별도 Windows 합성 파일의 SHA256은 위와 같으며 실제 Cline 요청에서 기존 window/session과 Tag offsets 1–4를 사용했다. CLI와 Main은 호환됐고 import task `cc3ce417-6b34-41d1-b7a7-8d8d733b099b`가 성공해 Dataset `cbba7e76-6d66-4d45-814f-c1fa6ed9cb4d`가 `ready`였다. 그러나 Cline은 view 입력 검사에서 `INVALID_INPUT`을 받고 DM·Tag view를 열거나 행을 조회하지 못했다고 최종 보고했다. 프로세스 종료 코드는 0이지만 요청된 공개 결과는 실패다. 입력 검사는 window/session 명령 옵션과 Dataset/View 입력을 포함했고 공개 오류는 지원하지 않는 필드가 있다고만 밝혔다. 후보의 `dataset.md`는 공개 view source 검사와 해당 precondition 및 명시적 JSON 입력을 안내한다. 별도 설정에서 스킬 호출의 원본 지침을 확인했다.

이 기준선 이후 같은 Dataset ID를 설치된 후보 스킬에 전달해 실제 Cline에서 가져오기를 반복하지 않고 DM·Tag를 조회했다. Cline 종료 코드 0, 두 공개 rows 결과는 각각 0–3 네 행과 `nextCursor:null`을 반환했고 위 기대값 및 typed serial에 일치했다. Tag의 화면 표시 여부는 확인되지 않았으며 공개 행 조회가 검증 대상이다. 별도 비교도 종료 코드 0이었다.
