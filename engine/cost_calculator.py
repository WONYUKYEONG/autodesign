"""일위대가 → 예산 산출"""
from models.budget import BudgetSummary
from models.work_item import WorkItem


class CostCalculator:
    def calculate(self, work_items: list) -> BudgetSummary:
        summary = BudgetSummary()
        for item in work_items:
            summary.labor_cost += item.labor_cost
            summary.material_cost += item.material_cost
            summary.expense_cost += item.expense_cost
        return summary
