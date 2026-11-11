#pragma once
#include <windows.h>
#include <string>
std::wstring FormatLastError(DWORD errorCode);
bool CheckWin32(BOOL result, const wchar_t* functionName, const wchar_t* operation);
