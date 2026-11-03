# Dataset 소스 조사 인수

공식 DART 2.1.0 agent bundle의 합성 `investigation-example/synthetic-values.sqlite`와 `investigation-example/source/`를 사용한다. SQLite SHA256은 `1c322713ef445d47cfdb64ed7746b0d64f01bdc7226f6e85282f139db52fd805`다. Windows에 입력을 준비하고 [Dataset 인수](issue-5.md)에 따라 가져온다. Linux의 새 디렉터리에 bundle의 `source/value_demo.c`와 `source/revision.txt`를 추출한다. 회사 소스와 연결 정보는 사용하지 않는다.

실제 Cline 요청 예: `dart-control 스킬로 Dataset <DATASET_ID>의 로그 행 1에서 output 43인 원인을 조사해 주세요. Linux 소스 루트는 <ABSOLUTE_LINUX_ROOT>입니다. 기록된 파일과 소스 줄을 조회하고 읽어서 근거와 한계를 보고해 주세요.` 연결 프로필과 확인된 app/window/session은 현장에 맞게 제공한다. Cline 실행은 `cline --provider openai-codex --json --cwd <FIXTURE_DIR> --timeout 600 '<요청>' </dev/null`이다. 최초 등록은 Dataset metadata를 변경하므로 합성 Dataset에만 수행한다.

기대값은 DM 로그 행 1의 기록 위치 `source/value_demo.c:8`이다. 실제 파일의 8행은 `printf` 호출이고, 변환 함수의 6행은 입력에 2를 곱한다. 입력 21이면 제공된 소스의 계산은 42이며 합성 로그의 43과 다르다. 이 비교는 실행된 바이너리나 실제 원인을 증명하지 않는다. 로그 행 1과 소스 줄 8은 별개다. 행 3의 `source/unavailable.c:8`은 합성 bundle에 없으며 다른 파일로 대체하지 않는다.

## 실제 후보 검증 (2026-11-03)

WSL2 Linux x86_64의 Cline CLI 3.0.74, 공식 Linux CLI 및 Windows DART 2.1.0/protocol 2를 사용했다. `uv run --no-project python tools/install.py --prepared-dir /tmp/dart-agent-implementation-batch/prepared-2 --update`로 개발 준비 자산과 후보를 설치했다. 공개 Release 설치 또는 회사 Linux/네트워크 검증은 아니다. bundle의 합성 소스 `value_demo.c` SHA256은 `0975c6bec7b55662ea8c9d90cc0b39af9435683e0a2e8a4a6830a3fef3eb8b8d`다.

위 형식의 실제 요청에서 Cline 종료 코드 0. 합성 Dataset `cbba7e76-6d66-4d45-814f-c1fa6ed9cb4d`을 확인하고 `dataset source set`으로 Linux root를 저장한 뒤 재조회했다. DM 행 1의 `source/value_demo.c:8`을 조회하고 해당 파일 8–9행과 변환 함수 6행을 읽었다. 로그의 43과 소스 계산 42의 불일치를 보고했으며 실행 원인과 실제 빌드 revision은 확인하지 못했다고 구분했다. Cline은 DM 표시 serial `9007199254740992`와 소스 literal `9007199254740993`을 기록 값의 불일치로 잘못 해석했다. DM 표시는 반올림되어 있으므로 이 주장은 뒷받침되지 않는다. 앞선 Tag typed 결과는 원래 값 `9007199254740993`이다. output 43과 소스 계산 42 비교는 이 serial 오류와 구분한다.

별도 실제 Cline 요청은 다른 합성 Dataset `a471d89a-288f-46ff-865e-99f481ad3f6c`의 행 3을 조회했다. 기록 위치 `source/unavailable.c:8`의 정확한 파일이 등록 루트에 없음을 확인하고 소스 내용을 확인한 것으로 주장하지 않았다. 이 두 실행은 같은 Linux 루트를 사용했다.

serial 지침을 보완해 다시 설치한 뒤 별도 실제 Cline 요청을 실행했다. 종료 코드 0, Cline은 첫 레코드 `LineNo=0`의 DM 표시 `9007199254740992`와 Tag typed integer `9007199254740993`, 소스 literal `9007199254740993`을 구분했다. 표시 차이와 실제 값의 차이를 혼동하지 않았고, 소스가 실행된 빌드와 일치하는지는 확인하지 못했다고 보고했다.

