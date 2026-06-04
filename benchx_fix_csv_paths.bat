@echo off
REM Fix CSV paths in BenchX configs

cd C:\Users\aya.alaswad\remote\BenchX

echo Fixing SIIM config CSV path...
powershell -Command "(Get-Content configs\classification\SIIM\sharp.yml) -replace 'csvpath: datasets/SIIM/siim_labels.csv', 'csvpath: datasets/SIIM/stage_2_train.csv' | Set-Content configs\classification\SIIM\sharp.yml"

echo Fixing RSNA config CSV path...
powershell -Command "(Get-Content configs\classification\RSNA\sharp.yml) -replace 'csvpath: datasets/RSNA/rsna_labels.csv', 'csvpath: datasets/RSNA/stage_2_train_labels.csv' | Set-Content configs\classification\RSNA\sharp.yml"

echo.
echo [OK] CSV paths fixed!
echo.
echo Now run:
echo   python bin/train.py configs/classification/SIIM/sharp.yml
echo.
pause
