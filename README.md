# dart-agent

DART 앱을 공식 CLI로 제어하는 에이전트 스킬 저장소.

현재 체크아웃은 DART 2.1.0 개발 후보의 Linux·Windows CLI와 참조 자료를 포함하며 [출처와 검증 범위](docs/release-preparation.md)를 기록한다. 공개 DART `v2.1.0` 릴리스는 이 후보와 계약이 다르다.

Linux Cline 전역 설치와 Windows Remote Access의 PIN 페어링 및 단일 창 세션 안내는 [설치·연결 문서](docs/installation.md)를 참고한다.

```bash
uv run --no-project python tools/install.py
```

설치 도구는 저장소 ZIP과 고정 해시·계약을 검증한다. 기존 설치가 있으면 같은 명령으로 갱신한다. 개발 후보 검증은 공개 Release 인수를 대신하지 않는다.
