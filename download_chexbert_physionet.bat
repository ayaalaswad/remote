@echo off
REM Download CheXbert from PhysioNet with authentication
REM
REM CheXbert is part of the MIMIC-CXR dataset, not MIMIC-CXR-JPG
REM You need PhysioNet credentials and signed data use agreement

echo ============================================================================
echo CheXbert Download from PhysioNet
echo ============================================================================
echo.
echo Note: CheXbert requires PhysioNet authentication
echo You must have:
echo   1. PhysioNet account
echo   2. Completed credentialing
echo   3. Signed MIMIC-CXR data use agreement
echo.
pause

REM Create output directory
mkdir checkpoints\stanford\chexbert 2>nul

REM Try multiple PhysioNet paths where CheXbert might be located

echo.
echo Attempting download...
echo.

REM Path 1: MIMIC-CXR (main dataset, not JPG version)
echo [1/3] Trying MIMIC-CXR dataset...
wget --user %1 --password %2 ^
  https://physionet.org/files/mimic-cxr/2.0.0/chexbert.pth ^
  -O checkpoints\stanford\chexbert\chexbert.pth

if exist checkpoints\stanford\chexbert\chexbert.pth (
    goto :verify
)

REM Path 2: Chest-ImaGenome dataset
echo [2/3] Trying Chest-ImaGenome dataset...
wget --user %1 --password %2 ^
  https://physionet.org/files/chest-imagenome/1.0.0/chexbert.pth ^
  -O checkpoints\stanford\chexbert\chexbert.pth

if exist checkpoints\stanford\chexbert\chexbert.pth (
    goto :verify
)

REM Path 3: MIMIC-CXR supplementary files
echo [3/3] Trying MIMIC-CXR supplementary...
wget --user %1 --password %2 ^
  https://physionet.org/files/mimic-cxr/2.0.0/supplementary/chexbert.pth ^
  -O checkpoints\stanford\chexbert\chexbert.pth

if exist checkpoints\stanford\chexbert\chexbert.pth (
    goto :verify
)

echo.
echo ============================================================================
echo ERROR: CheXbert not found at any expected PhysioNet path
echo ============================================================================
echo.
echo CheXbert is not hosted on PhysioNet.
echo Original sources:
echo   - Stanford Box (blocked/404)
echo   - Google Drive (blocked in your country)
echo.
echo Options:
echo   1. Ask colleague to download and transfer via Dropbox/OneDrive
echo   2. Use VPN + Google Drive
echo   3. Proceed without CheXbert (skip Stage 2 for now)
echo.
pause
exit /b 1

:verify
echo.
echo ============================================================================
echo Verifying download...
echo ============================================================================
python -c "from pathlib import Path; p = Path('checkpoints/stanford/chexbert/chexbert.pth'); size = p.stat().st_size / (1024**2); print(f'Downloaded: {size:.1f} MB'); exit(0 if size > 400 else 1)"

if errorlevel 1 (
    echo.
    echo ERROR: File too small or corrupted
    del checkpoints\stanford\chexbert\chexbert.pth
    exit /b 1
)

echo.
echo ============================================================================
echo SUCCESS! CheXbert downloaded
echo ============================================================================
echo.
pause
