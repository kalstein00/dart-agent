# Cline 설치와 Windows DART 연결

설치 도구는 Linux x64 glibc와 Windows x64에서 해당 OS의 현재 개발 후보의 CLI 2.1.0을 설치한다. DART 앱은 Windows 2.1.0, protocol 2다. Linux에서 연결할 때 WSL·공유 드라이브·특정 포트를 요구하지 않는다. 회사 Linux 배포판 및 회사 네트워크 검증은 별도로 필요하다.

## clone 설치

설치할 OS에 `git`, `uv`, Cline CLI를 준비한다. 설치에 `gh` 인증이 필요하지 않다.

```bash
git clone https://github.com/kalstein00/dart-agent.git
cd dart-agent
uv run --no-project python tools/install.py
```

설치 도구는 저장소에 포함된 `release/dart-agent-release-assets.zip`의 개발 후보 파일 10개를 고정 크기·SHA256·계약으로 검증한다. 이 후보는 공개 DART Release가 아니며 소스 커밋은 lock에 기록한다. 설치 시 다운로드나 GitHub 인증은 필요하지 않다. 설치 직전 현재 OS 실행 파일의 실제 version, 기존 identity/export와 버전된 identity/export도 확인한다. 검증 실패 시 기존 스킬은 보존된다.

별도로 준비한 ZIP을 사용할 경우 아래처럼 경로를 지정할 수 있다.

```bash
uv run --no-project python tools/install.py --asset-zip /path/to/dart-agent-release-assets.zip
```

로컬 파일도 동일한 lock과 실제 실행 검증을 거치며 설치 출처는 `local-release-assets`로 기록된다. 기존 설치가 있으면 자동으로 갱신한다.

체크아웃의 `skills/dart-control/compatibility.json`은 스킬 버전과 지원하는 DART/protocol과 contractVersion을 고정한다. 설치 전에 이 값과 checkout의 release lock이 일치해야 한다. 소스와 호환되는 버전을 명시적으로 checkout한 뒤 설치하며, 불일치하면 자동으로 다른 버전을 찾지 않는다.

설치 위치는 Cline 전역 `~/.cline/skills/dart-control`이다. 실행 파일은 Linux에서 `bin/dart`, Windows에서 `bin/dart.exe`이며 공개 명령 참조는 `references/`에 있다. `--skills-dir`은 별도 Cline 구성의 전역 skills 디렉터리 지정에만 사용한다. 일반 업데이트는 저장소를 명시적으로 갱신한 뒤 아래 명령을 실행한다. 공식 개인 연결 프로필 `~/.dart/connections` 또는 `DART_CLI_PROFILE_DIR`은 설치 경로 밖에 유지한다. 스킬 디렉터리에 개인 파일을 저장하지 않는다.

```bash
uv run --no-project python tools/install.py
```

초기 개발에서는 #2 준비 도구 출력으로 아래처럼 설치할 수 있다. `installation.json`에 `development-prepared-assets`로 표시된다. 이 실행은 공개 Release 설치 성공의 증거가 아니다. 준비 자산도 매번 동일한 검증을 거친다.

```bash
uv run --no-project python tools/install.py --prepared-dir /private/development-prepared-assets
```

## 계약 인수 기준

현재 개발 후보는 contractVersion 1.0.0과 fingerprint `478f2c998b51f7b6f3f7dd0d0670ed8583cf64561ecaafd23946875d5b79fd53`을 고정한다. 설치 전 자산과 실제 CLI의 버전된 export를 검증하고, 연결할 때 실제 CLI와 연결 Main을 각각 배포 기준에 비교한다. 릴리스·protocol·format·contractVersion·fingerprint가 모두 정확히 일치해야 새 업무를 시작한다. 동일 major나 additive 분류는 자동 허용이 아니다. 조회 실패·누락·버전 없는 응답은 unknown으로 처리하고 업무를 중단한다. 기존 legacy 기준을 새 버전으로 추정하거나 기준을 자동 갱신하지 않는다. 기존 Task의 조회·복구 규칙은 유지한다.

이 기준은 개발 후보에 대한 명시적 소비자 기준이며 정식 DART 발행이나 회사 환경 인수가 아니다. 후보 source commit/tree는 선언된 출처이고 해당 커밋으로부터 설치본의 바이트 재현을 입증하지 않는다.

## Windows 담당자와 PIN 페어링

