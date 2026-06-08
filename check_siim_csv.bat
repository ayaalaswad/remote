@echo off
echo Checking SIIM directory structure...
echo.

set SIIM_PATH=C:\Users\aya.alaswad\Downloads\archive\siim-acr-pneumothorax

echo Listing all files in siim-acr-pneumothorax:
dir /b "%SIIM_PATH%"
echo.

echo Looking for CSV files:
dir /b "%SIIM_PATH%\*.csv"
echo.

echo Checking png_images folder (first 5 files):
dir /b "%SIIM_PATH%\png_images" | more +0
echo.

echo Total images in png_images:
dir /b "%SIIM_PATH%\png_images" | find /c /v ""
echo.

pause
