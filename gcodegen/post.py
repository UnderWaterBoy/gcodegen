"""post.py — форматирование G-кода"""
from __future__ import annotations
import datetime as _dt
from dataclasses import dataclass, field
from typing import Optional
import yaml

@dataclass
class PostConfig:
    decimal_separator: str = "."
    precision: int = 3
    line_numbers: bool = True
    line_step: int = 10
    header_template: list[str] = field(default_factory=lambda: ["%","O{program_number}","(PART: {comment})","(DATE: {date})"])
    footer_template: list[str] = field(default_factory=lambda: ["M30","%"])
    coolant_on_cmd: str = "M8"
    coolant_off_cmd: str = "M9"
    spindle_on_cmd: str = "M3 S{spindle}"
    spindle_off_cmd: str = "M5"

class PostProcessor:
    def __init__(self, cfg: PostConfig):
        self.cfg = cfg
        self._ln = 0

    @classmethod
    def from_yaml(cls, path: str) -> "PostProcessor":
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(PostConfig(**data))

    @classmethod
    def default(cls) -> "PostProcessor":
        return cls(PostConfig())

    # ---------- helpers ----------
    def _num(self, v: Optional[float]) -> Optional[str]:
        if v is None:
            return None
        s = f"{v:.{self.cfg.precision}f}"
        if self.cfg.decimal_separator != '.':
            s = s.replace('.', self.cfg.decimal_separator)
        return s

    def _block(self, text: str) -> str:
        if not self.cfg.line_numbers:
            return text
        self._ln += self.cfg.line_step
        return f"N{self._ln} {text}".rstrip()

    def _raw(self, text: str) -> str:
        """Вернуть строку без нумерации (для %, Oxxxx и т.п.)."""
        return text.rstrip()

    # ---------- public emitters ----------
    def header(self, program_number: int, comment: str = "PROGRAM") -> str:
        """
        Строит header. Первую и последнюю строки со знаком % даём 'сырыми'.
        Остальные – через _block.
        """
        lines = []

        # Если в шаблоне есть %, выводим его сырым
        for t in self.cfg.header_template:
            formatted = t.format(program_number=program_number,
                                 comment=comment,
                                 date=_dt.date.today())
            if formatted.strip() == "%":
                lines.append(self._raw(formatted))
            else:
                lines.append(self._block(formatted))

        return "\n".join(lines)

    def footer(self) -> str:
        lines = []
        for t in self.cfg.footer_template:
            if t.strip() == "%":
                lines.append(self._raw(t))
            else:
                lines.append(self._block(t))
        return "\n".join(lines)

    def comment(self, text: str) -> str:
        return self._block(f"({text})")

    def line(self, data: dict) -> str:
        parts = [data.get('cmd', '').strip()]
        for axis in ("x", "y", "z", "i", "j", "k", "f", "s"):
            if axis in data and data[axis] is not None:
                parts.append(f"{axis.upper()}{self._num(data[axis])}")
        return self._block(" ".join(filter(None, parts)))

    def rapid(self, x: float | None = None, y: float | None = None, z: float | None = None) -> str:
        return self.line({"cmd": "G0", "x": x, "y": y, "z": z})

    def feed_move(self, x: float | None = None, y: float | None = None, z: float | None = None, feed: float | None = None) -> str:
        return self.line({"cmd": "G1", "x": x, "y": y, "z": z, "f": feed})

    def spindle_on(self, spindle: int) -> str:
        return self._block(self.cfg.spindle_on_cmd.format(spindle=spindle))

    def spindle_off(self) -> str:
        return self._block(self.cfg.spindle_off_cmd)

    def coolant_on(self) -> str:
        return self._block(self.cfg.coolant_on_cmd)

    def coolant_off(self) -> str:
        return self._block(self.cfg.coolant_off_cmd)

    # --- NEW: tool change helper ---
    def tool_change(self, tool: int) -> str:
        """
        Выбор инструмента. По Fanuc обычно T1 M6.
        """
        return self._block(f"T{tool} M6")