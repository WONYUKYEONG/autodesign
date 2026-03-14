"""이미지 분석 다이얼로그: 업로드 → 미리보기 → AI 분석 → 결과 적용"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from PIL import Image, ImageTk


class ImageAnalysisDialog(tk.Toplevel):
    """도면 이미지를 업로드하고 AI 분석 결과를 적용하는 다이얼로그"""

    def __init__(self, parent, analyzer, parser, on_apply=None):
        super().__init__(parent)
        self.title("AI 도면 분석")
        self.geometry("650x580")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.analyzer = analyzer
        self.parser = parser
        self.on_apply = on_apply

        self.image_path = None
        self.analysis_result = None  # 파싱된 dict
        self.raw_response = None     # 원본 텍스트
        self._photo_ref = None       # ImageTk 참조 유지

        self._create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _create_widgets(self):
        main = tk.Frame(self, padx=15, pady=10)
        main.pack(fill=tk.BOTH, expand=True)

        # --- 이미지 선택 ---
        select_frame = tk.LabelFrame(main, text="도면 이미지", font=("맑은 고딕", 10, "bold"))
        select_frame.pack(fill=tk.X, pady=(0, 8))

        btn_row = tk.Frame(select_frame)
        btn_row.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(
            btn_row, text="이미지 선택...", command=self._select_image,
            font=("맑은 고딕", 9)
        ).pack(side=tk.LEFT)

        self.path_label = tk.Label(
            btn_row, text="선택된 파일 없음", font=("맑은 고딕", 9),
            fg="gray", anchor="w"
        )
        self.path_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # 미리보기 캔버스
        self.preview_canvas = tk.Canvas(
            select_frame, width=600, height=250,
            bg="#f5f5f5", relief=tk.SUNKEN, bd=1
        )
        self.preview_canvas.pack(padx=10, pady=(0, 10))

        # --- 분석 제어 ---
        ctrl_frame = tk.Frame(main)
        ctrl_frame.pack(fill=tk.X, pady=5)

        self.analyze_btn = tk.Button(
            ctrl_frame, text="분석 시작", command=self._start_analysis,
            font=("맑은 고딕", 10, "bold"), bg="#FF8C00", fg="white",
            width=15, height=1, state=tk.DISABLED
        )
        self.analyze_btn.pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(ctrl_frame, mode="indeterminate", length=200)
        self.progress.pack(side=tk.LEFT, padx=15)

        self.status_label = tk.Label(
            ctrl_frame, text="", font=("맑은 고딕", 9)
        )
        self.status_label.pack(side=tk.LEFT)

        # --- 결과 ---
        result_frame = tk.LabelFrame(main, text="분석 결과", font=("맑은 고딕", 10, "bold"))
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        self.result_text = tk.Text(
            result_frame, height=8, font=("맑은 고딕", 9),
            state=tk.DISABLED, wrap=tk.WORD
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 적용 버튼
        bottom = tk.Frame(main)
        bottom.pack(fill=tk.X, pady=(8, 0))

        self.apply_btn = tk.Button(
            bottom, text="캔버스에 적용", command=self._apply_results,
            font=("맑은 고딕", 10, "bold"), bg="#4CAF50", fg="white",
            width=15, state=tk.DISABLED
        )
        self.apply_btn.pack(side=tk.RIGHT)

        tk.Button(
            bottom, text="닫기", command=self.destroy,
            font=("맑은 고딕", 9), width=8
        ).pack(side=tk.RIGHT, padx=10)

    def _select_image(self):
        path = filedialog.askopenfilename(
            title="도면 이미지 선택",
            filetypes=[
                ("이미지 파일", "*.jpg *.jpeg *.png *.gif *.webp"),
                ("모든 파일", "*.*"),
            ],
        )
        if not path:
            return

        self.image_path = path
        self.path_label.config(text=os.path.basename(path), fg="black")
        self.analyze_btn.config(state=tk.NORMAL)
        self._show_preview(path)

    def _show_preview(self, path):
        try:
            img = Image.open(path)
            # 캔버스 크기에 맞게 리사이즈
            cw, ch = 600, 250
            img.thumbnail((cw, ch), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._photo_ref = photo

            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(
                cw // 2, ch // 2, image=photo, anchor=tk.CENTER
            )
        except Exception as e:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(
                300, 125, text=f"미리보기 실패: {e}",
                font=("맑은 고딕", 10), fill="red"
            )

    def _start_analysis(self):
        if not self.image_path:
            return

        self.analyze_btn.config(state=tk.DISABLED)
        self.apply_btn.config(state=tk.DISABLED)
        self.progress.start(15)
        self.status_label.config(text="AI 분석 중...", fg="blue")
        self._set_result_text("Claude API에 이미지를 전송하고 분석 중입니다...\n잠시 기다려 주세요.")

        def do_analysis():
            try:
                result, raw = self.analyzer.analyze_image(self.image_path)
                self.after(0, lambda: self._on_analysis_done(result, raw))
            except Exception as e:
                self.after(0, lambda: self._on_analysis_error(str(e)))

        threading.Thread(target=do_analysis, daemon=True).start()

    def _on_analysis_done(self, result, raw):
        self.progress.stop()
        self.analysis_result = result
        self.raw_response = raw

        elements = result.get("elements", [])
        connections = result.get("connections", [])
        annotations = result.get("work_annotations", [])

        # 요소 타입별 개수
        type_counts = {}
        type_names = {
            "pole": "전주", "cable": "케이블", "terminal": "단자함",
            "house": "집", "dropwire": "인입선",
        }
        for e in elements:
            t = e.get("element_type", "기타")
            name = type_names.get(t, t)
            type_counts[name] = type_counts.get(name, 0) + 1

        summary_parts = [f"{name} {count}개" for name, count in type_counts.items()]
        summary = ", ".join(summary_parts) if summary_parts else "인식된 요소 없음"

        text = f"감지 결과: {summary}\n"
        text += f"연결: {len(connections)}개\n"
        text += f"작업 지시: {len(annotations)}건\n\n"

        if annotations:
            text += "--- 작업 내용 ---\n"
            for ann in annotations:
                text += f"  • {ann.get('description', '')}\n"

        text += f"\n--- 상세 요소 ---\n"
        for e in elements:
            name = type_names.get(e.get("element_type", ""), "")
            label = e.get("label", "")
            status_names = {
                "existing": "기존", "damaged": "파손",
                "new": "신설", "demolish": "철거",
            }
            status = status_names.get(e.get("status", ""), "")
            text += f"  [{name}] {label} ({status})\n"

        self.status_label.config(text=f"분석 완료 - {summary}", fg="green")
        self._set_result_text(text)
        self.analyze_btn.config(state=tk.NORMAL)
        self.apply_btn.config(state=tk.NORMAL)

    def _on_analysis_error(self, error_msg):
        self.progress.stop()
        self.status_label.config(text="분석 실패", fg="red")
        self._set_result_text(f"분석 중 오류가 발생했습니다:\n\n{error_msg}")
        self.analyze_btn.config(state=tk.NORMAL)

    def _set_result_text(self, text):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", text)
        self.result_text.config(state=tk.DISABLED)

    def _apply_results(self):
        if not self.analysis_result:
            return

        if self.on_apply:
            self.on_apply(self.analysis_result, self.raw_response, self.image_path)

        self.destroy()
