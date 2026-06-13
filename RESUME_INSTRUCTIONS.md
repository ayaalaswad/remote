# Resume Unfinished Training - Quick Guide

## 🎯 Three Ways to Resume

### Option 1: Auto-Resume Everything (Recommended)
**Fully automated, no prompts, runs all unfinished experiments sequentially**

```cmd
cd C:\Users\aya.alaswad\remote
git pull origin main
resume_all_auto.bat
```

**What it does:**
1. Checks SIIM (1%, 10%, 100%) - resumes any incomplete
2. Checks RSNA Linear Probe - resumes if incomplete
3. Checks RadDINO - resumes if incomplete
4. Extracts all results at the end

**Time:** Depends on what's incomplete (could be 5-20 hours total)

**Best for:** Running overnight or when you want hands-off operation

---

### Option 2: Interactive Resume (Confirm Each)
**Shows status, lets you confirm before each experiment**

```cmd
cd C:\Users\aya.alaswad\remote
git pull origin main
resume_all_unfinished.bat
```

**What it does:**
- Shows what's incomplete
- Asks "Press any key" before each experiment
- Lets you skip experiments with Ctrl+C

**Best for:** When you want control over what resumes

---

### Option 3: Manual Resume (One at a Time)
**Resume specific experiments individually**

#### SIIM Only:
```cmd
cd C:\Users\aya.alaswad\remote
run_siim_all_splits.bat
```

#### RSNA Linear Probe Only:
```cmd
cd C:\Users\aya.alaswad\remote
copy sharp_rsna_lp.yml BenchX\configs\classification\RSNA\sharp.yml /Y
cd BenchX
python bin/train.py configs/classification/RSNA/sharp.yml
```

#### RadDINO Only:
```cmd
cd C:\Users\aya.alaswad\remote
run_raddino_exp3_hardneg.bat
```

**Best for:** When you know exactly which experiment to resume

---

## 📊 Check Status First (Before Resuming)

```cmd
cd C:\Users\aya.alaswad\remote
check_all_training_status.bat
```

This shows:
- ✅ What's complete
- ⏳ What's in progress
- ❌ What needs to resume
- 📈 Latest checkpoints and progress

---

## 🔍 Quick Status Check Commands

### SIIM:
```cmd
dir C:\Users\aya.alaswad\remote\BenchX\experiments\classification\siim\SHARP_*\SHARP_*\*.pth
```

### RSNA Linear Probe:
```cmd
dir C:\Users\aya.alaswad\remote\BenchX\experiments\classification\rsna\SHARP_LP\SHARP_LP\*.pth
```

### RadDINO:
```cmd
python -c "import torch; ckpt=torch.load('D:/experiments/exp_raddino_hardneg/p3_last.pt'); print(f'Step: {ckpt[\"step\"]:,} / 100,000')"
```

---

## ⏱️ Expected Training Times

| Experiment | Status | Remaining Time |
|------------|--------|----------------|
| SIIM 1% | Check status | ~20-30 min |
| SIIM 10% | Check status | ~1-1.5 hours |
| SIIM 100% | Check status | ~2-3 hours |
| RSNA Linear Probe | Check status | ~1-2 hours |
| RadDINO | Check status | Depends on step (max ~20 hours) |

---

## 🎯 Recommended Workflow

1. **Check what's incomplete:**
   ```cmd
   check_all_training_status.bat
   ```

2. **Resume everything automatically:**
   ```cmd
   resume_all_auto.bat
   ```

3. **Let it run (overnight if needed)**

4. **Check results:**
   ```cmd
   python extract_all_results.py
   ```

---

## ❓ FAQ

**Q: Will resuming overwrite my existing results?**
A: No! Each experiment saves to a different directory.

**Q: Can I resume if the CMD window was closed?**
A: Yes! All experiments auto-resume from their last checkpoint.

**Q: How do I know if training is still running?**
A: Run `check_all_training_status.bat` - it shows active Python processes.

**Q: What if I want to stop and resume later?**
A: Just close the window. Checkpoints are saved every 1000-2000 steps. Re-run the resume script later.

**Q: Which resume option should I use?**
A: Use `resume_all_auto.bat` if you want everything to run automatically without prompts.

---

## 🚀 TL;DR - Quick Start

**Just want everything to finish automatically?**

```cmd
cd C:\Users\aya.alaswad\remote
git pull origin main
resume_all_auto.bat
```

Then go do something else. It will run all unfinished experiments and extract results when done.
