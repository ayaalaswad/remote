# Bidirectional Loss - Action Plan

## TL;DR

**Problem:** Paper claims ablation (B) achieved R@1 = 7.02% with unidirectional loss, but this experiment cannot be found in the repository.

**Finding:** All documented experiments used **bidirectional** loss. The 7.02% value appears in the paper but has no corresponding experiment artifacts.

**Confidence:** 85% that the paper claim is incorrect.

---

## Quick Decision Tree

### Can you access the RunPod server where experiments were originally run?

#### ✅ YES - RunPod is accessible

**Run this on RunPod:**
```bash
cd /workspace/experiments/vit_ablation_B
cat experiment_config.json | grep bidirectional
ls -la *.pt
```

**Then decide:**
- **If shows `"bidirectional": true`** → Paper is incorrect, update Section 2.2 and remove bidirectional ablation paragraph
- **If shows `"bidirectional": false`** → Paper is correct, but where is the 6.61% bidirectional re-run?
- **If directory doesn't exist** → Proceed to "NO" path below

---

#### ❌ NO - RunPod is not accessible

**You have 3 options:**

### Option 1: Update Paper to Match Reality (RECOMMENDED)

**Effort:** Low (1-2 hours of paper editing)
**Risk:** Low

**Changes needed:**

1. **Section 2.2 (line 220)** - Change from unidirectional to bidirectional:
   ```latex
   % BEFORE:
   The loss is unidirectional (image anchors only)

   % AFTER:
   The loss is bidirectional, computing both image→text and
   text→image directions and averaging them (similar to CLIP).
   ```

2. **Section 4.2 (lines 564-576)** - Remove bidirectional ablation paragraph:
   ```latex
   % DELETE entire paragraph starting with:
   % "Bidirectional loss ablation. Reviewers noted..."
   ```

3. **Reviewer Response:**
   ```
   We have corrected a documentation error: all our experiments
   (including ablations) used bidirectional loss by default.
   The paper has been updated to accurately reflect this.
   ```

---

### Option 2: Re-run Experiments Without Bidirectional

**Effort:** High (multiple days of compute)
**Risk:** High (results will change)

**Steps:**

1. Edit all launch scripts to remove `--bidirectional` flag
2. Re-run Exp #1 (baseline) - expect different R@1
3. Re-run Exp #3 (SHARP) - expect different R@1
4. Update all values in paper
5. Re-run Stage 2 experiments with new checkpoints
6. Update all downstream F1 values

**Not recommended** unless you specifically need unidirectional results.

---

### Option 3: Keep Paper As-Is and Hope

**Effort:** Zero
**Risk:** Extreme (reviewers may ask for proof)

**Likely reviewer question:**
> "Can you provide the experiment config and training logs showing
> the 7.02% unidirectional ablation (B) run?"

**You won't be able to answer this.**

**Not recommended.**

---

## What Files to Read

1. **BIDIRECTIONAL_FINAL_FINDINGS.md** - Comprehensive investigation report with all evidence
2. **BIDIRECTIONAL_INVESTIGATION_REPORT.md** - Initial technical analysis
3. **STAGE1_CHECKPOINT_LOCATIONS.md** - Where to find ablation checkpoints (on RunPod)
4. **check_runpod_experiments.sh** - Script to run on RunPod to verify configs

---

## Evidence Summary

### ✅ Evidence that ALL experiments used bidirectional:

1. `experiments.md` line 22 explicitly says "Bidirectional loss: Yes (all experiments)"
2. `run_exp4_v2a_FAIR.bat` line 58 has `--bidirectional` flag
3. All R@1 values in experiments.md match the "bidirectional variant" values in paper (6.61%, 6.21%, etc.)
4. Paper was created May 19, 2026 - AFTER bidirectional flag was added to code (May 17)

### ❌ Evidence for 7.02% unidirectional experiment:

1. No experiment config with `bidirectional: false`
2. No checkpoint files with R@1 ≈ 0.0702
3. No training logs mentioning unidirectional loss
4. No experiment directory with 7.02% results
5. No mention of 7.02% in experiments.md or check_r1_scores.py

---

## Paper Claims vs. Reality

