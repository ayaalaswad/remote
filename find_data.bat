@echo off
echo ========================================
echo FINDING MIMIC-CXR DATA ON REMOTE
echo ========================================
echo.

echo Searching for scene_data folder...
dir /s /b /ad scene_data 2>nul
echo.

echo Searching for mimic-cxr-jpg folder...
dir /s /b /ad mimic-cxr-jpg 2>nul
echo.

echo Searching for split CSV file...
dir /s /b mimic-cxr-2.0.0-split.csv.gz 2>nul
echo.

echo ========================================
echo Common locations to check:
echo   D:\mimic-cxr-jpg\
echo   /workspace/mimic-cxr-jpg/
echo   /data/mimic-cxr-jpg/
echo   C:\Users\aya.alaswad\data\
echo ========================================
echo.

pause
