#include "disk_info.h"

#include <algorithm>
#include <vector>

namespace {
DriveType ToDriveType(UINT type) {
	switch (type) {
	case DRIVE_REMOVABLE: return DriveType::Removable;
	case DRIVE_FIXED: return DriveType::Fixed;
	case DRIVE_REMOTE: return DriveType::Remote;
	case DRIVE_CDROM: return DriveType::Cdrom;
	case DRIVE_RAMDISK: return DriveType::RamDisk;
	case DRIVE_NO_ROOT_DIR: return DriveType::NoRootDirectory;
	default: return DriveType::Unknown;
	}
}
}

double CalcUsedPercent(unsigned long long totalBytes, unsigned long long freeBytes) {
	if (totalBytes == 0) return 0.0;
	const auto used = totalBytes > freeBytes ? totalBytes - freeBytes : 0ULL;
	return static_cast<double>(used) * 100.0 / static_cast<double>(totalBytes);
}

std::vector<DiskRecord> EnumerateDisks() {
	const DWORD length = GetLogicalDriveStringsW(0, nullptr);
	if (length == 0) return {};
	std::vector<wchar_t> buffer(length + 1);
	if (GetLogicalDriveStringsW(static_cast<DWORD>(buffer.size()), buffer.data()) == 0) return {};

	std::vector<DiskRecord> result;
	for (const wchar_t* current = buffer.data(); *current != L'\0'; current += wcslen(current) + 1) {
		DiskRecord record;
		record.root = current;
		record.driveType = ToDriveType(GetDriveTypeW(current));
		wchar_t label[MAX_PATH] = {};
		wchar_t fileSystem[MAX_PATH] = {};
		if (!GetVolumeInformationW(current, label, MAX_PATH, nullptr, nullptr, nullptr, fileSystem, MAX_PATH)) {
			record.lastError = GetLastError();
		} else {
			record.label = label;
			record.fileSystem = fileSystem;
		}
		ULARGE_INTEGER freeBytes = {}, totalBytes = {}, totalFreeBytes = {};
		if (GetDiskFreeSpaceExW(current, &freeBytes, &totalBytes, &totalFreeBytes)) {
			record.totalBytes = totalBytes.QuadPart;
			record.freeBytes = freeBytes.QuadPart;
			record.usedPercent = CalcUsedPercent(record.totalBytes, record.freeBytes);
			record.ok = true;
			record.lastError = ERROR_SUCCESS;
		} else {
			record.lastError = GetLastError();
		}
		result.push_back(std::move(record));
	}
	return result;
}

const wchar_t* DriveTypeName(DriveType type) {
	switch (type) {
	case DriveType::Removable: return L"removable";
	case DriveType::Fixed: return L"fixed";
	case DriveType::Remote: return L"remote";
	case DriveType::Cdrom: return L"cdrom";
	case DriveType::RamDisk: return L"ramdisk";
	case DriveType::NoRootDirectory: return L"no_root";
	default: return L"unknown";
	}
}
