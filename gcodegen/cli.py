"""cli.py — Typer CLI с поддержкой RU/EN"""
import os, sys
import typer
from rich.console import Console
from rich.table import Table

from .core import generate_face, generate_round_pocket, generate_square_pocket, help_text
from .post import PostProcessor
from .validator import validate_gcode
from .i18n import tr

LANG = os.getenv("GCODEGEN_LANG", "ru").lower()

app = typer.Typer(help=tr(LANG, "app_help"))
console = Console()

def _load_post(path: str | None) -> PostProcessor:
    return PostProcessor.from_yaml(path) if path else PostProcessor.default()

@app.command(help=tr(LANG, "cmd_face_help"))
def face(
    width: float = typer.Option(..., help=tr(LANG, "opt_width")),
    length: float = typer.Option(..., help=tr(LANG, "opt_length")),
    depth: float = typer.Option(..., help=tr(LANG, "opt_depth")),
    step_down: float = typer.Option(0.5, help=tr(LANG, "opt_step_down")),
    feed: float = typer.Option(800.0, help=tr(LANG, "opt_feed")),
    spindle: int = typer.Option(10000, help=tr(LANG, "opt_spindle")),
    tool_diam: float = typer.Option(10.0, help=tr(LANG, "opt_tool_diam")),
    safe: float = typer.Option(5.0, help=tr(LANG, "opt_safe")),

    start_x: float = typer.Option(0.0),
    start_y: float = typer.Option(0.0),
    post: str | None = typer.Option(None, help="YAML post"),
    output: str | None = typer.Option(None, help="Output file"),
):
    pp = _load_post(post)
    code = generate_face(width, length, depth, step_down, feed, spindle, tool_diam, safe, (start_x, start_y), pp)
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(code)
    else:
        sys.stdout.write(code)

@app.command(name="round", help=tr(LANG, "cmd_round_help"))
def round_pocket(
    diameter: float = typer.Option(..., help="Диаметр кармана, мм"),
    depth: float = typer.Option(..., help="Глубина, мм"),
    step_down: float = typer.Option(0.5, help="Шаг по Z, мм"),
    feed: float = typer.Option(800.0, help="Подача, мм/мин"),
    spindle: int = typer.Option(10000, help="Обороты шпинделя"),
    tool_diam: float = typer.Option(10.0, help="Диаметр фрезы, мм"),
    safe: float = typer.Option(5.0, help="Безопасная высота Z, мм"),
    center_x: float = typer.Option(0.0, help="Центр X"),
    center_y: float = typer.Option(0.0, help="Центр Y"),
    post: str | None = typer.Option(None, help="YAML пост"),
    output: str | None = typer.Option(None, help="Файл вывода"),
    cw: bool = typer.Option(True, "--cw/--ccw", help="CW=G12, CCW=G13"),
    start_r: float = typer.Option(None, help="Начальный радиус I (мм)"),
    radial_step: float = typer.Option(None, help="Радиальный шаг Q (мм)")
):
    pp = _load_post(post)
    code = generate_round_pocket(
        diameter, depth, step_down, feed, spindle, tool_diam, safe,
        (center_x, center_y), pp,
        cw=cw, start_r=start_r, radial_step=radial_step
    )
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(code)
    else:
        sys.stdout.write(code)


@app.command(name="round", help=tr(LANG, "cmd_round_help"))
def round_pocket(
    diameter: float = typer.Option(..., help="Диаметр кармана, мм"),
    depth: float = typer.Option(..., help="Глубина, мм"),
    step_down: float = typer.Option(0.5, help="Шаг по Z, мм"),
    feed: float = typer.Option(800.0, help="Подача, мм/мин"),
    spindle: int = typer.Option(10000, help="Обороты шпинделя"),
    tool_diam: float = typer.Option(10.0, help="Диаметр фрезы, мм"),
    safe: float = typer.Option(5.0, help="Безопасная Z, мм"),
    center_x: float = typer.Option(0.0, help="Центр X"),
    center_y: float = typer.Option(0.0, help="Центр Y"),
    stepover_ratio: float = typer.Option(0.6, help="Степовер, доля D инструмента"),
    cw: bool = typer.Option(True, "--cw/--ccw", help="CW=G2, CCW=G3"),
    post: str | None = typer.Option(None, help="YAML пост"),
    output: str | None = typer.Option(None, help="Файл вывода"),
):
    pp = _load_post(post)
    code = generate_round_pocket(
        diameter, depth, step_down, feed, spindle, tool_diam, safe,
        (center_x, center_y), pp,
        stepover_ratio=stepover_ratio, cw=cw
    )
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(code)
    else:
        sys.stdout.write(code)
@app.command(name="square", help=tr(LANG, "cmd_square_help"))
def square(
    width: float = typer.Option(...),
    length: float = typer.Option(...),
    depth: float = typer.Option(...),
    step_down: float = typer.Option(0.5),
    feed: float = typer.Option(800.0),
    spindle: int = typer.Option(10000),
    tool_diam: float = typer.Option(10.0),
    safe: float = typer.Option(5.0),
    start_x: float = typer.Option(0.0),
    start_y: float = typer.Option(0.0),
    post: str | None = typer.Option(None),
    output: str | None = typer.Option(None),
):
    pp = _load_post(post)
    code = generate_square_pocket(
        width, length, depth, step_down, feed, spindle, tool_diam, safe,
        (start_x, start_y), pp
    )
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(code)
    else:
        sys.stdout.write(code)
@app.command(help=tr(LANG, "cmd_validate_help"))
def validate(file: str = typer.Argument(...)):
    with open(file, "r", encoding="utf-8") as f:
        txt = f.read()
    warns = validate_gcode(txt, LANG)
    if not warns:
        console.print(f"[green]{tr(LANG,'validate_ok')}[/green]")
        raise typer.Exit(0)
    table = Table(title=tr(LANG, 'validate_title'))
    table.add_column("#", justify="right")
    table.add_column("Message", justify="left")
    for i,w in enumerate(warns,1):
        table.add_row(str(i), w)
    console.print(table)
    raise typer.Exit(1)

@app.command(name="helpcmd", help=tr(LANG, "cmd_help_help"))
def helpcmd(topic: str | None = typer.Argument(None)):
    console.print(help_text(topic))

if __name__ == "__main__":
    app()
