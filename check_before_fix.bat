@echo off
REM Check what exists before running the fix

echo ========================================
echo Pre-Fix Diagnostic Check
echo ========================================
echo.

echo [1] Checking source files exist...
echo.

if exist "D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz" (
    echo ✓ Source split.csv.gz exists
    for %%A in ("D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz") do echo    Size: %%~zA bytes
) else (
    echo ✗ Source split.csv.gz NOT FOUND
)

if exist "D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-metadata.csv.gz" (
    echo ✓ Source metadata.csv.gz exists
    for %%A in ("D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-metadata.csv.gz") do echo    Size: %%~zA bytes
) else (
    echo ✗ Source metadata.csv.gz NOT FOUND
)

if exist "D:\datasets\mimic-cxr-jpg\mimic_cxr_sectioned\mimic_cxr_sectioned.csv" (
    echo ✓ Source sectioned CSV exists
    for %%A in ("D:\datasets\mimic-cxr-jpg\mimic_cxr_sectioned\mimic_cxr_sectioned.csv") do echo    Size: %%~zA bytes
) else (
    echo ✗ Source sectioned CSV NOT FOUND
)

if exist "D:\datasets\mimic_cxr_merged\splits_reports_metadata.csv" (
    echo ✓ Merged CSV exists
    for %%A in ("D:\datasets\mimic_cxr_merged\splits_reports_metadata.csv") do echo    Size: %%~zA bytes
) else (
    echo ✗ Merged CSV NOT FOUND
)

echo.
echo [2] Checking current symlinks/junctions...
echo.

if exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\files" (
    echo ✓ files junction exists
) else (
    echo ✗ files junction NOT FOUND
)

if exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-split.csv.gz" (
    echo ? split.csv.gz symlink exists
    for %%A in ("D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-split.csv.gz") do (
        if %%~zA EQU 0 (
            echo    WARNING: Size is 0 bytes - BROKEN SYMLINK
        ) else (
            echo    Size: %%~zA bytes - OK
        )
    )
) else (
    echo - split.csv.gz does not exist yet
)

if exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-metadata.csv.gz" (
    echo ? metadata.csv.gz symlink exists
    for %%A in ("D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-metadata.csv.gz") do (
        if %%~zA EQU 0 (
            echo    WARNING: Size is 0 bytes - BROKEN SYMLINK
        ) else (
            echo    Size: %%~zA bytes - OK
        )
    )
) else (
    echo - metadata.csv.gz does not exist yet
)

echo.
echo [3] Checking what CXRMate needs...
echo.

echo CXRMate dataset_dir: D:/datasets/physionet.org/files/mimic-cxr-jpg/2.0.0
echo.
echo CXRMate will look for:
echo   - D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-split.csv.gz
echo   - D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-metadata.csv.gz
echo   - D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\files\
echo   - D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic_cxr_sectioned\
echo.
echo CXRMate might also look for (in parent directories):
echo   - D:\datasets\mimic_cxr_merged\splits_reports_metadata.csv
echo   - OR D:\datasets\physionet.org\files\mimic-cxr-jpg\mimic_cxr_merged\splits_reports_metadata.csv
echo.

echo [4] Potential issues:
echo.

REM Check if merged CSV is accessible from CXRMate's perspective
if not exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\mimic_cxr_merged" (
    echo ! mimic_cxr_merged not in CXRMate's parent directory
    echo   Location: D:\datasets\mimic_cxr_merged\
    echo   CXRMate might look for: D:\datasets\physionet.org\files\mimic-cxr-jpg\mimic_cxr_merged\
    echo   SOLUTION: Need to create junction or copy this too
    echo.
)

echo ========================================
echo Recommendation
echo ========================================
echo.
echo Run fix_cxrmate_directory_structure_v3.bat to:
echo   1. Delete broken symlinks
echo   2. Copy CSV files with proper sizes
echo.
echo ALSO need to make mimic_cxr_merged accessible to CXRMate
echo.
pause
