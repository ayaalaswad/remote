@echo off
mkdir D:\experiments\exp3_full_sharp 2>nul
python train_sharp_large_batch.py --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs\scene_data --image_dir D:\datasets\mimic-cxr-jpg --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz --output_dir D:\experiments\exp3_full_sharp --batch_size 32 --bidirectional --hard_neg_max_frac 0.6 > D:\experiments\exp3_full_sharp\training.log 2>&1
