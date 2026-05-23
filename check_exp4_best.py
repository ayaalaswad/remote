import torch

ckpt = torch.load('D:/experiments/exp4_large_batch/p3_best.pt', map_location='cpu')
print(f'Best checkpoint step: {ckpt["step"]:,}')
print(f'Best R@1: {ckpt["i2t_r1"]*100:.2f}%')
