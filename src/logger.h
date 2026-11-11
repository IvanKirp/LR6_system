#pragma once
#include <string>
class Logger {
public:
	explicit Logger(const std::wstring& path);
	void Write(const std::string& operation, const std::string& key, const std::string& value, bool ok, unsigned long error = 0);
private:
	std::wstring path_;
};
