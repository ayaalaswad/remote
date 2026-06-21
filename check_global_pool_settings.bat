@echo off
REM Check global_pool settings for RSNA and SIIM configs

echo ========================================
echo Checking global_pool Settings
echo ========================================
echo.

echo RSNA Configs:
echo ----------------------------------------
findstr /n "global_pool" sharp_rsna_1pct.yml
findstr /n "global_pool" sharp_rsna_10pct.yml
findstr /n "global_pool" sharp_rsna_100pct.yml
echo.

echo SIIM Configs:
echo ----------------------------------------
findstr /n "global_pool" sharp_siim_1pct.yml
findstr /n "global_pool" sharp_siim_10pct.yml
findstr /n "global_pool" sharp_siim_100pct.yml
echo.

echo ========================================
echo Checking Base Config (if referenced)
echo ========================================
echo.

if exist "BenchX\configs\_base_\models\mgca_vit.yml" (
    echo Base config: BenchX\configs\_base_\models\mgca_vit.yml
    findstr /n "global_pool" "BenchX\configs\_base_\models\mgca_vit.yml"
) else (
    echo Base config not found
)

echo.
pause
