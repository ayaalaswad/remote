@echo off
REM Stage 2 Preprocessing: Prepare MIMIC-CXR for CXRMate (Option A - Proper)
REM
REM This extracts report sections and creates the required CSV files.
REM Takes 30-60 minutes.

echo ============================================================================
echo Stage 2 Preprocessing: Option A (Proper)
echo ============================================================================
echo.
echo This will:
echo   1. Extract Findings/Impression sections from ~370,000 reports
echo   2. Create mimic_cxr_sectioned.csv
echo   3. Merge splits + metadata + reports into splits_reports_metadata.csv
echo   4. Create directory structure matching CXRMate expectations
echo.
echo Estimated time: 30-60 minutes
echo.
echo Results will be fair and valid (proper section extraction).
echo.
pause

python preprocess_mimic_for_cxrmate.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================================
    echo Preprocessing Successful!
    echo ============================================================================
    echo.
    echo Files created:
    echo   - D:\datasets\mimic_cxr_sections\mimic_cxr_sectioned.csv
    echo   - D:\datasets\mimic_cxr_merged\splits_reports_metadata.csv
    echo   - D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\
    echo.
    echo Configs already updated to use dataset_dir: D:/datasets
    echo.
    echo Next step: Run Stage 2 training
    echo   cd C:\Users\aya.alaswad\remote\stage2_training
    echo   run_exp1_exp3.bat
    echo.
) else (
    echo.
    echo ============================================================================
    echo ERROR: Preprocessing failed
    echo ============================================================================
    echo.
    echo Check the error messages above.
    echo.
)

pause
