@echo off
echo Searching for RSNA experiment results...
echo.

cd C:\Users\aya.alaswad\remote\BenchX

echo === Searching for SHARP directories ===
dir experiments\classification\rsna /s /b 2>nul | findstr /i "SHARP"

echo.
echo === Searching for .pth checkpoints ===
dir experiments\classification\rsna\*.pth /s /b 2>nul

echo.
echo === Searching for metrics files ===
dir experiments\classification\rsna\*metrics.txt /s /b 2>nul

echo.
pause
