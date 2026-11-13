#include "../src/csv_export.h"
#include "../src/disk_info.h"
#include <cmath>
#include <fstream>
#include <iostream>
#include <string>
#include <cstdlib>
#include <filesystem>
#include <windows.h>

static std::filesystem::path GetSystemExecutablePath() {
    wchar_t modulePath[MAX_PATH]{};
    const DWORD length = GetModuleFileNameW(nullptr, modulePath, MAX_PATH);
    if (length == 0 || length == MAX_PATH) return {};
    return std::filesystem::path(modulePath).parent_path() / L"LR6_system.exe";
}

int main() {
    int passed = 0;
    int total = 5;
    std::cout << "Running LR6_system tests (5 total)\n\n";

    std::cout << "[1/5] ExportToCsv rejects an invalid output path\n";
    DWORD error = ERROR_SUCCESS;
    const bool invalidPathRejected = !ExportToCsv(L"Z:\\invalid\\lab06.csv", {}, error) && error != ERROR_SUCCESS;
    if (invalidPathRejected) {
        ++passed;
        std::cout << "  PASS: export failed with error code " << error << "\n\n";
    } else {
        std::cerr << "  FAIL: invalid path was accepted or no error was returned\n\n";
    }

    const std::filesystem::path systemExecutable = GetSystemExecutablePath();
    std::cout << "[2/5] CLI rejects --csv without a following file path\n";
    std::cout << "  Executable: " << systemExecutable.string() << "\n";
    const std::wstring command = L"\"" + systemExecutable.wstring() + L"\" --csv > missing_csv_arg.txt 2>&1";
    const int cliCode = _wsystem(command.c_str());
    std::ifstream usage("missing_csv_arg.txt");
    std::string usageText((std::istreambuf_iterator<char>(usage)), std::istreambuf_iterator<char>());
    const bool cliRejectedArgument = cliCode != 0 && usageText.find("Usage") != std::string::npos;
    std::cout << "  Exit code: " << cliCode << "\n";
    std::cout << "  Output: " << usageText;
    if (cliRejectedArgument) {
        ++passed;
        std::cout << "  PASS: command was rejected and Usage was displayed\n\n";
    } else {
        std::cerr << "  FAIL: expected a non-zero exit code and Usage in the output\n\n";
    }

    std::cout << "[3/5] CalcUsedPercent handles division by zero\n";
    const double zeroPercentage = CalcUsedPercent(0, 0);
    if (zeroPercentage == 0.0) {
        ++passed;
        std::cout << "  PASS: result = " << zeroPercentage << "\n\n";
    } else {
        std::cerr << "  FAIL: expected 0, got " << zeroPercentage << "\n\n";
    }

    std::cout << "[4/5] CalcUsedPercent calculates the used percentage\n";
    const double percentage = CalcUsedPercent(100, 50);
    if (std::abs(percentage - 50.0) < 1e-9) {
        ++passed;
        std::cout << "  PASS: result = " << percentage << "%\n\n";
    } else {
        std::cerr << "  FAIL: expected 50, got " << percentage << "\n\n";
    }

    std::cout << "[5/5] CsvEscape quotes fields containing commas and quotes\n";
    const std::string escaped = CsvEscape("label, \"quoted\"");
    const std::string expected = "\"label, \"\"quoted\"\"\"";
    if (escaped == expected) {
        ++passed;
        std::cout << "  PASS: result = " << escaped << "\n\n";
    } else {
        std::cerr << "  FAIL: expected " << expected << ", got " << escaped << "\n\n";
    }

    std::cout << "Result: " << passed << "/" << total << " tests passed\n";
    return passed == total ? 0 : 1;
}
