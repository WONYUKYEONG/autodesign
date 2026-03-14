"""API 키 설정 다이얼로그"""
import os
import tkinter as tk
from tkinter import messagebox
import threading
from config import BASE_DIR, ANTHROPIC_API_KEY


class ApiKeyDialog(tk.Toplevel):
    """Anthropic API 키를 입력하고 .env에 저장하는 다이얼로그"""

    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.title("API 키 설정")
        self.geometry("450x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_save = on_save
        self._create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _create_widgets(self):
        frame = tk.Frame(self, padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame, text="Anthropic API 키",
            font=("맑은 고딕", 10, "bold")
        ).pack(anchor="w")

        tk.Label(
            frame, text="Claude API 호출에 필요한 키를 입력하세요.",
            font=("맑은 고딕", 9), fg="gray"
        ).pack(anchor="w", pady=(0, 5))

        self.key_var = tk.StringVar(value=ANTHROPIC_API_KEY)
        self.key_entry = tk.Entry(
            frame, textvariable=self.key_var,
            show="•", width=50, font=("Consolas", 10)
        )
        self.key_entry.pack(fill=tk.X, pady=5)

        # 보기/숨기기 토글
        self.show_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            frame, text="키 표시", variable=self.show_var,
            command=self._toggle_show, font=("맑은 고딕", 9)
        ).pack(anchor="w")

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.test_btn = tk.Button(
            btn_frame, text="연결 테스트", command=self._test_connection,
            font=("맑은 고딕", 9)
        )
        self.test_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.status_label = tk.Label(
            btn_frame, text="", font=("맑은 고딕", 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="저장", command=self._save,
            font=("맑은 고딕", 9), bg="#4CAF50", fg="white", width=8
        ).pack(side=tk.RIGHT)

        tk.Button(
            btn_frame, text="취소", command=self.destroy,
            font=("맑은 고딕", 9), width=8
        ).pack(side=tk.RIGHT, padx=5)

    def _toggle_show(self):
        self.key_entry.config(show="" if self.show_var.get() else "•")

    def _test_connection(self):
        key = self.key_var.get().strip()
        if not key:
            messagebox.showwarning("경고", "API 키를 입력하세요.")
            return

        self.test_btn.config(state=tk.DISABLED)
        self.status_label.config(text="테스트 중...", fg="gray")

        def do_test():
            from ai.vision_analyzer import VisionAnalyzer
            analyzer = VisionAnalyzer(api_key=key)
            result = analyzer.test_connection()

            def update_ui():
                self.test_btn.config(state=tk.NORMAL)
                if result is True:
                    self.status_label.config(text="✓ 연결 성공", fg="green")
                else:
                    self.status_label.config(text="✗ 연결 실패", fg="red")
                    messagebox.showerror("연결 실패", str(result))

            self.after(0, update_ui)

        threading.Thread(target=do_test, daemon=True).start()

    def _save(self):
        key = self.key_var.get().strip()
        if not key:
            messagebox.showwarning("경고", "API 키를 입력하세요.")
            return

        env_path = os.path.join(BASE_DIR, ".env")
        lines = []

        # 기존 .env 파일 읽기
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        # ANTHROPIC_API_KEY 업데이트 또는 추가
        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith("ANTHROPIC_API_KEY"):
                lines[i] = f"ANTHROPIC_API_KEY={key}\n"
                found = True
                break
        if not found:
            lines.append(f"ANTHROPIC_API_KEY={key}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        # 런타임 환경변수 갱신
        os.environ["ANTHROPIC_API_KEY"] = key

        # config 모듈 값도 갱신
        import config
        config.ANTHROPIC_API_KEY = key

        if self.on_save:
            self.on_save(key)

        messagebox.showinfo("저장 완료", "API 키가 저장되었습니다.")
        self.destroy()
