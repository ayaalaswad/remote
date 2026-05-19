@echo off
mkdir D:\experiments\exp4_large_batch 2>nul
python train_sharp_large_batch.py --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs\scene_data --image_dir D:\datasets\mimic-cxr-jpg --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz --output_dir D:\experiments\exp4_large_batch --batch_size 512 --bidirectional --hard_neg_max_frac 0.6 > D:\experiments\exp4_large_batch\training.log 2>&1
