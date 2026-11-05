# 반복 조사와 새 대화 검증 (#9)

상태: 시나리오 평가 완료. #11은 파일을 통한 기존 자료 유입이 있는 제한부 관측이다. 이 기록은 기존 관측을 이번 실제 조사 성공으로 취급하지 않는다. 시작 후보는 `dart-agent` commit `850abb7d4f1804ba5e3703b455f0fd4bd7ade611`, 작업 트리는 깨끗했다. 2026-11-05 WSL SSH에서 Cline CLI 3.0.74, 설치된 DART CLI 2.1.0/protocol 2, Windows 개발 DART 앱으로 검증을 시작했다. 회사 Linux 및 네트워크는 검증하지 않았다.

## 연결 준비

앱 실행 전과 후 기존 `[기존 프로필]` 프로필의 `app inspect`는 완료되지 않았다. 앱 실행 후 별도의 20초 제한 조회는 종료 124였고 공식 오류 객체를 받지 못했다. 기존 프로필 endpoint는 현재 Windows 앱의 수신 주소와 일치하지 않았으며 해당 endpoint TCP 연결은 시간 초과였다. 프로필이나 인증서의 내용을 기록하지 않았다. 첫 조회는 중단했다. 이 시점에는 새로운 신뢰 등록을 하지 않았고 실제 app/window/session과 Dataset 상태를 확인하지 못했다. 후속 페어링과 상태 확인은 아래에 기록한다.

## #11: 전달 기록 없는 새 대화

새 Cline 세션 `conv_1793872064387_xvp5qqq`에서 빈 작업 디렉터리 `/tmp/dart-agent-issue9-neutral`을 사용했다. `cline --provider openai-codex --json --cwd /tmp/dart-agent-issue9-neutral --timeout 300`에 단 한 요청을 전달했다: “아까 그 로그 불일치의 원인을 어디까지 확인했지? 다음에 뭘 봐야 해?” 이전 대화, Dataset ID, 조사 전달 기록은 직접 제공하지 않았다. 설치된 전역 스킬, 사용자 환경, 파일 시스템은 격리하지 않았다.

Cline은 스킬을 호출하고 전체 파일 시스템과 홈 디렉터리를 검색했다. 검색 두 번이 각각 30초 시간 초과된 뒤 저장소를 찾아 기존 `docs/verification/issue-6.md`와 `issue-5.md`를 직접 읽었다. 따라서 기존 조사 근거가 파일을 통해 유입됐다. 빈 cwd와 새 세션만으로 이전 조사 정보가 차단됐다고 볼 수 없다. 실행은 132.8초, 종료 0, 최종 응답 완료였다. 원본 JSONL은 WSL `/tmp/dart-agent-issue9-no-handoff.jsonl`에 있으며 환경 출력이 포함될 수 있어 공개 첨부하지 않는다.

응답은 기존 기록에 근거해 합성 Dataset 로그 행 1의 output 43, 기록된 소스 `source/value_demo.c:8`, 소스 계산 21×2=42, 표시 큰 정수와 typed 정수의 차이를 설명했다. 실행 바이너리의 소스 일치와 원인은 미확인으로 명시했고, 별도 이전 대화와 현재 Dataset ID가 없음을 밝히며 다른 대상이라면 ID와 행 번호를 요청했다. 현재 연결이나 Dataset을 조회하지 않았다. **판정: #11 인수 조건 충족, 제한부 관측.** 이전 조사 내용을 직접 제공하지 않은 새 대화에서 문서 유입과 출처, 미확인 사항을 기록했고 응답은 다른 대상이라면 식별을 요청했다. 명세는 유입이 있으면 한계를 기록하도록 한다. 파일로 이전 근거가 유입됐으므로 정보가 전혀 없는 완전 격리 시험의 성공은 입증하지 못했다.

## #10 및 #12

아래의 후속 관측을 따른다. 이전 #5–#8의 결과는 기대값과 선행 사례일 뿐 이번 시험의 성공 증거가 아니다.

### 현재 DART의 Pair 방식과 설치 자산 차이

