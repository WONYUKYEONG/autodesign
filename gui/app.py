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
from gui.dialogs.api_key_dialog import ApiKeyDialog
from gui.dialogs.image_analysis_dialog import ImageAnalysisDialog
from export.excel_exporter import export_to_excel, export_ai_analysis
from models import project as proj_model
from models.drawing_element import DrawingElement
from ai.vision_analyzer import VisionAnalyzer
from ai.response_parser import ResponseParser
from ai.feedback_manager import FeedbackManager
import config


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("통신선로 설계 및 예산 산출 프로그램")
        self.geometry("1400x850")
        self.minsize(1000, 600)

        self.current_project_id = None
        self.current_project_name = "새 프로젝트"

        # AI 모듈 초기화
        self.vision_analyzer = VisionAnalyzer()
        self.response_parser = ResponseParser()
        self.feedback_manager = FeedbackManager()
        self._last_analysis_result = None
        self._last_analysis_image = None
        self._last_analysis_id = None
        self._ai_placed_elements = []  # AI가 배치한 원본 요소 (피드백용)

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

        ai_menu = tk.Menu(menubar, tearoff=0)
        ai_menu.add_command(label="사진 분석...", command=self._analyze_image, accelerator="Ctrl+I")
        ai_menu.add_command(label="분석 결과 엑셀 출력", command=self._export_ai_excel, accelerator="Ctrl+Shift+E")
        ai_menu.add_separator()
        ai_menu.add_command(label="API 키 설정...", command=self._setup_api_key)
        menubar.add_cascade(label="AI 분석", menu=ai_menu)

        data_menu = tk.Menu(menubar, tearoff=0)
        data_menu.add_command(label="일위대가 관리...", command=self._manage_unit_prices)
        menubar.add_cascade(label="데이터", menu=data_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="사용법", command=self._show_help)
        menubar.add_cascade(label="도움말", menu=help_menu)

        self.config(menu=menubar)

    def _create_toolbar(self):
        self.toolbar = Toolbar(self, on_tool_change=self._on_tool_change,
                               on_analyze=self._analyze_image)
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
            on_status_update=self._on_status_update,
            on_feedback=self._send_feedback,
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
        self.bind("<Control-i>", lambda e: self._analyze_image())
        self.bind("<Control-Shift-E>", lambda e: self._export_ai_excel())
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
        # 시나리오 결과가 있으면 예산 엑셀, 없으면 AI 분석 엑셀
        if self.result_view.work_items:
            self._do_export(self.result_view.work_items, self.result_view.budget_summary)
        elif self.canvas_view.elements:
            self._export_ai_excel()
        else:
            messagebox.showwarning("엑셀 출력", "캔버스에 요소가 없습니다.")

    def _export_ai_excel(self):
        """AI 분석 결과를 엑셀로 출력"""
        if not self.canvas_view.elements:
            messagebox.showwarning("엑셀 출력", "캔버스에 요소가 없습니다.\n사진 분석을 먼저 실행하세요.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel 파일", "*.xlsx")],
            initialfile=f"{self.current_project_name}_도면분석.xlsx"
        )
        if not filepath:
            return
        try:
            export_ai_analysis(
                filepath,
                elements=self.canvas_view.elements,
                connections=self.canvas_view.connections,
                ai_response=self._last_analysis_result,
                project_name=self.current_project_name,
            )
            messagebox.showinfo("엑셀 출력", f"AI 분석 결과가 저장되었습니다:\n{filepath}")
        except Exception as e:
            messagebox.showerror("오류", f"엑셀 출력 실패:\n{e}")

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

    # --- AI 분석 ---
    def _analyze_image(self):
        """사진 분석 워크플로우 시작"""
        if not config.ANTHROPIC_API_KEY:
            if messagebox.askyesno(
                "API 키 필요",
                "AI 분석을 사용하려면 Anthropic API 키가 필요합니다.\n"
                "지금 설정하시겠습니까?"
            ):
                self._setup_api_key()
            return

        self.vision_analyzer.set_api_key(config.ANTHROPIC_API_KEY)

        # 현재 캔버스 요소 수를 기반으로 ID 시작점 결정
        start_id = self.canvas_view._next_id

        ImageAnalysisDialog(
            self,
            analyzer=self.vision_analyzer,
            parser=self.response_parser,
            on_apply=lambda result, raw, path: self._apply_ai_results(result, raw, path, start_id),
        )

    def _setup_api_key(self):
        """API 키 설정 다이얼로그"""
        ApiKeyDialog(self, on_save=self._on_api_key_saved)

    def _on_api_key_saved(self, key):
        self.vision_analyzer.set_api_key(key)

    def _apply_ai_results(self, analysis_result, raw_response, image_path, start_id):
        """AI 분석 결과를 캔버스에 적용하고 시나리오를 자동 실행"""
        import copy

        elements, connections = self.response_parser.parse_response(
            analysis_result, start_id=start_id
        )

        if not elements:
            messagebox.showwarning("AI 분석", "인식된 요소가 없습니다.")
            return

        # 캔버스에 요소 추가
        for elem in elements:
            self.canvas_view.elements.append(elem)
        for conn in connections:
            self.canvas_view.connections.append(conn)

        # next_id 갱신
        max_id = max(e.id for e in self.canvas_view.elements)
        self.canvas_view._next_id = max_id + 1

        self.canvas_view.redraw()

        # AI 배치 원본 저장 (피드백용)
        self._ai_placed_elements = [copy.deepcopy(e) for e in elements]
        self._last_analysis_result = analysis_result
        self._last_analysis_image = image_path

        # DB에 분석 이력 저장
        self._last_analysis_id = self.feedback_manager.save_analysis(
            project_id=self.current_project_id,
            image_path=image_path,
            prompt_used="DRAWING_ANALYSIS_PROMPT",
            raw_response=raw_response,
            parsed_elements=analysis_result,
        )

        # 시나리오 패널에 피드백 기능 활성화
        self.scenario_panel.enable_feedback(True)

        self._update_status()

        # 자동 시나리오 실행 여부 확인
        damaged_count = sum(1 for e in elements if e.status == "damaged")
        if damaged_count > 0:
            if messagebox.askyesno(
                "AI 분석 완료",
                f"요소 {len(elements)}개, 연결 {len(connections)}개가 배치되었습니다.\n"
                f"파손 요소 {damaged_count}개 감지.\n\n"
                "시나리오를 자동 실행하시겠습니까?"
            ):
                self.scenario_panel.run_scenario()
        else:
            if messagebox.askyesno(
                "AI 분석 완료",
                f"요소 {len(elements)}개, 연결 {len(connections)}개가 캔버스에 배치되었습니다.\n\n"
                "엑셀로 출력하시겠습니까?"
            ):
                self._export_ai_excel()

    def _send_feedback(self):
        """사용자 수정사항을 AI에 피드백하여 재분석"""
        if not self._last_analysis_result or not self._last_analysis_image:
            messagebox.showwarning("피드백", "이전 AI 분석 결과가 없습니다.")
            return

        # 델타 계산
        corrections = self.feedback_manager.compute_delta(
            self._ai_placed_elements,
            self.canvas_view.elements,
        )

        if corrections == "수정 사항 없음":
            messagebox.showinfo("피드백", "수정된 내용이 없습니다.")
            return

        # DB에 수정사항 저장
        if self._last_analysis_id:
            self.feedback_manager.save_corrections(self._last_analysis_id, corrections)

        if messagebox.askyesno(
            "피드백 전송",
            f"다음 수정사항을 반영하여 재분석하시겠습니까?\n\n{corrections}"
        ):
            # 재분석 다이얼로그 열기
            self._reanalyze_with_feedback(corrections)

    def _reanalyze_with_feedback(self, corrections):
        """수정사항을 반영하여 재분석"""
        import threading

        def do_reanalysis():
            try:
                result, raw = self.vision_analyzer.analyze_with_corrections(
                    self._last_analysis_image,
                    self._last_analysis_result,
                    corrections,
                )
                self.after(0, lambda: self._on_reanalysis_done(result, raw))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("재분석 실패", str(e)))

        messagebox.showinfo("재분석", "AI에 피드백을 전송하고 재분석을 시작합니다.\n완료되면 알려드립니다.")
        threading.Thread(target=do_reanalysis, daemon=True).start()

    def _on_reanalysis_done(self, result, raw):
        """재분석 완료 처리"""
        if messagebox.askyesno(
            "재분석 완료",
            "재분석이 완료되었습니다.\n기존 요소를 지우고 새 결과를 적용하시겠습니까?"
        ):
            self.canvas_view.clear_all()
            self.result_view.clear()
            start_id = 1
            self._apply_ai_results(result, raw, self._last_analysis_image, start_id)

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
            "  Ctrl+I: AI 사진 분석\n"
            "  Delete: 선택 요소 삭제\n"
            "  ESC: 선택 모드로 전환"
        )
        messagebox.showinfo("사용법", help_text)
