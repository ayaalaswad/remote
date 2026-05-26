@echo off
REM Fix CXRMate directory structure by creating junctions/symlinks
REM
REM CXRMate expects: D:/datasets/physionet.org/files/mimic-cxr-jpg/2.0.0/
REM Actual location:  D:/datasets/mimic-cxr-jpg/
REM
REM Solution: Create directory junctions (like symlinks but for directories)

echo ========================================
echo Fix CXRMate Directory Structure
echo ========================================
echo.
echo This will create directory junctions so CXRMate can find files.
echo.
echo CXRMate expects:
echo   D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\
echo.
echo Your files are at:
echo   D:\datasets\mimic-cxr-jpg\
echo.
echo Solution: Create junction pointing to your actual data.
echo.
pause

REM Create the nested directory structure
echo Creating directory structure...
mkdir "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0" 2>nul

REM Create junction from expected path to actual path
echo.
echo Creating directory junction...
echo   From: D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\files
echo   To:   D:\datasets\mimic-cxr-jpg\files
echo.

mklink /J "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\files" "D:\datasets\mimic-cxr-jpg\files"

if %ERRORLEVEL% EQU 0 (
    echo ✓ Junction created successfully!
) else (
    echo ERROR: Failed to create junction
    echo Make sure you run this as Administrator
    pause
    exit /b 1
)

REM Also link the CSV files
echo.
echo Creating junction for CSV files...
mklink /J "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic_cxr_sectioned" "D:\datasets\mimic-cxr-jpg\mimic_cxr_sectioned"
mklink "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-split.csv.gz" "D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz"
mklink "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-metadata.csv.gz" "D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-metadata.csv.gz"

echo.
echo ========================================
echo Verifying Structure
echo ========================================
echo.

REM Verify the junction works
if exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\files\p10\p10000032" (
    echo ✓ Junction verified - files accessible!
    dir "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\files\p10\p10000032" /b | findstr "s"
) else (
    echo ERROR: Junction not working properly
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ Structure Fixed!
echo ========================================
echo.
echo Now update your config to use:
echo   dataset_dir: D:/datasets/physionet.org/files/mimic-cxr-jpg/2.0.0
echo.
echo Then run Stage 2 training again.
echo.
pause
