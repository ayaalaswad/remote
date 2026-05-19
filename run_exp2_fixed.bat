@echo off
mkdir D:\experiments\exp2_paired_fixed 2>nul
python train_sharp_large_batch.py --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs\scene_data --image_dir D:\datasets\mimic-cxr-jpg --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz --output_dir D:\experiments\exp2_paired_fixed --batch_size 32 --bidirectional --paired_sampling --hard_neg_max_frac 0.0 > D:\experiments\exp2_paired_fixed\training.log 2>&1
