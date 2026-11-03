# Linux Cline 설치와 Windows DART 연결

지원 조합은 Linux x64 glibc, Cline CLI, Windows DART 앱 2.1.0, 공식 CLI 2.1.0, protocol 2다. 회사 Linux에서 Windows로 직접 HTTPS 연결한다. WSL·공유 드라이브·특정 포트를 요구하지 않는다. 현재 WSL 검증은 회사 Linux 배포판 및 회사 네트워크 검증을 대신하지 않는다.

## clone 설치

Linux에 `git`, `gh`(GitHub CLI), `uv`, Cline CLI를 준비한다. 비공개 저장소라면 `gh auth login`으로 접근 권한을 설정한다.

```bash
git clone https://github.com/kalstein00/dart-agent.git
cd dart-agent
uv run --no-project python tools/install.py
```

설치 도구는 이 저장소의 고정 Release `v0.1.0` 첨부물 7개를 내려받아 저장소의 고정 크기·SHA256·계약으로 검증한다. 설치 직전 Linux 실행 파일의 실제 version/contract identity/export도 확인한다. 검증 실패 시 기존 스킬은 보존된다. Release가 아직 발행되지 않았거나 접근할 수 없으면 설치 실패로 보고한다. 다른 버전이나 공식 upstream으로 자동 대체하지 않는다.

설치 위치는 Cline 전역 `~/.cline/skills/dart-control`이다. 실행 파일은 그 안의 `bin/dart`, 공개 명령 참조는 `references/`에 있다. `--skills-dir`은 별도 Cline 구성의 전역 skills 디렉터리 지정에만 사용한다. 일반 업데이트는 저장소를 명시적으로 갱신한 뒤 아래 명령을 실행한다. 공식 개인 연결 프로필 `~/.dart/connections` 또는 `DART_CLI_PROFILE_DIR`은 설치 경로 밖에 유지한다. 스킬 디렉터리에 개인 파일을 저장하지 않는다.

```bash
uv run --no-project python tools/install.py --update
```

초기 개발에서는 #2 준비 도구 출력으로 아래처럼 설치할 수 있다. `installation.json`에 `development-prepared-assets`로 표시된다. 이 실행은 공개 Release 설치 성공의 증거가 아니다. 준비 자산도 매번 동일한 검증을 거친다.

```bash
uv run --no-project python tools/install.py --prepared-dir /private/development-prepared-assets
```

## Windows 담당자

1. 지원하는 Windows DART 2.1.0을 직접 실행한다.
2. Settings > External Control에서 Remote Access를 활성화한다.
3. Linux에서 도달할 수 있는 실제 HTTPS endpoint를 사용해 새 일회용 연결 번들을 발급한다. 필요한 Windows 방화벽·회사 네트워크 접근을 허용한다.
4. 번들을 Linux 사용자에게 비공개 전달한다. 저장소·채팅·배포물·공개 실행 증거에 번들 또는 토큰을 넣지 않는다. 만료되거나 이미 사용한 번들은 새로 발급한다.

Linux는 Windows 앱 실행, Remote Access 활성화, 번들 발급을 대신하지 않는다.

## Cline 업무 요청

Cline을 다시 시작한 후 실제 업무 요청으로 스킬 호출을 확인한다.

> dart-control 스킬로 DART 상태를 확인하고 연결해 주세요. 프로필은 work-dart입니다. 등록이 필요하면 비공개 번들 파일 경로를 알려 드리겠습니다. 단일 창에 제어 세션을 만들고 앱·창·세션 ID를 보고해 주세요.

Cline은 설치된 `references/connection.md`에 따라 공식 CLI로 등록·상태 조회·양쪽 버전/계약 비교·창 목록 조회·세션 생성 및 재확인을 수행한다. 번들은 파일을 stdin으로 전달하고 내용을 출력하지 않는다. 현재 요청에서 지정한 창이 이전 선택보다 우선한다. 지정이 없으면 유효한 이전 선택을 재사용하고, 이전 선택이 없을 때 단일 창을 선택한다. 현재 지정 없이 이전 창이 사라졌다면 남은 창이 하나여도 대체 대상을 사용자에게 확인한다. 여러 창에서 대상을 구분할 수 없으면 공개 창 ID와 역할을 제시하고 선택을 요청한다. 이후 업무에서는 명시적인 appId/windowId/sessionId를 재확인해서 재사용하며 GUI 포커스로 대상을 바꾸지 않는다. 세션이 유효하지 않으면 앱과 창을 다시 확인해 사용자의 의도에 맞게 세션을 재선택한다. 의도가 모호하면 사용자에게 확인한다. 재시작 후 이전 ID를 그대로 사용하지 않는다.

접속 거부/시간 초과는 Windows 앱·Remote Access·발급 endpoint·방화벽과 Linux 경로를 확인한다. 등록 실패 또는 만료/사용된 번들은 새로 발급한다. 프로필을 읽지 못하면 Linux 프로필 이름/위치를 확인한다. 인증서 변경은 Windows 담당자에게 대상을 확인한 뒤 명시적으로 trust를 갱신한다. 버전/protocol/fingerprint 불일치는 호환 조합을 설치하기 전 업무를 중단한다. 실패의 공식 code/phase/nextAction을 비밀 없이 보고한다.

## 인수 증거

스킬 파일 존재만으로 성공 판정하지 않는다. 실제 Cline `skills` 호출, 공식 Linux CLI 실행 버전·계약 및 연결된 Main의 독립적인 공개 상태, 선택한 단일 창과 열린 세션의 재조회 결과를 보존한다. 번들·프로필·인증서·토큰은 기록하지 않는다. 설치 출처, Cline 버전, OS/아키텍처, WSL 여부와 회사 네트워크 검증 여부를 함께 기록한다. 실제 연결이 막힌 경우 연결 인수는 미검증이며 완료 처리하지 않는다. 초기 개발 단계(#3)는 준비 자산 설치와 실제 Cline 연결을 기록한다. 공개 Release 설치 성공을 주장하지 않으며, 발행된 Release를 통한 최종 설치 검증은 #8의 인수 게이트다.

## Dataset 가져오기와 로그 조회

Windows DART에서 접근할 수 있는 절대 입력 경로를 준비한 뒤 Cline에 예를 들어 요청한다. 파일은 Windows에 미리 두어야 하며, Linux 스킬이 전송하거나 원격 SQLite를 직접 열지 않는다.

> dart-control 스킬로 Windows의 `C:\DART\input\capture.sqlite`를 가져와 Dataset 준비 완료를 확인하고 DM과 원하는 Tag의 로그 값과 행 번호를 보여 주세요. 프로필과 사용할 창은 앞서 선택한 대상을 사용해 주세요.

SQLite 외 입력은 해당 형식의 공개 명령을 확인한다. Cline은 입력과 대상에 대한 preflight 후 가져오기를 요청하고 원래 taskId의 최종 상태와 Dataset 준비 상태를 확인한다. 접수만 된 작업은 완료가 아니다. Tag 정의를 지정할 수 없으면 사용자가 선택할 근거를 요청한다. 잘못된 경로, 실패·취소된 작업 또는 없는 Dataset은 공식 오류와 조치로 보고한다. 보고서의 입력 파일 출처, 로그 행 번호와 로그에 기록된 소스 파일·소스 줄은 서로 다르다. 소스 코드 읽기는 별도 작업이다.

공식 합성 예제와 실제 Cline 검증 절차는 [Dataset 인수 기록](verification/issue-5.md)을 참고한다. 회사 DB나 연결 비밀을 예제 또는 증거에 넣지 않는다.
