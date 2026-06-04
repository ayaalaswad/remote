@echo off
REM ============================================================================
REM BenchX SHARP Integration - Complete Setup and Run
REM ============================================================================

echo ========================================
echo   BenchX SHARP Setup and Run
echo   %date% %time%
echo ========================================
echo.

set BENCHX=C:\Users\aya.alaswad\remote\BenchX
set LOGFILE=D:\experiments\benchx_setup.log

echo Starting BenchX SHARP setup... > %LOGFILE%
echo. >> %LOGFILE%

REM ============================================================================
REM Step 1: Create datasets directory and symlinks
REM ============================================================================
echo [1/5] Setting up datasets...
cd %BENCHX%

if not exist "datasets" mkdir datasets
echo   Created datasets directory

REM Remove old symlinks if they exist
if exist "datasets\SIIM" rmdir "datasets\SIIM" 2>nul
if exist "datasets\RSNA" rmdir "datasets\RSNA" 2>nul

REM Create new symlinks
mklink /D datasets\SIIM D:\datasets\siim-pneumothorax\siim-acr-pneumothorax-segmentation >> %LOGFILE% 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to create SIIM symlink!
    echo   Trying to copy instead...
    xcopy /E /I /Q D:\datasets\siim-pneumothorax\siim-acr-pneumothorax-segmentation datasets\SIIM >> %LOGFILE% 2>&1
)

mklink /D datasets\RSNA D:\datasets\rsna-pneumonia\rsna-pneumonia-detection-challenge >> %LOGFILE% 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to create RSNA symlink!
    echo   Trying to copy instead...
    xcopy /E /I /Q D:\datasets\rsna-pneumonia\rsna-pneumonia-detection-challenge datasets\RSNA >> %LOGFILE% 2>&1
)

echo [OK] Datasets linked
echo.

REM ============================================================================
REM Step 2: Fix SIIM config
REM ============================================================================
echo [2/5] Fixing SIIM config...

(
echo includes:
echo   - configs/_base_/models/sharp.yml
echo.
echo name: SHARP
echo ckpt_dir: D:/experiments/benchx_results/siim_sharp/
echo use_amp: True
echo seed: 42
echo.
echo dataset:
echo   proto: SIIM_Pneumothorax_Dataset
echo   data_path: datasets/SIIM
echo   csvpath: datasets/SIIM/siim_labels.csv
echo   split: "train_1"
echo   num_workers: 4
echo.
echo transforms:
echo   type: NIHTransforms
echo.
echo model:
echo   proto: ImageClassifier
echo.
echo   cnn:
echo     output_layer: avgpool
echo     pretrained: D:/experiments/exp3_full_sharp/p3_best.pt
echo     freeze: False
echo.
echo   classifier:
echo     proto: Classifier
echo     num_classes: 2
echo     use_fc_norm: True
echo     trunc_init: True
echo     dropout: 0.
echo.
echo   loss:
echo     proto: CrossEntropyLoss
echo.
echo trainer:
echo   optimizer: AdamW
echo   optim_params:
echo     lr: 1e-4
echo     eps: 1e-08
echo     optim_groups: ve_only
echo     lr_multiplier_ve: 0.1
echo     weight_decay: 0.01
echo   batch_size: 32
echo   clip_grad_norm: 1.0
echo   lr_decay: WarmupCosineScheduler
echo   lr_decay_params:
echo     warmup_steps: 50
echo     t_total: 1200
echo   epochs: 30
echo   early_stop: 10
echo   eval_start: 5
echo   eval_interval: 2
echo   early_stop_metric: multiclass_f1
echo.
echo validator:
echo   batch_size: 128
echo   metrics: [multiclass_accuracy, multiclass_precision, multiclass_recall, multiclass_f1, multiclass_auroc]
echo   splits: [val]
) > configs\classification\SIIM\sharp.yml

echo [OK] SIIM config fixed
echo.

