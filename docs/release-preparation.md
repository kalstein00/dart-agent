# dart-control 0.2.0 — DART v2.1.1

공식 [DART v2.1.1 Release](https://github.com/kalstein00/DART/releases/tag/v2.1.1)의 CLI와 공개 명세를 사용한다. 앱·CLI는 `2.1.1`, control protocol은 `3`, contractVersion은 `2.0.0`이다. protocol 2 앱·CLI와 혼용할 수 없으며 Windows 앱도 함께 갱신해야 한다.

## 고정 출처

`release/dart-2.1.1.lock.json`은 공식 첨부물 10개의 자산 ID, 크기와 SHA256을 고정한다. `release/dart-agent-release-assets.zip`에는 이 파일들만 포함한다. 설치는 저장소 ZIP을 사용하며 GitHub 인증이나 다운로드를 요구하지 않는다.

- Upstream source commit: `9ca11298b64d5e1a5ae83927c667c46d3e0748d7`
- Source tree: `fc037e46257d4dc3bfa315a315f870170809edbb`
- Candidate ID: `83c9a568daa59dbe0dfdee078d4caebcdcc64f7a97316d1c7555370f82878a64`
- Contract format: `2`; fingerprint algorithm: `sha256`; projection: `1`
- Contract fingerprint: `0eca1fe6c52db9a2cb7aa6960c4b32fc4715cd29fd801dd7d74a7e633a294807`
- Windows CLI SHA256: `a74ca4823a08eef517c37f1bef55f3bad17bfe4b0ed05a31f573e3a9d3241831`
- Linux CLI SHA256: `25ef24273566f273e111d1cba30a23c512e85a998761efe4102dad5834b72da9`

GitHub Release는 공개됐지만 첨부된 versioned manifest의 `status: candidate`와 source의 `status: declared`는 upstream 원본 그대로 유지한다. 태그가 가리키는 실제 commit과 tree는 위 선언과 일치한다. 해시는 파일 동일성을 확인하며 소스에서의 바이트 재현이나 게시자 인증을 대신하지 않는다.

## 준비와 패키징

유지보수자는 `gh` 인증 후 고정 자산 ID로 다운로드하고 새 디렉터리에 준비한다. 이미 내려받은 공식 첨부물을 검증할 때는 `--source-dir`을 지정한다. 기존 출력은 덮어쓰지 않는다.

```bash
uv run --no-project python tools/prepare_release.py --output dist/prepared-2.1.1
uv run --no-project python tools/package_release.py --source-dir dist/prepared-2.1.1 --output dist/dart-agent-release-assets.zip
```

준비 도구는 10개 파일과 agent/CLI manifest, bundle 내부 파일, 기존·버전된 catalog의 결합을 검증한다. 현재 OS의 최종 CLI로 `version`, `contract identity`, `contract export full`, `contract identity versioned`, `contract export versioned`를 실행한다. 응답 protocol은 lock과 같아야 하며 export는 해당 catalog와 정확히 일치해야 한다. protocol 3에는 버전된 기준이 필수다.

설치 직전에도 같은 검증을 실행한다. 연결 후의 Main은 별도 `app inspect versioned` 관측으로 배포 기준과 비교한다. CLI의 오프라인 성공으로 Main 호환성이나 업무 성공을 추정하지 않는다.

## 검증 범위 — 2026-11-10

이번 환경은 Windows x64이며 Linux/WSL 실행 환경은 없다. Linux 파일은 크기·SHA256과 공식 manifest의 플랫폼 결합을 확인한다. Linux 네이티브 실행, 실제 Cline 호출, 설치된 Windows Main 연결·PIN 페어링·업무 실행, 회사 Linux·회사 네트워크 인수는 이번 검증 범위에 포함하지 않는다.

Windows의 최종 공식 CLI로 준비 명령을 실행해 종료 0, version `2.1.1`, protocol `3`, mode `installed`, 기존·버전된 identity와 catalog/export의 정확한 일치를 확인했다. 새 ZIP을 사용한 임시 경로 최초 설치와 기존 설치 업데이트도 통과했다. 설치된 CLI를 다시 실행해 versioned identity를 확인했으며, 후보 ID 불일치·변조 자산·호환성 불일치·누락 ZIP은 기존 설치를 보존했다.

전체 테스트 27개 중 23개 통과, Linux shell fixture 4개는 Windows에서 skip됐다. 실패는 없다. 공식 자산 메타데이터, 문서 링크와 스킬의 명시적 명령을 v2.1.1 catalog와 대조했다.

검증 명령:

```bash
uv run --no-project python -m unittest discover -s tests -v
```

DART 2.1.0 개발 후보와 이전 공개 릴리스의 검증 이력은 [이전 준비 기록](release-preparation-2.1.0.md)에 보존한다. 이전 lock 두 개도 이력으로 유지하며 기본 설치에는 사용하지 않는다.
