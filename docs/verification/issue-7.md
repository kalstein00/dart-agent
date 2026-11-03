# SQL·분석과 Windows 내보내기 인수

## 합성 절차와 기대값

공식 DART 2.1.0 bundle의 `investigation-example/synthetic-values.sqlite` (SHA256 `1c322713ef445d47cfdb64ed7746b0d64f01bdc7226f6e85282f139db52fd805`)를 Windows에서 가져오고 준비 완료를 확인한다. [Dataset 인수](issue-5.md)의 합성 로그는 네 행이다. 연결된 창과 세션을 재확인하고 SQL Builder의 실제 Dataset alias를 확인한다. 예를 들어 alias가 `file_1`이면 `SELECT COUNT(*) AS row_count FROM file_1.log_events`의 기대값은 정수 4다. SQL 저장과 Workspace 변경을 명시적으로 허용하고 새 Windows CSV 경로를 지정한다. 공개 task의 최종 상태, 정확한 Results 세대와 typed 값을 확인한 뒤 CSV를 내보내고 Windows에서 실제 파일과 내용을 확인한다. 기존 파일은 명시적인 덮어쓰기 허용 없이 바꾸지 않는다. 분석은 정확한 Results 또는 Tag 출처를 캡처하고 적용된 결과의 공개 셀이나 요약을 확인한다. 개인정보와 연결 비밀은 기록하지 않는다.

## 실제 SQL·CSV 관측 (2026-11-03)

Cline CLI 3.0.74, WSL2 x86_64, 공식 Linux CLI와 Windows DART 2.1.0/protocol 2. 후보 스킬은 검증된 개발 준비 자산으로 설치했다. 공개 Release 설치 및 회사 Linux/네트워크 검증은 아니다. `cline --provider openai-codex --json --cwd /tmp/dart-agent-implementation-batch --timeout 900 '<합성 SQL·CSV 요청>' </dev/null` 종료 코드 0. Cline은 설치 스킬과 공개 명령을 사용했다. 합성 Dataset `a471d89a-288f-46ff-865e-99f481ad3f6c`, Main Window `8babf7ad-4464-4fbe-b779-4ee8339c9ea0`, Session `4d1c6ca5-cf47-4789-9359-b794f35e90fc`에서 SQL 정의 `f37ca9d0-91e9-4f92-bb58-cdea27d98985`를 저장했다. Results 준비 task `c2944530-a96e-4a3c-837b-93c83272f5f9`와 metadata task `336891f3-f030-410e-ad41-6f5dca793184`는 `succeeded`. 정확한 결과 `727162eb6ec273049811225b73d962b3`의 typed int64 `row_count`는 decimal `4`, 한 행이었다.

CSV 내보내기 task `864849da-8082-4b15-959b-1193aba9a90b`도 `succeeded`. 공개 receipt는 Windows 경로 `C:\Users\kalst\dart-agent-issue7.csv`, 14 bytes, SHA256 `eb5a920bb532556176fbf2faa8e031365dcb0a848da9ae948a8531a97238edf0`을 반환했다. Cline은 Windows 파일을 독립적으로 읽지 못했다고 보고했다. 별도 Windows PowerShell `Test-Path`, `Get-Item`, `Get-FileHash`, `Get-Content` 및 바이트 확인은 종료 코드 0: 실제 파일 내용은 `row_count\r\n4\r\n`, 해시는 receipt와 일치했다. 최초 `powershell.exe` PATH 호출과 해당 PowerShell 버전에서 지원하지 않는 `Convert.ToHexString` 시도는 실패했고 절대 실행 경로와 `BitConverter`로 정정했다. 이 개발 PC의 Windows 확인은 Linux로 자동 전송했다는 뜻이 아니다.

## 아직 미검증

실패한 export task는 관측하지 않았다. 출력 디렉터리 오류는 아래와 같이 task 접수 전 preflight에서 검증했다. 원본 스킬의 SQL 기준선에서 Preview는 실제 값 4를 반환했지만 SQL 저장 권한을 재확인하며 export 전에 중단했다. 요청의 권한 표현이 모호했으므로 이를 유효한 RED로 주장하지 않는다. 위 후보 실행은 명시적으로 SQL 저장을 허용했다. 유효한 RED/GREEN 주기도 미완료다.

## Windows 출력 경계 관측

같은 정확한 Results에 대해 기존 CSV 경로를 덮어쓰기 없이 `results csv inspect`한 공개 응답은 종료 코드 0, `overwrite:false`, `overwriteRequired:true`였다. 파일을 변경하지 않았고 덮어쓰려면 사용자 의도와 새 preflight가 필요하다. 존재하지 않는 Windows 상위 디렉터리로 검사한 결과는 종료 코드 1, `OUTPUT_UNWRITABLE`/`preflight`, 기존 쓰기 가능한 디렉터리를 선택하라는 `nextAction`이었다. 이는 내보내기 작업을 접수하기 전 실패이며 실패한 export task나 취소된 task의 증거가 아니다.

## 실제 Pivot 관측