REM ============================================================================
REM Step 3: Fix RSNA config
REM ============================================================================
echo [3/5] Fixing RSNA config...

(
echo includes:
echo   - configs/_base_/models/sharp.yml
echo.
echo name: SHARP
echo ckpt_dir: D:/experiments/benchx_results/rsna_sharp/
echo use_amp: True
echo seed: 42
echo.
echo dataset:
echo   proto: RSNA_Pneumonia_Dataset
echo   data_path: datasets/RSNA
echo   csvpath: datasets/RSNA/rsna_labels.csv
echo   split: "train_1"
echo   num_workers: 4
echo.
echo transforms:
echo   type: NIHTransforms
echo.
echo model:
echo   proto: ImageClassifier
echo.
echo   cnn:
echo     output_layer: avgpool
echo     pretrained: D:/experiments/exp3_full_sharp/p3_best.pt
echo     freeze: False
echo.
echo   classifier:
echo     proto: Classifier
echo     num_classes: 2
echo     use_fc_norm: True
echo     trunc_init: True
echo     dropout: 0.
echo.
echo   loss:
echo     proto: CrossEntropyLoss
echo.
echo trainer:
echo   optimizer: AdamW
echo   optim_params:
echo     lr: 5e-5
echo     eps: 1e-08
echo     optim_groups: ve_only
echo     lr_multiplier_ve: 0.1
echo     weight_decay: 0.01
echo   batch_size: 32
echo   clip_grad_norm: 1.0
echo   lr_decay: WarmupCosineScheduler
echo   lr_decay_params:
echo     warmup_steps: 60
echo     t_total: 1200
echo   epochs: 30
echo   early_stop: 10
echo   eval_start: 5
echo   eval_interval: 2
echo   early_stop_metric: multiclass_f1
echo.
echo validator:
echo   batch_size: 128
echo   metrics: [multiclass_accuracy, multiclass_precision, multiclass_recall, multiclass_f1, multiclass_auroc]
echo   splits: [val]
) > configs\classification\RSNA\sharp.yml

echo [OK] RSNA config fixed
echo.

REM ============================================================================
REM Step 4: Test SHARP import
REM ============================================================================
echo [4/5] Testing SHARP import...
python -c "from unifier.models.vilmedic.SHARP import SHARP; print('  SHARP imported successfully!')" >> %LOGFILE% 2>&1

if errorlevel 1 (
    echo [ERROR] SHARP import failed!
    type %LOGFILE%
    pause
    exit /b 1
)

echo [OK] SHARP imports correctly
echo.

REM ============================================================================
REM Step 5: Check dataset paths
REM ============================================================================
echo [5/5] Checking dataset paths...

if exist "datasets\SIIM\stage_2_images" (
    echo   [OK] SIIM data found
) else (
    echo   [WARNING] SIIM data not found at datasets\SIIM\stage_2_images
)

if exist "datasets\RSNA\stage_2_train_images" (
    echo   [OK] RSNA data found
) else (
    echo   [WARNING] RSNA data not found at datasets\RSNA\stage_2_train_images
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.

REM ============================================================================
REM Ask user if they want to run SIIM training now
REM ============================================================================
echo Ready to run SIIM training (30-45 minutes)
echo.
set /p RUN_NOW=Start SIIM training now? (y/n):

if /i "%RUN_NOW%"=="y" (
    echo.
    echo ========================================
    echo   Starting SIIM Training
    echo ========================================
    echo.
    echo Training output: D:\experiments\benchx_results\siim_sharp\
    echo Press Ctrl+C to stop
    echo.
    python bin/train.py configs/classification/SIIM/sharp.yml
) else (
    echo.
    echo To run training later, use:
    echo   cd C:\Users\aya.alaswad\remote\BenchX
    echo   python bin/train.py configs/classification/SIIM/sharp.yml
    echo.
)

echo.
echo Log file: %LOGFILE%
pause
