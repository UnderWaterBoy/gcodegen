"""i18n.py — простейшая локализация строк для CLI/валидатора."""

STRINGS = {
    "ru": {
        "app_help": "Генераторы G-кода: плоскость, круглый и квадратный карманы",
        "opt_width": "Размер по X",
        "opt_length": "Размер по Y",
        "opt_depth": "Глубина",
        "opt_step_down": "Шаг по Z",
        "opt_feed": "Подача мм/мин",
        "opt_spindle": "Обороты шпинделя",
        "opt_tool_diam": "Диаметр фрезы",
        "opt_safe": "Безопасная высота",
        "validate_ok": "OK",
        "validate_title": "Предупреждения/Ошибки",
        "cmd_face_help": "Фрезеровка плоскости",
        "cmd_round_help": "Круглый карман",
        "cmd_square_help": "Квадратный карман",
        "cmd_validate_help": "Проверка G-кода",
        "cmd_help_help": "Описание функций",
    },
    "en": {
        "app_help": "G-code generators: face, round pocket, square pocket",
        "opt_width": "Size along X",
        "opt_length": "Size along Y",
        "opt_depth": "Depth",
        "opt_step_down": "Step down",
        "opt_feed": "Feed mm/min",
        "opt_spindle": "Spindle rpm",
        "opt_tool_diam": "Tool diameter",
        "opt_safe": "Safe height",
        "validate_ok": "OK",
        "validate_title": "Warnings/Errors",
        "cmd_face_help": "Face milling",
        "cmd_round_help": "Round pocket",
        "cmd_square_help": "Square pocket",
        "cmd_validate_help": "Validate G-code",
        "cmd_help_help": "Show function help",
    },
}

def tr(lang: str, key: str) -> str:
    return STRINGS.get(lang, STRINGS["ru"]).get(key, key)
