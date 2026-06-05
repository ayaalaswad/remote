@echo off
REM ============================================================================
REM BenchX Complete Fix - Create working SIIM and RSNA configs
REM ============================================================================

echo ========================================
echo   BenchX Complete Fix
echo ========================================
echo.

set BENCHX=C:\Users\aya.alaswad\remote\BenchX

cd %BENCHX%

REM ============================================================================
REM Step 1: Create symlinks for CSV files with expected names
REM ============================================================================
echo [1/3] Creating CSV file links...

REM BenchX expects siim_labels.csv but we have stage_2_train.csv
if not exist "datasets\SIIM\siim_labels.csv" (
    copy datasets\SIIM\stage_2_train.csv datasets\SIIM\siim_labels.csv >nul
    echo   Created siim_labels.csv
)

REM BenchX expects rsna_labels.csv but we have stage_2_train_labels.csv
if not exist "datasets\RSNA\rsna_labels.csv" (
    copy datasets\RSNA\stage_2_train_labels.csv datasets\RSNA\rsna_labels.csv >nul
    echo   Created rsna_labels.csv
)

echo [OK] CSV files ready
echo.

REM ============================================================================
REM Step 2: Create base SHARP config
REM ============================================================================
echo [2/3] Creating base config...

mkdir configs\_base_\models 2>nul

(
echo # SHARP Base Model Config
echo model:
echo   proto: ImageClassifier
echo   cnn:
echo     proto: SHARP
) > configs\_base_\models\sharp.yml

echo [OK] Base config created
echo.

REM ============================================================================
REM Step 3: Create SIIM SHARP config
REM ============================================================================
echo [3/3] Creating dataset configs...

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
echo   optimizer: Adam
echo   optim_params:
echo     lr: 1e-4
echo     eps: 1e-08
echo     optim_groups: ve_only
echo     lr_multiplier_ve: 0.1
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

echo   Created SIIM config

REM ============================================================================
REM Create RSNA SHARP config
REM ============================================================================

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
echo   optimizer: Adam
echo   optim_params:
echo     lr: 5e-5
echo     eps: 1e-08
echo     optim_groups: ve_only
echo     lr_multiplier_ve: 0.1
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

echo   Created RSNA config

echo [OK] All configs created
echo.

REM ============================================================================
REM Verify setup
REM ============================================================================
echo ========================================
echo   Verifying Setup
echo ========================================
echo.

echo Checking CSV files...
if exist "datasets\SIIM\siim_labels.csv" (
    echo   [OK] SIIM CSV exists
) else (
    echo   [ERROR] SIIM CSV missing!
)

if exist "datasets\RSNA\rsna_labels.csv" (
    echo   [OK] RSNA CSV exists
) else (
    echo   [ERROR] RSNA CSV missing!
)

echo.
echo Checking configs...
if exist "configs\classification\SIIM\sharp.yml" (
    echo   [OK] SIIM config exists
) else (
    echo   [ERROR] SIIM config missing!
)

if exist "configs\classification\RSNA\sharp.yml" (
    echo   [OK] RSNA config exists
) else (
    echo   [ERROR] RSNA config missing!
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Ready to run SIIM training:
echo   python bin/train.py configs/classification/SIIM/sharp.yml
echo.
pause
