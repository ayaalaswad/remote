@echo off
REM Run Stage 2 preprocessing to create missing CSV files

echo ========================================
echo Stage 2 Preprocessing - CSV Creation
echo ========================================
echo.
echo This will create:
echo   1. D:\datasets\mimic-cxr-jpg\mimic_cxr_sectioned\mimic_cxr_sectioned.csv
echo   2. D:\datasets\mimic_cxr_merged\splits_reports_metadata.csv
echo.
echo This will take approximately 15-30 minutes depending on dataset size.
echo.
pause

python create_stage2_csvs.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Preprocessing completed successfully!
    echo ========================================
    echo.
    echo You can now run Stage 2 training:
    echo   cd stage2_training
    echo   run_exp1_exp3.bat
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR: Preprocessing failed
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause
