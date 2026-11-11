#include "csv_export.h"

#include <fstream>
#include <sstream>

namespace {
std::string Utf8(const std::wstring& value) {
	if (value.empty()) return {};
	const int size = WideCharToMultiByte(CP_UTF8, 0, value.data(), static_cast<int>(value.size()), nullptr, 0, nullptr, nullptr);
	std::string result(size, '\0');
	WideCharToMultiByte(CP_UTF8, 0, value.data(), static_cast<int>(value.size()), result.data(), size, nullptr, nullptr);
	return result;
}
}

std::string CsvEscape(const std::string& value) {
	if (value.find_first_of(",\"\r\n") == std::string::npos) return value;
	std::string escaped = "\"";
	for (char c : value) escaped += c == '"' ? "\"\"" : std::string(1, c);
	return escaped + "\"";
}

bool ExportToCsv(const std::wstring& path, const std::vector<DiskRecord>& records, DWORD& errorCode) {
	std::ofstream output(path, std::ios::binary);
	if (!output) { errorCode = ERROR_OPEN_FAILED; return false; }
	output << "\xEF\xBB\xBFroot,drive_type,fs,label,total_bytes,free_bytes,used_percent,ok,error\n";
	for (const auto& record : records) {
		output << CsvEscape(Utf8(record.root)) << ','
				  << CsvEscape(Utf8(DriveTypeName(record.driveType))) << ','
			   << CsvEscape(Utf8(record.fileSystem)) << ','
			   << CsvEscape(Utf8(record.label)) << ','
			   << record.totalBytes << ',' << record.freeBytes << ','
			   << record.usedPercent << ',' << (record.ok ? "true" : "false") << ','
			   << record.lastError << '\n';
	}
	if (!output) { errorCode = ERROR_WRITE_FAULT; return false; }
	errorCode = ERROR_SUCCESS;
	return true;
}
