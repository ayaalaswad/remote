@echo off
REM ============================================================================
REM Test All SHARP Checkpoints on RSNA 10%% Split
REM ============================================================================

echo ========================================
echo   SHARP Checkpoint Comparison - RSNA
echo ========================================
echo.
echo Testing 3 checkpoints on RSNA 10%% split:
echo   [1/3] Exp #1 Baseline  (R@1=6.61%%, F1=31.2%%)
echo   [2/3] Exp #3 Full SHARP (R@1=6.21%%, F1=37.4%%) - CURRENT
echo   [3/3] Exp #4 v2a        (R@1=8.77%%, F1=34.6%%) - BEST R@1
echo.
echo Expected time: 3-4 hours total
echo.
pause

cd C:\Users\aya.alaswad\remote

REM ============================================================================
REM Step 0: Pull latest code and convert checkpoints
REM ============================================================================
echo [0/4] Pulling latest code...
git pull origin main
echo.

echo Converting checkpoints to timm format...
python convert_all_checkpoints.py
echo.

if errorlevel 1 (
    echo [ERROR] Checkpoint conversion failed!
    pause
    exit /b 1
)

REM ============================================================================
REM Step 1: Test Exp #1 Baseline (Less report gen fine-tuning)
REM ============================================================================
echo [1/4] Testing Exp #1 Baseline checkpoint...
echo   - R@1: 6.61%% (Stage 1)
echo   - F1: 31.2%% (Stage 2 - less degradation)
echo   - Expected: Better than Exp #3 for classification
echo.

copy sharp_rsna_10pct_exp1.yml BenchX\configs\classification\RSNA\sharp.yml /Y
cd BenchX
python bin/train.py configs/classification/RSNA/sharp.yml

if errorlevel 1 (
    echo [WARNING] Exp #1 training failed - continuing...
)
cd ..
echo.

REM ============================================================================
REM Step 2: Test Exp #3 Full SHARP (Current baseline)
REM ============================================================================
echo [2/4] Testing Exp #3 Full SHARP checkpoint (current)...
echo   - R@1: 6.21%% (Stage 1)
echo   - F1: 37.4%% (Stage 2 - heavily optimized for report gen)
echo   - Expected F1: 43.1 (from previous run)
echo.

copy sharp_rsna_10pct.yml BenchX\configs\classification\RSNA\sharp.yml /Y
cd BenchX
python bin/train.py configs/classification/RSNA/sharp.yml

if errorlevel 1 (
    echo [WARNING] Exp #3 training failed - continuing...
)
cd ..
echo.

REM ============================================================================
REM Step 3: Test Exp #4 v2a (Best retrieval)
REM ============================================================================
echo [3/4] Testing Exp #4 v2a checkpoint (best R@1)...
echo   - R@1: 8.77%% (Stage 1 - BEST retrieval)
echo   - F1: 34.6%% (Stage 2 - moderate report gen)
echo   - Expected: BEST classification performance
echo.

copy sharp_rsna_10pct_exp4v2a.yml BenchX\configs\classification\RSNA\sharp.yml /Y
cd BenchX
python bin/train.py configs/classification/RSNA/sharp.yml

if errorlevel 1 (
    echo [WARNING] Exp #4 v2a training failed - continuing...
)
cd ..
echo.

REM ============================================================================
REM Summary
REM ============================================================================
echo.
echo ========================================
echo   All Training Complete!
echo ========================================
echo.
echo Results saved in:
echo   BenchX\experiments\classification\rsna\SHARP_EXP1_10pct\
echo   BenchX\experiments\classification\rsna\SHARP_10pct\
echo   BenchX\experiments\classification\rsna\SHARP_EXP4v2a_10pct\
echo.
echo Next: Compare F1 scores to see which checkpoint performs best
echo.

pause