사용자 지적 후 현재 DART `14a85e60d8ce69098bfba04e708abf409d5d2ff8`의 사용자 안내와 실행 중 앱에서 **Pair a CLI**를 확인했다. 현재 개발 CLI는 `connection pair`를 지원한다. 설치된 Release CLI의 계약 fingerprint는 `6fc2f2381407bc3b1193293dae8a78dbfec6412ca1e8619d061a957dbb597042`, 현재 개발 CLI는 `4f523920d4db114df90df3e46ea828de0d08bc7a52514d8d36b2035ad09418d5`이다. 설치 스킬은 이전 계약과 번들 절차를 고정하고 있어 현재 앱과 호환된다고 가정할 수 없다. 버전 문자열은 둘 다 2.1.0이다. WSL에서 Windows 체크아웃의 Node CLI 계약 조회는 성공했으나 이 개발 CLI는 설치 스킬의 공식 자산과 구별해야 한다.

앱에서 페어링을 열고 개발 CLI를 실행해 PIN 프롬프트까지 도달했으나 등록을 완료하지 않고 CLI를 중단하고 앱의 대기를 취소했다. PIN 및 자격은 기록하지 않았다. 이후 PIN 자동 전달을 위한 실행은 호스트 자동 승인 정책이 거부해 실행되지 않았다. 연결 성공이나 #10/#12 검증을 주장하지 않는다. 명세가 요구하는 설치 스킬 평가를 개발 CLI로 대체하지 않으며, 현 자산 호환성 차이를 해결하거나 범위 결정을 받은 뒤 재개해야 한다.

2026-11-05 후속: 사용자가 Pair a CLI 방식으로 수정하라고 지시했다. DART 소스 커밋 `14a85e60d8ce69098bfba04e708abf409d5d2ff8`의 개발 후보로 설치 스킬과 CLI를 갱신했다. 사용자가 새 프로필을 대화형 PIN으로 등록한 뒤 설치 CLI의 `app inspect`는 app `06ae190e-9dc4-4546-a0ac-cbd48c954768`, mode development, connected-main, protocol 2와 후보 fingerprint `4f523920d4db114df90df3e46ea828de0d08bc7a52514d8d36b2035ad09418d5`를 확인했다. 프로필/PIN 자격을 보존하지 않는다. 이것은 연결 증거이며 #10/#12의 조사 결과는 아니다.


### #10 실제 동일 대화 조사 — 2026-11-05

실제 Cline 3.0.74, provider `openai-codex`의 새 CLI 세션 `1793873886312_ywqmv`에서 빈 `/tmp/dart-agent-issue9-session`을 사용했다. 최초 요청은 “dart-control 스킬을 사용해 현재 연결 프로필 [새 프로필]의 Windows DART에서 기존 공식 합성 Dataset 706fe0ed-0f44-4300-8038-6d3736dd901c의 현재 상태를 확인하고 로그 입력과 출력에서 이상을 찾아 근거를 알려주세요. 사용 가능한 기존 대상이 아니면 추측하지 말고 멈춰 주세요.”였다. 예상 결론은 주지 않았다. Cline은 app `06ae190e-9dc4-4546-a0ac-cbd48c954768`, window `8babf7ad-4464-4fbe-b779-4ee8339c9ea0`, 새 session `1e70ad30-52e2-4790-a903-08506427eb9b`을 재확인했다. `dataset list`가 빈 목록을 반환해 대상 부재를 보고하고 중단했다. 이는 로그 분석 성공이 아니다.

같은 세션을 Cline TUI의 `--id 1793873886312_ywqmv`로 재개했다. 이 전에 `--id`와 비대화형 JSON 모드를 사용한 두 시도는 prompt 요구 오류로 종료 1이었고 업무 명령을 제출하지 않았다. 후속 요청은 기존 공식 합성 입력 `C:\Users\kalst\dart-agent-issue8-release-final\synthetic-values.sqlite`을 새 출력 `C:\Users\kalst\dart-agent-issue8-release-final\issue9-20261105.sqlite`으로 덮어쓰기 없이 가져와 같은 질문을 수행하도록 했다. 입력의 SHA256은 `1c322713ef445d47cfdb64ed7746b0d64f01bdc7226f6e85282f139db52fd805`다. preflight는 `outputExists:false`, `overwrite:false`; import task `8f803e0f-ce91-4870-b4ac-869706f520cd`는 `succeeded`, `catalogCommitted:true`, `outputPublished:true`; Dataset `2b0ee9ff-bf64-4330-9118-1c7174d0082f`은 `ready`였다. 재실행하지 않았다.

