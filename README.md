# dart-agent

DART 앱을 공식 CLI로 제어하는 에이전트 스킬 저장소.

dart-control **0.2.0**은 공식 [DART v2.1.1](https://github.com/kalstein00/DART/releases/tag/v2.1.1)의 Linux·Windows CLI와 참조 자료를 포함한다. DART 앱·CLI **2.1.1**, protocol **3**, contractVersion **2.0.0**을 함께 사용한다. protocol 2 앱과 혼용할 수 없다. [출처와 검증 범위](docs/release-preparation.md)를 참고한다.

Linux Cline 전역 설치와 Windows Remote Access의 PIN 페어링 및 단일 창 세션 안내는 [설치·연결 문서](docs/installation.md)를 참고한다.

```bash
uv run --no-project python tools/install.py
```

설치 도구는 저장소 ZIP과 고정 해시·계약을 검증한다. 기존 설치가 있으면 같은 명령으로 갱신한다. 설치·업데이트와 실제 앱 연결의 검증 범위는 출처 문서에 구분한다.