1. Windows DART를 실행하고 Settings > **Remote Access**에서 Linux가 접근할 수 있는 **Network adapter**를 선택해 접근을 활성화한다.
2. **Pair a CLI**를 선택한다. 새 프로필 이름과 화면에 표시된 HTTPS endpoint로 Linux의 대화형 터미널에서 설치된 스킬의 CLI를 실행한다.

```bash
~/.cline/skills/dart-control/bin/dart connection pair --endpoint HTTPS_URL --profile PROFILE
```

3. 앱에 표시되는 6자리 PIN을 터미널에 직접 입력한다. PIN, 프로필 및 토큰은 비공개로 유지하며 채팅이나 기록에 넣지 않는다. 비대화형 에이전트는 이 단계를 사용자에게 맡긴다. 이후 `dart app inspect --profile PROFILE`로 앱 ID를 확인하고, `dart app inspect versioned --profile PROFILE --app APP_ID`로 연결된 Main의 계약을 독립적으로 확인한다. 주소가 바뀌면 새 이름의 프로필로 다시 페어링한다. 기존 프로필을 자동 교체하지 않는다.

앱이 지원하는 기존 bundle 등록은 명시적으로 선택한 경우 stdin으로 사용할 수 있다. 기존 인증서 신뢰를 자동 변경하지 않는다.

## Cline 업무 요청

Cline을 다시 시작한 후 실제 업무 요청으로 스킬 호출을 확인한다.

> dart-control 스킬로 DART 상태를 확인하고 연결해 주세요. 프로필은 work-dart입니다. 등록이 필요하면 PIN 페어링을 진행하겠습니다. 단일 창에 제어 세션을 만들고 앱·창·세션 ID를 보고해 주세요.

Cline은 설치된 `references/connection.md`에 따라 공식 CLI로 등록·상태 조회·양쪽 버전/계약 비교·창 목록 조회·세션 생성 및 재확인을 수행한다. 새 등록은 대화형 PIN 페어링으로 수행한다. 현재 요청에서 지정한 창이 이전 선택보다 우선한다. 지정이 없으면 유효한 이전 선택을 재사용하고, 이전 선택이 없을 때 단일 창을 선택한다. 현재 지정 없이 이전 창이 사라졌다면 남은 창이 하나여도 대체 대상을 사용자에게 확인한다. 여러 창에서 대상을 구분할 수 없으면 공개 창 ID와 역할을 제시하고 선택을 요청한다. 이후 업무에서는 명시적인 appId/windowId/sessionId를 재확인해서 재사용하며 GUI 포커스로 대상을 바꾸지 않는다. 세션이 유효하지 않으면 앱과 창을 다시 확인해 사용자의 의도에 맞게 세션을 재선택한다. 의도가 모호하면 사용자에게 확인한다. 재시작 후 이전 ID를 그대로 사용하지 않는다.

접속 거부/시간 초과는 Windows 앱·Remote Access·발급 endpoint·방화벽과 Linux 경로를 확인한다. 페어링이 만료되거나 실패하면 앱에서 새 페어링을 시작한다. 프로필을 읽지 못하면 Linux 프로필 이름/위치를 확인한다. 인증서 변경은 Windows 담당자에게 대상을 확인한 뒤 명시적으로 trust를 갱신한다. 버전/protocol/contractVersion/fingerprint 불일치나 누락은 호환 조합을 설치하기 전 업무를 중단한다. 실패의 공식 code/phase/nextAction을 비밀 없이 보고한다.

## 인수 증거

