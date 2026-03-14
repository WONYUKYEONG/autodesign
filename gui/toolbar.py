"""도구모음 바"""
import tkinter as tk
from tkinter import ttk


class Toolbar(tk.Frame):
    TOOLS = [
        ("select", "선택", "arrow"),
        ("pole", "전주", "circle"),
        ("cable", "케이블", "tcross"),
        ("terminal", "단자함", "plus"),
        ("house", "집", "dotbox"),
        ("dropwire", "인입선", "right_side"),
        ("delete", "삭제", "X_cursor"),
    ]

    def __init__(self, parent, on_tool_change=None, on_analyze=None):
        super().__init__(parent, bd=1, relief=tk.RAISED)
        self.current_tool = tk.StringVar(value="select")
        self.on_tool_change = on_tool_change

        for tool_id, label, cursor in self.TOOLS:
            btn = tk.Radiobutton(
                self, text=label, variable=self.current_tool,
                value=tool_id, indicatoron=False,
                width=8, height=1,
                font=("맑은 고딕", 10),
                command=lambda t=tool_id: self._tool_changed(t),
            )
            btn.pack(side=tk.LEFT, padx=2, pady=2)

        # 구분선
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=2)

        # AI 사진 분석 버튼
        self.analyze_btn = tk.Button(
            self, text="📷 사진 분석", command=on_analyze,
            font=("맑은 고딕", 10, "bold"), bg="#FF8C00", fg="white",
            relief=tk.RAISED, padx=8,
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=4, pady=2)

    def _tool_changed(self, tool_id):
        if self.on_tool_change:
            self.on_tool_change(tool_id)

    def get_cursor(self):
        for tool_id, label, cursor in self.TOOLS:
            if tool_id == self.current_tool.get():
                return cursor
        return "arrow"
