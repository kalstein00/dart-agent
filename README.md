# dart-agent

DART 앱을 공식 CLI로 제어하는 에이전트 스킬 저장소.

공식 DART 2.1.0의 Linux·Windows CLI와 참조 자료를 검증해 Release 첨부물로 준비한다. [준비 방법과 실제 Linux 실행 검증](docs/release-preparation.md)을 참고한다.

```bash
uv run --no-project python tools/prepare_release.py --output /tmp/dart-agent-release-0.1.0
```

실행 파일은 Git 소스에 포함하지 않는다. 준비 도구는 공식 DART Release에서 직접 내려받으므로 최초 dart-agent Release 준비에도 사용할 수 있다.
