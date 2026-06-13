@echo off
REM ============================================================================
REM Auto-Resume All Unfinished Training Experiments
REM ============================================================================

echo ========================================
echo   Auto-Resume Unfinished Training
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote

REM Pull latest code first
echo [0] Pulling latest code...
git pull origin main
echo.

REM ============================================================================
REM Check and Resume SIIM Training
REM ============================================================================
echo [1/3] Checking SIIM Training...
echo ========================================
echo.

set SIIM_DIR=C:\Users\aya.alaswad\remote\BenchX\experiments\classification\siim
set SIIM_RESUME=0

REM Check which splits need to resume
for %%S in (SHARP_1pct SHARP_10pct SHARP_100pct) do (
    if exist "%SIIM_DIR%\%%S\%%S\42.log" (
        REM Check if completed
        findstr /C:"Early stopping" "%SIIM_DIR%\%%S\%%S\42.log" >nul 2>&1
        if %errorlevel% NEQ 0 (
            findstr /C:"Epoch 50" "%SIIM_DIR%\%%S\%%S\42.log" >nul 2>&1
            if %errorlevel% NEQ 0 (
                echo [INCOMPLETE] %%S - needs to resume
                set SIIM_RESUME=1
            ) else (
                echo [COMPLETE] %%S
            )
        ) else (
            echo [COMPLETE] %%S
        )
    ) else (
        if exist "%SIIM_DIR%\%%S" (
            echo [INCOMPLETE] %%S - needs to resume
            set SIIM_RESUME=1
        ) else (
            echo [NOT STARTED] %%S - will start
            set SIIM_RESUME=1
        )
    )
)

echo.
if %SIIM_RESUME% EQU 1 (
    echo [ACTION] Resuming SIIM training...
    echo.
    echo This will train all incomplete SIIM splits.
    echo Press Ctrl+C to skip SIIM, or
    pause

    echo.
    echo Starting SIIM training...
    call run_siim_all_splits.bat

    if %errorlevel% NEQ 0 (
        echo.
        echo [ERROR] SIIM training failed!
        echo.
        pause
    )
) else (
    echo [OK] All SIIM training complete - nothing to resume
)

echo.
echo.

REM ============================================================================
REM Check and Resume RSNA Linear Probe
REM ============================================================================
echo [2/3] Checking RSNA Linear Probe...
echo ========================================
echo.

set RSNA_LP_DIR=C:\Users\aya.alaswad\remote\BenchX\experiments\classification\rsna\SHARP_LP
set RSNA_RESUME=0

if exist "%RSNA_LP_DIR%\SHARP_LP\42.log" (
    REM Check if completed
    findstr /C:"Early stopping" "%RSNA_LP_DIR%\SHARP_LP\42.log" >nul 2>&1
    if %errorlevel% NEQ 0 (
        findstr /C:"Epoch 30" "%RSNA_LP_DIR%\SHARP_LP\42.log" >nul 2>&1
        if %errorlevel% NEQ 0 (
            echo [INCOMPLETE] Linear Probe - needs to resume
            set RSNA_RESUME=1
        ) else (
            echo [COMPLETE] Linear Probe
        )
    ) else (
        echo [COMPLETE] Linear Probe
    )
) else (
    if exist "%RSNA_LP_DIR%" (
        echo [INCOMPLETE] Linear Probe - needs to resume
        set RSNA_RESUME=1
    ) else (
        echo [NOT STARTED] Linear Probe - will start
        set RSNA_RESUME=1
    )
)

echo.
if %RSNA_RESUME% EQU 1 (
    echo [ACTION] Starting/Resuming RSNA Linear Probe...
    echo.
    echo This will train the linear probe (encoder frozen).
    echo Expected time: 1-2 hours
    echo.
    echo Press Ctrl+C to skip Linear Probe, or
    pause

    echo.
    echo Starting Linear Probe training...
    copy sharp_rsna_lp.yml BenchX\configs\classification\RSNA\sharp.yml /Y
    cd BenchX
    python bin/train.py configs/classification/RSNA/sharp.yml
    cd ..

    if %errorlevel% NEQ 0 (
        echo.
        echo [ERROR] Linear Probe training failed!
        echo.
        pause
    )
) else (
    echo [OK] Linear Probe complete - nothing to resume
)

echo.
echo.

REM ============================================================================
REM Check and Resume RadDINO Training
REM ============================================================================
echo [3/3] Checking RadDINO Training...
echo ========================================
echo.

set RADDINO_DIR=D:\experiments\exp_raddino_hardneg
set RADDINO_RESUME=0

if exist "%RADDINO_DIR%\training.log" (
    REM Check if completed
    findstr /C:"Training complete" "%RADDINO_DIR%\training.log" >nul 2>&1
    if %errorlevel% NEQ 0 (
        echo [INCOMPLETE] RadDINO - needs to resume
        set RADDINO_RESUME=1

        REM Show current progress
        if exist "%RADDINO_DIR%\p3_last.pt" (
            echo.
            echo Current progress:
            python -c "import torch; ckpt=torch.load(r'%RADDINO_DIR%\p3_last.pt', map_location='cpu'); print(f'  Step: {ckpt[\"step\"]:,} / 100,000'); print(f'  Current R@1: {ckpt.get(\"r1\", \"N/A\")}')" 2>nul
        )
    ) else (
        echo [COMPLETE] RadDINO
    )
) else (
    if exist "%RADDINO_DIR%" (
        echo [INCOMPLETE] RadDINO - needs to resume
        set RADDINO_RESUME=1
    ) else (
        echo [NOT STARTED] RadDINO - will start
        set RADDINO_RESUME=1
    )
)

echo.
if %RADDINO_RESUME% EQU 1 (
    echo [ACTION] Resuming RadDINO training...
    echo.
    echo This will resume RadDINO from last checkpoint.
    echo Expected remaining time: depends on current step
    echo.
    echo Press Ctrl+C to skip RadDINO, or
    pause

    echo.
    echo Resuming RadDINO training...
    call run_raddino_exp3_hardneg.bat

    if %errorlevel% NEQ 0 (
        echo.
        echo [ERROR] RadDINO training failed!
        echo.
        pause
    )
) else (
    echo [OK] RadDINO complete - nothing to resume
)

REM ============================================================================
REM Summary
REM ============================================================================
echo.
echo.
echo ========================================
echo   Resume Complete
echo ========================================
echo.

echo All unfinished experiments have been processed.
echo.
echo To check final results, run:
echo   python extract_all_results.py
echo.

pause
