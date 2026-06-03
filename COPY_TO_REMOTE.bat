@echo off
REM ============================================================================
REM Copy RadDINO files from local to remote desktop
REM ============================================================================

echo Copying RadDINO files to remote desktop...
echo.

xcopy /Y "C:\Users\ZA\lawer\MyReasearch\train_sharp_raddino_v2.py" "C:\Users\aya.alaswad\remote\MyReasearch\"
xcopy /Y "C:\Users\ZA\lawer\MyReasearch\run_raddino_exp3_hardneg.bat" "C:\Users\aya.alaswad\remote\MyReasearch\"
xcopy /Y "C:\Users\ZA\lawer\MyReasearch\run_raddino_smoketest.bat" "C:\Users\aya.alaswad\remote\MyReasearch\"
xcopy /Y "C:\Users\ZA\lawer\MyReasearch\verify_raddino_setup.py" "C:\Users\aya.alaswad\remote\MyReasearch\"
xcopy /Y "C:\Users\ZA\lawer\MyReasearch\RADDINO_INTEGRATION_README.md" "C:\Users\aya.alaswad\remote\MyReasearch\"

echo.
echo ============================================
echo Files copied to remote desktop:
echo   - train_sharp_raddino_v2.py
echo   - run_raddino_exp3_hardneg.bat
echo   - run_raddino_smoketest.bat
echo   - verify_raddino_setup.py
echo   - RADDINO_INTEGRATION_README.md
echo ============================================
echo.
pause
