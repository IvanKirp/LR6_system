from pathlib import Path
import csv
import subprocess
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, Inches

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ЛР6_Кирпичёв.docx"

def set_font(run, name="Times New Roman", size=14, bold=False):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold

def paragraph(doc, text="", align=None, size=14, bold=False, first=True):
    p = doc.add_paragraph()
    if align is not None: p.alignment = align
    pf = p.paragraph_format
    pf.line_spacing = 1.5
    pf.space_before = Pt(0); pf.space_after = Pt(0)
    if first: pf.first_line_indent = Cm(1.25)
    r = p.add_run(text); set_font(r, size=size, bold=bold)
    return p

def heading(doc, text):
    p = paragraph(doc, text.upper(), WD_ALIGN_PARAGRAPH.CENTER, 14, True, False)
    p.paragraph_format.page_break_before = True
    p.paragraph_format.space_after = Pt(12)
    return p

def table(doc, headers, rows):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for cell, value in zip(t.rows[0].cells, headers):
        cell.text = str(value); cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for r in cell.paragraphs[0].runs: set_font(r, size=10, bold=False)
    for row in rows:
        cells = t.add_row().cells
        for cell, value in zip(cells, row):
            cell.text = str(value); cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for p in cell.paragraphs:
                p.paragraph_format.line_spacing = 1.0
                for r in p.runs: set_font(r, size=10)
    return t

def caption(doc, text):
    return paragraph(doc, text, WD_ALIGN_PARAGRAPH.CENTER, 12, False, False)

def code_block(doc, path):
    if not path.exists(): return
    p = doc.add_paragraph(); p.paragraph_format.line_spacing = 1.0; p.paragraph_format.first_line_indent = Cm(0)
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        r = p.add_run(line + "\n"); set_font(r, "Consolas", 8, False)

def add_toc(doc):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(); fld = OxmlElement("w:fldSimple"); fld.set(qn("w:instr"), 'TOC \\o "1-3" \\h \\z \\u'); r._r.addnext(fld)

