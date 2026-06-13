@echo off
REM ============================================================================
REM Check Status of All Running/Completed Training Experiments
REM ============================================================================

echo ========================================
echo   Training Status Check
echo ========================================
echo.

REM ============================================================================
REM 1. Check for Python processes (indicates training is running)
REM ============================================================================
echo [1/4] Checking for active Python training processes...
echo.

tasklist /FI "IMAGENAME eq python.exe" /FO TABLE 2>nul | find "python.exe" >nul
if %errorlevel% EQU 0 (
    echo [RUNNING] Python processes found:
    tasklist /FI "IMAGENAME eq python.exe" /FO TABLE
    echo.
    echo Training is likely still running in background.
) else (
    echo [IDLE] No Python processes running.
    echo All training has either completed or crashed.
)
echo.

REM ============================================================================
REM 2. Check SIIM Training Status
REM ============================================================================
echo [2/4] SIIM Training Status
echo ========================================
echo.

set SIIM_DIR=C:\Users\aya.alaswad\remote\BenchX\experiments\classification\siim

REM Check each split
for %%S in (SHARP_1pct SHARP_10pct SHARP_100pct) do (
    echo Checking %%S...

    if exist "%SIIM_DIR%\%%S" (
        REM Find latest checkpoint
        dir /B /O:D "%SIIM_DIR%\%%S\%%S\*.pth" 2>nul | find /C ".pth" >nul
        if %errorlevel% EQU 0 (
            echo   [OK] Checkpoints found
            for /F "delims=" %%F in ('dir /B /O:-D "%SIIM_DIR%\%%S\%%S\*.pth" 2^>nul ^| findstr /R "^[0-9]"') do (
                echo   Latest: %%F
                goto :next_siim
            )
            :next_siim
        ) else (
            echo   [MISSING] No checkpoints found
        )

        REM Check log file for completion
        if exist "%SIIM_DIR%\%%S\%%S\42.log" (
            findstr /C:"Early stopping" "%SIIM_DIR%\%%S\%%S\42.log" >nul 2>&1
            if %errorlevel% EQU 0 (
                echo   [COMPLETE] Training completed with early stopping
            ) else (
                findstr /C:"Epoch 50" "%SIIM_DIR%\%%S\%%S\42.log" >nul 2>&1
                if %errorlevel% EQU 0 (
                    echo   [COMPLETE] Training completed all 50 epochs
                ) else (
                    echo   [UNKNOWN] Check log manually
                )
            )
        ) else (
            echo   [MISSING] No log file found
        )
    ) else (
        echo   [NOT STARTED] Directory does not exist
    )
    echo.
)

REM ============================================================================
REM 3. Check RSNA Linear Probe Status
REM ============================================================================
echo [3/4] RSNA Linear Probe Status
echo ========================================
echo.

set RSNA_LP_DIR=C:\Users\aya.alaswad\remote\BenchX\experiments\classification\rsna\SHARP_LP

if exist "%RSNA_LP_DIR%" (
    echo Directory exists: %RSNA_LP_DIR%

    REM Find latest checkpoint
    dir /B /O:D "%RSNA_LP_DIR%\SHARP_LP\*.pth" 2>nul | find /C ".pth" >nul
    if %errorlevel% EQU 0 (
        echo [OK] Checkpoints found
        for /F "delims=" %%F in ('dir /B /O:-D "%RSNA_LP_DIR%\SHARP_LP\*.pth" 2^>nul ^| findstr /R "^[0-9]"') do (
            echo Latest: %%F
            goto :next_rsna
        )
        :next_rsna
    ) else (
        echo [MISSING] No checkpoints found
    )

    REM Check log for completion
    if exist "%RSNA_LP_DIR%\SHARP_LP\42.log" (
        findstr /C:"Early stopping" "%RSNA_LP_DIR%\SHARP_LP\42.log" >nul 2>&1
        if %errorlevel% EQU 0 (
            echo [COMPLETE] Training completed with early stopping
        ) else (
            findstr /C:"Epoch 30" "%RSNA_LP_DIR%\SHARP_LP\42.log" >nul 2>&1
            if %errorlevel% EQU 0 (
                echo [COMPLETE] Training completed all 30 epochs
            ) else (
                echo [UNKNOWN] Check log manually
            )
        )
    ) else (
        echo [MISSING] No log file found
    )
) else (
    echo [NOT STARTED] Linear probe not started yet
)
echo.

REM ============================================================================
REM 4. Check RadDINO Training Status
REM ============================================================================
echo [4/4] RadDINO Training Status
echo ========================================
echo.

set RADDINO_DIR=D:\experiments\exp_raddino_hardneg

if exist "%RADDINO_DIR%" (
    echo Directory exists: %RADDINO_DIR%

    REM Check for checkpoints
    if exist "%RADDINO_DIR%\p3_best.pt" (
        echo [OK] Best checkpoint exists: p3_best.pt

        REM Get checkpoint info
        python -c "import torch; ckpt=torch.load(r'%RADDINO_DIR%\p3_best.pt', map_location='cpu'); print(f'  Step: {ckpt[\"step\"]:,}'); print(f'  Best R@1: {ckpt.get(\"best_r1\", \"N/A\")}')" 2>nul

    ) else (
        echo [MISSING] No best checkpoint found
    )

    if exist "%RADDINO_DIR%\p3_last.pt" (
        echo [OK] Last checkpoint exists: p3_last.pt

        REM Get checkpoint info
        python -c "import torch; ckpt=torch.load(r'%RADDINO_DIR%\p3_last.pt', map_location='cpu'); print(f'  Step: {ckpt[\"step\"]:,}'); print(f'  Current R@1: {ckpt.get(\"r1\", \"N/A\")}')" 2>nul

    ) else (
        echo [MISSING] No last checkpoint found
    )

    REM Check training log
    if exist "%RADDINO_DIR%\training.log" (
        echo [OK] Training log exists

        REM Check if training completed
        findstr /C:"Training complete" "%RADDINO_DIR%\training.log" >nul 2>&1
        if %errorlevel% EQU 0 (
            echo [COMPLETE] Training finished
        ) else (
            REM Check latest step
            echo [IN PROGRESS or STOPPED] Last few lines:
            powershell -Command "Get-Content '%RADDINO_DIR%\training.log' -Tail 5"
        )
    ) else (
        echo [MISSING] No training log found
    )
) else (
    echo [NOT STARTED] RadDINO experiment not started yet
)
echo.

REM ============================================================================
REM Summary and Next Steps
REM ============================================================================
echo ========================================
echo   Summary
echo ========================================
echo.

echo To view detailed results:
echo.
echo SIIM:
echo   - Logs: %SIIM_DIR%\SHARP_*\SHARP_*\42.log
echo   - Metrics: %SIIM_DIR%\SHARP_*\SHARP_*\val_42_metrics.txt
echo.
echo RSNA Linear Probe:
echo   - Log: %RSNA_LP_DIR%\SHARP_LP\42.log
echo   - Metrics: %RSNA_LP_DIR%\SHARP_LP\val_42_metrics.txt
echo.
echo RadDINO:
echo   - Log: %RADDINO_DIR%\training.log
echo   - History: %RADDINO_DIR%\p3_history.json
echo.

echo To resume any stopped training:
echo   - SIIM: run_siim_all_splits.bat
echo   - RSNA LP: (see LINEAR_PROBE_COMPARISON.md)
echo   - RadDINO: resume_raddino.bat
echo.

pause
