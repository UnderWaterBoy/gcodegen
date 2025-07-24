# gcodegen

**Генератор G‑кода для базовых фрезерных операций (плоскость, круглые и прямоугольные карманы) с CLI, постпроцессором и валидатором.** Проект ориентирован на учебно-практическое применение и последующую публикацию на PyPI.

---

## 1. Постановка задачи и соответствие

**Задание:** написать скрипт на Python, реализующий функции генерации G-кода для:

1. фрезерования плоскости;
2. фрезерования круглого кармана;
3. фрезерования квадратного кармана;
4. вывода справки (help) по любому из этих пунктов.

**Как выполнено в проекте:**

* `generate_face()` — плоскость (face milling);
* `generate_round_pocket()` — круглый карман (режим «кольца» G2/G3);
* `generate_square_pocket()` — прямоугольный/квадратный карман;
* `help_text()` + команда `helpcmd` в CLI — вывод краткой справки.

CLI обёртка на Typer предоставляет одноимённые команды `face`, `round`, `square`, `validate`, `helpcmd`. Все функции вынесены в модуль `core.py`, постпроцессор — в `post.py`, проверки — в `validator.py`.

---

## 2. Краткая аннотация

Проект предоставляет набор функций и консольных команд для автоматической генерации управляющих программ (G‑кода) под ЧПУ-станки. Поддерживаются:

* фрезерование плоскости (face milling),
* фрезерование круглого кармана (round pocket),
* фрезерование квадратного/прямоугольного кармана (square pocket).

Дополнительно включён минимальный валидатор G‑кода и система постпроцессорных профилей (YAML) для адаптации формата вывода под разные стойки. Интерфейс командной строки локализован (RU/EN).

---

## 3. Требования

* Python ≥ 3.9
* Зависимости: `pyyaml`, `typer`, `rich`

---

## 4. Установка

### Из исходников

```bash
pip install -e .
```

> При установке под Windows следите, чтобы путь к `Scripts` попал в `PATH` (pip предупредит).

---

## 5. Быстрый старт

После установки выполните:

```bash
gcodegen --help
```

или если Scripts стал не в тот PATH

```bash
python -m gcodegen.cli --help
```

Пример:

```bash
python -m gcodegen.cli face --width 100 --length 50 --depth 2 --step-down 0.5 --feed 800 --spindle 12000 --tool-diam 10 --safe 5 --post gcodegen/data/posts/fanuc_ru.yaml > face.nc
```

> **PowerShell:** для корректной кодировки используйте `Out-File -Encoding ascii` или `utf8` вместо простого `>`.

---

## 6. Команды CLI и параметры

Ниже описаны все доступные команды. Значения по умолчанию указаны в скобках. Обязательные параметры отмечены **(обязательно)**.

### 5.1 `face` — фрезерование плоскости

```bash
python -m gcodegen.cli face --width 100 --length 50 --depth 2 --step-down 0.5 --feed 800 --spindle 12000 --tool-diam 10 --safe 5 --post gcodegen/data/posts/fanuc_ru.yaml --output face.nc
```

**Параметры:**

* `--width` (**обязательно**, мм) — размер по оси X.
* `--length` (**обязательно**, мм) — размер по оси Y.
* `--depth` (**обязательно**, мм) — суммарная глубина съёма.
* `--step-down` (0.5 мм) — шаг по Z.
* `--feed` (800 мм/мин) — подача.
* `--spindle` (10000 об/мин) — обороты шпинделя.
* `--tool-diam` (10 мм) — диаметр фрезы.
* `--safe` (5 мм) — безопасная высота Z.
* `--start-x`, `--start-y` (0, 0 мм) — левый нижний угол области.
* `--post` (None) — путь к YAML-профилю постпроцессора.
* `--output` (None) — файл вывода; если не указан, печать в stdout.

### 5.2 `round` — круглый карман (режим «кольца» G2/G3)

```bash
python -m gcodegen.cli round --diameter 150 --depth 10 --step-down 2 --feed 200 --spindle 4000 --tool-diam 2 --safe 5 --center-x 0 --center-y 0 --stepover-ratio 0.6 --cw --post gcodegen/data/posts/fanuc_ru.yaml > pocket.nc
```

**Параметры:**

