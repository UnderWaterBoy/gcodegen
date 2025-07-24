"""core.py — генераторы G-кода и help_text."""
from math import ceil, pi, cos, sin
from typing import Tuple, List
from .post import PostProcessor

Number = float

def help_text(topic: str | None = None) -> str:
    base = (
        "Доступные функции:\n"
        "  - face(width, length, depth, step_down, feed, spindle, tool_diam, safe, ...)\n"
        "  - round_pocket(diameter, depth, step_down, feed, spindle, tool_diam, safe, ...)\n"
        "  - square_pocket(width, length, depth, step_down, feed, spindle, tool_diam, safe, ...)\n"
    )
    if topic is None:
        return base
    if topic.lower() in {"face","round_pocket","square_pocket"}:
        return base + f"\nПодробнее о {topic}: см. README.md"
    return "Неизвестная тема."

def _passes(depth: Number, step_down: Number) -> List[Number]:
    n = ceil(depth / step_down)
    return [-(min((i+1)*step_down, depth)) for i in range(n)]

def generate_face(
    width: Number, length: Number, depth: Number, step_down: Number,
    feed: Number, spindle: int, tool_diam: Number, safe: Number,
    start_xy: Tuple[Number, Number] = (0.0, 0.0),
    post: PostProcessor | None = None,
    *,
    overlap: float = 0.5,
    finish_contour: bool = True,
) -> str:
    if post is None: post = PostProcessor.default()

    x0,y0 = start_xy
    x1,y1 = x0+width, y0+length
    extra = tool_diam * overlap
    x0e, x1e = x0 - extra, x1 + extra
    y0e, y1e = y0 - extra, y1 + extra
    stepover = tool_diam*0.6
    g=[]; emit=g.append
    emit(post.header(program_number=1000, comment="FACE"))
    emit(post.line({"cmd":"G17 G21 G90"}))
    emit(post.line({"cmd":"G54"}))
    emit(post.tool_change(tool=1))
    emit(post.spindle_on(spindle))
    emit(post.coolant_on())
    emit(post.rapid(z=safe))
    emit(post.rapid(x=x0,y=y0))
    emit(post.rapid(x=x0e, y=y0e))
    for i, z in enumerate(_passes(depth, step_down), 1):
        emit(post.comment(f"PASS {i} Z{z:.3f}"))
        emit(post.feed_move(z=z, feed=feed))
        direction = 1
        y = y0e
        while y <= y1e + 1e-6:
            if direction > 0:
                emit(post.feed_move(x=x1e, y=y, feed=feed))
            else:
                emit(post.feed_move(x=x0e, y=y, feed=feed))
            y += stepover
            direction *= -1
            if y <= y1e + 1e-6:
                emit(post.feed_move(y=y, feed=feed))

    emit(post.rapid(z=safe))
    emit(post.coolant_off())
    emit(post.spindle_off())
    emit(post.footer())
    return "\n".join(filter(None,g))+"\n"

# core.py
from math import pi
from typing import Tuple, List
from .post import PostProcessor

