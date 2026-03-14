"""작업 목록 + 금액 표시"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from models.budget import BudgetSummary


class ResultView(tk.LabelFrame):
    def __init__(self, parent, on_export=None):
        super().__init__(parent, text="작업 내역", font=("맑은 고딕", 10, "bold"))
        self.on_export = on_export
        self.work_items = []
        self.budget_summary = None

        # Treeview
        columns = ("type", "name", "spec", "unit", "qty",
                   "labor", "material", "expense", "total")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)

        headers = [
            ("type", "구분", 50), ("name", "공종/자재명", 120),
            ("spec", "규격", 80), ("unit", "단위", 40),
            ("qty", "수량", 50), ("labor", "노무비", 80),
            ("material", "재료비", 80), ("expense", "경비", 70),
            ("total", "합계", 90),
        ]
        for col, text, width in headers:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="e" if col not in ("type", "name", "spec", "unit") else "center")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, pady=5)

        # 하단 요약 + 버튼
        bottom = tk.Frame(self)
        bottom.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)

        self.summary_text = tk.Text(bottom, height=8, font=("맑은 고딕", 9),
                                     state=tk.DISABLED, bg="#f5f5f5")
        self.summary_text.pack(fill=tk.X, pady=(0, 5))

        tk.Button(bottom, text="엑셀 출력", command=self._export_excel,
                  font=("맑은 고딕", 10, "bold"), bg="#2196F3", fg="white",
                  width=12).pack()

    def show_results(self, work_items, budget_summary):
        self.work_items = work_items
        self.budget_summary = budget_summary

        self.tree.delete(*self.tree.get_children())
        for item in work_items:
            type_label = "공종" if item.item_type == "work" else "자재"
            self.tree.insert("", tk.END, values=(
                type_label, item.name, item.spec, item.unit,
                f"{item.quantity:.1f}",
                f"{item.labor_cost:,}", f"{item.material_cost:,}",
                f"{item.expense_cost:,}", f"{item.total_cost:,}",
            ))

        self._show_summary(budget_summary)

    def _show_summary(self, s):
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete("1.0", tk.END)
        lines = [
            f"■ 직접비 합계: {s.direct_cost:>15,}원",
            f"  - 노무비:    {s.labor_cost:>15,}원",
            f"  - 재료비:    {s.material_cost:>15,}원",
            f"  - 경비:      {s.expense_cost:>15,}원",
            f"■ 간접노무비:  {s.indirect_labor:>15,}원",
            f"■ 안전관리비:  {s.safety_management:>15,}원",
            f"■ 일반관리비:  {s.general_management:>15,}원",
            f"■ 이윤:        {s.profit:>15,}원",
            f"■ 소계:        {s.subtotal:>15,}원",
            f"■ 부가세(10%): {s.vat:>15,}원",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"■ 총 예산:     {s.grand_total:>15,}원",
        ]
        self.summary_text.insert("1.0", "\n".join(lines))
        self.summary_text.config(state=tk.DISABLED)

    def _export_excel(self):
        if not self.work_items:
            messagebox.showwarning("엑셀 출력", "작업 내역이 없습니다.\n시나리오를 먼저 실행하세요.")
            return
        if self.on_export:
            self.on_export(self.work_items, self.budget_summary)

    def clear(self):
        self.tree.delete(*self.tree.get_children())
        self.work_items = []
        self.budget_summary = None
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.config(state=tk.DISABLED)
