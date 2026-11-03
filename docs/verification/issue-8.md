# 업데이트와 통합 인수 상태

이 인수는 **미완료**다. `kalstein00/dart-agent`의 `v0.1.0` Release가 아직 발행되지 않아 실제 Release 다운로드 설치를 검증하지 못했다. 공개 설치 실패를 성공으로 간주하지 않는다. 회사 Linux와 회사 네트워크 역시 미검증이다. WSL2 관측은 두 환경의 대체 증거가 아니다.

## 배포 및 재현

유지보수 담당자는 [Release 준비](../release-preparation.md)의 명령으로 공식 7개 첨부물과 배포 정보를 준비하고, 검토 후 고정 태그 `v0.1.0`의 Release에 개별 파일을 게시해야 한다. 이 기록 작성 시 게시하지 않았다. 준비 결과는 별도 통합 ZIP이 아니며, 공식 bundle ZIP은 upstream 원본이다. 실제 공개 인수는 발행 후 새 clone에서 `uv run --no-project python tools/install.py`를 실행하고 다른 작업 디렉터리에서 실제 Cline이 전역 스킬을 호출하는지 확인해야 한다. 이후 같은 clone에서 `--update`를 명시하고 같은 프로필·대상·Dataset의 공개 동작을 다시 확인한다. 실패 사례는 기존 스킬과 프로필을 보존하는지도 확인한다. Release 접근 오류와 준비 자산 사용을 구분한다.

Windows 앱 준비, 일회용 연결 번들, 소스 루트 및 문제 해결은 [사용자 설치 안내](../installation.md)를 따른다. 연결 비밀은 증거에 포함하지 않는다. [Dataset](issue-5.md), [소스 조사](issue-6.md), [SQL·분석](issue-7.md)은 실제 Cline과 Windows에서 각각 수행한 합성 작업 및 한계를 기록한다. 이들은 하나의 최종 Release 설치 여정을 대신하지 않는다.

## 현재 개발 자산 관측

2026-11-04 현재 WSL2 x86_64의 Cline 3.0.74, Windows DART 2.1.0, 공식 Linux CLI 2.1.0/protocol 2로 검사했다. 준비 자산의 Linux CLI SHA256은 `7ba8d9a6ebce309b24368b5e7d9804ce2dbd26893c520248d3caf69d4aff0639`, Windows CLI는 `56b417c0c32860d0f1b87db15cac06498d1f4989a5247ed246516c3f6f5f3021`이다. 버전과 전체 공개 계약 fingerprint `6fc2f2381407bc3b1193293dae8a78dbfec6412ca1e8619d061a957dbb597042` 및 7개 자산 검증의 범위는 [준비 기록](../release-preparation.md)에 있다. 별도로 해당 준비 Windows 실행 파일을 Windows 파일 시스템에 복사하고 `version`을 실행해 종료 0, version `2.1.0`, protocol `2`, mode `installed`를 확인한 뒤 복사본을 삭제했다. 이는 Windows CLI의 오프라인 버전 확인이며 업무 실행 증거는 아니다.

기존 개인 연결로 업데이트 전후 `app inspect`는 같은 Windows app `2d6a2777-871b-4006-849e-740b134a37ba`와 독립적인 connected-main identity를 반환했다. `uv run --no-project python tools/install.py --prepared-dir /tmp/dart-agent-implementation-batch/prepared-2 --update` 종료 0 후 `session inspect`는 같은 window `8babf7ad-4464-4fbe-b779-4ee8339c9ea0`와 session `4d1c6ca5-cf47-4789-9359-b794f35e90fc`가 모두 open이라고 반환했다. 이는 개발 준비 자산을 이용한 명시 업데이트이며 공개 Release 검증이 아니다.

업데이트 후 다른 작업 디렉터리에서 실제 `cline --provider openai-codex --json --cwd /tmp/dart-agent-implementation-batch/8-other-work --timeout 600 '<기존 합성 Dataset 조회 요청>' </dev/null`은 종료 0이며 전역 `dart-control` 스킬을 호출했다. 같은 연결·대상에서 이전 합성 Dataset `a471d89a-288f-46ff-865e-99f481ad3f6c`의 `ready`를 재확인하고 기존 DM view의 로그 행 1에서 입력 21, 출력 43, 기록 위치 `source/value_demo.c:8`을 조회했다. 기존 Linux 소스 binding 아래 실제 소스에서 입력의 두 배가 42임을 확인하고 실행된 소스와 원인은 확인되지 않았다고 구분했다. DM의 반올림된 serial 표시는 typed 증거가 아님을 보고했다. Cline의 최초 전체 파일 검색은 30초 timeout, 직접 `python` 호출은 명령이 없어 종료 127, 잘못된 input inspect는 `INVALID_INPUT`으로 실패한 뒤 다른 공개 조회를 진행했다. 이 실행은 새 import나 Windows export를 반복하지 않았다.

