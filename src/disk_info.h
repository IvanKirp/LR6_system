#pragma once

#include <windows.h>
#include <string>
#include <vector>

enum class DriveType {
	Unknown,
	NoRootDirectory,
	Removable,
	Fixed,
	Remote,
	Cdrom,
	RamDisk
};

struct DiskRecord {
	std::wstring root;
	DriveType driveType = DriveType::Unknown;
	std::wstring fileSystem;
	std::wstring label;
	unsigned long long totalBytes = 0;
	unsigned long long freeBytes = 0;
	double usedPercent = 0.0;
	bool ok = false;
	DWORD lastError = ERROR_SUCCESS;
};

double CalcUsedPercent(unsigned long long totalBytes, unsigned long long freeBytes);
std::vector<DiskRecord> EnumerateDisks();
const wchar_t* DriveTypeName(DriveType type);
