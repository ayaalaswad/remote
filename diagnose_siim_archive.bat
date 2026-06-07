@echo off
echo ========================================
echo SIIM Archive Diagnostic
echo ========================================
echo.

echo Checking: C:\Users\aya.alaswad\Downloads\archive\
echo.

echo All files and directories:
dir C:\Users\aya.alaswad\Downloads\archive\ /b
echo.

echo.
echo CSV files specifically:
dir C:\Users\aya.alaswad\Downloads\archive\*.csv /b 2>nul
echo.

echo.
echo Is png_images extracted?
if exist "C:\Users\aya.alaswad\Downloads\archive\png_images" (
    echo YES - png_images directory exists
    dir C:\Users\aya.alaswad\Downloads\archive\png_images\*.png | find /c ".png"
) else (
    echo NO - png_images directory not found
)
echo.

echo Is png_masks extracted?
if exist "C:\Users\aya.alaswad\Downloads\archive\png_masks" (
    echo YES - png_masks directory exists
) else (
    echo NO - png_masks directory not found
)
echo.

echo ========================================
echo.
echo If you see a .zip file above, the archive needs to be extracted first!
echo If you see png_images and csv files, we can proceed.
echo.
pause