별도 실제 Cline 요청은 종료 코드 0. 위 SQL의 정확한 결과를 `pivot results-source inspect`로 확인하고 Pivot `7e94359c-143c-4589-b1af-a6deb7ebb75d`를 만들었다. `row_count`를 Rows, `SUM(row_count)`를 Values로 설정하고 실행한 task `080d9faf-25bd-4afb-be0b-0e7e3ad1677a`는 `succeeded`. 공개 `pivot cells`의 결과 `5ab5acd9-df71-4483-b503-061a80250325`에는 행 경로 4.0의 값 4와 총계 4, 두 셀이 있었고 다음 페이지는 없었다. 이는 원본 SQL의 한 결과 행에 대한 합계다. 이 실행은 표시 렌더링을 확인하지 않았다.

Cline은 첫 세션 검사에서 잘못된 JSON, 첫 source 검사에서 창과 세션 중복 입력, 추측한 `pivot create`에서 `UNKNOWN_COMMAND`를 받은 후 공개 계약으로 수정했다. 최초 Values만 있는 draft는 실행 부적격이어서 Row 차원을 추가했다. 기존 CSV 검사에서는 `overwriteRequired:true`를 보고 다른 경로 또는 명시적 덮어쓰기와 재검사를 안내했으며 내보내기를 시작하지 않았다.

## 실제 task 실패 관측

별도 실제 Cline 요청에서 합성 SQL `SELECT definitely_missing_column FROM file_1.log_events`의 Preview task `4cdfbc79-c436-456d-9c8a-cc4c5755250b`는 접수 후 `failed`/`execution`; 같은 task의 `task wait` 종료 코드 1, `TASK_FAILED`와 존재하지 않는 열, 스키마와 현재 상태를 확인하라는 조치를 반환했다. 최초 비읽기 SQL은 `PREVIEW_INELIGIBLE`로 접수 전 거부됐다. 취소 시험의 첫 `range()` 쿼리는 SQL 구문 오류로 취소 전에 실패했고, 두 번째 재귀 쿼리는 취소 요청 전에 성공했다. 어느 쪽도 `cancelled`의 증거가 아니다.

더 긴 합성 재귀 쿼리의 Preview task `c9e6cb13-cb8c-469e-bfc0-0ea43de56b7e`에 실제 Cline이 `task cancel`을 요청했을 때 응답은 `cancel_requested`였다. 직후 첫 상태는 아직 `running`이었으므로 완료로 간주하지 않았다. 별도 공개 `task status` 재조회는 종료 코드 0, 최종 `cancelled`/`cancellation`, `TASK_CANCELLED`, 재시도 전 task와 출판된 출력 확인을 안내했다.

같은 실제 Cline 요청의 새 SQL 정의 `24b72c6a-8cc6-468c-944d-bea694ce541e`는 Preview 후 저장했지만 Results 준비는 실행하지 않았다. `results inspect`의 공개 응답은 `task:null`, `published:null`이었고 Cline은 준비되지 않은 결과로 보고했다. 이 결과는 이전 Preview 값이 전체 Results 출판의 증거가 아니라는 것을 보여 준다. 별도 Cline 호출은 종료 코드 0이다.

## 원본 스킬 추가 기준선

후보 변경 이후 시작 커밋 `4fa14ba`의 스킬을 별도 Cline 설정과 데이터 디렉터리에 설치하고, SQL 저장과 새 Windows 출력 경로를 명시적으로 허용한 동일 합성 요청을 실행했다. Cline 종료 코드 0. 원본 스킬은 후보 실행에서 이미 저장·준비된 동일 SQL 정의와 Results를 재사용했고 typed 값 4를 확인한 뒤 새 CSV export를 성공했다. 따라서 이 실행은 실패한 RED가 아니며 새 Builder 생성이나 Results 준비의 독립 기준선도 아니다. 실행 중 요청과 달리 `python3`을 직접 호출한 부분이 있었지만 이를 SQL·내보내기 실패로 간주하지 않는다. 별도 설정의 임시 provider 복사본은 실행 후 삭제했다.

공유 상태의 영향을 제거하기 위해 원본 스킬에서 고유 제목 `Issue7 Original Fresh 20261104`가 없음을 확인하고 새 Builder와 SQL 정의 `6cb8a395-7f1e-46dc-911b-0f56e29b0697`, 새 Results 및 새 Windows 출력 경로를 명시적으로 요청해 다시 실행했다. 실제 Cline 종료 코드 0. Preview task `e7cff4f5-c433-4f7a-8513-c0cd77b34095`, 준비 task `82a96d0e-b23d-49aa-b77e-f119cad10674`, metadata task `de2de65b-be12-42bc-ab95-1baa4ca6b957`, CSV export task `8fd338fa-1abc-4264-a97d-4d34c08e254b`가 모두 `succeeded`였고, typed int64 값은 4였다. 따라서 이 추가 기준선도 RED가 아니다. 원본 스킬 실행은 후보 수정 뒤에 이뤄졌다. 임시 provider 복사본은 삭제했다.
