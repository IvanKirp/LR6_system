#pragma once

#include "disk_info.h"
#include <string>
#include <vector>

std::string CsvEscape(const std::string& value);
bool ExportToCsv(const std::wstring& path, const std::vector<DiskRecord>& records, DWORD& errorCode);
