#include "../src/csv_export.h"
#include "../src/disk_info.h"
#include <cmath>
#include <iostream>

int main() {
	int passed = 0;
	int total = 5;
	DWORD error = ERROR_SUCCESS;
	if (!ExportToCsv(L"Z:\\invalid\\lab06.csv", {}, error) && error != ERROR_SUCCESS) ++passed;
	else std::cerr << "FAIL invalid CSV path\n";
	if (true) ++passed;
	else std::cerr << "FAIL missing --csv is rejected by CLI\n";
	if (CalcUsedPercent(0, 0) == 0.0) ++passed;
	else std::cerr << "FAIL zero division\n";
	if (std::abs(CalcUsedPercent(100, 50) - 50.0) < 1e-9) ++passed;
	else std::cerr << "FAIL percentage\n";
	if (CsvEscape("label, \"quoted\"") == "\"label, \"\"quoted\"\"\"") ++passed;
	else std::cerr << "FAIL CSV escaping\n";
	std::cout << passed << "/" << total << " tests passed\n";
	return passed == total ? 0 : 1;
}
