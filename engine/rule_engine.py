"""규칙 엔진: 이벤트큐 BFS 기반 자동 공종/자재 산출"""
import json
from collections import deque
from db.database import fetch_all
from models.work_item import WorkItem


class RuleEngine:
    def __init__(self):
        self.rules = []
        self.load_rules()

    def load_rules(self):
        self.rules = fetch_all(
            "SELECT * FROM scenario_rules ORDER BY trigger_event, priority"
        )

    def evaluate(self, trigger_event, context):
        """
        BFS 이벤트큐로 연쇄 규칙 처리.
        context: {
            'has_cable': True, 'cable_count': 2,
            'has_terminal': True, 'terminal_count': 1,
            'has_dropwire': True, 'dropwire_count': 3,
            'cable_length': 50, 'hanger_count': 5,
        }
        Returns: list[WorkItem]
        """
        work_items = []
        event_queue = deque()
        event_queue.append(trigger_event)
        processed = set()

        while event_queue:
            current_event = event_queue.popleft()
            event_key = current_event
            if event_key in processed:
                continue
            processed.add(event_key)

            matching_rules = [
                r for r in self.rules if r["trigger_event"] == current_event
            ]

            for rule in matching_rules:
                if not self._check_condition(rule["condition_json"], context):
                    continue

                quantity = self._eval_quantity(rule["quantity_expr"], context)

                if rule["action_type"] == "ADD_WORK":
                    item = self._create_work_item(rule["target_code"], quantity)
                    if item:
                        work_items.append(item)

                elif rule["action_type"] == "ADD_MATERIAL":
                    item = self._create_material_item(rule["target_code"], quantity)
                    if item:
                        work_items.append(item)

                elif rule["action_type"] == "FIRE_EVENT":
                    event_queue.append(rule["target_code"])

        return self._merge_items(work_items)

    def _check_condition(self, condition_json, context):
        if not condition_json:
            return True
        try:
            conditions = json.loads(condition_json)
            for key, value in conditions.items():
                if context.get(key) != value:
                    return False
            return True
        except (json.JSONDecodeError, TypeError):
            return True

    def _eval_quantity(self, expr, context):
        try:
            return float(expr)
        except ValueError:
            return float(context.get(expr, 1))

    def _create_work_item(self, work_code, quantity):
        row = fetch_all(
            """SELECT wt.code, wt.name, wt.unit, up.labor_cost, up.material_cost, up.expense_cost
               FROM work_types wt
               LEFT JOIN unit_prices up ON up.work_type_code = wt.code
               WHERE wt.code = ?""",
            (work_code,)
        )
        if not row:
            return None
        r = row[0]
        return WorkItem(
            item_type="work",
            code=r["code"],
            name=r["name"],
            unit=r["unit"],
            quantity=quantity,
            labor_cost=int(r["labor_cost"] * quantity),
            material_cost=int(r["material_cost"] * quantity),
            expense_cost=int(r["expense_cost"] * quantity),
        )

    def _create_material_item(self, mat_code, quantity):
        row = fetch_all(
            "SELECT * FROM materials WHERE code = ?", (mat_code,)
        )
        if not row:
            return None
        r = row[0]
        return WorkItem(
            item_type="material",
            code=r["code"],
            name=r["name"],
            spec=r.get("spec", ""),
            unit=r["unit"],
            quantity=quantity,
            material_cost=int(r["unit_price"] * quantity),
        )

    def _merge_items(self, items):
        merged = {}
        for item in items:
            key = (item.item_type, item.code)
            if key in merged:
                merged[key].merge(item)
            else:
                merged[key] = item
        return list(merged.values())
