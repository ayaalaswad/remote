@echo off
REM Find original SHARP R@1 from training logs

echo ========================================
echo   Finding SHARP Baseline R@1
echo ========================================
echo.

set SHARP_DIR=D:\experiments\exp3_full_sharp

if not exist "%SHARP_DIR%" (
    echo [ERROR] SHARP directory not found: %SHARP_DIR%
    echo.
    pause
    exit /b 1
)

echo Searching for R@1 metrics in SHARP training logs...
echo.

REM Search for R@1 in logs
echo === Checking training.log ===
if exist "%SHARP_DIR%\training.log" (
    findstr /i "R@1" "%SHARP_DIR%\training.log" | more
) else (
    echo training.log not found
)

echo.
echo === Checking p3_history.json ===
if exist "%SHARP_DIR%\p3_history.json" (
    findstr /i "R@1" "%SHARP_DIR%\p3_history.json" | more
) else (
    echo p3_history.json not found
)

echo.
echo === Checking for any log files ===
dir /b "%SHARP_DIR%\*.log" 2>nul
dir /b "%SHARP_DIR%\*.json" 2>nul

echo.
echo === Available files in SHARP directory ===
dir /b "%SHARP_DIR%" 2>nul | more

echo.
pause
