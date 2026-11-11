#include "logger.h"
#include "error_utils.h"
#include <chrono>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>

Logger::Logger(const std::wstring& path) : path_(path) {}
void Logger::Write(const std::string& operation, const std::string& key, const std::string& value, bool ok, unsigned long error) {
	const auto now = std::chrono::system_clock::now();
	const auto millis = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;
	const std::time_t time = std::chrono::system_clock::to_time_t(now);
	std::tm local{};
	localtime_s(&local, &time);
	std::ostringstream line;
	line << '[' << std::put_time(&local, "%H:%M:%S") << '.' << std::setfill('0') << std::setw(3) << millis.count() << "] "
		 << operation << " " << key << '=' << value << " status=" << (ok ? "OK" : "FAIL");
	if (!ok) line << " err=" << error;
	line << '\n';
	std::cout << line.str();
	std::ofstream file(path_, std::ios::app);
	file << line.str();
}