첫 분석 응답은 DM `12ddb292-84a9-4faa-a835-2d554e07e9af`의 네 행을 모두 읽고 행 1 출력 차이와 행 2 빈 입력을 보고했다. 입력·출력은 `information` 표시 문자열인데 처음에는 행 데이터에서도 확인됐다고 설명해 typed 근거와 혼동할 소지가 있었다. 별도 후속 요청은 “방금 찾은 이상이 나머지 행과 어떻게 다른지 비교해 주세요. 입력 누락의 의미와 큰 정수도 표시값이 아닌 원래 데이터로 확인하고, 확인 범위를 알려 주세요.”였다. 응답은 같은 대상의 전체 DM 행을 비교했고 DM만으로 원래 NULL과 큰 정수 정확성을 입증할 수 없다고 정정했다. 이 시점에는 요청한 typed 조회를 수행하지 못했다.

그 다음 별도 후속 요청은 “앞에서 발견한 출력 차이에 대해 해당 로그에 기록된 소스 위치의 실제 코드를 조사해 주세요. 이 Dataset의 Linux 소스 루트는 /tmp/dart-agent-implementation-batch/issue-6-fixture 입니다. 코드와 로그의 관계, 확인된 사실과 아직 모르는 부분을 구분해 주세요.”였다. Cline은 fresh Dataset source binding을 등록·재조회하고 실제 `source/value_demo.c:8`과 변환 함수 6행을 읽었다. 또한 Tag `c73d65a2-a9fc-48b8-88de-ff0af508b2ae`의 offsets 1–4, 전체 4행, `nextCursor:null` typed 값을 확인했다. 행 0–3의 input/output은 `21/42`, `21/43`, `null/42`, `21/42`; serial은 모두 정확한 `9007199254740993`, DM 표시 `9007199254740992`와 다르다. 로그 행 1과 소스 줄 8을 구분하고 21×2=42와 로그 43을 비교했다. 실제 실행 바이너리와 소스 일치, 차이의 원인, NULL 생성 경로와 표시 변환 계층은 미확인으로 뒀다.

실제 오류: `view list`의 잘못된 JSON은 `INVALID_JSON`; DM 진단 조회는 `UNSUPPORTED_VIEW_TYPE`; source set의 input inspect에서 profile 누락은 `PROFILE_REQUIRED`. 이후 공개 상태를 확인하고 진행했다. 원본 CLI JSONL `/tmp/dart-agent-issue9-turn1.jsonl`, Cline 세션 메시지 `/home/kalstein/.cline/data/sessions/1793873886312_ywqmv/1793873886312_ywqmv.messages.json`은 개인 환경을 포함할 수 있으므로 공개하지 않는다. #10 판정: 동일 대화 후속 대상 유지와 typed·소스 근거는 개발 후보 CLI 및 앱에서 관측했다. 공개 Release의 설치 앱 인수는 아니다. typed 확인은 요청 직후가 아니라 다음 소스 조사에서 완료됐다. 별도의 회사 환경이나 실제 바이너리 원인은 미검증이다.

### 실제 조사에서 작성한 전달 기록

## 새 대화용 전달 기록

**조사는 여기서 중단합니다.** 아래 내용은 새 대화에서 이어볼 수 있도록 정리한 기록입니다. 모든 상태는 **2026년 11월 5일 마지막 확인 시점의 관찰**이며, 새 대화에서는 연결·세션·Dataset·뷰 상태를 다시 검증해야 합니다. 현재 상태가 그대로라고 가정하지 마세요.

### 마지막으로 확인한 대상과 상태

