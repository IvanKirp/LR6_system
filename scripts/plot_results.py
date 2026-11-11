from pathlib import Path
import csv
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "diagrams"
OUT.mkdir(exist_ok=True)
with (DATA / "results.csv").open(encoding="utf-8", newline="") as stream:
    rows = list(csv.DictReader(stream))
configs = ["baseline", "10", "50", "100"]
labels = ["baseline", "10 МБ", "50 МБ", "100 МБ"]
fig, ax = plt.subplots(figsize=(9, 5))
for run in ("1", "2", "3"):
    values = [float(next(r["elapsed_ms"] for r in rows if r["config"] == c and r["run"] == run)) for c in configs]
    ax.plot(labels, values, marker="o", label=f"Запуск {run}")
ax.set_title("Время анализа логических дисков")
ax.set_xlabel("Конфигурация")
ax.set_ylabel("Время выполнения, мс")
ax.grid(True, alpha=.3)
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "plot_time_vs_size.png", dpi=150)
plt.close(fig)

sizes = [10, 50, 100]
expected = [s * 1024 * 1024 for s in sizes]
actual = [float(next(r["free_delta_bytes"] for r in rows if r["config"] == str(s) and r["run"] == "1")) for s in sizes]
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(sizes, expected, marker="o", label="Ожидаемое уменьшение")
ax.plot(sizes, actual, marker="s", label="Фактическая дельта")
ax.set_title("Изменение свободного места")
ax.set_xlabel("Размер файла, МБ")
ax.set_ylabel("Уменьшение свободного места, байты")
ax.grid(True, alpha=.3)
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "plot_free_space_delta.png", dpi=150)
plt.close(fig)
print("Plots written to", OUT)