* `--diameter` (**обязательно**, мм) — диаметр кармана.
* `--depth` (**обязательно**, мм) — глубина.
* `--step-down` (0.5 мм) — шаг по Z.
* `--feed` (800 мм/мин) — подача.
* `--spindle` (10000 об/мин) — обороты шпинделя.
* `--tool-diam` (10 мм) — диаметр инструмента.
* `--safe` (5 мм) — безопасная Z.
* `--center-x`, `--center-y` (0, 0 мм) — координаты центра кармана.
* `--stepover-ratio` (0.6) — радиальный шаг между кольцами (в долях D инструмента).
* `--cw/--ccw` (`--cw`) — направление дуг: CW → G2, CCW → G3.
* `--post`, `--output` — как выше.

> CAMotics корректно визуализирует дуги G2/G3, поэтому код получается коротким.

### 5.3 `square` — квадратный/прямоугольный карман

```bash
python -m gcodegen.cli square --width 50 --length 30 --depth 5 --step-down 1 --feed 600 --spindle 9000 --tool-diam 8 --safe 5 --start-x 0 --start-y 0 --post gcodegen/data/posts/fanuc_ru.yaml > sq.nc
```

**Параметры:** аналогичны команде `face`: `--width`, `--length`, `--depth`, `--step-down`, `--feed`, `--spindle`, `--tool-diam`, `--safe`, `--start-x`, `--start-y`, `--post`, `--output`.

### 5.4 `validate` — проверка G‑кода

```bash
python -m gcodegen.cli validate part.nc
```

* При отсутствии проблем: вывод `OK`, код возврата 0.
* При предупреждениях: таблица сообщений, код возврата 1.

### 5.5 `helpcmd` — текстовая справка по функциям

```bash
python -m gcodegen.cli helpcmd          # общий список
python -m gcodegen.cli helpcmd face     # подробнее о face
```

---

## 7. Валидатор (validator.py)

Проверки (RU/EN):

* наличие G17/G21/G90;
* запрет G1 до включения шпинделя (M3);
* запрет G1 без положительной подачи F;
* контроль «подозрительно низкого» Z (настраивается).

Файл читается в UTF‑8. Для других кодировок используйте `encoding=` при открытии.

---

## 8. Постпроцессор (post.py) и YAML-профили

Пример `gcodegen/data/posts/fanuc_ru.yaml`:

```yaml
decimal_separator: "."
precision: 3
line_numbers: true
line_step: 10
header_template:
  - "%"
  - "O{program_number}"
  - "(PART: {comment})"
  - "(DATE: {date})"
footer_template:
  - "M5"
  - "M9"
  - "G0 Z100.000"
  - "M30"
  - "%"
coolant_on_cmd: "M8"
coolant_off_cmd: "M9"
spindle_on_cmd: "M3 S{spindle}"
spindle_off_cmd: "M5"
```

Настраивайте шаблоны под вашу стойку (формат чисел, команды, заголовок/концовка). Загрузка: `PostProcessor.from_yaml(path)`.

---

## 9. Локализация

Язык определяется:

* переменной окружения `GCODEGEN_LANG` (`ru`/`en`),
* либо параметром CLI (если добавите `--lang`).

Строки хранятся в `gcodegen/i18n.py`. Добавление новых языков возможно через расширение словаря.

---

## 10. Ограничения и возможные доработки

* Сейчас генерация круглого кармана реализована дугами G2/G3 («кольца»). Спираль и циклы G12/G13 отключены.
* Для квадратного кармана используется растровая стратегия; можно добавить финишный обход и параметр `stepover_ratio`.
* Валидатор проверяет только базовые ошибки.
* Нет GUI. 

---

**Приложение А. Примеры вызова одной строкой**

* Face:

  ```
  python -m gcodegen.cli face --width 100 --length 50 --depth 2 --step-down 0.5 --feed 800 --spindle 12000 --tool-diam 10 --safe 5 --post gcodegen/data/posts/fanuc_ru.yaml > face.nc
  ```
* Round:

  ```
  python -m gcodegen.cli round --diameter 150 --depth 10 --step-down 2 --feed 200 --spindle 4000 --tool-diam 2 --safe 5 --center-x 0 --center-y 0 --stepover-ratio 0.6 --post gcodegen/data/posts/fanuc_ru.yaml > pocket.nc
  ```
* Square:

  ```
  python -m gcodegen.cli square --width 50 --length 30 --depth 5 --step-down 1 --feed 600 --spindle 9000 --tool-diam 8 --safe 5 --start-x 0 --start-y 0 --post gcodegen/data/posts/fanuc_ru.yaml > sq.nc
  ```
