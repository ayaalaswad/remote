# Remote Desktop - Quick Instructions

## ✅ Git Push Complete!

All changes have been pushed to GitHub. You can now pull on the remote desktop.

---

## 📋 What to Do on Remote Desktop

### Step 1: Open Remote Desktop & Pull Changes

1. **Connect to remote desktop**
2. **Open Command Prompt or PowerShell**
3. **Navigate to project:**
   ```batch
   cd C:\Users\aya.alaswad\remote\MyReasearch
   ```

4. **Pull latest changes:**
   ```batch
   git pull
   ```

   You should see:
   ```
   Updating 5cf26a3..8ff0846
   Fast-forward
    13 files changed, 2132 insertions(+)
    create mode 100644 run_raddino_both_experiments.bat
    create mode 100644 write_progress.bat
    ...
   ```

---

### Step 2: Run RadDINO Experiments

**Single command to run everything:**
```batch
run_raddino_both_experiments.bat
```

**What happens:**
1. ✓ Checks prerequisites (5 min)
2. ✓ Creates vanilla RadDINO checkpoint from HuggingFace (5 min)
3. ✓ Runs Experiment 1: RadDINO+SHARP Stage 1 → Stage 2 (2h 15m)
4. ✓ Runs Experiment 2: RadDINO vanilla → Stage 2 (2h 15m)
5. ✓ Auto-compares results and generates markdown report (1 min)

**Total time: ~4 hours 30 minutes**

---

### Step 3: Check Progress (While Running)

**Progress file location:**
```
C:\Users\aya.alaswad\Desktop\sharp_progress.txt
```

**How to check:**
- **Option A:** On remote desktop, open Desktop → double-click `sharp_progress.txt`
- **Option B:** Remote desktop → Notepad Desktop\sharp_progress.txt
- **Option C:** If you stay connected, just watch the console output

**What you'll see in progress file:**
```
[06/23/2026 10:30:15] RadDINO experiments started - Setup complete
[06/23/2026 10:35:22] Experiment 1 (RadDINO+SHARP) - Training started (~2h)
[06/23/2026 12:45:18] Experiment 1 - Training complete! Starting testing (~15min)
[06/23/2026 13:00:42] Experiment 1 COMPLETE! Starting Experiment 2 (~2h 15m)
[06/23/2026 15:15:30] Experiment 2 - Training complete! Starting testing (~15min)
[06/23/2026 15:30:51] Experiment 2 COMPLETE! Generating comparison report...
[06/23/2026 15:32:05] ALL DONE! Results in raddino_results\COMPARISON_RESULTS.md
```

---

### Step 4: After Training Completes (~4-5 hours)

**Results location:**
```
C:\Users\aya.alaswad\remote\MyReasearch\raddino_results\COMPARISON_RESULTS.md
```

**This file contains:**
- ✓ CheXbert F1 for both experiments
- ✓ Comparison: Exp 1 vs Exp 2 vs Main SHARP
- ✓ Auto-generated interpretation
- ✓ Whether to include in paper
- ✓ Suggested paper text (if results are good)

**How to open:**
```batch
cd C:\Users\aya.alaswad\remote\MyReasearch
notepad raddino_results\COMPARISON_RESULTS.md
```

Or just open it in File Explorer.

---

## 📊 Files Created (After Training)

```
MyReasearch/
├── Desktop/
│   └── sharp_progress.txt          ← Progress updates (check anytime)
│
├── raddino_results/
│   ├── COMPARISON_RESULTS.md       ← Main results report (after ~5h)
│   └── comparison.json             ← Detailed metrics (JSON)
│
├── stage2_training/logs/
│   ├── raddino_exp1_train.log      ← Exp 1 training log
│   ├── raddino_exp1_test.log       ← Exp 1 testing log
│   ├── raddino_exp2_train.log      ← Exp 2 training log
│   ├── raddino_exp2_test.log       ← Exp 2 testing log
│   └── raddino_master.log          ← Master timeline
│
└── D:/experiments/
    └── raddino_vanilla/
        └── pretrained.pt           ← Vanilla RadDINO checkpoint (created automatically)
```

---

## ⏰ Timeline

| Time | What's Happening | Progress File Says |
|------|------------------|-------------------|
| 0:00 | Start training | "Setup complete" |
| 0:10 | Exp 1 training starts | "Training started (~2h)" |
| 2:15 | Exp 1 testing starts | "Training complete! Starting testing" |
| 2:30 | Exp 1 done, Exp 2 starts | "Exp 1 COMPLETE! Starting Exp 2" |
| 4:45 | Exp 2 testing starts | "Training complete! Starting testing" |
| 5:00 | All done! | "ALL DONE! Results in..." |

---

## 🎯 Quick Commands Cheat Sheet

```batch
# Pull latest code
cd C:\Users\aya.alaswad\remote\MyReasearch
git pull

# Run experiments
run_raddino_both_experiments.bat

# Check progress (while running)
notepad C:\Users\aya.alaswad\Desktop\sharp_progress.txt

# View results (after done)
notepad raddino_results\COMPARISON_RESULTS.md

# Check detailed logs (if needed)
notepad stage2_training\logs\raddino_exp1_train.log
```

---

## ⚠️ If Something Goes Wrong

**Error during training:**
1. Progress file will say "ERROR: ..."
2. Check logs: `stage2_training\logs\raddino_exp*_train.log`
3. Common issues:
   - GPU out of memory → Reduce batch size in configs
   - Checkpoint not found → Verify RadDINO Stage 1 completed
   - Preprocessing missing → Run `cd stage2_training && run_preprocessing.bat`

---

## 💡 Pro Tips

1. **You can close remote desktop** after starting - training continues in background
2. **To reconnect and check:** Remote desktop → Open progress file on Desktop
3. **Last line of progress file** = current status
4. **If "ALL DONE!"** appears → Training complete, check results
5. **Set a reminder:** Check back after ~5 hours

---

## ✅ You're Ready!

**Summary:**
1. Connect to remote desktop
2. `cd C:\Users\aya.alaswad\remote\MyReasearch`
3. `git pull`
4. `run_raddino_both_experiments.bat`
5. Wait ~5 hours (or disconnect and come back)
6. Check `raddino_results\COMPARISON_RESULTS.md`

That's it! Good luck! 🚀