## 원본 스킬의 serial 비교 기준선

후보를 작성한 뒤 `bd192a8`의 스킬을 별도 Cline 구성에 설치하고 동일 합성 Dataset의 로그와 소스를 조사하도록 요청했다. 공개 CLI 연결, 기존 소스 루트와 DM view를 사용한 실제 Cline 실행은 종료 코드 0이었고 `LineNo=1`, `source/value_demo.c:8`을 올바르게 찾았다. 그러나 DM의 반올림된 표시 `9007199254740992`를 기록된 serial로 보고 소스 literal과 다르다고 잘못 결론냈다. [기존 Tag 검증](issue-5.md)의 typed serial은 `9007199254740993`이다. 이 관측은 serial 비교에 대한 좁은 실패이며 루트 등록이나 경로 해석의 실패가 아니다. 후보 작성 후 얻은 기준선으로 원래 테스트 우선 순서나 단일 실행의 인과성을 주장하지 않는다.

합성 Dataset의 바인딩을 별도 잘못된 Linux 루트로 설정한 후 후보 Cline에 올바른 루트로 변경하도록 요청했다. Cline 종료 코드 0, 공개 source set으로 사용자가 지정한 루트를 저장하고 재조회했으며 기록된 파일의 8행을 읽었다. 원본 스킬에 같은 잘못된 루트와 교체 요청을 제공한 실행도 성공했으므로 이것은 원본 실패의 증거가 아니다.

기준선 이후 보완된 후보로 같은 Dataset의 `LineNo=1`을 명시해 다시 요청했다. 실제 Cline 종료 코드 0이며 DM의 표시 serial과 Tag의 typed serial을 분리하고, typed serial이 소스 literal과 일치한다고 보고했다. 로그 output 43은 Tag 값으로도 확인했고, 소스의 곱셈이 42를 나타낸다는 점 및 실행 원인과 revision 미확인을 구분했다. 이 재검증은 기존 루트와 view를 재사용한 좁은 serial 비교다.

서로 다른 Linux 루트가 미리 등록된 두 합성 Dataset에 대해 별도 실제 Cline 요청으로 각 binding을 확인하고 `LineNo=1`을 조회했다. 두 기록 경로는 `source/value_demo.c:8`이었지만 첫 루트의 8행은 `/* alternate project source line 8 */`, 둘째 루트의 8행은 위 공식 예제의 `printf`였다. Cline 종료 코드 0이며 각각의 Dataset binding 아래 정확한 파일을 읽었다. 첫 `--version`은 지원하지 않아 공식 `version`으로 재시도했고 두 번째 view의 cursor가 `INVALID_CURSOR`로 거부되어 새 페이지를 조회했다. 최종 표의 root/path 차이 열 설명은 혼란스럽지만 각 루트와 실제 행 내용은 구분해 보고했다.

별도 실제 Cline 요청에서 합성 Dataset에 존재하지 않는 Linux 루트를 등록해 두었다. Cline 종료 코드 0, binding은 저장되어 있으나 Linux 디렉터리가 없다고 구분하고 DM `LineNo=1`의 경로와 줄을 보고했다. 파일·소스 줄을 읽었다고 주장하지 않았으며 올바른 절대 루트를 제공하거나 기존 루트를 준비하라고 안내했다. 첫 `--version` 실패 후 공식 `version`으로 재시도했다. 검증 후 해당 합성 Dataset의 기존 루트를 복원했다.

별도의 실제 Cline 요청에서는 다른 합성 Dataset의 source binding을 미등록 상태로 만들었다. Cline 종료 코드 0, DM `LineNo=1`의 기록 위치를 조회했지만 Windows 입력 DB 경로를 Linux 루트로 사용하지 않았다. 등록된 루트가 없어서 소스 파일을 확인하지 못했다고 보고하고 절대 Linux 루트를 요청했다. 첫 `--version`은 실패 후 공식 `version`으로 재시도했다. 검증 후 해당 합성 Dataset의 기존 루트를 복원했다.
