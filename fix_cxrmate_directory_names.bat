@echo off
REM Fix directory names to match what CXRMate expects

echo ========================================
echo Fix CXRMate Directory Names
echo ========================================
echo.
echo CXRMate expects: mimic_cxr_sections (plural)
echo We created:      mimic_cxr_sectioned (with 'ed')
echo.
echo This will:
echo   1. Remove old junction
echo   2. Create new junction with correct name
echo.
pause

REM Remove old mimic_cxr_sectioned junction
echo Removing old mimic_cxr_sectioned junction...
rmdir "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic_cxr_sectioned" 2>nul

REM Create new mimic_cxr_sections junction (note the 's' at end)
echo Creating mimic_cxr_sections junction (correct name)...
mklink /J "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic_cxr_sections" "D:\datasets\mimic-cxr-jpg\mimic_cxr_sectioned"

echo.
echo Verifying...
if exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic_cxr_sections\mimic_cxr_sectioned.csv" (
    echo ✓ mimic_cxr_sections/mimic_cxr_sectioned.csv accessible
) else (
    echo ✗ File not accessible - check junction
)

echo.
echo Also checking if we need parent-level directory...
echo CXRMate might also look in parent directories
echo.

REM Check if we need mimic_cxr_sections at parent level too
if not exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\mimic_cxr_sections" (
    echo Creating parent-level mimic_cxr_sections junction...
    mklink /J "D:\datasets\physionet.org\files\mimic-cxr-jpg\mimic_cxr_sections" "D:\datasets\mimic-cxr-jpg\mimic_cxr_sectioned"
)

echo.
echo Complete!
pause
