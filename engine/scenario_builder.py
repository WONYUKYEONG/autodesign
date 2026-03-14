"""도면 분석 → 시나리오 액션 추출"""


class ScenarioBuilder:
    def __init__(self, elements, connections):
        """
        elements: list[DrawingElement]
        connections: list[(from_id, to_id, type)]
        """
        self.elements = {e.id: e for e in elements}
        self.connections = connections
        self._adjacency = {}
        self._build_adjacency()

    def _build_adjacency(self):
        for from_id, to_id, conn_type in self.connections:
            self._adjacency.setdefault(from_id, []).append((to_id, conn_type))
            self._adjacency.setdefault(to_id, []).append((from_id, conn_type))

    def get_connected(self, element_id, element_type=None, conn_type_filter=None):
        """특정 요소에 연결된 요소 목록 반환"""
        result = []
        for neighbor_id, conn_type in self._adjacency.get(element_id, []):
            if conn_type_filter and conn_type != conn_type_filter:
                continue
            elem = self.elements.get(neighbor_id)
            if elem and (element_type is None or elem.element_type == element_type):
                result.append(elem)
        return result

    def get_connections_by_type(self, element_id, conn_type_filter):
        """특정 연결 타입의 연결 수 반환"""
        return [
            (nid, ct) for nid, ct in self._adjacency.get(element_id, [])
            if ct == conn_type_filter
        ]

    def build_context_for_pole(self, pole_element):
        """전주 관련 컨텍스트 생성"""
        # 케이블: 연결 타입이 cable인 것 (상대방이 전주든 다른 요소든)
        cable_conns = self.get_connections_by_type(pole_element.id, "cable")
        terminals = self.get_connected(pole_element.id, "terminal")
        # 인입선: 연결 타입이 dropwire인 것
        dropwire_conns = self.get_connections_by_type(pole_element.id, "dropwire")
        # terminal도 cable 타입 연결로 붙을 수 있으니 element_type으로도 탐색
        terminals += self.get_connected(pole_element.id, "terminal", conn_type_filter="cable")

        # 중복 제거
        seen_terminal_ids = set()
        unique_terminals = []
        for t in terminals:
            if t.id not in seen_terminal_ids:
                seen_terminal_ids.add(t.id)
                unique_terminals.append(t)
        terminals = unique_terminals

        return {
            "has_cable": len(cable_conns) > 0,
            "cable_count": len(cable_conns),
            "has_terminal": len(terminals) > 0,
            "terminal_count": len(terminals),
            "has_dropwire": len(dropwire_conns) > 0,
            "dropwire_count": len(dropwire_conns),
            "cable_length": 50 * len(cable_conns),
            "hanger_count": 5 * len(cable_conns),
        }

    def analyze_damaged_elements(self):
        """파손 표시된 요소에 대해 (trigger_event, context) 리스트 반환"""
        events = []
        for elem in self.elements.values():
            if elem.status != "damaged":
                continue
            if elem.element_type == "pole":
                ctx = self.build_context_for_pole(elem)
                events.append(("POLE_DEMOLISH", ctx, elem))
            elif elem.element_type == "cable":
                events.append(("CABLE_INSTALL", {
                    "cable_length": float(elem.properties.get("length", 50)),
                    "hanger_count": int(float(elem.properties.get("length", 50)) / 10),
                }, elem))
        return events