def generate_round_pocket(
    diameter: float, depth: float, step_down: float,
    feed: float, spindle: int, tool_diam: float, safe: float,
    center_xy: Tuple[float, float] = (0.0, 0.0),
    post: PostProcessor | None = None,
    *, stepover_ratio: float = 0.6, cw: bool = True
) -> str:
    if post is None:
        post = PostProcessor.default()

    cx, cy = center_xy
    tool_r = tool_diam / 2.0
    r_final = diameter / 2.0 - tool_r
    if r_final <= 0:
        raise ValueError("Диаметр кармана должен быть больше диаметра фрезы.")

    stepover = tool_diam * stepover_ratio
    arc_cmd = "G2" if cw else "G3"

    g: List[str] = []
    emit = g.append

    emit(post.header(program_number=1001, comment="ROUND_POCKET_RINGS"))
    emit(post.line({"cmd": "G17 G21 G90"}))
    emit(post.line({"cmd": "G54"}))
    emit(post.tool_change(tool=1))
    emit(post.spindle_on(spindle))
    emit(post.coolant_on())
    emit(post.rapid(z=safe))

    current_depth = 0.0
    pass_idx = 0
    while current_depth < depth - 1e-9:
        pass_idx += 1
        layer = min(step_down, depth - current_depth)
        current_depth += layer
        z = -current_depth

        emit(post.comment(f"PASS {pass_idx} Z{z:.3f}"))
        emit(post.rapid(x=cx, y=cy))
        emit(post.feed_move(z=z, feed=feed))

        r = max(tool_r * 0.6, 0.001)
        while r <= r_final + 1e-6:
            # стартовая точка окружности — справа от центра
            x0 = cx + r
            y0 = cy
            emit(post.feed_move(x=x0, y=y0, feed=feed))

            # центр дуги от стартовой точки
            I = cx - x0
            J = cy - y0
            # одна полная окружность
            emit(post.line({"cmd": arc_cmd, "x": x0, "y": y0, "i": I, "j": J, "f": feed}))

            r += stepover

        emit(post.rapid(z=safe))

    emit(post.coolant_off())
    emit(post.spindle_off())
    emit(post.footer())
    return "\n".join(filter(None, g)) + "\n"





def generate_square_pocket(
    width: Number, length: Number, depth: Number, step_down: Number,
    feed: Number, spindle: int, tool_diam: Number, safe: Number,
    start_xy: Tuple[Number, Number] = (0.0, 0.0),
    post: PostProcessor | None = None,
    *,
    stepover_ratio: float = 0.6,      # доля диаметра фрезы
    overlap: float = 0.5,             # заход за габарит (в долях D)
    finish_contour: bool = True,      # делать ли обход контура
    raster_axis: str = "X"            # "X" или "Y" – направление зигзага
) -> str:
    if post is None:
        post = PostProcessor.default()

    x0, y0 = start_xy
    x1, y1 = x0 + width, y0 + length

    # расширяем область, чтобы не оставлять бортик
    extra = tool_diam * overlap
    X0, X1 = x0 - extra, x1 + extra
    Y0, Y1 = y0 - extra, y1 + extra

    stepover = tool_diam * stepover_ratio

    g = []; emit = g.append
    emit(post.header(program_number=1002, comment="SQUARE_POCKET"))
    emit(post.line({"cmd": "G17 G21 G90"}))
    emit(post.line({"cmd": "G54"}))
    emit(post.tool_change(tool=1))
    emit(post.spindle_on(spindle))
    emit(post.coolant_on())
    emit(post.rapid(z=safe))
    emit(post.rapid(x=X0, y=Y0))

    for i, z in enumerate(_passes(depth, step_down), 1):
        emit(post.comment(f"PASS {i} Z{z:.3f}"))
        emit(post.feed_move(z=z, feed=feed))

        if raster_axis.upper() == "X":
            # зигзаг по X, шаг по Y
            direction = 1
            y = Y0
            while y <= Y1 + 1e-6:
                if direction > 0:
                    emit(post.feed_move(x=X1, y=y))
                else:
                    emit(post.feed_move(x=X0, y=y))
                y += stepover
                direction *= -1
                if y <= Y1 + 1e-6:
                    emit(post.feed_move(y=y))
        else:
            # зигзаг по Y, шаг по X
            direction = 1
            x = X0
            while x <= X1 + 1e-6:
                if direction > 0:
                    emit(post.feed_move(x=x, y=Y1))
                else:
                    emit(post.feed_move(x=x, y=Y0))
                x += stepover
                direction *= -1
                if x <= X1 + 1e-6:
                    emit(post.feed_move(x=x))

        # финишный контур на том же Z
        if finish_contour:
            emit(post.feed_move(x=X0, y=Y0))
            emit(post.feed_move(x=X1, y=Y0))
            emit(post.feed_move(x=X1, y=Y1))
            emit(post.feed_move(x=X0, y=Y1))
            emit(post.feed_move(x=X0, y=Y0))

        emit(post.rapid(z=safe))

    emit(post.coolant_off())
    emit(post.spindle_off())
    emit(post.footer())
    return "\n".join(filter(None, g)) + "\n"