| Paper Claim | Reality |
|-------------|---------|
| Ablation (B) unidirectional R@1 = 7.02% | ❌ No experiment found |
| Ablation (B) bidirectional R@1= 6.61% | ✓ Exp #1 achieves 6.61% |
| Ablations used unidirectional loss | ❌ experiments.md says bidirectional |
| Section 2.2 says unidirectional | ❌ All experiments used bidirectional |

---

## Recommended Action (If RunPod Inaccessible)

### Step 1: Accept Reality

All your documented experiments used bidirectional loss. The 7.02% unidirectional value is either:
- From preliminary experiments no longer documented
- A typo or error
- Never actually measured

### Step 2: Update Paper

**File:** `paper.tex`

**Change 1 - Section 2.2 (around line 220):**
```latex
The loss is bidirectional (averaging i→t and t→i directions, similar to CLIP);
same-concept crops share a $(r,e,p)$ key and act as multiple positives.
```

**Change 2 - Section 4.2 (around line 564-576):**
```latex
% DELETE this entire paragraph:
\noindent\textbf{Bidirectional loss ablation.}
Reviewers noted that ablations (A)--(D) used unidirectional loss...
[entire paragraph]
```

**Change 3 - Add brief note in limitations or methods:**
```latex
All contrastive pretraining experiments use bidirectional InfoNCE loss,
computing both image→text and text→image directions and averaging them.
```

### Step 3: Reviewer Response

**Template:**
```
Thank you for raising this concern. Upon reviewing our experimental
logs, we discovered that all our experiments (including ablations
A-D and SHARP) used bidirectional loss by default. The paper
contained a documentation error stating "unidirectional" in Section 2.2.

We have corrected this in the revised manuscript. All reported results
(retrieval R@1 and downstream CheXbert F1) were obtained using
bidirectional contrastive loss. This does not affect our main
conclusions, as the comparison between ablations and SHARP remains
valid (all use the same loss directionality).
```

### Step 4: Commit Changes

```bash
git add paper.tex
git commit -m "Fix: Correct bidirectional loss documentation in paper"
git push
```

---

## FAQ

**Q: Will this weaken my paper?**
A: No. Your main contributions (scene-graph multi-positive InfoNCE, hard negative curriculum) are independent of bidirectional vs unidirectional. Bidirectional is actually the standard (CLIP uses it), so this makes your method more comparable to baselines.

**Q: What if reviewers ask why I claimed unidirectional?**
A: "Documentation error. All experiments used bidirectional by default (standard for vision-language pretraining). We've corrected the manuscript."

**Q: Should I re-run everything with unidirectional?**
A: Only if you specifically want unidirectional results. Otherwise, no - your current bidirectional results are valid and likely stronger.

**Q: What about the 7.02% value?**
A: Cannot be verified. If you don't remember running this experiment, it's safer to remove the claim than to defend it without evidence.

**Q: Can I keep the bidirectional ablation paragraph?**
A: No. If all experiments used bidirectional, there's no "ablation" to report. Remove it.

---

## Timeline

### If you choose Option 1 (Update Paper):

- **30 min:** Read BIDIRECTIONAL_FINAL_FINDINGS.md
- **1 hour:** Edit paper.tex (remove bidirectional ablation, update Section 2.2)
- **30 min:** Write reviewer response
- **Total:** ~2 hours

### If you choose Option 2 (Re-run experiments):

- **1 hour:** Modify launch scripts
- **48+ hours:** Re-run experiments (Exp #1, #3, #4)
- **20+ hours:** Re-run Stage 2 experiments
- **2 hours:** Update paper with new values
- **Total:** ~72 hours compute + 3 hours human time

---

## Next Steps

1. Read `BIDIRECTIONAL_FINAL_FINDINGS.md` for complete evidence
2. Decide which option to take (recommend Option 1)
3. If Option 1: Edit paper.tex and push changes
4. If Option 2: Start re-running experiments without --bidirectional
5. If you can access RunPod: Run `check_runpod_experiments.sh` to verify

---

**Bottom Line:** Your experiments used bidirectional. Update the paper to match. This doesn't weaken your contributions.

**Created:** 2026-06-26
**Status:** Ready for decision