- **프로필:** `[새 프로필]`
- **Windows Main 앱 ID:** `06ae190e-9dc4-4546-a0ac-cbd48c954768`
- **DART 버전/프로토콜:** CLI와 Main 모두 `2.1.0`, protocol `2`; 계약 지문이 승인된 값과 일치
- **창 ID:** `8babf7ad-4464-4fbe-b779-4ee8339c9ea0` — 마지막 목록 조회 때 사용 가능
- **세션 ID:** `1e70ad30-52e2-4790-a903-08506427eb9b` — 마지막 검사 때 `open`, 창도 `open`
- **Import task ID:** `8f803e0f-ce91-4870-b4ac-869706f520cd` — 마지막 상태 조회 결과 `succeeded`, `catalogCommitted:true`
- **Dataset ID:** `2b0ee9ff-bf64-4330-9118-1c7174d0082f` — 마지막 검사 때 `ready`
- **Windows 원본 입력:** `C:\Users\kalst\dart-agent-issue8-release-final\synthetic-values.sqlite`
- **게시된 출력:** `C:\Users\kalst\dart-agent-issue8-release-final\issue9-20261105.sqlite`
- **DM 뷰 ID:** `12ddb292-84a9-4faa-a835-2d554e07e9af`
- **Tag 뷰 ID:** `c73d65a2-a9fc-48b8-88de-ff0af508b2ae` — offsets `1–4`로 열린 비활성 뷰
- **Dataset 소스 바인딩:** 사용자가 지정한 Linux 루트 `/tmp/dart-agent-implementation-batch/issue-6-fixture`를 해당 Dataset의 Source Workspace 메타데이터로 저장했으며, 마지막 검사에서 `state:"saved"`, `revision:1`로 확인됨

Import는 이미 성공해 재실행하지 않았습니다. 새 대화에서도 불확실한 결과가 보이면 새 Import를 시작하지 말고 기존 task 상태부터 확인하세요.

### 확인된 관찰과 근거

Tag 뷰에서 4행을 모두 조회했습니다(`totalRowCount:"4"`, `nextCursor:null`, `sampled:false`). `arg[0]`–`arg[3]`는 각각 정의상 `input`, `output`, `nullable`, `serial`입니다.

| Dataset LineNo | Tag | typed 입력 | typed 출력 | typed serial |
|---:|---|---:|---:|---:|
| 0 | `VALUE_1` | 21 | 42 | 9007199254740993 |
| 1 | `VALUE_2` | 21 | **43** | 9007199254740993 |
| 2 | `VALUE_3` | **NULL** | 42 | 9007199254740993 |
| 3 | `VALUE_4` | 21 | 42 | 9007199254740993 |

- **출력 차이:** LineNo 1은 입력 `21`에 출력 `43`을 기록했습니다. 같은 입력의 LineNo 0·3은 `42`입니다.
- **입력 누락의 실제 저장값:** LineNo 2의 `arg[0]`은 단순 빈 텍스트가 아니라 Tag typed cell에서 `type:"null"`, 값 `null`로 반환됐습니다. 출력은 정수 `42`로 기록됐습니다.
- **큰 정수 표시 차이:** 네 행의 원본 Tag typed `serial`은 모두 정확한 정수 `9007199254740993`입니다. DM의 파생 `information` 문자열은 네 행 모두 `serial=9007199254740992`로 표시했습니다. 확인된 원본 typed 값과 DM 표시값 사이에는 1의 차이가 있습니다.
- **추가 차이:** LineNo 3의 DM `file`은 `source/unavailable.c`였고, 다른 세 행은 `source/value_demo.c`였습니다. 해당 unavailable 경로의 실제 파일은 이번 조사에서 확인하지 않았습니다.

### 코드 조사

- 사용자가 지정한 Linux 루트가 실제 디렉터리임을 확인했습니다.
- 정확한 로그 상대 경로 `source/value_demo.c`를 루트 아래에서 해석했고, `realpath` 결과도 루트 안에 있었습니다.
- 읽은 코드: `/tmp/dart-agent-implementation-batch/issue-6-fixture/source/value_demo.c`
- DM 기록 위치는 **8행**이며, 관련 문맥은 6–10행입니다. 코드에는 `convert_value(int64_t input) { return input * 2; }`가 있고, 8행의 `printf` 형식 문자열에는 `serial=9007199254740993`이 있습니다. 9행에서 `input`과 `convert_value(input)`을 출력 인자로 전달합니다. `main`은 `emit_value(21)`을 한 번 호출합니다.
- 따라서 이 코드대로라면 입력 `21`의 변환 출력은 `42`입니다. LineNo 1의 `21 → 43` 로그와는 다릅니다. 코드의 serial 리터럴은 Tag typed serial 값 `9007199254740993`과 일치합니다.

### 아직 확인되지 않은 사항

