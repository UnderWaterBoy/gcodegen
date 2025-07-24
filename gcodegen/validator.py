"""validator.py — расширенные проверки"""
from __future__ import annotations
from typing import List
import re

MSG = {
    'ru': {
        'no_g17': 'Нет G17 (плоскость XY)',
        'no_g21': 'Нет G21 (мм)',
        'no_g90': 'Нет G90 (абсолютные координаты)',
        'no_wcs': 'Не выбрана система координат (G54..G59)',
        'g1_before_m3': 'G1 до включения шпинделя (M3)',
        'g1_no_feed': 'G1 без положительной подачи F',
        'g0_with_feed': 'В G0 указана подача F (некорректно)',
        'neg_feed': 'Отрицательная или нулевая подача F',
        'dup_feed': 'В строке несколько F',
        'coolant_before_cut': 'G1 до включения СОЖ (M8)',
        'missing_footer': 'Нет завершающих команд (например, M30)',
        'no_spindle_off': 'Нет отключения шпинделя (M5)',
        'no_coolant_off': 'Нет выключения СОЖ (M9)',
        'no_safe_retract': 'Нет возврата на безопасную Z перед концом программы',
        'g0_down': 'Быстрый ход G0 в минус Z (опасно)',
        'absurd_z': 'Подозрительно низкий Z: {z}',
        'arc_no_radius': 'G2/G3 без R и без I/J',
        'g91_mode': 'Используется G91 (относительные), но не вернулись в G90',
        'long_line': 'Строка длиннее 80 символов (#{n})',
        'unknown_code': 'Неизвестный или неподдерживаемый код: {code}',
    },
    'en': {
        'no_g17': 'Missing G17 (XY plane)',
        'no_g21': 'Missing G21 (mm)',
        'no_g90': 'Missing G90 (absolute coords)',
        'no_wcs': 'No work coordinate system selected (G54..G59)',
        'g1_before_m3': 'G1 before spindle on (M3)',
        'g1_no_feed': 'G1 without positive feed F',
        'g0_with_feed': 'Feed F specified on G0 line',
        'neg_feed': 'Negative or zero feed F',
        'dup_feed': 'Multiple F in one line',
        'coolant_before_cut': 'G1 before coolant on (M8)',
        'missing_footer': 'No program end command (e.g. M30)',
        'no_spindle_off': 'No spindle off (M5)',
        'no_coolant_off': 'No coolant off (M9)',
        'no_safe_retract': 'No safe Z retract before program end',
        'g0_down': 'Rapid G0 move into negative Z (dangerous)',
        'absurd_z': 'Suspiciously low Z: {z}',
        'arc_no_radius': 'G2/G3 without R and without I/J',
        'g91_mode': 'G91 (incremental) used but not switched back to G90',
        'long_line': 'Line longer than 80 chars (#{n})',
        'unknown_code': 'Unknown/unsupported code: {code}',
    }
}

RE_BLOCK = re.compile(r"^(?:N\d+\s+)?(?P<body>.*)$", re.I)
RE_FLOAT = r"[-+]?\d+(?:\.\d+)?"
RE_FEED = re.compile(r"F(" + RE_FLOAT + ")", re.I)
RE_Z = re.compile(r"Z(" + RE_FLOAT + ")", re.I)
RE_G = re.compile(r"G(\d+)", re.I)
RE_M = re.compile(r"M(\d+)", re.I)

# Коды, которые считаем допустимыми (минимальный набор). Можно расширять.
KNOWN_G = {0,1,2,3,17,18,19,20,21,28,40,41,42,43,49,54,55,56,57,58,59,80,81,82,83,84,85,86,87,88,89,90,91}
KNOWN_M = {0,1,2,3,5,6,8,9,30}

