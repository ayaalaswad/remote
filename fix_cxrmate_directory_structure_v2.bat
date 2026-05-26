@echo off
REM Fix CXRMate directory structure - Version 2 (Copy files instead of symlink)
REM More reliable on Windows

echo ========================================
echo Fix CXRMate Directory Structure V2
echo ========================================
echo.
echo This will COPY CSV files to the expected location.
echo (More reliable than symlinks on Windows)
echo.
pause

REM Create the directory structure
echo Creating directory structure...
mkdir "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0" 2>nul

REM Copy CSV files (instead of symlinking)
echo.
echo Copying CSV files...
echo   From: D:\datasets\mimic-cxr-jpg\
echo   To:   D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\
echo.

copy "D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz" "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\"
copy "D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-metadata.csv.gz" "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\"

REM Copy or link the sectioned directory
echo.
echo Copying sectioned reports directory...
xcopy "D:\datasets\mimic-cxr-jpg\mimic_cxr_sectioned" "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic_cxr_sectioned\" /E /I /Y

REM The files junction should already exist from v1 script
if not exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\files" (
    echo.
    echo Creating files junction...
    mklink /J "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\files" "D:\datasets\mimic-cxr-jpg\files"
)

echo.
echo ========================================
echo Verifying Files
echo ========================================
echo.

REM Check files exist
if exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-split.csv.gz" (
    echo ✓ split.csv.gz found
) else (
    echo ✗ split.csv.gz NOT FOUND
)

if exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-metadata.csv.gz" (
    echo ✓ metadata.csv.gz found
) else (
    echo ✗ metadata.csv.gz NOT FOUND
)

if exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\files\p10" (
    echo ✓ files directory accessible
) else (
    echo ✗ files directory NOT accessible
)

if exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic_cxr_sectioned\mimic_cxr_sectioned.csv" (
    echo ✓ sectioned reports found
) else (
    echo ✗ sectioned reports NOT FOUND
)

echo.
echo ========================================
echo Complete!
echo ========================================
echo.

dir "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\"

echo.
pause
