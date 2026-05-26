@echo off
REM Complete Stage 2 Solution - Find working config and run training
echo ========================================
echo Complete Stage 2 Training Solution
echo ========================================
echo.

cd /d C:\Users\aya.alaswad\remote\cxrmate

echo Step 1: Finding a working config to copy...
echo.

REM Use CXRMate's existing single_tf config as template
set TEMPLATE_CONFIG=config\train\single_tf.yaml

if exist "%TEMPLATE_CONFIG%" (
    echo Found single_tf.yaml template
) else (
    echo single_tf.yaml not found, using longitudinal_gt_prompt_tf.yaml as template
    set TEMPLATE_CONFIG=config\train\longitudinal_gt_prompt_tf.yaml
)

echo Template config: %TEMPLATE_CONFIG%
echo.
echo Template contents:
type "%TEMPLATE_CONFIG%"
echo.
echo ========================================
echo.

echo Step 2: Creating exp1_baseline.yaml based on template...
echo.

REM Create exp1 config using CXRMate's structure
(
echo defaults:
echo   - single_tf
echo   - _self_
echo.
echo module: modules.lightning_modules.single
echo definition: SingleCXR
echo.
echo exp_dir: experiments
echo dataset_dir: D:/datasets
echo ckpt_zoo_dir: checkpoints
echo.
echo strategy: auto
echo devices: 1
echo num_workers: 5
echo.
echo vit_ckpt_path: D:/experiments/exp1_baseline/p3_best.pt
echo.
echo sections_to_evaluate:
echo   - report
echo max_images_per_study: 5
echo lr: 5.0e-05
echo max_epochs: 10
echo mbatch_size: 8
echo accumulated_mbatch_size: 32
echo every_n_epochs: 1
echo monitor: val_report_chexbert_f1_macro
echo monitor_mode: max
echo precision: 16
echo deterministic: false
echo decoder_max_len: 256
echo num_test_beams: 4
echo enable_progress_bar: true
echo weights_summary: full
) > config\train\exp1_baseline.yaml

echo Created exp1_baseline.yaml
echo.

echo Step 3: Creating exp3_full.yaml...
echo.

(
echo defaults:
echo   - single_tf
echo   - _self_
echo.
echo module: modules.lightning_modules.single
echo definition: SingleCXR
echo.
echo exp_dir: experiments
echo dataset_dir: D:/datasets
echo ckpt_zoo_dir: checkpoints
echo.
echo strategy: auto
echo devices: 1
echo num_workers: 5
echo.
echo vit_ckpt_path: D:/experiments/exp3_full_sharp/p3_best.pt
echo.
echo sections_to_evaluate:
echo   - report
echo max_images_per_study: 5
echo lr: 5.0e-05
echo max_epochs: 10
echo mbatch_size: 8
echo accumulated_mbatch_size: 32
echo every_n_epochs: 1
echo monitor: val_report_chexbert_f1_macro
echo monitor_mode: max
echo precision: 16
echo deterministic: false
echo decoder_max_len: 256
echo num_test_beams: 4
echo enable_progress_bar: true
echo weights_summary: full
) > config\train\exp3_full.yaml

echo Created exp3_full.yaml
echo.
echo ========================================
echo.

echo Step 4: Testing if config is valid...
echo.

dlhpcstarter -t cxrmate --config_dir config/train -c single_tf --stages_module tools.stages --help >nul 2>&1

if errorlevel 1 (
    echo WARNING: single_tf config doesn't work
    echo.
    echo Trying alternative: Use existing working config directly
    echo.

    REM If single_tf doesn't exist, modify approach
    echo Listing all available configs:
    dir /b config\train\*.yaml
    echo.
    echo Using longitudinal_gt_prompt_tf as base instead
    echo.

    REM Recreate configs without defaults (standalone)
    (
    echo module: modules.lightning_modules.single
    echo definition: SingleCXR
    echo.
    echo exp_dir: experiments
    echo dataset_dir: D:/datasets
    echo ckpt_zoo_dir: checkpoints
    echo.
    echo strategy: auto
    echo devices: 1
    echo num_workers: 5
    echo.
    echo vit_ckpt_path: D:/experiments/exp1_baseline/p3_best.pt
    echo.
    echo sections_to_evaluate:
    echo   - report
    echo max_images_per_study: 5
    echo lr: 5.0e-05
    echo max_epochs: 10
    echo mbatch_size: 8
    echo accumulated_mbatch_size: 32
    echo every_n_epochs: 1
    echo monitor: val_report_chexbert_f1_macro
    echo monitor_mode: max
    echo precision: 16
    echo deterministic: false
    echo decoder_max_len: 256
    echo num_test_beams: 4
    echo enable_progress_bar: true
    echo weights_summary: full
    ) > config\train\exp1_baseline.yaml

    echo Recreated exp1_baseline.yaml as standalone config
)

echo.
echo ========================================
echo Step 5: Starting Training
echo ========================================
echo.

echo Starting Exp #1 Baseline...
echo Command: dlhpcstarter -t cxrmate --config_dir config/train -c exp1_baseline --stages_module tools.stages --train --trial 0
echo.

dlhpcstarter -t cxrmate --config_dir config/train -c exp1_baseline --stages_module tools.stages --train --trial 0

if errorlevel 1 (
    echo.
    echo ========================================
    echo Training failed. Diagnostics:
    echo ========================================
    echo.
    echo Checking if vit_ckpt_path exists:
    if exist "D:\experiments\exp1_baseline\p3_best.pt" (
        echo OK - D:\experiments\exp1_baseline\p3_best.pt exists
    ) else (
        echo ERROR - D:\experiments\exp1_baseline\p3_best.pt NOT FOUND
    )
    echo.
    echo Checking if dataset_dir exists:
    if exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0" (
        echo OK - D:\datasets\physionet.org structure exists
    ) else (
        echo ERROR - D:\datasets\physionet.org structure NOT FOUND
    )
    echo.
    echo Checking if checkpoints exist:
    if exist "checkpoints\stanford\chexbert\chexbert.pth" (
        echo OK - CheXbert checkpoint exists
    ) else (
        echo ERROR - CheXbert checkpoint NOT FOUND
    )
    echo.
    pause
    exit /b 1
)

echo.
echo Exp #1 completed! Starting Exp #3...
echo.

REM Create exp3 config
(
echo module: modules.lightning_modules.single
echo definition: SingleCXR
echo.
echo exp_dir: experiments
echo dataset_dir: D:/datasets
echo ckpt_zoo_dir: checkpoints
echo.
echo strategy: auto
echo devices: 1
echo num_workers: 5
echo.
echo vit_ckpt_path: D:/experiments/exp3_full_sharp/p3_best.pt
echo.
echo sections_to_evaluate:
echo   - report
echo max_images_per_study: 5
echo lr: 5.0e-05
echo max_epochs: 10
echo mbatch_size: 8
echo accumulated_mbatch_size: 32
echo every_n_epochs: 1
echo monitor: val_report_chexbert_f1_macro
echo monitor_mode: max
echo precision: 16
echo deterministic: false
echo decoder_max_len: 256
echo num_test_beams: 4
echo enable_progress_bar: true
echo weights_summary: full
) > config\train\exp3_full.yaml

dlhpcstarter -t cxrmate --config_dir config/train -c exp3_full --stages_module tools.stages --train --trial 0

echo.
echo ========================================
echo ALL TRAINING COMPLETE!
echo ========================================
echo.

pause
