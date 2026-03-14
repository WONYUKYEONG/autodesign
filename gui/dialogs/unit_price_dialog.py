"""일위대가 관리 다이얼로그"""
import tkinter as tk
from tkinter import ttk, messagebox
from db.database import fetch_all, execute_query


class UnitPriceDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("일위대가 관리")
        self.geometry("700x500")
        self.transient(parent)
        self.grab_set()

        # Treeview
        columns = ("code", "name", "unit", "labor", "material", "expense", "total")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)

        for col, text, w in [
            ("code", "코드", 70), ("name", "공종명", 120), ("unit", "단위", 50),
            ("labor", "노무비", 90), ("material", "재료비", 90),
            ("expense", "경비", 80), ("total", "합계", 100),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="e" if col in ("labor", "material", "expense", "total") else "center")

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 편집 영역
        edit_frame = tk.LabelFrame(self, text="단가 편집", font=("맑은 고딕", 9))
        edit_frame.pack(fill=tk.X, padx=10, pady=5)

        self._vars = {}
        for i, (key, label) in enumerate([
            ("labor", "노무비"), ("material", "재료비"), ("expense", "경비")
        ]):
            tk.Label(edit_frame, text=label, font=("맑은 고딕", 9)).grid(row=0, column=i*2, padx=5)
            var = tk.StringVar()
            tk.Entry(edit_frame, textvariable=var, width=12).grid(row=0, column=i*2+1, padx=5)
            self._vars[key] = var

        tk.Button(edit_frame, text="수정", command=self._update,
                  font=("맑은 고딕", 9)).grid(row=0, column=6, padx=10)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self._load()

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        rows = fetch_all(
            """SELECT wt.code, wt.name, wt.unit,
                      up.labor_cost, up.material_cost, up.expense_cost
               FROM work_types wt
               LEFT JOIN unit_prices up ON up.work_type_code = wt.code
               ORDER BY wt.code"""
        )
        for r in rows:
            labor = r["labor_cost"] or 0
            mat = r["material_cost"] or 0
            exp = r["expense_cost"] or 0
            self.tree.insert("", tk.END, values=(
                r["code"], r["name"], r["unit"],
                f"{labor:,}", f"{mat:,}", f"{exp:,}", f"{labor+mat+exp:,}"
            ))

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        self._vars["labor"].set(vals[3].replace(",", ""))
        self._vars["material"].set(vals[4].replace(",", ""))
        self._vars["expense"].set(vals[5].replace(",", ""))

    def _update(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("수정", "항목을 선택하세요.", parent=self)
            return
        vals = self.tree.item(sel[0], "values")
        code = vals[0]
        try:
            labor = int(self._vars["labor"].get())
            material = int(self._vars["material"].get())
            expense = int(self._vars["expense"].get())
        except ValueError:
            messagebox.showerror("오류", "숫자를 입력하세요.", parent=self)
            return

        execute_query(
            """UPDATE unit_prices SET labor_cost=?, material_cost=?, expense_cost=?
               WHERE work_type_code=?""",
            (labor, material, expense, code)
        )
        self._load()
        messagebox.showinfo("완료", "단가가 수정되었습니다.", parent=self)
