@echo off
REM Extract Per-Condition CheXbert F1 for All Stage 2 Experiments
REM
REM R2 explicitly asked for per-condition breakdown (14 diseases).
REM This extracts from existing Stage 2 results - NO retraining needed.
REM
REM Extracts for: Exp #1, #3, #4 v2a (completed experiments)
REM Runtime: ~1 minute (just reading CSV files)

echo ============================================================================
echo Extracting Per-Condition CheXbert F1 Metrics
echo ============================================================================
echo.
echo R2 asked for disease-specific F1 breakdown for:
echo   - Atelectasis, Cardiomegaly, Consolidation, Edema
echo   - Enlarged Cardiomediastinum, Fracture, Lung Lesion, Lung Opacity
echo   - No Finding, Pleural Effusion, Pleural Other, Pneumonia
echo   - Pneumothorax, Support Devices
echo.
echo This will extract from completed Stage 2 experiments:
echo   - Exp #1 (baseline): trial_0
echo   - Exp #3 (hard neg): trial_1
echo   - Exp #4 v2a (large batch): trial_2
echo.

cd C:\Users\aya.alaswad\remote\cxrmate\experiments\cxrmate\single_tf

echo ============================================================================
echo Exp #1 (Baseline) - Per-Condition F1 at Best Epoch (25)
echo ============================================================================
echo.

cd trial_0
powershell -Command "$csv = Import-Csv lightning_logs\version_0\metrics.csv; $best = $csv | Where-Object {$_.epoch -eq '25'} | Select-Object -First 1; if ($best) { Write-Host ('Epoch: ' + $best.epoch); Write-Host ('Macro F1: ' + $best.val_report_chexbert_f1_macro); Write-Host ''; Write-Host 'Per-Condition F1:'; Write-Host ('  Atelectasis: ' + $best.val_report_chexbert_f1_atelectasis); Write-Host ('  Cardiomegaly: ' + $best.val_report_chexbert_f1_cardiomegaly); Write-Host ('  Consolidation: ' + $best.val_report_chexbert_f1_consolidation); Write-Host ('  Edema: ' + $best.val_report_chexbert_f1_edema); Write-Host ('  Enlarged Cardiomediastinum: ' + $best.val_report_chexbert_f1_enlarged_cardiomediastinum); Write-Host ('  Fracture: ' + $best.val_report_chexbert_f1_fracture); Write-Host ('  Lung Lesion: ' + $best.val_report_chexbert_f1_lung_lesion); Write-Host ('  Lung Opacity: ' + $best.val_report_chexbert_f1_lung_opacity); Write-Host ('  No Finding: ' + $best.val_report_chexbert_f1_no_finding); Write-Host ('  Pleural Effusion: ' + $best.val_report_chexbert_f1_pleural_effusion); Write-Host ('  Pleural Other: ' + $best.val_report_chexbert_f1_pleural_other); Write-Host ('  Pneumonia: ' + $best.val_report_chexbert_f1_pneumonia); Write-Host ('  Pneumothorax: ' + $best.val_report_chexbert_f1_pneumothorax); Write-Host ('  Support Devices: ' + $best.val_report_chexbert_f1_support_devices) } else { Write-Host 'Could not find epoch 25 data' }" > ..\..\..\..\exp1_percondition_f1.txt

echo Saved to: exp1_percondition_f1.txt
echo.

cd ..

echo ============================================================================
echo Exp #3 (Hard Negatives) - Per-Condition F1 at Best Epoch (23)
echo ============================================================================
echo.

