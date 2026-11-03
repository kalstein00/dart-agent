# Windows Dataset과 Linux 소스 코드의 위치를 분리한다

회사 환경에서는 WSL 없이 Linux 컴퓨터의 Cline 에이전트가 Windows DART 앱에 원격 접속한다. Dataset SQLite는 Windows에 두고 공개 DART CLI로 조회하며, 로그에 기록된 소스 위치는 Dataset에 연결된 Linux 소스 루트에서 해석한다.

DB나 소스 코드를 같은 호스트로 옮기거나 WSL 공유 드라이브를 사용하는 방식을 전제로 삼지 않는다. 이 경계는 현재 개발 PC의 WSL 환경이 회사 배포 환경의 필수 조건으로 굳어지는 것을 방지하고, 로그 행의 식별자와 실제 소스 코드 위치를 구분한다. 가져오기·내보내기 경로는 Windows에서 해석하며, Linux로 파일을 자동 전송한 것으로 간주하지 않는다.
