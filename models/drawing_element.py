"""도면 요소 데이터클래스"""
from dataclasses import dataclass, field
import json


@dataclass
class DrawingElement:
    id: int = 0
    project_id: int = 0
    element_type: str = "pole"      # pole/cable/terminal/house/dropwire
    label: str = ""
    x: float = 0.0
    y: float = 0.0
    status: str = "existing"        # existing/damaged/new/demolish
    properties: dict = field(default_factory=dict)
    # 런타임 전용 (DB 미저장)
    canvas_id: int = 0              # tkinter 캔버스 아이템 ID
    connected_ids: list = field(default_factory=list)

    @property
    def properties_json(self):
        return json.dumps(self.properties, ensure_ascii=False)

    @classmethod
    def from_db_row(cls, row):
        props = json.loads(row.get("properties_json", "{}") or "{}")
        return cls(
            id=row["id"],
            project_id=row["project_id"],
            element_type=row["element_type"],
            label=row.get("label", ""),
            x=row["x"],
            y=row["y"],
            status=row["status"],
            properties=props,
        )

    def display_name(self):
        type_names = {
            "pole": "전주",
            "cable": "케이블",
            "terminal": "단자함",
            "house": "집",
            "dropwire": "인입선",
        }
        name = type_names.get(self.element_type, self.element_type)
        if self.label:
            return f"{name}({self.label})"
        return f"{name}#{self.id}"
