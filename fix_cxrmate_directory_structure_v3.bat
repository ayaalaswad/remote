@echo off
REM Fix CXRMate directory structure - Version 3
REM Delete symlinks first, then copy actual files

echo ========================================
echo Fix CXRMate Directory Structure V3
echo ========================================
echo.
echo This will:
echo   1. Delete broken symlinks
echo   2. Copy actual CSV files
echo.
pause

REM Delete the broken symlinks
echo.
echo Deleting broken symlinks...
del "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-split.csv.gz" 2>nul
del "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-metadata.csv.gz" 2>nul

REM Delete and recreate sectioned directory
echo Removing old mimic_cxr_sectioned junction...
rmdir "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic_cxr_sectioned" 2>nul

echo.
echo Copying CSV files...
copy "D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz" "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\" /Y
copy "D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-metadata.csv.gz" "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\" /Y

echo.
echo Creating mimic_cxr_sectioned junction...
mklink /J "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic_cxr_sectioned" "D:\datasets\mimic-cxr-jpg\mimic_cxr_sectioned"

echo.
echo ========================================
echo Verifying Files
echo ========================================
echo.

dir "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\"

echo.
echo Checking file sizes (should NOT be 0 bytes):
echo.

dir "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\*.csv.gz"

echo.
pause