`uv run --no-project python tools/install.py --update`는 실제 `v0.1.0` 다운로드 실패로 종료 1이었다. 테스트는 공개 설치 명령을 통해 버전 불일치를 거부하고 기존 스킬을 유지함을 확인한다. 프로필은 스킬 밖의 공식 위치에 있으므로 설치 도구는 프로필 파일을 변경하지 않는다. 설치 후 연결된 실제 app 재조회가 프로필 사용 가능성의 관측이다.

이전 실제 Cline 합성 여정에서 SQLite 입력 SHA256 `1c322713ef445d47cfdb64ed7746b0d64f01bdc7226f6e85282f139db52fd805`, 네 행의 input/output `21/42`, `21/43`, `null/42`, `21/42`를 확인했다. 대표 SQL 행 수는 4이고 Windows CSV는 14 bytes 및 SHA256 `eb5a920bb532556176fbf2faa8e031365dcb0a848da9ae948a8531a97238edf0`으로 독립 확인했다. 로그 행 1의 `source/value_demo.c:8`은 소스 6행의 21×2=42와 로그 output 43을 비교할 근거를 제공했으나 실행 바이너리의 원인은 증명하지 않는다. 개별 결과의 app/window/session, task, Dataset, 실행 명령과 재시도는 링크된 기록을 참조한다.

## 개발 준비 자산을 이용한 단일 통합 여정

명시적 업데이트 후 `cline --provider openai-codex --json --cwd /tmp/dart-agent-implementation-batch/8-other-work --timeout 1200 '<합성 통합 여정 요청>' </dev/null`을 실행해 한 대화에서 새 합성 입력의 가져오기부터 소스 조사까지 수행했다. Cline 3.0.74 종료 0, 전역 `dart-control` 호출을 확인했다. Windows에 둔 공식 bundle의 SQLite는 가져오기 전 SHA256 `1c322713ef445d47cfdb64ed7746b0d64f01bdc7226f6e85282f139db52fd805`였다. 기존 개인 연결과 위 app/window/session을 확인했으며, 이 실행은 공개 Release 설치가 아닌 준비 자산 설치 이후의 관측이다.

- Windows `C:\Users\kalst\dart-agent-issue8\synthetic-values.sqlite` 가져오기 task `93ef47f5-37d2-4c12-ac13-2e38ad76b73c`는 `succeeded`, `catalogCommitted:true`; Dataset `a50f1564-881e-431d-948b-c5ded31109c6`은 `ready`였다.
- DM view `6584853a-826d-4e9f-a31e-4a3ca0dad3e4`와 Tag view `79e9b96c-9ed4-4f8b-9162-79ea7f5f1483`는 각각 다음 cursor 없이 네 행을 반환했다. Tag typed input/output은 순서대로 `21/42`, `21/43`, `null/42`, `21/42`; serial은 모두 정확한 정수 `9007199254740993`이었다. DM 표시 serial의 반올림과 typed 값을 구분했다.
- 실제 alias `file_3`의 `SELECT COUNT(*) AS row_count FROM file_3.log_events`를 저장하고 preview task `17d4ce6a-fa00-4966-91d4-f7beebefa90f`, Results 준비 task `d3a20662-f191-4b32-929a-45427c5ea411` 성공을 확인했다. 결과 `dfc11cd21d2a078ad9071891ea84a73a`의 typed int64 행 수는 4였다.
- 해당 결과의 CSV export task `c9794a3d-07d1-4179-a23d-5ac6c57548b9`는 성공했고 Windows `C:\Users\kalst\dart-agent-issue8\row-count.csv`에 14 bytes, SHA256 `eb5a920bb532556176fbf2faa8e031365dcb0a848da9ae948a8531a97238edf0`를 보고했다. 별도 Windows PowerShell의 파일 존재·bytes·SHA256 검사도 종료 0이며 내용은 `row_count\r\n4\r\n`이었다. Cline 자체는 Windows 파일을 독립적으로 읽지 않았다.
- 같은 Dataset에 Linux root `/tmp/dart-agent-implementation-batch/issue-6-fixture`를 등록하고 재조회했다. 로그 행 1은 `source/value_demo.c:8`을 가리켰고 실제 파일 SHA256은 `0975c6bec7b55662ea8c9d90cc0b39af9435683e0a2e8a4a6830a3fef3eb8b8d`였다. 6행의 계산은 21×2=42인데 typed 로그 output은 43이다. 실행에 사용된 빌드의 소스나 차이의 원인은 확인하지 않았다.

이 실행의 초기 전체 파일 검색은 30초 timeout이었고 `builder preview inspect --help`도 종료 1이었다. 이후 공개 계약을 확인해 진행했다. 실제 Cline transcript와 Windows 파일 검증 로그는 이번 작업의 `/tmp/dart-agent-implementation-batch/8-integrated*`에 보관했다. 이 단일 개발 자산 여정은 Release 발행 후 새 clone으로 수행하는 실제 다운로드·설치·업데이트 인수나 회사 환경 검증을 대체하지 않는다.