def main():
    doc = Document()
    sec = doc.sections[0]; sec.left_margin=Cm(3); sec.right_margin=Cm(1.5); sec.top_margin=Cm(2); sec.bottom_margin=Cm(2)
    normal = doc.styles["Normal"]; normal.font.name="Times New Roman"; normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman"); normal.font.size=Pt(14)
    for text in ["Министерство образования Республики Беларусь", "Учреждение образования «Белорусский государственный университет информатики и радиоэлектроники»", "Факультет компьютерных систем и сетей", "Кафедра информатики"]:
        paragraph(doc, text, WD_ALIGN_PARAGRAPH.CENTER, 14, False, False)
    for _ in range(4): paragraph(doc, "", None, 14, False, False)
    paragraph(doc, "ОТЧЁТ", WD_ALIGN_PARAGRAPH.CENTER, 14, True, False)
    paragraph(doc, "к лабораторной работе № 6", WD_ALIGN_PARAGRAPH.CENTER, 14, True, False)
    paragraph(doc, "на тему: «Анализ логических дисков»", WD_ALIGN_PARAGRAPH.CENTER, 14, False, False)
    for _ in range(6): paragraph(doc, "", None, 14, False, False)
    paragraph(doc, "Выполнил: студент группы 6-05-0612-02", WD_ALIGN_PARAGRAPH.RIGHT, 14, False, False)
    paragraph(doc, "Кирпичёв, билет № 54", WD_ALIGN_PARAGRAPH.RIGHT, 14, False, False)
    paragraph(doc, "Минск 2026", WD_ALIGN_PARAGRAPH.CENTER, 14, False, False)
    doc.add_page_break()
    paragraph(doc, "СОДЕРЖАНИЕ", WD_ALIGN_PARAGRAPH.CENTER, 14, True, False); add_toc(doc)
    heading(doc, "Введение"); paragraph(doc, "Работа посвящена сбору сведений о логических дисках Windows и измерению времени выполнения операций системной диагностики. Программа использует Windows API напрямую, сохраняет результаты в CSV и ведёт журнал операций.")
    heading(doc, "1 Цель работы"); paragraph(doc, "Изучить механизмы получения информации о логических дисках Windows, научиться обрабатывать ошибки API, экспортировать результаты и анализировать экспериментальные данные.")
    heading(doc, "2 Индивидуальное задание"); paragraph(doc, "Вариант 15 — «Анализ логических дисков». Требуется перечислить логические диски, определить тип, файловую систему, метку, общий и свободный объём, а также процент заполнения.")
    heading(doc, "3 Краткие теоретические сведения"); paragraph(doc, "GetLogicalDriveStringsW возвращает список корней логических дисков. GetDiskFreeSpaceExW предоставляет объёмы в байтах и подходит для больших дисков. GetVolumeInformationW возвращает метку и файловую систему. GetDiskFreeSpaceW работает с геометрией кластеров и требует ручного пересчёта, поэтому в реализации не используется. GiB равен 2^30 байтам, GB — 10^9 байтам.")
    heading(doc, "4 Архитектура разработанного приложения"); paragraph(doc, "main.cpp координирует измерение и экспорт. Модуль disk_info взаимодействует с тремя обязательными API, csv_export создаёт CSV, logger записывает операции, error_utils форматирует ошибки. Исходная схема находится в diagrams/architecture.puml.")
    heading(doc, "5 Описание алгоритма"); paragraph(doc, "Сначала определяется размер буфера списка дисков, затем перечисляются корни. Для каждого корня последовательно запрашиваются тип, параметры тома и свободное место. Ошибка сохраняется в конкретной записи, после чего обработка продолжается. Алгоритм приведён в diagrams/algorithm.md.")
    heading(doc, "6 Перечень использованных Windows API"); table(doc, ["Функция", "Назначение", "Где используется"], [["GetLogicalDriveStringsW", "Список логических дисков", "disk_info.cpp"],["GetDiskFreeSpaceExW", "Общий и свободный объём в байтах", "disk_info.cpp"],["GetVolumeInformationW", "Файловая система и метка", "disk_info.cpp"],["GetDriveTypeW", "Тип диска", "disk_info.cpp"],["QueryPerformanceCounter", "Высокоточный таймер", "main.cpp"],["FormatMessageW", "Описание Win32-ошибки", "error_utils.cpp"]])
    heading(doc, "7 Описание структур данных"); paragraph(doc, "DiskRecord содержит root, driveType, fileSystem, label, totalBytes, freeBytes, usedPercent, ok и lastError. Вектор записей передаётся из перечислителя в CSV-экспортёр.")
    heading(doc, "8 Схемы и диаграммы"); paragraph(doc, "В репозитории сохранены редактируемые исходники PlantUML и Mermaid. PlantUML не рендерился автоматически, поскольку локальный plantuml.jar не найден; исходник architecture.puml готов к рендерингу локальным инструментом.")
    heading(doc, "9 Обработка ошибок"); table(doc, ["Сценарий", "Код", "Реакция"], [["Недоступный том", "ERROR_NOT_READY", "ok=false, код сохраняется в DiskRecord"],["Ошибка получения списка", "GetLastError", "пустой результат и код API"],["Невозможно открыть CSV", "ERROR_OPEN_FAILED", "сообщение и ненулевой код"],["Отсутствует аргумент CLI", "2", "вывод Usage и завершение"]])
    heading(doc, "10 Тестовые сценарии"); table(doc, ["№", "Сценарий", "Результат"], [["1", "Некорректный путь CSV", "Пройден"],["2", "--csv без значения", "Пройден"],["3", "CalcUsedPercent(0,0)", "0.0, пройден"],["4", "CalcUsedPercent(100,50)", "50.0, пройден"],["5", "CSV-экранирование запятой и кавычек", "Пройден"]])
    heading(doc, "11 Методика проведения экспериментов"); paragraph(doc, "Для baseline и трёх размеров файла запускался Release x64 exe по три раза. Перед созданием файла и после него фиксировалось свободное место через shutil.disk_usage. Каждая конфигурация сохранялась в отдельный CSV, после чего вычислялись суммы объёмов, средний процент заполнения и время запуска.")
    heading(doc, "12 Экспериментальные результаты");
    rows=[]
    with (ROOT/"data"/"results.csv").open(encoding="utf-8", newline="") as f:
        data=list(csv.DictReader(f))
    for r in data: rows.append([r["config"],r["run"],r["elapsed_ms"],r["total_bytes_sum"],r["free_bytes_sum"],r["used_percent_avg"],r["disks_count"]])
    table(doc,["Конфигурация","Запуск","мс","Всего, байт","Свободно, байт","Заполнение, %","Диски"],rows)
    heading(doc, "13 Графики и анализ результатов"); paragraph(doc, "На рисунке 1 показано время трёх запусков для каждой конфигурации. Изменение размеров файла не меняет алгоритмическую сложность перечисления дисков; небольшие колебания связаны с кэшем и фоновой активностью ОС.")
    if (ROOT/"diagrams"/"plot_time_vs_size.png").exists(): doc.add_picture(str(ROOT/"diagrams"/"plot_time_vs_size.png"), width=Inches(6.2)); caption(doc,"Рисунок 1 – Время анализа логических дисков")
    paragraph(doc, "На рисунке 2 сопоставлены ожидаемая и фактическая дельты свободного места. Отличие объясняется кластерным выделением, служебными структурами файловой системы и MFT NTFS. Поэтому фактическое уменьшение может быть кратно размеру кластера и не обязано совпадать с номинальным размером файла.")
    if (ROOT/"diagrams"/"plot_free_space_delta.png").exists(): doc.add_picture(str(ROOT/"diagrams"/"plot_free_space_delta.png"), width=Inches(6.2)); caption(doc,"Рисунок 2 – Изменение свободного места")
    heading(doc, "14 Заключение"); paragraph(doc, "Разработана консольная утилита анализа логических дисков Windows с прямым использованием обязательных API, экспортом CSV, журналированием, обработкой ошибок и тестами. Экспериментальные данные и графики сохранены в репозитории.")
    heading(doc, "15 Список использованных источников");
    for s in ["[1] Microsoft Learn. GetLogicalDriveStringsW [Электронный ресурс].", "[2] Microsoft Learn. GetDiskFreeSpaceExW [Электронный ресурс].", "[3] Microsoft Learn. GetVolumeInformationW [Электронный ресурс].", "[4] Microsoft Learn. System Error Codes [Электронный ресурс].", "[5] Matplotlib documentation [Электронный ресурс]."]: paragraph(doc,s)
    heading(doc, "ПРИЛОЖЕНИЕ А (обязательное) Использование искусственного интеллекта"); paragraph(doc,"Инструмент: GitHub Copilot (Visual Studio). Модель: точная версия модели недоступна в интерфейсе агента. Цель: автономное выполнение лабораторной работы по заданному промпту. Полученный результат: код проекта, тесты, скрипты, графики и отчёт. Место использования: src/*.cpp, src/*.h, Tests/tests.cpp, scripts/*.py, diagrams/*.puml, diagrams/*.md. Самостоятельная проверка: сборка, запуск тестов, ручная проверка CSV, визуальная проверка графиков, вычитка отчёта. Самостоятельные изменения: стили DOCX приведены к ЛР4; исправлены ошибки сборки и получение свободного места. Оригинальный текст промпта: полный текст запроса находится в истории чата Visual Studio Agent и должен быть перенесён студентом без сокращений при необходимости документальной проверки.")
    heading(doc, "ПРИЛОЖЕНИЕ Б (обязательное) Сведения о репозитории Git");
    try: head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(); log=subprocess.check_output(["git","log","--oneline"],cwd=ROOT,text=True).strip()
    except Exception: head="не определён"; log="не определён"
    paragraph(doc,"Ссылка: укажите ссылку на удалённый репозиторий. Финальный хеш на момент генерации: " + head); paragraph(doc,"Контрольные коммиты:\n" + log)
    heading(doc, "ПРИЛОЖЕНИЕ В (обязательное) Листинг кода программы");
    for name in ["disk_info.h","disk_info.cpp","csv_export.h","csv_export.cpp","logger.h","logger.cpp","error_utils.h","error_utils.cpp","main.cpp"]: paragraph(doc,name, None, 12, True, False); code_block(doc,ROOT/"src"/name)
    code_block(doc,ROOT/"Tests"/"tests.cpp")
    heading(doc, "ПРИЛОЖЕНИЕ Г (обязательное) Листинг кода графических материалов"); code_block(doc,ROOT/"scripts"/"run_experiments.py"); code_block(doc,ROOT/"scripts"/"plot_results.py")
    doc.save(OUT); print(f"saved {OUT}")

if __name__ == "__main__": main()