- `value_demo.c`가 이 Dataset을 생성한 실제 바이너리 또는 실행과 일치하는지 여부. 로그의 `information`은 `Synthetic value ...` 형식인 반면 해당 코드의 형식 문자열은 `VALUE input=...`입니다. 코드가 4행 전체의 출처라는 점은 입증되지 않았습니다.
- LineNo 2에 입력값이 왜 NULL로 저장됐는지, 어떤 생성 경로가 그 값을 기록했는지.
- DM `information`에서 serial 값이 1 작게 표시된 정확한 변환 위치. 원본 Tag typed 값은 확인됐지만, 손실이 발생한 계층은 확인되지 않았습니다.
- `/tmp/dart-agent-implementation-batch/issue-6-fixture/source/unavailable.c:8`의 실제 코드와 해당 기록 경로가 왜 다른지.
- 마지막 조회 이후 프로필 연결, 창·세션, task 기록, Dataset 및 두 뷰가 여전히 유효한지.

### 새 대화에서 이어갈 때

1. `dart-control` 스킬 절차에 따라 CLI/Main 호환성과 `[새 프로필]` 연결을 확인합니다.
2. 기존 app/window/session을 재검증하고, 같은 task ID의 상태와 Dataset readiness를 읽습니다. **Import는 재실행하지 않습니다.**
3. 코드 근거가 더 필요하면 저장된 Linux 소스 루트와 Dataset source binding을 다시 확인합니다.
4. 로그 데이터나 Dataset 상태를 변경하지 말고, 확인 가능한 추가 사실과 한계를 구분해 보고합니다.


### #12: 전달 기록을 제공한 새 대화 — 2026-11-05

아래에 표시된 전달 기록 전체(실제 요청에는 동일한 새 프로필 이름이 들어 있었으며 여기서는 비식별화)와 “조사를 이어가기 전에 현재 대상과 상태를 확인하고, 무엇이 확인됐으며 무엇을 더 봐야 하는지 알려주세요. 이전 기록만으로 현재 상태를 단정하지 마세요.”를 새 Cline CLI 대화에 제공했다. 작업 디렉터리 `/tmp/dart-agent-issue9-handoff-session`, Cline 3.0.74, provider `openai-codex`; 별도 새 세션이며 원본 출력 `/tmp/dart-agent-issue9-resume.jsonl`은 개인 환경이 포함될 수 있어 공개하지 않는다. 이 실행은 종료 0과 최종 응답을 확인했다.

Cline은 `app inspect`, `window list`, `session inspect`, 원래 `task status`, `dataset inspect`, view 목록 및 DM·Tag rows를 실행해 연결·대상·task·네 행과 source binding을 현재 상태로 확인했다. 소스 파일을 직접 재조회했다. `connection inspect` 및 `help connection/app`은 지원되지 않았으며, 별도의 공개 명령으로 상태를 확인했다. 기존 import나 Dataset 변경은 수행하지 않았다. #11과 구별되는 제공 맥락은 위 전체 전달 기록이다. #11은 파일 탐색으로 기존 문서가 유입돼 완전 무정보 조건을 증명하지 못했고, #12는 기록에 담긴 사실과 한계를 유지하면서 현재 상태를 확인했다. **#12 판정: 개발 후보 CLI 및 앱에서 실제 전달 기록을 통한 이 재개 사례 통과.** 공개 Release 설치 앱 인수는 아니다. 설치된 앱이나 회사 환경 일반화는 검증하지 않았다.

최종 응답:

