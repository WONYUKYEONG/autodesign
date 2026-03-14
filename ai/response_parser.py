"""AI 응답 JSON을 DrawingElement 및 연결 정보로 변환"""
from config import CANVAS_WIDTH, CANVAS_HEIGHT, GRID_SIZE
from models.drawing_element import DrawingElement


class ResponseParser:
    """AI 응답을 캔버스 요소로 변환"""

    # 캔버스 영역 (여백 확보)
    MARGIN = 60
    DRAW_WIDTH = CANVAS_WIDTH - 2 * MARGIN
    DRAW_HEIGHT = CANVAS_HEIGHT - 2 * MARGIN

    def __init__(self, start_id=1):
        self.start_id = start_id

    def _snap(self, v):
        return round(v / GRID_SIZE) * GRID_SIZE

    def _to_canvas_coords(self, rel_x, rel_y):
        """상대 좌표(0~1)를 캔버스 좌표로 변환"""
        x = self.MARGIN + rel_x * self.DRAW_WIDTH
        y = self.MARGIN + rel_y * self.DRAW_HEIGHT
        return self._snap(x), self._snap(y)

    def parse_response(self, api_response, start_id=None):
        """API 응답 dict를 (elements, connections) 튜플로 변환

        Args:
            api_response: AI가 반환한 JSON dict
            start_id: 요소 ID 시작 번호 (None이면 self.start_id 사용)

        Returns:
            (list[DrawingElement], list[tuple(from_id, to_id, conn_type)])
        """
        if start_id is not None:
            self.start_id = start_id

        raw_elements = api_response.get("elements", [])
        raw_connections = api_response.get("connections", [])

        # temp_id → 정수 ID 매핑
        id_map = {}
        elements = []
        current_id = self.start_id

        for raw in raw_elements:
            temp_id = raw.get("temp_id", f"E{current_id}")
            element_type = raw.get("element_type", "pole")

            # 유효한 타입인지 확인
            if element_type not in ("pole", "cable", "terminal", "house", "dropwire"):
                element_type = "pole"

            rel_x = float(raw.get("relative_x", 0.5))
            rel_y = float(raw.get("relative_y", 0.5))
            x, y = self._to_canvas_coords(rel_x, rel_y)

            status = raw.get("status", "existing")
            if status not in ("existing", "damaged", "new", "demolish"):
                status = "existing"

            properties = raw.get("properties", {})
            label = raw.get("label", f"{current_id}")

            elem = DrawingElement(
                id=current_id,
                element_type=element_type,
                label=label,
                x=x,
                y=y,
                status=status,
                properties=properties,
            )
            elements.append(elem)
            id_map[temp_id] = current_id
            current_id += 1

        # 연결 변환
        connections = []
        for raw_conn in raw_connections:
            from_temp = raw_conn.get("from_id", "")
            to_temp = raw_conn.get("to_id", "")
            conn_type = raw_conn.get("connection_type", "cable")
            if conn_type not in ("cable", "dropwire"):
                conn_type = "cable"

            from_id = id_map.get(from_temp)
            to_id = id_map.get(to_temp)
            if from_id is not None and to_id is not None:
                connections.append((from_id, to_id, conn_type))

        return elements, connections
