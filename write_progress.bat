@echo off
REM Simple progress writer - Desktop only
REM Usage: call write_progress.bat "Message"

set PROGRESS_FILE=C:\Users\aya.alaswad\Desktop\sharp_progress.txt

REM Write with timestamp
echo [%DATE% %TIME%] %~1 >> "%PROGRESS_FILE%"
