#include "csv_export.h"
#include "disk_info.h"
#include "logger.h"
#include "error_utils.h"
#include <windows.h>
#include <iostream>
#include <string>

static void Usage() { std::wcout << L"Usage: LR6_system.exe --csv <path> [--runs N]\n"; }
int wmain(int argc, wchar_t* argv[]) {
	std::wstring csvPath;
	int runs = 1;
	for (int i = 1; i < argc; ++i) {
		std::wstring arg = argv[i];
		if (arg == L"--help") { Usage(); return 0; }
		if (arg == L"--csv" && i + 1 < argc) { csvPath = argv[++i]; continue; }
		if (arg == L"--runs" && i + 1 < argc) { runs = _wtoi(argv[++i]); continue; }
		Usage(); return 2;
	}
	if (csvPath.empty() || runs < 1) { Usage(); return 2; }
	Logger logger(L"lab06.log");
	LARGE_INTEGER frequency{}, start{}, finish{};
	QueryPerformanceFrequency(&frequency);
	for (int run = 1; run <= runs; ++run) {
		QueryPerformanceCounter(&start);
		const auto records = EnumerateDisks();
		DWORD error = ERROR_SUCCESS;
		const bool exported = ExportToCsv(csvPath, records, error);
		QueryPerformanceCounter(&finish);
		const double elapsed = (finish.QuadPart - start.QuadPart) * 1000.0 / frequency.QuadPart;
		logger.Write("ENUMERATE", "run", std::to_string(run), exported, error);
		std::wcout << L"run=" << run << L" disks=" << records.size() << L" elapsed_ms=" << elapsed << L"\n";
		if (!exported) { std::wcerr << L"CSV error " << error << L": " << FormatLastError(error) << L"\n"; return 1; }
	}
	return 0;
}
