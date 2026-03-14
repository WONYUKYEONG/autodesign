"""도면 분석 전용 프롬프트 템플릿"""

DRAWING_ANALYSIS_PROMPT = """당신은 한국 통신선로 현장 도면을 분석하는 전문가입니다.
첨부된 이미지는 통신선로 설계 도면(현장 사진 또는 CAD 도면)입니다.

## 인식해야 할 요소
- **전주(pole)**: 원형 또는 사각형 기호, 번호가 표기됨 (예: "신태봉 직2", "SF019")
- **케이블(cable)**: 전주 사이를 연결하는 선, 규격이 표기됨 (예: "C38 8C", "22C")
- **단자함(terminal)**: 전주에 부착된 사각형 기호, "단자함" 또는 "T" 표기
- **집/건물(house)**: 건물 기호, 가입자 정보가 표기될 수 있음
- **인입선(dropwire)**: 전주에서 건물로 연결되는 가는 선

## 상태 판별 기준
- **기존(existing)**: 검정/갈색으로 표기된 요소
- **파손(damaged)**: 빨간색 X 또는 "파손" 표기
- **신설(new)**: 파란색 또는 "신설" 표기
- **철거(demolish)**: 회색 또는 취소선, "철거" 표기

## 빨간 글씨/표시 해석
빨간색 글씨나 표시는 **작업 지시**를 의미합니다:
- "철거", "제거" → 해당 요소를 demolish 상태로
- "신설", "설치" → 새 요소를 new 상태로
- "접속", "변경" → 관련 작업 기록

## 좌표 규칙
- relative_x, relative_y: 이미지 내 위치를 0.0~1.0 비율로 표현
  - (0.0, 0.0) = 이미지 왼쪽 상단
  - (1.0, 1.0) = 이미지 오른쪽 하단

## 출력 형식
반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트 없이 JSON만 출력합니다.

```json
{
  "elements": [
    {
      "temp_id": "E1",
      "element_type": "pole|cable|terminal|house|dropwire",
      "label": "요소 이름/번호",
      "status": "existing|damaged|new|demolish",
      "relative_x": 0.0,
      "relative_y": 0.0,
      "properties": {
        "spec": "규격 정보(있는 경우)"
      }
    }
  ],
  "connections": [
    {
      "from_id": "E1",
      "to_id": "E2",
      "connection_type": "cable|dropwire",
      "label": "케이블 규격"
    }
  ],
  "work_annotations": [
    {
      "description": "작업 내용 설명",
      "related_elements": ["E1", "E2"],
      "work_type": "install|demolish|replace|splice"
    }
  ]
}
```

도면에서 인식 가능한 모든 요소를 빠짐없이 추출하세요."""


CORRECTION_PROMPT_TEMPLATE = """이전에 이 도면을 분석한 결과에 대해 사용자가 수정 사항을 제출했습니다.

## 이전 분석 결과
```json
{original_response}
```

## 사용자 수정 내용
{corrections}

위 수정 사항을 반영하여 도면을 다시 분석하세요.
동일한 JSON 형식으로 개선된 결과를 출력하세요."""
