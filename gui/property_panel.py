"""선택 요소 속성 편집 패널"""
import tkinter as tk
from tkinter import ttk


class PropertyPanel(tk.LabelFrame):
    def __init__(self, parent, on_update=None):
        super().__init__(parent, text="속성 패널", font=("맑은 고딕", 10, "bold"))
        self.on_update = on_update
        self.current_element = None

        self._widgets = {}
        self._create_widgets()
        self.show_empty()

    def _create_widgets(self):
        row = 0
        fields = [
            ("type_label", "유형:", None),
            ("id_label", "ID:", None),
            ("label_entry", "라벨:", "entry"),
            ("status_combo", "상태:", "combo"),
            ("length_entry", "길이(m):", "entry"),
        ]
        for key, text, widget_type in fields:
            tk.Label(self, text=text, font=("맑은 고딕", 9)).grid(
                row=row, column=0, sticky="w", padx=5, pady=2
            )
            if widget_type == "entry":
                var = tk.StringVar()
                w = tk.Entry(self, textvariable=var, width=15, font=("맑은 고딕", 9))
                w.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
                self._widgets[key] = (w, var)
            elif widget_type == "combo":
                var = tk.StringVar()
                w = ttk.Combobox(self, textvariable=var, width=12,
                                 values=["existing", "damaged", "new", "demolish"],
                                 state="readonly")
                w.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
                self._widgets[key] = (w, var)
            else:
                var = tk.StringVar()
                w = tk.Label(self, textvariable=var, font=("맑은 고딕", 9),
                             anchor="w")
                w.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
                self._widgets[key] = (w, var)
            row += 1

        btn = tk.Button(self, text="적용", command=self._apply,
                        font=("맑은 고딕", 9))
        btn.grid(row=row, column=0, columnspan=2, pady=8)
        self._apply_btn = btn

        self.columnconfigure(1, weight=1)

    def show_element(self, elem):
        self.current_element = elem
        if not elem:
            self.show_empty()
            return

        type_names = {
            "pole": "전주", "cable": "케이블", "terminal": "단자함",
            "house": "집", "dropwire": "인입선",
        }
        self._widgets["type_label"][1].set(type_names.get(elem.element_type, elem.element_type))
        self._widgets["id_label"][1].set(str(elem.id))
        self._widgets["label_entry"][1].set(elem.label)
        self._widgets["status_combo"][1].set(elem.status)

        length = elem.properties.get("length", "")
        self._widgets["length_entry"][1].set(str(length))

        # 길이 필드는 케이블/인입선에만 표시
        if elem.element_type in ("cable", "dropwire"):
            self._widgets["length_entry"][0].grid()
        else:
            self._widgets["length_entry"][0].grid()

        self._apply_btn.config(state="normal")

    def show_empty(self):
        self.current_element = None
        for key, (w, var) in self._widgets.items():
            var.set("")
        self._apply_btn.config(state="disabled")

    def _apply(self):
        elem = self.current_element
        if not elem:
            return
        elem.label = self._widgets["label_entry"][1].get()
        elem.status = self._widgets["status_combo"][1].get()

        length_str = self._widgets["length_entry"][1].get()
        if length_str:
            try:
                elem.properties["length"] = float(length_str)
            except ValueError:
                pass

        if self.on_update:
            self.on_update(elem)