> 2026년 11월 5일 현재 상태를 다시 확인했습니다. **전달 기록의 주요 ID와 상태는 지금도 일치합니다.** 기존 Import를 재실행하지 않았고 Dataset이나 뷰도 변경하지 않았습니다.
>
> ### 지금 확인된 상태
>
> - `[새 프로필]`로 연결된 Main의 App ID는 `06ae190e-9dc4-4546-a0ac-cbd48c954768`입니다.
> - CLI와 Main 모두 버전 `2.1.0`, protocol `2`이며 계약 지문도 승인된 값과 일치합니다.
> - 창 `8babf7ad-4464-4fbe-b779-4ee8339c9ea0`이 현재 목록에 있고, 세션 `1e70ad30-52e2-4790-a903-08506427eb9b`도 `open`; 창 상태도 `open`입니다.
> - 기존 Import task `8f803e0f-ce91-4870-b4ac-869706f520cd`는 `succeeded`이며, `catalogCommitted:true`, 결과 Dataset ID `2b0ee9ff-bf64-4330-9118-1c7174d0082f`로 확인됐습니다.
> - Dataset은 현재도 `ready`입니다. 저장된 Source Workspace binding은 Linux 경로 `/tmp/dart-agent-implementation-batch/issue-6-fixture`, 상태 `saved`, revision `1`입니다.
> - DM 뷰 `12ddb292-84a9-4faa-a835-2d554e07e9af`와 Tag 뷰 `c73d65a2-a9fc-48b8-88de-ff0af508b2ae`가 현재 View 목록에 있습니다. Tag 뷰는 offsets `1–4` 정의를 가리킵니다.
> - Tag와 DM 행을 각각 다시 조회했습니다. 두 조회 모두 4행 전체를 반환했고 `sampled:false`, `nextCursor:null`이었습니다.
>
> ### 다시 확인한 데이터 관찰
>
> - Tag typed cells에서 LineNo 1은 `21 → 43`, LineNo 0·3은 `21 → 42`입니다.
> - LineNo 2의 Tag `arg[0]`은 typed `null`이고, `arg[1]`은 정수 `42`입니다.
> - 네 행 모두 Tag typed serial은 정확히 `9007199254740993`입니다. DM 파생 `information`에는 네 행 모두 `9007199254740992`로 표시됩니다.
> - 이번 DM 조회에서는 네 행 모두 `source_line=8`입니다. LineNo 0–2의 `file`은 `source/value_demo.c`, LineNo 3의 `file`은 `source/unavailable.c`입니다.
>
> ### 소스 경로에서 지금 확인된 것과 한계
>
> 바인딩 루트는 현재 Linux에서 존재하고, `source/value_demo.c`도 그 루트 아래에서 실제 경로를 확인했습니다. 파일 6–10행에는 `input * 2` 변환 코드와 `input`, 변환 결과, serial을 출력하는 코드가 있습니다. 따라서 **이 파일 내용만 보면 입력 21의 출력은 42**입니다.
>
> 반면 DM에 기록된 `source/unavailable.c:8`은 현재 바인딩 루트의 정확한 위치에서 찾을 수 없습니다. 또 `value_demo.c` 내용의 출력 형식과 DM의 `Synthetic value ...` 기록 형식이 서로 달라, 이 파일이 Dataset의 실제 기록을 생성한 바이너리·실행과 일치하는지는 확인되지 않았습니다. 따라서 불일치의 원인이나 serial 표시 손실이 발생한 계층도 아직 확정할 수 없습니다.
>
> ### 더 조사할 때 필요한 점
>
> 1. 실제 실행 또는 바이너리와 `value_demo.c`의 대응 관계
> 2. `source/unavailable.c`의 올바른 매핑 또는 해당 파일이 없는 이유
> 3. LineNo 1의 `21 → 43`과 LineNo 2의 NULL 입력이 생성된 경로
> 4. DM 파생 문자열에서 큰 정수가 1 작게 표시되는 변환 위치
>
> 현재 조사는 읽기 전용으로 마쳤습니다. `connection inspect`와 `help connection/app`은 이 CLI에서 지원되지 않아 사용할 수 없었지만, `app inspect`, `window list`, `session inspect`로 연결과 대상 상태를 직접 확인했습니다.

## 종합 판정

#10의 동일 대화 후속 조사, #11의 전달 없는 새 대화와 유입 한계, #12의 실제 전달 기록을 이용한 재개를 각각 관측했다. #11은 완전 격리가 아닌 실제 환경에서 문서가 유입된 제한부 결과다. #10에서 typed 검증은 다음 소스 조사 요청에서 완료됐고 최초 응답은 표시값의 한계를 충분히 밝히지 못했다. #12는 해당 기록의 사실과 미확인 사항을 유지하고 현재 상태를 다시 확인했다. 대상은 WSL2와 Windows 개발 후보 DART이며 공개 릴리스 설치본, 회사 Linux·네트워크, 실제 업무 데이터와 실행 바이너리의 원인은 검증하지 않았다.
