@echo off
cd C:\Users\aya.alaswad\remote\BenchX
echo Searching for SHARP_LP directories...
dir experiments\classification\rsna /s /b | findstr /i "SHARP_LP"
echo.
echo Searching for recent .pth files...
dir experiments\classification\rsna\*.pth /s /b 2>nul
echo.
pause
