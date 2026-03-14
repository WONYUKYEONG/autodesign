"""메인 윈도우: 3분할 PanedWindow"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from gui.toolbar import Toolbar
from gui.canvas_view import CanvasView
from gui.property_panel import PropertyPanel
from gui.scenario_panel import ScenarioPanel
from gui.result_view import ResultView
from gui.dialogs.project_dialog import ProjectDialog
from gui.dialogs.unit_price_dialog import UnitPriceDialog
from export.excel_exporter import export_to_excel
from models import project as proj_model
from models.drawing_element import DrawingElement


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("통신선로 설계 및 예산 산출 프로그램")
        self.geometry("1400x850")
        self.minsize(1000, 600)

        self.current_project_id = None
        self.current_project_name = "새 프로젝트"

        self._create_menu()
        self._create_toolbar()
        self._create_main_area()
        self._create_statusbar()
        self._bind_shortcuts()

        self._update_status()

    def _create_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="새 프로젝트", command=self._new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="프로젝트 관리...", command=self._manage_projects)
        file_menu.add_separator()
        file_menu.add_command(label="저장", command=self._save_project, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="엑셀 출력", command=self._export_excel, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.quit)
        menubar.add_cascade(label="파일", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="전체 삭제", command=self._clear_canvas)
        menubar.add_cascade(label="편집", menu=edit_menu)

        data_menu = tk.Menu(menubar, tearoff=0)
        data_menu.add_command(label="일위대가 관리...", command=self._manage_unit_prices)
        menubar.add_cascade(label="데이터", menu=data_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="사용법", command=self._show_help)
        menubar.add_cascade(label="도움말", menu=help_menu)

        self.config(menu=menubar)

    def _create_toolbar(self):
        self.toolbar = Toolbar(self, on_tool_change=self._on_tool_change)
        self.toolbar.pack(fill=tk.X)

    def _create_main_area(self):
        # 3분할: 왼쪽(시나리오) | 중앙(캔버스) | 오른쪽(속성+결과)
        main_pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # 왼쪽: 시나리오 패널
        left_frame = tk.Frame(main_pane, width=200)
        self.result_view = ResultView(left_frame, on_export=self._do_export)
        # 시나리오 패널은 result_view 필요

        # 중앙: 캔버스
        self.canvas_view = CanvasView(main_pane, on_select=self._on_element_select)

        # 오른쪽: 속성 + 결과
        right_frame = tk.Frame(main_pane, width=350)

        self.property_panel = PropertyPanel(right_frame, on_update=self._on_property_update)
        self.property_panel.pack(fill=tk.X, padx=5, pady=5)

        self.result_view = ResultView(right_frame, on_export=self._do_export)
        self.result_view.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 시나리오 패널 (왼쪽)
        self.scenario_panel = ScenarioPanel(
            left_frame, self.canvas_view, self.result_view,
            on_status_update=self._on_status_update
        )
        self.scenario_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        main_pane.add(left_frame, minsize=180)
        main_pane.add(self.canvas_view, minsize=500)
        main_pane.add(right_frame, minsize=300)

    def _create_statusbar(self):
        self.statusbar = tk.Label(
            self, text="", bd=1, relief=tk.SUNKEN,
            anchor=tk.W, font=("맑은 고딕", 9), padx=10
        )
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)

    def _bind_shortcuts(self):
        self.bind("<Control-n>", lambda e: self._new_project())
        self.bind("<Control-s>", lambda e: self._save_project())
        self.bind("<Control-e>", lambda e: self._export_excel())
        self.bind("<Escape>", lambda e: self.toolbar.current_tool.set("select"))
        self.bind("<Delete>", lambda e: self._delete_selected())

    # --- 콜백 ---
    def _on_tool_change(self, tool):
        self.canvas_view.set_tool(tool)

    def _on_element_select(self, elem):
        self.property_panel.show_element(elem)
        self._update_status()

    def _on_property_update(self, elem):
        self.canvas_view.redraw()
        self._update_status()

    def _on_status_update(self, elem_count, total_budget):
        self._update_status(total_budget=total_budget)

    def _update_status(self, total_budget=None):
        count = self.canvas_view.get_element_count()
        budget_str = f" | 총 예산: {total_budget:,.0f}원" if total_budget else ""
        self.statusbar.config(
            text=f"프로젝트: {self.current_project_name} | "
                 f"요소 수: {count}{budget_str}"
        )

    # --- 프로젝트 ---
    def _new_project(self):
        if messagebox.askyesno("새 프로젝트", "현재 작업을 초기화하시겠습니까?"):
            self.canvas_view.clear_all()
            self.result_view.clear()
            self.current_project_id = None
            self.current_project_name = "새 프로젝트"
            self._update_status()

    def _manage_projects(self):
        ProjectDialog(self, on_load=self._load_project)

    def _load_project(self, project_id, name):
        self.current_project_id = project_id
        self.current_project_name = name
        self.canvas_view.clear_all()
        self.result_view.clear()

        rows = proj_model.load_elements(project_id)
        for row in rows:
            elem = DrawingElement.from_db_row(row)
            self.canvas_view.elements.append(elem)

        conns = proj_model.load_connections(project_id)
        for c in conns:
            self.canvas_view.connections.append(
                (c["from_element_id"], c["to_element_id"], c["connection_type"])
            )

        if self.canvas_view.elements:
            self.canvas_view._next_id = max(e.id for e in self.canvas_view.elements) + 1

        self.canvas_view.redraw()
        self._update_status()

    def _save_project(self):
        if not self.current_project_id:
            from tkinter import simpledialog
            name = simpledialog.askstring("저장", "프로젝트 이름:")
            if not name:
                return
            self.current_project_id = proj_model.create_project(name)
            self.current_project_name = name

        id_map = proj_model.save_elements(
            self.current_project_id, self.canvas_view.elements
        )
        proj_model.save_connections(
            self.current_project_id, self.canvas_view.connections, id_map
        )
        messagebox.showinfo("저장", "프로젝트가 저장되었습니다.")
        self._update_status()

    # --- 삭제 ---
    def _delete_selected(self):
        elem = self.canvas_view.selected_element
        if elem:
            self.canvas_view._handle_delete(elem.x, elem.y)

    def _clear_canvas(self):
        if messagebox.askyesno("전체 삭제", "모든 요소를 삭제하시겠습니까?"):
            self.canvas_view.clear_all()
            self.result_view.clear()
            self._update_status()

    # --- 엑셀 ---
    def _export_excel(self):
        if self.result_view.work_items:
            self._do_export(self.result_view.work_items, self.result_view.budget_summary)
        else:
            messagebox.showwarning("엑셀 출력", "시나리오를 먼저 실행하세요.")

    def _do_export(self, work_items, budget_summary):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel 파일", "*.xlsx")],
            initialfile=f"{self.current_project_name}_예산내역서.xlsx"
        )
        if not filepath:
            return
        try:
            export_to_excel(filepath, work_items, budget_summary, self.current_project_name)
            messagebox.showinfo("엑셀 출력", f"파일이 저장되었습니다:\n{filepath}")
        except Exception as e:
            messagebox.showerror("오류", f"엑셀 출력 실패:\n{e}")

    # --- 데이터 관리 ---
    def _manage_unit_prices(self):
        UnitPriceDialog(self)

    def _show_help(self):
        help_text = (
            "통신선로 설계 및 예산 산출 프로그램\n\n"
            "1. 도구바에서 요소를 선택하고 캔버스에 클릭하여 배치\n"
            "2. 케이블/인입선: 두 요소를 순서대로 클릭하여 연결\n"
            "3. 우클릭으로 요소 상태 변경 (기존/파손/신설/철거)\n"
            "4. 시나리오 패널에서 '파손 검색' → '시나리오 실행'\n"
            "5. 결과 확인 후 '엑셀 출력'\n\n"
            "단축키:\n"
            "  Ctrl+N: 새 프로젝트\n"
            "  Ctrl+S: 저장\n"
            "  Ctrl+E: 엑셀 출력\n"
            "  Delete: 선택 요소 삭제\n"
            "  ESC: 선택 모드로 전환"
        )
        messagebox.showinfo("사용법", help_text)
