@echo off
REM ============================================================================
REM BenchX Setup - Step 1: Clone repo and create environment
REM ============================================================================

echo ========================================
echo   BenchX Setup - Environment Creation
echo ========================================
echo.
echo This will:
echo   1. Clone BenchX repo
echo   2. Create conda environment
echo   3. Install dependencies
echo.
echo Location: C:\Users\aya.alaswad\remote\BenchX
echo.
pause

cd C:\Users\aya.alaswad\remote

REM Clone BenchX repo
echo.
echo [1/3] Cloning BenchX repository...
git clone https://github.com/yangzhou12/BenchX.git
cd BenchX

REM Create conda environment
echo.
echo [2/3] Creating conda environment (benchx)...
call conda create -n benchx python=3.10 -y

REM Install dependencies
echo.
echo [3/3] Installing dependencies...
call conda activate benchx
pip install -r requirements.txt

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Download datasets (run: benchx_download_data.bat)
echo   2. Integrate SHARP (run: benchx_integrate_sharp.bat)
echo   3. Run evaluation (run: benchx_run_all.bat)
echo.
pause
