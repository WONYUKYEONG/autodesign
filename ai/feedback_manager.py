"""AI 분석 결과의 피드백(수정사항) 관리"""
import json
from db.database import execute_query, fetch_all


class FeedbackManager:
    """AI 분석 이력 저장 및 수정사항 델타 계산"""

    def save_analysis(self, project_id, image_path, prompt_used,
                      raw_response, parsed_elements):
        """분석 결과를 DB에 저장하고 ID 반환"""
        return execute_query(
            """INSERT INTO ai_analysis_history
               (project_id, image_path, prompt_used, raw_response, parsed_elements_json)
               VALUES (?, ?, ?, ?, ?)""",
            (
                project_id,
                image_path,
                prompt_used,
                raw_response,
                json.dumps(parsed_elements, ensure_ascii=False),
            ),
        )

    def save_corrections(self, analysis_id, corrections):
        """사용자 수정사항을 DB에 저장"""
        execute_query(
            "UPDATE ai_analysis_history SET corrections_json = ? WHERE id = ?",
            (json.dumps(corrections, ensure_ascii=False), analysis_id),
        )

    def get_history(self, project_id):
        """프로젝트의 분석 이력 조회"""
        return fetch_all(
            "SELECT * FROM ai_analysis_history WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,),
        )

    def compute_delta(self, original_elements, current_elements):
        """원본 요소 목록과 현재 요소 목록의 차이를 계산

        Returns:
            str: 사람이 읽을 수 있는 수정 내용 설명
        """
        orig_map = {e.id: e for e in original_elements}
        curr_map = {e.id: e for e in current_elements}

        changes = []

        # 삭제된 요소
        for eid in set(orig_map) - set(curr_map):
            e = orig_map[eid]
            changes.append(f"- 삭제: {e.display_name()}")

        # 추가된 요소
        for eid in set(curr_map) - set(orig_map):
            e = curr_map[eid]
            changes.append(f"- 추가: {e.display_name()} ({e.status})")

        # 수정된 요소
        for eid in set(orig_map) & set(curr_map):
            orig = orig_map[eid]
            curr = curr_map[eid]
            diffs = []
            if orig.element_type != curr.element_type:
                diffs.append(f"타입: {orig.element_type}→{curr.element_type}")
            if orig.label != curr.label:
                diffs.append(f"이름: {orig.label}→{curr.label}")
            if orig.status != curr.status:
                diffs.append(f"상태: {orig.status}→{curr.status}")
            if abs(orig.x - curr.x) > 20 or abs(orig.y - curr.y) > 20:
                diffs.append("위치 이동")
            if diffs:
                changes.append(f"- 수정: {curr.display_name()} ({', '.join(diffs)})")

        if not changes:
            return "수정 사항 없음"
        return "\n".join(changes)
