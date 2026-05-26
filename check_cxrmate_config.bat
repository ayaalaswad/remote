@echo off
REM Check existing CXRMate config to understand the format
echo Checking existing CXRMate config format...
echo.

cd /d C:\Users\aya.alaswad\remote\cxrmate

echo [1] Showing content of existing config:
echo.
type config\train\longitudinal_gt_prompt_tf.yaml
echo.
echo ========================================
echo.

echo [2] Showing our copied config:
echo.
type config\train\exp1_baseline.yaml
echo.
echo ========================================
echo.

pause
