#include "error_utils.h"
#include <iostream>

std::wstring FormatLastError(DWORD errorCode) {
	wchar_t* buffer = nullptr;
	const DWORD length = FormatMessageW(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
		nullptr, errorCode, 0, reinterpret_cast<LPWSTR>(&buffer), 0, nullptr);
	std::wstring result = length ? std::wstring(buffer, length) : L"Unknown error";
	if (buffer) LocalFree(buffer);
	while (!result.empty() && (result.back() == L'\r' || result.back() == L'\n')) result.pop_back();
	return result;
}

bool CheckWin32(BOOL result, const wchar_t* functionName, const wchar_t* operation) {
	if (result) return true;
	const DWORD error = GetLastError();
	std::wcerr << L"ERROR function=" << functionName << L" code=" << error << L" description=" << FormatLastError(error) << L" operation=" << operation << L"\n";
	return false;
}
