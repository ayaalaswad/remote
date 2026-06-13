@echo off
REM ============================================================================
REM Auto-Resume All Unfinished Training (FULLY AUTOMATED)
REM ============================================================================
REM
REM This version runs completely automated without prompts
REM Use this if you want to leave it running overnight
REM ============================================================================

echo ========================================
echo   AUTO-RESUME (No Prompts)
echo ========================================
echo.
echo This will automatically resume ALL unfinished experiments:
echo   - SIIM (1%%, 10%%, 100%%)
echo   - RSNA Linear Probe
echo   - RadDINO
echo.
echo No further prompts will be shown.
echo.
echo Press Ctrl+C NOW to cancel, or
timeout /t 10
echo.
echo Starting automated resume...
echo.

cd C:\Users\aya.alaswad\remote

REM Pull latest
echo [0] Pulling latest code...
git pull origin main >nul 2>&1
echo [OK] Code updated
echo.

REM ============================================================================
REM SIIM
REM ============================================================================
echo [1/3] SIIM Training...

set SIIM_DIR=C:\Users\aya.alaswad\remote\BenchX\experiments\classification\siim
set NEED_SIIM=0

REM Quick check if any SIIM split is incomplete
for %%S in (SHARP_1pct SHARP_10pct SHARP_100pct) do (
    if exist "%SIIM_DIR%\%%S\%%S\42.log" (
        findstr /C:"Early stopping" "%SIIM_DIR%\%%S\%%S\42.log" >nul 2>&1
        if %errorlevel% NEQ 0 (
            findstr /C:"Epoch 50" "%SIIM_DIR%\%%S\%%S\42.log" >nul 2>&1
            if %errorlevel% NEQ 0 (
                set NEED_SIIM=1
            )
        )
    ) else (
        set NEED_SIIM=1
    )
)

if %NEED_SIIM% EQU 1 (
    echo [RUNNING] Starting SIIM training...
    call run_siim_all_splits.bat
    echo [DONE] SIIM training completed
) else (
    echo [SKIP] SIIM already complete
)
echo.

REM ============================================================================
REM RSNA Linear Probe
REM ============================================================================
echo [2/3] RSNA Linear Probe...

set RSNA_LP_DIR=C:\Users\aya.alaswad\remote\BenchX\experiments\classification\rsna\SHARP_LP
set NEED_LP=0

if exist "%RSNA_LP_DIR%\SHARP_LP\42.log" (
    findstr /C:"Early stopping" "%RSNA_LP_DIR%\SHARP_LP\42.log" >nul 2>&1
    if %errorlevel% NEQ 0 (
        findstr /C:"Epoch 30" "%RSNA_LP_DIR%\SHARP_LP\42.log" >nul 2>&1
        if %errorlevel% NEQ 0 (
            set NEED_LP=1
        )
    )
) else (
    set NEED_LP=1
)

if %NEED_LP% EQU 1 (
    echo [RUNNING] Starting Linear Probe...
    copy sharp_rsna_lp.yml BenchX\configs\classification\RSNA\sharp.yml /Y >nul
    cd BenchX
    python bin/train.py configs/classification/RSNA/sharp.yml
    cd ..
    echo [DONE] Linear Probe completed
) else (
    echo [SKIP] Linear Probe already complete
)
echo.

REM ============================================================================
REM RadDINO
REM ============================================================================
echo [3/3] RadDINO Training...

set RADDINO_DIR=D:\experiments\exp_raddino_hardneg
set NEED_RADDINO=0

if exist "%RADDINO_DIR%\training.log" (
    findstr /C:"Training complete" "%RADDINO_DIR%\training.log" >nul 2>&1
    if %errorlevel% NEQ 0 (
        set NEED_RADDINO=1
    )
) else (
    set NEED_RADDINO=1
)

if %NEED_RADDINO% EQU 1 (
    echo [RUNNING] Resuming RadDINO...
    if exist "%RADDINO_DIR%\p3_last.pt" (
        python -c "import torch; ckpt=torch.load(r'%RADDINO_DIR%\p3_last.pt', map_location='cpu'); print(f'  Resuming from step {ckpt[\"step\"]:,}')" 2>nul
    )
    call run_raddino_exp3_hardneg.bat
    echo [DONE] RadDINO completed
) else (
    echo [SKIP] RadDINO already complete
)
echo.

REM ============================================================================
REM Final Summary
REM ============================================================================
echo.
echo ========================================
echo   All Training Complete!
echo ========================================
echo.

REM Extract results automatically
echo Extracting results...
python extract_all_results.py

echo.
echo Done! All experiments finished.
echo.

pause