스킬 파일 존재만으로 성공 판정하지 않는다. 실제 Cline `skills` 호출, 공식 Linux CLI 실행 버전·계약 및 연결된 Main의 독립적인 공개 상태, 선택한 단일 창과 열린 세션의 재조회 결과를 보존한다. 번들·프로필·인증서·토큰은 기록하지 않는다. 설치 출처, Cline 버전, OS/아키텍처, WSL 여부와 회사 네트워크 검증 여부를 함께 기록한다. 실제 연결이 막힌 경우 연결 인수는 미검증이며 완료 처리하지 않는다. 초기 개발 단계(#3)는 준비 자산 설치와 실제 Cline 연결을 기록한다. 공개 Release 설치 성공을 주장하지 않으며, 발행된 Release를 통한 최종 설치 검증은 #8의 인수 게이트다.

## Dataset 가져오기와 로그 조회

Windows DART에서 접근할 수 있는 절대 입력 경로를 준비한 뒤 Cline에 예를 들어 요청한다. 파일은 Windows에 미리 두어야 하며, Linux 스킬이 전송하거나 원격 SQLite를 직접 열지 않는다.

> dart-control 스킬로 Windows의 `C:\DART\input\capture.sqlite`를 가져와 Dataset 준비 완료를 확인하고 DM과 원하는 Tag의 로그 값과 행 번호를 보여 주세요. 프로필과 사용할 창은 앞서 선택한 대상을 사용해 주세요.

SQLite 외 입력은 해당 형식의 공개 명령을 확인한다. Cline은 입력과 대상에 대한 preflight 후 가져오기를 요청하고 원래 taskId의 최종 상태와 Dataset 준비 상태를 확인한다. 접수만 된 작업은 완료가 아니다. Tag 정의를 지정할 수 없으면 사용자가 선택할 근거를 요청한다. 잘못된 경로, 실패·취소된 작업 또는 없는 Dataset은 공식 오류와 조치로 보고한다. 보고서의 입력 파일 출처, 로그 행 번호와 로그에 기록된 소스 파일·소스 줄은 서로 다르다. 소스 코드 읽기는 별도 작업이다.

공식 합성 예제와 실제 Cline 검증 절차는 [Dataset 인수 기록](verification/issue-5.md)을 참고한다. 회사 DB나 연결 비밀을 예제 또는 증거에 넣지 않는다.

## Dataset 소스 조사

Windows Dataset의 로그가 가리키는 Linux 프로젝트 디렉터리를 준비하고 Cline에 Dataset과 절대 소스 루트를 지정한다. 예를 들어 다음과 같이 요청한다.

> dart-control 스킬로 선택한 Dataset의 로그 원인을 조사해 주세요. 이 Dataset의 Linux 소스 루트는 `/work/project`입니다. 기록된 소스 파일과 줄을 읽어 근거를 보여 주세요.

Cline은 공개 `dataset inspect`의 Dataset별 source binding을 조회하고, 사용자가 지정한 루트를 `dataset source set`으로 등록한 뒤 재조회한다. 등록은 메타데이터 저장이며 파일을 복사하지 않는다. 같은 상대 경로라도 Dataset마다 다른 루트를 사용한다. Windows DB·가져오기 경로와 Linux 루트를 혼동하지 않는다. 등록되지 않은 루트, 잘못된 디렉터리, 없는 소스 파일은 구분해서 안내하며, 기록된 경로를 해석할 수 없으면 확인을 요청한다. 이름만 같은 파일이나 임의 빌드 경로 변환으로 대체하지 않는다. DM `file`/`source_line`은 소스 위치이고 DM `LineNo` 및 Tag `lineNo`는 로그 행이다. 조사 결과는 실제 읽은 파일과 줄, 추론의 한계를 함께 제시한다. 합성 예제와 실제 인수 결과는 [소스 조사 검증](verification/issue-6.md)을 참고한다.

## SQL·분석과 Windows 내보내기

준비된 Dataset, 원하는 조회 또는 분석과 Windows 절대 출력 경로를 Cline에 지정한다. 예를 들어 “이 합성 Dataset의 로그 행 수를 SQL로 구하고 CSV를 Windows 경로에 저장해 결과와 파일을 확인해 주세요”라고 요청한다. 필요한 SQL 저장과 결과 준비는 Workspace를 변경할 수 있다. 덮어쓰기는 별도 명시가 필요하다.

Cline은 필요한 공개 계약을 선택해 SQL Builder, Results 또는 Charts·Pivot·Comparison을 사용한다. 작업 접수와 완료, 결과 준비, Windows 파일 출판을 따로 확인한다. 기존 결과가 남아 있어도 새 작업이 실패하거나 취소됐다면 새 결과로 보고하지 않는다. 파일은 Windows에 생성되며 Linux로 자동 전송되지 않는다. 성공 결과와 실제 Windows 파일 위치·내용 확인 여부, 실패나 미확인 항목을 구분해 보고한다.

합성 데이터 기대값과 수행한 인수 범위는 [SQL·분석 인수 기록](verification/issue-7.md)을 참고한다.

최종 배포 및 재설치 인수의 현재 상태와 남은 실제 Release·회사 환경 게이트는 [통합 인수 기록](verification/issue-8.md)을 참고한다.
