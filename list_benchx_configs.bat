@echo off
REM List all BenchX classification configs

echo ============================================
echo BenchX Classification Configs
echo ============================================
echo.

cd C:\Users\aya.alaswad\remote\BenchX\configs\classification

echo Available datasets:
dir /AD /B
echo.

echo Looking for SIIM configs:
if exist SIIM (
    echo [FOUND] SIIM directory
    dir /B SIIM\*.yml 2>nul
) else (
    echo [NOT FOUND] SIIM directory
)
echo.

echo Looking for RSNA configs:
if exist RSNA (
    echo [FOUND] RSNA directory
    dir /B RSNA\*.yml 2>nul
) else (
    echo [NOT FOUND] RSNA directory
)
echo.

echo Listing one working example (NIH):
if exist NIH (
    echo [Example NIH config]:
    type NIH\convirt.yml 2>nul | more
)

pause
