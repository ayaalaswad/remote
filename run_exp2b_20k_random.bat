@echo off
REM Exp #2b: 20k random control (NO paired sampling)
REM Purpose: Isolate dataset size confound
REM
REM This tests: Does 20k random files give similar performance to 60k+ baseline?
REM - If R@1 ~6.6% (similar to baseline) → dataset size NOT the issue
REM - If R@1 tanks → dataset size IS the issue
REM
REM Config: Same as Exp #1 EXCEPT only 20k files used
REM Time: ~12 hours

mkdir D:\experiments\exp2b_20k_random 2>nul

echo Running Exp #2b: 20k random control
echo This isolates the dataset size confound (20k vs 60k+ files)
echo.
pause

python train_sharp_large_batch.py ^
  --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs\scene_data ^
  --image_dir D:\datasets\mimic-cxr-jpg ^
  --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz ^
  --output_dir D:\experiments\exp2b_20k_random ^
  --batch_size 32 ^
  --bidirectional ^
  --hard_neg_max_frac 0.0 ^
  --max_train_files 20000 ^
  > D:\experiments\exp2b_20k_random\training.log 2>&1

echo.
echo Training complete!
echo Check results: D:\experiments\exp2b_20k_random\training.log
pause
