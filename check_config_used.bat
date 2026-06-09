@echo off
echo Checking which config was actually used for the training...
echo.
cd C:\Users\aya.alaswad\remote\BenchX
echo Config file location:
dir configs\classification\RSNA\sharp_rsna_10pct_exp4v2a.yml
echo.
echo Config contents:
type configs\classification\RSNA\sharp_rsna_10pct_exp4v2a.yml
pause
