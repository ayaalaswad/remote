@echo off
REM Verify MIMIC-CXR data structure for Stage 2 preprocessing

echo ============================================
echo MIMIC-CXR Data Structure Verification
echo ============================================
echo.

echo [1] Checking MIMIC-CXR version...
echo.
if exist "D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz" (
    echo    Found: mimic-cxr-2.0.0-split.csv.gz
    echo    Version: 2.0.0
    set VERSION=2.0.0
) else if exist "D:\datasets\mimic-cxr-jpg\mimic-cxr-2.1.0-split.csv.gz" (
    echo    Found: mimic-cxr-2.1.0-split.csv.gz
    echo    Version: 2.1.0
    set VERSION=2.1.0
) else (
    echo    ERROR: No split CSV found in D:\datasets\mimic-cxr-jpg\
)
echo.

echo [2] Checking metadata file...
echo.
if exist "D:\datasets\mimic-cxr-jpg\mimic-cxr-%VERSION%-metadata.csv.gz" (
    echo    Found: mimic-cxr-%VERSION%-metadata.csv.gz
) else (
    echo    ERROR: Metadata CSV not found
)
echo.

echo [3] Checking image directory structure...
echo.
if exist "D:\datasets\mimic-cxr-jpg\files\p10\p10000032" (
    echo    Found: Image directory structure OK
    dir "D:\datasets\mimic-cxr-jpg\files\p10\p10000032" /b | findstr /C:"s"
) else (
    echo    ERROR: Image directory structure not found
)
echo.

echo [4] Checking report directory structure...
echo.
if exist "D:\datasets\mimic-cxr-reports\reports\files\p10\p10000032\s50414267" (
    echo    Found: Report directory exists
    echo    Listing files in this study:
    dir "D:\datasets\mimic-cxr-reports\reports\files\p10\p10000032\s50414267" /b
) else (
    echo    ERROR: Report directory not found
)
echo.

echo [5] Checking a sample report file content...
echo.
for %%f in ("D:\datasets\mimic-cxr-reports\reports\files\p10\p10000032\s50414267\*.txt") do (
    echo    Sample report content:
    echo    --------------------------------------------------
    type "%%f" | findstr /N "^" | findstr /R "^[1-9]:"
    echo    --------------------------------------------------
)
echo.

echo [6] Checking scene graph structure...
echo.
if exist "D:\datasets\mimic-ext-cxr-qba\scene_data" (
    echo    Found: Scene graph directory
) else (
    echo    ERROR: Scene graph directory not found
)
echo.

echo ============================================
echo Verification Complete
echo ============================================
echo.
pause
