# Telecom Line Designer

통신선로 설계 자동화 도구 - 도면 기반 시나리오 분석, 자재/공종 자동 산출, 예산 계산 및 엑셀 출력

## 주요 기능

- **도면 캔버스 GUI** - 전주, 케이블, 단자함, 집, 인입선 등 통신선로 요소를 시각적으로 배치/편집
- **자동 규칙 엔진** - 이벤트큐 BFS 기반 연쇄 처리 (전주 철거 → 신설 → 부속자재 자동 산출)
- **예산 산출** - 일위대가 기반 직접비/간접비/이윤/부가세 자동 계산
- **엑셀 출력** - 총괄표, 내역서, 일위대가표 3개 시트 자동 생성

## 기술 스택

- **Python 3** + **Tkinter** (GUI)
- **SQLite** (데이터베이스)
- **openpyxl** (엑셀 출력)
- **pandas** (데이터 처리)

## 설치

```bash
pip install openpyxl pandas
```

## 프로젝트 구조

```
telecom_line_designer/
├── main.py                       # 진입점
├── config.py                     # DB 경로, 상수
├── db/
│   ├── database.py               # SQLite 연결 관리
│   ├── schema.sql                # DDL
│   └── seed_data.sql             # 초기 데이터 (자재, 공종, 일위대가, 규칙)
├── models/
│   ├── drawing_element.py        # 도면 요소 데이터클래스
│   ├── work_item.py              # 작업 항목 모델
│   ├── budget.py                 # 예산 모델
│   └── project.py                # 프로젝트 CRUD
├── engine/
│   ├── rule_engine.py            # 자동 규칙 엔진 (이벤트큐 BFS)
│   ├── cost_calculator.py        # 일위대가 → 예산 산출
│   └── scenario_builder.py       # 도면 분석 → 시나리오 액션 추출
├── gui/
│   ├── main_window.py            # 메인 윈도우
│   ├── toolbar.py                # 도구 모드 전환
│   ├── canvas_view.py            # 도면 캔버스
│   ├── canvas_items/             # 전주/케이블/단자함/집/인입선 렌더링
│   ├── property_panel.py         # 속성 편집 패널
│   ├── scenario_panel.py         # 시나리오 실행 UI
│   ├── result_view.py            # 작업 목록 + 금액 Treeview
│   └── dialogs/                  # 프로젝트/일위대가관리/엑셀출력 다이얼로그
└── export/
    └── excel_exporter.py         # 엑셀 출력 (총괄표/내역서/일위대가표)
```

## 데이터베이스 설계

SQLite 기반 핵심 테이블 10개로 구성 (자재, 공종, 일위대가, 규칙, 프로젝트 등)

## 규칙 엔진 동작 예시

```
POLE_DEMOLISH 이벤트 발생
  ├→ 전주 철거 1본
  ├→ 케이블 미절단? → 케이블 이설
  └→ POLE_INSTALL 이벤트 연쇄
      ├→ 전주 신설 1본
      ├→ 디딤쇠 6개
      ├→ 단자함 있음? → 단자 취부 → TERMINAL_ATTACH
      │                              └→ 고무링 4개소
      └→ 인입선 있음? → 인입선 설치 → DROPWIRE_INSTALL
                                       └→ 왕관밴드 1개
```

- BFS 이벤트큐로 연쇄 처리, processed set으로 무한루프 방지
- 규칙은 DB에 저장되므로 코드 수정 없이 추가/변경 가능

## GUI

- **도구 모드**: SELECT / POLE / CABLE / TERMINAL / HOUSE / DROPWIRE / DELETE
- **상태별 색상**: 기존(갈색), 파손(빨강), 신설(파랑), 철거(회색)

## 예산 산출 구조

| 항목 | 산출 기준 |
|------|-----------|
| 직접비 | 노무비 + 재료비 + 경비 |
| 간접노무비 | 노무비 x 12% |
| 안전관리비 | (노무비 + 재료비) x 3% |
| 일반관리비 | (노무비 + 경비) x 6% |
| 이윤 | (노무비 + 일반관리비) x 5% |
| 부가세 | 소계 x 10% |

## 엑셀 출력

1. **총괄표** - 직접비/간접비/이윤/부가세 총괄
2. **내역서** - 공종별 상세 항목 (번호/공종명/규격/단위/수량/재료비/노무비/경비/합계)
3. **일위대가표** - 각 공종의 단가 구성 내역
