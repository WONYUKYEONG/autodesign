"""프로젝트 관리 다이얼로그"""
import tkinter as tk
from tkinter import messagebox, simpledialog
from models import project as proj_model


class ProjectDialog(tk.Toplevel):
    def __init__(self, parent, on_load=None):
        super().__init__(parent)
        self.title("프로젝트 관리")
        self.geometry("400x350")
        self.resizable(False, False)
        self.on_load = on_load
        self.result = None

        self.transient(parent)
        self.grab_set()

        # 프로젝트 목록
        tk.Label(self, text="프로젝트 목록", font=("맑은 고딕", 11, "bold")).pack(pady=5)

        self.listbox = tk.Listbox(self, height=10, font=("맑은 고딕", 10))
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(btn_frame, text="새 프로젝트", command=self._new,
                  font=("맑은 고딕", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="불러오기", command=self._load,
                  font=("맑은 고딕", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="삭제", command=self._delete,
                  font=("맑은 고딕", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="닫기", command=self.destroy,
                  font=("맑은 고딕", 9)).pack(side=tk.RIGHT, padx=2)

        self._projects = []
        self._refresh()

    def _refresh(self):
        self.listbox.delete(0, tk.END)
        self._projects = proj_model.list_projects()
        for p in self._projects:
            self.listbox.insert(tk.END, f"{p['name']} ({p['created_at'][:10]})")

    def _new(self):
        name = simpledialog.askstring("새 프로젝트", "프로젝트 이름:", parent=self)
        if name:
            pid = proj_model.create_project(name)
            self._refresh()
            if self.on_load:
                self.on_load(pid, name)
            self.destroy()

    def _load(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("불러오기", "프로젝트를 선택하세요.", parent=self)
            return
        p = self._projects[sel[0]]
        if self.on_load:
            self.on_load(p["id"], p["name"])
        self.destroy()

    def _delete(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        p = self._projects[sel[0]]
        if messagebox.askyesno("삭제", f"'{p['name']}' 프로젝트를 삭제하시겠습니까?", parent=self):
            proj_model.delete_project(p["id"])
            self._refresh()