cd trial_1
powershell -Command "$csv = Import-Csv lightning_logs\version_0\metrics.csv; $best = $csv | Where-Object {$_.epoch -eq '23'} | Select-Object -First 1; if ($best) { Write-Host ('Epoch: ' + $best.epoch); Write-Host ('Macro F1: ' + $best.val_report_chexbert_f1_macro); Write-Host ''; Write-Host 'Per-Condition F1:'; Write-Host ('  Atelectasis: ' + $best.val_report_chexbert_f1_atelectasis); Write-Host ('  Cardiomegaly: ' + $best.val_report_chexbert_f1_cardiomegaly); Write-Host ('  Consolidation: ' + $best.val_report_chexbert_f1_consolidation); Write-Host ('  Edema: ' + $best.val_report_chexbert_f1_edema); Write-Host ('  Enlarged Cardiomediastinum: ' + $best.val_report_chexbert_f1_enlarged_cardiomediastinum); Write-Host ('  Fracture: ' + $best.val_report_chexbert_f1_fracture); Write-Host ('  Lung Lesion: ' + $best.val_report_chexbert_f1_lung_lesion); Write-Host ('  Lung Opacity: ' + $best.val_report_chexbert_f1_lung_opacity); Write-Host ('  No Finding: ' + $best.val_report_chexbert_f1_no_finding); Write-Host ('  Pleural Effusion: ' + $best.val_report_chexbert_f1_pleural_effusion); Write-Host ('  Pleural Other: ' + $best.val_report_chexbert_f1_pleural_other); Write-Host ('  Pneumonia: ' + $best.val_report_chexbert_f1_pneumonia); Write-Host ('  Pneumothorax: ' + $best.val_report_chexbert_f1_pneumothorax); Write-Host ('  Support Devices: ' + $best.val_report_chexbert_f1_support_devices) } else { Write-Host 'Could not find epoch 23 data' }" > ..\..\..\..\exp3_percondition_f1.txt

echo Saved to: exp3_percondition_f1.txt
echo.

cd ..

echo ============================================================================
echo Exp #4 v2a (Large Batch) - Per-Condition F1 at Best Epoch (21)
echo ============================================================================
echo.

cd trial_2
powershell -Command "$csv = Import-Csv lightning_logs\version_0\metrics.csv; $best = $csv | Where-Object {$_.epoch -eq '21'} | Select-Object -First 1; if ($best) { Write-Host ('Epoch: ' + $best.epoch); Write-Host ('Macro F1: ' + $best.val_report_chexbert_f1_macro); Write-Host ''; Write-Host 'Per-Condition F1:'; Write-Host ('  Atelectasis: ' + $best.val_report_chexbert_f1_atelectasis); Write-Host ('  Cardiomegaly: ' + $best.val_report_chexbert_f1_cardiomegaly); Write-Host ('  Consolidation: ' + $best.val_report_chexbert_f1_consolidation); Write-Host ('  Edema: ' + $best.val_report_chexbert_f1_edema); Write-Host ('  Enlarged Cardiomediastinum: ' + $best.val_report_chexbert_f1_enlarged_cardiomediastinum); Write-Host ('  Fracture: ' + $best.val_report_chexbert_f1_fracture); Write-Host ('  Lung Lesion: ' + $best.val_report_chexbert_f1_lung_lesion); Write-Host ('  Lung Opacity: ' + $best.val_report_chexbert_f1_lung_opacity); Write-Host ('  No Finding: ' + $best.val_report_chexbert_f1_no_finding); Write-Host ('  Pleural Effusion: ' + $best.val_report_chexbert_f1_pleural_effusion); Write-Host ('  Pleural Other: ' + $best.val_report_chexbert_f1_pleural_other); Write-Host ('  Pneumonia: ' + $best.val_report_chexbert_f1_pneumonia); Write-Host ('  Pneumothorax: ' + $best.val_report_chexbert_f1_pneumothorax); Write-Host ('  Support Devices: ' + $best.val_report_chexbert_f1_support_devices) } else { Write-Host 'Could not find epoch 21 data' }" > ..\..\..\..\exp4v2a_percondition_f1.txt

echo Saved to: exp4v2a_percondition_f1.txt
echo.

cd C:\Users\aya.alaswad\remote

echo.
echo ============================================================================
echo Extraction Complete!
echo ============================================================================
echo.
echo Per-condition F1 results saved to:
echo   - exp1_percondition_f1.txt (baseline)
echo   - exp3_percondition_f1.txt (hard negatives - BEST downstream)
echo   - exp4v2a_percondition_f1.txt (large batch - BEST retrieval)
echo.
echo To view results:
echo   type exp1_percondition_f1.txt
echo   type exp3_percondition_f1.txt
echo   type exp4v2a_percondition_f1.txt
echo.
echo This answers R2's explicit request for disease-specific metrics.
echo.
pause
