"""작업 항목 모델"""
from dataclasses import dataclass


@dataclass
class WorkItem:
    item_type: str = "work"     # work / material
    code: str = ""
    name: str = ""
    spec: str = ""
    unit: str = ""
    quantity: float = 0.0
    unit_cost: int = 0
    labor_cost: int = 0
    material_cost: int = 0
    expense_cost: int = 0

    @property
    def total_cost(self):
        return self.labor_cost + self.material_cost + self.expense_cost

    def merge(self, other):
        """같은 코드의 항목을 수량 합산"""
        if self.code == other.code and self.item_type == other.item_type:
            self.quantity += other.quantity
            self.labor_cost += other.labor_cost
            self.material_cost += other.material_cost
            self.expense_cost += other.expense_cost
