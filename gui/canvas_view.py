"""도면 캔버스: 드래그앤드롭, 연결, 요소 배치"""
import tkinter as tk
from config import CANVAS_WIDTH, CANVAS_HEIGHT, GRID_SIZE, STATUS_COLORS
from models.drawing_element import DrawingElement
from gui.canvas_items.renderers import (
    draw_pole, draw_terminal, draw_house, draw_cable, draw_dropwire
)


class CanvasView(tk.Frame):
    def __init__(self, parent, on_select=None):
        super().__init__(parent)
        self.on_select_callback = on_select

        self.canvas = tk.Canvas(
            self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
            bg="white", scrollregion=(0, 0, 2000, 1500)
        )
        h_scroll = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 데이터
        self.elements = []          # list[DrawingElement]
        self.connections = []       # list[(from_id, to_id, type)]
        self._canvas_to_element = {}  # canvas_item_id -> element
        self._element_canvas_ids = {} # element.id -> [canvas_item_ids]
        self._next_id = 1

        # 상태
        self.current_tool = "select"
        self.selected_element = None
        self._drag_data = None
        self._cable_start = None    # 케이블/인입선 연결 시작점

        # 이벤트 바인딩
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Button-3>", self._on_right_click)

        self._draw_grid()

    def _draw_grid(self):
        for x in range(0, 2000, GRID_SIZE):
            self.canvas.create_line(x, 0, x, 1500, fill="#f0f0f0", tags=("grid",))
        for y in range(0, 1500, GRID_SIZE):
            self.canvas.create_line(0, y, 2000, y, fill="#f0f0f0", tags=("grid",))

    def set_tool(self, tool):
        self.current_tool = tool
        cursors = {
            "select": "arrow", "pole": "circle", "cable": "tcross",
            "terminal": "plus", "house": "dotbox",
            "dropwire": "right_side", "delete": "X_cursor",
        }
        self.canvas.config(cursor=cursors.get(tool, "arrow"))

    def _snap(self, v):
        return round(v / GRID_SIZE) * GRID_SIZE

    def _on_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.current_tool == "select":
            self._handle_select(x, y)
        elif self.current_tool == "delete":
            self._handle_delete(x, y)
        elif self.current_tool in ("cable", "dropwire"):
            self._handle_line_click(x, y)
        else:
            self._handle_place(x, y)

    def _handle_select(self, x, y):
        item = self._find_element_at(x, y)
        self._select_element(item)
        if item:
            self._drag_data = {"elem": item, "ox": x, "oy": y}

    def _handle_place(self, x, y):
        sx, sy = self._snap(x), self._snap(y)
        elem = DrawingElement(
            id=self._next_id,
            element_type=self.current_tool,
            label=f"{self._next_id}",
            x=sx, y=sy,
            status="existing",
        )
        self._next_id += 1
        self.elements.append(elem)
        self._render_element(elem)
        self._select_element(elem)

    def _handle_line_click(self, x, y):
        elem = self._find_element_at(x, y)
        if not elem:
            return

        if self._cable_start is None:
            self._cable_start = elem
            self._highlight(elem, True)
        else:
            start = self._cable_start
            self._highlight(start, False)
            self._cable_start = None

            if start.id == elem.id:
                return

            conn_type = self.current_tool
            self.connections.append((start.id, elem.id, conn_type))
            self._render_connection(start, elem, conn_type)

    def _handle_delete(self, x, y):
        elem = self._find_element_at(x, y)
        if not elem:
            return
        # 캔버스에서 제거
        for cid in self._element_canvas_ids.get(elem.id, []):
            self.canvas.delete(cid)
        # 연결선 제거
        self.connections = [
            c for c in self.connections
            if c[0] != elem.id and c[1] != elem.id
        ]
        self.elements.remove(elem)
        if self.selected_element == elem:
            self._select_element(None)
        self.redraw()

    def _on_drag(self, event):
        if self.current_tool != "select" or not self._drag_data:
            return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        elem = self._drag_data["elem"]
        dx = x - self._drag_data["ox"]
        dy = y - self._drag_data["oy"]
        elem.x += dx
        elem.y += dy
        self._drag_data["ox"] = x
        self._drag_data["oy"] = y
        self.redraw()

    def _on_release(self, event):
        if self._drag_data:
            elem = self._drag_data["elem"]
            elem.x = self._snap(elem.x)
            elem.y = self._snap(elem.y)
            self._drag_data = None
            self.redraw()

    def _on_right_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        elem = self._find_element_at(x, y)
        if not elem:
            return

        menu = tk.Menu(self.canvas, tearoff=0)
        for status, label in [
            ("existing", "기존"), ("damaged", "파손"),
            ("new", "신설"), ("demolish", "철거")
        ]:
            menu.add_command(
                label=f"상태: {label}",
                command=lambda s=status, e=elem: self._set_status(e, s)
            )
        menu.tk_popup(event.x_root, event.y_root)

    def _set_status(self, elem, status):
        elem.status = status
        self.redraw()
        if self.selected_element == elem and self.on_select_callback:
            self.on_select_callback(elem)

    def _find_element_at(self, x, y):
        items = self.canvas.find_overlapping(x - 15, y - 15, x + 15, y + 15)
        for item_id in reversed(items):
            if item_id in self._canvas_to_element:
                return self._canvas_to_element[item_id]
        return None

    def _select_element(self, elem):
        # 이전 선택 해제
        if self.selected_element:
            self._highlight(self.selected_element, False)
        self.selected_element = elem
        if elem:
            self._highlight(elem, True)
        if self.on_select_callback:
            self.on_select_callback(elem)

    def _highlight(self, elem, on):
        for cid in self._element_canvas_ids.get(elem.id, []):
            tags = self.canvas.gettags(cid)
            if "element" in tags:
                if on:
                    self.canvas.itemconfig(cid, outline="#00CC00", width=3)
                else:
                    self.canvas.itemconfig(cid, outline="black", width=2)

    def _render_element(self, elem):
        ids = []
        if elem.element_type == "pole":
            ids = draw_pole(self.canvas, elem.x, elem.y, elem.status, elem.label)
        elif elem.element_type == "terminal":
            ids = draw_terminal(self.canvas, elem.x, elem.y, elem.status, elem.label)
        elif elem.element_type == "house":
            ids = draw_house(self.canvas, elem.x, elem.y, elem.status, elem.label)

        self._element_canvas_ids[elem.id] = ids
        for cid in ids:
            self._canvas_to_element[cid] = elem

    def _render_connection(self, elem1, elem2, conn_type):
        if conn_type == "cable":
            ids = draw_cable(self.canvas, elem1.x, elem1.y, elem2.x, elem2.y,
                             elem1.status if elem1.element_type == "cable" else "existing")
        else:
            ids = draw_dropwire(self.canvas, elem1.x, elem1.y, elem2.x, elem2.y,
                                elem1.status if elem1.element_type == "dropwire" else "existing")

        # 연결선에 대한 가상 요소는 만들지 않지만 canvas 매핑은 양쪽 요소에 연결
        self._element_canvas_ids.setdefault(elem1.id, []).extend(ids)
        for cid in ids:
            self._canvas_to_element[cid] = elem1

    def redraw(self):
        """전체 캔버스 다시 그리기"""
        self.canvas.delete("element")
        self.canvas.delete("label")
        self._canvas_to_element.clear()
        self._element_canvas_ids.clear()

        for elem in self.elements:
            self._render_element(elem)

        elem_map = {e.id: e for e in self.elements}
        for from_id, to_id, conn_type in self.connections:
            e1 = elem_map.get(from_id)
            e2 = elem_map.get(to_id)
            if e1 and e2:
                self._render_connection(e1, e2, conn_type)

        if self.selected_element:
            self._highlight(self.selected_element, True)

    def clear_all(self):
        self.elements.clear()
        self.connections.clear()
        self._next_id = 1
        self.selected_element = None
        self.redraw()

    def get_element_count(self):
        return len(self.elements)
