"""예산 모델"""
from dataclasses import dataclass, field
from config import (
    INDIRECT_LABOR_RATE, SAFETY_MGMT_RATE,
    GENERAL_MGMT_RATE, PROFIT_RATE, VAT_RATE
)


@dataclass
class BudgetSummary:
    labor_cost: int = 0         # 직접 노무비
    material_cost: int = 0      # 직접 재료비
    expense_cost: int = 0       # 직접 경비

    @property
    def direct_cost(self):
        return self.labor_cost + self.material_cost + self.expense_cost

    @property
    def indirect_labor(self):
        return int(self.labor_cost * INDIRECT_LABOR_RATE)

    @property
    def safety_management(self):
        return int((self.labor_cost + self.material_cost) * SAFETY_MGMT_RATE)

    @property
    def general_management(self):
        return int((self.labor_cost + self.expense_cost) * GENERAL_MGMT_RATE)

    @property
    def profit(self):
        return int((self.labor_cost + self.general_management) * PROFIT_RATE)

    @property
    def subtotal(self):
        return (self.direct_cost + self.indirect_labor +
                self.safety_management + self.general_management + self.profit)

    @property
    def vat(self):
        return int(self.subtotal * VAT_RATE)

    @property
    def grand_total(self):
        return self.subtotal + self.vat