def validate_gcode(text: str, lang: str = 'ru', safe_min: float = 0.0) -> List[str]:
    m = MSG.get(lang, MSG['ru'])
    warns: List[str] = []

    # Глобальные флаги
    if 'G17' not in text: warns.append(m['no_g17'])
    if 'G21' not in text: warns.append(m['no_g21'])
    if 'G90' not in text: warns.append(m['no_g90'])
    if not any(g in text for g in ('G54', 'G55', 'G56', 'G57', 'G58', 'G59')):
        warns.append(m['no_wcs'])

    spindle_on = False
    coolant_on = False
    feed_current = None
    absurd = -1000.0
    g91_mode = False
    last_safe_z_ok = False

    # для footer
    saw_m30 = False
    saw_m5 = False
    saw_m9 = False

    lines = text.splitlines()
    for idx, raw in enumerate(lines, start=1):
        line = raw.strip()
        mm = RE_BLOCK.match(line)
        if not mm:
            continue
        body = mm.group('body')
        if not body or body.startswith('('):
            continue

        # Длина строки
        if len(body) > 80:
            warns.append(m['long_line'].format(n=idx))

        # Найдём G/M коды
        g_codes = [int(x) for x in RE_G.findall(body)]
        m_codes = [int(x) for x in RE_M.findall(body)]

        # Неизвестные коды
        for gcode in g_codes:
            if gcode not in KNOWN_G:
                warns.append(m['unknown_code'].format(code=f"G{gcode}"))
        for mcode in m_codes:
            if mcode not in KNOWN_M:
                warns.append(m['unknown_code'].format(code=f"M{mcode}"))

        # Состояние шпинделя/СОЖ
        if any(c == 3 for c in m_codes):  # M3
            spindle_on = True
        if any(c == 5 for c in m_codes):  # M5
            saw_m5 = True
            spindle_on = False
        if any(c == 8 for c in m_codes):  # M8
            coolant_on = True
        if any(c == 9 for c in m_codes):  # M9
            saw_m9 = True
            coolant_on = False
        if any(c == 30 for c in m_codes):  # M30
            saw_m30 = True

        # G90/G91
        if 90 in g_codes:
            g91_mode = False
        if 91 in g_codes:
            g91_mode = True

        # FEED
        feeds = RE_FEED.findall(body)
        if len(feeds) > 1:
            warns.append(m['dup_feed'])
        if feeds:
            try:
                feed_current = float(feeds[-1])
            except ValueError:
                pass

        # Z
        mz = RE_Z.search(body)
        if mz:
            try:
                z = float(mz.group(1))
                if z < absurd:
                    warns.append(m['absurd_z'].format(z=z))
                if 'G0' in body.upper() and z < 0:
                    warns.append(m['g0_down'])
                # пометим что был безопасный retract выше safe_min
                if 'G0' in body.upper() and z >= safe_min:
                    last_safe_z_ok = True
            except ValueError:
                pass

        # Проверки на G1
        if any(code == 1 for code in g_codes):
            if not spindle_on:
                warns.append(m['g1_before_m3'])
            if feed_current is None or feed_current <= 0:
                warns.append(m['g1_no_feed'])
            if not coolant_on:
                warns.append(m['coolant_before_cut'])

        # Проверка на G0 с подачей
        if any(code == 0 for code in g_codes) and feeds:
            warns.append(m['g0_with_feed'])
            # feed_current не сбрасываем, это модальная величина

        # Арки
        if any(code in (2,3) for code in g_codes):
            if not re.search(r"[RIJij]", body):
                warns.append(m['arc_no_radius'])

    # Итоги
    if g91_mode:
        warns.append(m['g91_mode'])
    if not saw_m30:
        warns.append(m['missing_footer'])
    if not saw_m5:
        warns.append(m['no_spindle_off'])
    if not saw_m9:
        warns.append(m['no_coolant_off'])
    if not last_safe_z_ok:
        warns.append(m['no_safe_retract'])

    return list(dict.fromkeys(warns))  # убираем дубли
