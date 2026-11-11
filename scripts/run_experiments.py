from pathlib import Path
import csv
import os
import subprocess
import sys
import time
import shutil

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EXE = ROOT / "system" / "x64" / "Release" / "LR6_system.exe"
SIZES = [("baseline", 0), ("10", 10), ("50", 50), ("100", 100)]


def free_bytes(path: Path) -> int:
    return shutil.disk_usage(path).free


def parse_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    if not EXE.exists():
        raise SystemExit(f"Executable not found: {EXE}")
    DATA.mkdir(exist_ok=True)
    results = []
    for config, size_mb in SIZES:
        test_file = DATA / f"testfile_{size_mb}mb.bin" if size_mb else None
        before = free_bytes(DATA)
        if test_file:
            with test_file.open("wb") as stream:
                remaining = size_mb * 1024 * 1024
                block = b"LR6" * (1024 * 1024 // 3)
                while remaining:
                    chunk = block[:min(len(block), remaining)]
                    stream.write(chunk)
                    remaining -= len(chunk)
        after_create = free_bytes(DATA)
        actual_delta = before - after_create if test_file else 0
        for run in range(1, 4):
            csv_path = DATA / f"disks_{config}_run{run}.csv"
            start = time.perf_counter()
            subprocess.run([str(EXE), "--csv", str(csv_path), "--runs", "1"], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            rows = parse_csv(csv_path)
            valid = [row for row in rows if row["ok"].lower() == "true"]
            total_sum = sum(int(row["total_bytes"]) for row in valid)
            free_sum = sum(int(row["free_bytes"]) for row in valid)
            used_avg = sum(float(row["used_percent"]) for row in valid) / len(valid) if valid else 0.0
            results.append({"config": config, "run": run, "elapsed_ms": f"{elapsed_ms:.3f}", "total_bytes_sum": total_sum, "free_bytes_sum": free_sum, "used_percent_avg": f"{used_avg:.6f}", "disks_count": len(rows), "file_size_bytes": size_mb * 1024 * 1024, "free_before_bytes": before, "free_after_create_bytes": after_create, "free_delta_bytes": actual_delta, "expected_delta_bytes": size_mb * 1024 * 1024})
        if test_file:
            test_file.unlink()
    with (DATA / "results.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = list(results[0])
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    print(f"Wrote {len(results)} rows to {DATA / 'results.csv'}")


if __name__ == "__main__":
    main()
