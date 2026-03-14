"""시나리오 선택/실행 패널"""
import tkinter as tk
from tkinter import messagebox
from engine.scenario_builder import ScenarioBuilder
from engine.rule_engine import RuleEngine
from engine.cost_calculator import CostCalculator


class ScenarioPanel(tk.LabelFrame):
    def __init__(self, parent, canvas_view, result_view,
                 on_status_update=None, on_feedback=None):
        super().__init__(parent, text="시나리오", font=("맑은 고딕", 10, "bold"))
        self.canvas_view = canvas_view
        self.result_view = result_view
        self.on_status_update = on_status_update
        self.on_feedback = on_feedback

        self.rule_engine = RuleEngine()
        self.cost_calc = CostCalculator()

        info = tk.Label(self, text="파손 표시된 요소를\n자동 분석합니다",
                        font=("맑은 고딕", 9), justify=tk.LEFT)
        info.pack(padx=5, pady=5, anchor="w")

        # 파손 요소 목록
        self.damage_listbox = tk.Listbox(self, height=8, font=("맑은 고딕", 9))
        self.damage_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(btn_frame, text="파손 검색", command=self.scan_damaged,
                  font=("맑은 고딕", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="시나리오 실행", command=self.run_scenario,
                  font=("맑은 고딕", 9), bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=2)

        # AI 피드백 버튼 (초기 비활성)
        self.feedback_btn = tk.Button(
            btn_frame, text="피드백 전송", command=self._send_feedback,
            font=("맑은 고딕", 9), bg="#2196F3", fg="white",
            state=tk.DISABLED,
        )
        self.feedback_btn.pack(side=tk.LEFT, padx=2)

    def enable_feedback(self, enabled):
        """피드백 버튼 활성화/비활성화"""
        self.feedback_btn.config(state=tk.NORMAL if enabled else tk.DISABLED)

    def _send_feedback(self):
        """피드백 콜백 호출"""
        if self.on_feedback:
            self.on_feedback()

    def scan_damaged(self):
        self.damage_listbox.delete(0, tk.END)
        for elem in self.canvas_view.elements:
            if elem.status == "damaged":
                self.damage_listbox.insert(tk.END, f"{elem.display_name()} - 파손")

        count = self.damage_listbox.size()
        if count == 0:
            messagebox.showinfo("파손 검색", "파손된 요소가 없습니다.\n우클릭으로 상태를 '파손'으로 변경하세요.")

    def run_scenario(self):
        elements = self.canvas_view.elements
        connections = self.canvas_view.connections

        builder = ScenarioBuilder(elements, connections)
        events = builder.analyze_damaged_elements()

        if not events:
            messagebox.showinfo("시나리오", "파손된 요소가 없습니다.")
            return

        all_items = []
        self.rule_engine.load_rules()

        for trigger, context, elem in events:
            items = self.rule_engine.evaluate(trigger, context)
            all_items.extend(items)

        # 중복 병합
        merged = {}
        for item in all_items:
            key = (item.item_type, item.code)
            if key in merged:
                merged[key].merge(item)
            else:
                merged[key] = item
        all_items = list(merged.values())

        summary = self.cost_calc.calculate(all_items)

        self.result_view.show_results(all_items, summary)

        if self.on_status_update:
            self.on_status_update(len(elements), summary.grand_total)

        messagebox.showinfo(
            "시나리오 완료",
            f"작업 항목 {len(all_items)}건 생성\n"
            f"총 예산: {summary.grand_total:,.0f}원"
        )
