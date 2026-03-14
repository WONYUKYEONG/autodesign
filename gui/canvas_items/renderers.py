"""도면 요소 렌더링 함수들"""
from config import STATUS_COLORS

POLE_RADIUS = 12
TERMINAL_SIZE = 20
HOUSE_SIZE = 28


def get_color(status):
    return STATUS_COLORS.get(status, "#8B4513")


def draw_pole(canvas, x, y, status="existing", label=""):
    color = get_color(status)
    r = POLE_RADIUS
    items = []
    # 원형 전주
    cid = canvas.create_oval(x - r, y - r, x + r, y + r,
                             fill=color, outline="black", width=2,
                             tags=("element", "pole"))
    items.append(cid)
    # 라벨
    if label:
        tid = canvas.create_text(x, y - r - 10, text=label,
                                 font=("맑은 고딕", 8), tags=("label",))
        items.append(tid)
    return items


def draw_terminal(canvas, x, y, status="existing", label=""):
    color = get_color(status)
    s = TERMINAL_SIZE // 2
    items = []
    cid = canvas.create_rectangle(x - s, y - s, x + s, y + s,
                                  fill=color, outline="black", width=2,
                                  tags=("element", "terminal"))
    items.append(cid)
    # T 표시
    tid = canvas.create_text(x, y, text="T", fill="white",
                             font=("맑은 고딕", 9, "bold"), tags=("label",))
    items.append(tid)
    if label:
        lid = canvas.create_text(x, y - s - 10, text=label,
                                 font=("맑은 고딕", 8), tags=("label",))
        items.append(lid)
    return items


def draw_house(canvas, x, y, status="existing", label=""):
    color = get_color(status)
    s = HOUSE_SIZE // 2
    items = []
    # 집 모양: 사각형 + 삼각형 지붕
    cid = canvas.create_rectangle(x - s, y - s // 2, x + s, y + s,
                                  fill="#FFE4B5", outline="black", width=2,
                                  tags=("element", "house"))
    items.append(cid)
    # 지붕
    rid = canvas.create_polygon(x - s - 4, y - s // 2,
                                x, y - s - 4,
                                x + s + 4, y - s // 2,
                                fill="#CD853F", outline="black", width=2,
                                tags=("element", "house"))
    items.append(rid)
    if label:
        lid = canvas.create_text(x, y + s + 10, text=label,
                                 font=("맑은 고딕", 8), tags=("label",))
        items.append(lid)
    return items


def draw_cable(canvas, x1, y1, x2, y2, status="existing"):
    color = get_color(status)
    cid = canvas.create_line(x1, y1, x2, y2,
                             fill=color, width=3, dash=(6, 3),
                             tags=("element", "cable"))
    return [cid]


def draw_dropwire(canvas, x1, y1, x2, y2, status="existing"):
    color = get_color(status)
    cid = canvas.create_line(x1, y1, x2, y2,
                             fill=color, width=2,
                             arrow="last", arrowshape=(10, 12, 5),
                             tags=("element", "dropwire"))
    return [cid]
