# DART Agent

AI 에이전트가 DART 앱을 제어하기 위한 스킬의 도메인 용어를 정의한다.

## Language

**DART 앱**:
제어 대상인 Windows 데이터 분석 애플리케이션.
_Avoid_: Dart 언어, DART CLI

**DART CLI**:
DART 앱의 기능을 명령으로 제공하는 공식 클라이언트.
_Avoid_: DART 앱

**DART 제어 스킬**:
AI 에이전트가 사용자의 요청을 DART 작업으로 수행하도록 안내하는 재사용 가능한 지침과 보조 자료.
_Avoid_: DART 앱, DART CLI

**Dataset**:
DART 앱에서 조회·분석하는 로그 데이터 단위. 로그에 기록된 소스 위치와 실제 소스 코드는 별도로 구분한다.
_Avoid_: 소스 코드 저장소

**소스 루트**:
Dataset의 로그에 기록된 소스 파일을 찾기 위한 기준 디렉터리.
_Avoid_: DB 경로, 로그 원본 경로

**소스 위치**:
로그에 기록된 소스 코드 파일 경로와 해당 파일의 줄 번호.
_Avoid_: 로그 행 번호

**로그 행 번호**:
Dataset 안의 로그 행을 식별하는 번호.
_Avoid_: 소스 줄 번호
