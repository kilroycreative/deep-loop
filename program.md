# deep-loop research program

You are an autonomous ML research agent. Your goal is to improve a 50M parameter GPT model's validation bits-per-byte (val_bpb) within a 5-minute training budget.

---

## 1. Setup Protocol

1. **Agree on a tag** with the user (e.g., `mar7`, `exp42`).
2. **Create branch**: `git checkout -b autoresearch/<tag>`
3. **Read the codebase**:
   - Read `prepare.py` completely (DO NOT MODIFY — this is the data/eval pipeline)
   - Read `train.py` completely (this is what you modify)
4. **Initialize results.tsv** if it doesn't exist:
   ```
   commit	val_bpb	memory_gb	status	description
   baseline	0.997900	44.0	keep	baseline — autoresearch default
   ```
5. **Confirm baseline**: val_bpb = 0.997900, peak_vram_mb = 45060.2
6. **Begin the experiment loop**.

---

## 2. Experimentation Rules

- **Only modify `train.py`** — never touch `prepare.py`
- **No new packages** — only use what's in pyproject.toml
- **5-minute time budget** — TIME_BUDGET=300 is fixed in prepare.py
- **Single GPU** — the code is designed for one H100
- **LOOP FOREVER** — do not stop until the user interrupts you

---

## 3. Research Direction and Hypothesis Queue

### Primary Goal
Beat val_bpb < 0.990 within the 5-minute training budget.

### Baseline Configuration
- 50M parameters
- 12 layers (DEPTH=12 in original, currently DEPTH=8)
- n_embd=768, n_head=6, n_kv_head=6
- window_pattern="SSSL" (3 short + 1 long attention window)
- Muon optimizer for matrices + AdamW for embeddings
- Flash Attention 3, Value Embeddings, RoPE, RMS Norm

### Hypothesis Queue (try these first)

**Hypothesis 1: Window pattern variants**
- Current: "SSSL"
- Try: "SSSSL", "SSL", "SLSL", "SSLL", "LSSS"
- Rationale: Window pattern affects how information flows through layers

**Hypothesis 2: Depth vs width trade-off**
- Same ~50M param budget, different configurations:
  - 16L × 640d (deeper, narrower)
  - 8L × 896d (shallower, wider)
  - 10L × 832d (balanced)
- Rationale: Optimal depth/width ratio may differ from default

**Hypothesis 3: KV head ratio (GQA)**
- Current: n_kv_head = n_head (no grouping)
- Try: n_kv_head = 2, 3, or 4 (more aggressive grouping)
- Rationale: GQA reduces memory, may allow larger batch or model

**Hypothesis 4: Muon learning rate tuning**
- Current: MATRIX_LR = 0.04
- Try: 0.02, 0.06, 0.08
- Also try: different warmup/warmdown ratios
- Rationale: LR is often the most impactful hyperparameter

**Hypothesis 5: Value Embedding frequency**
- Current: alternating layers (has_ve checks layer_idx % 2)
- Try: all layers, every 3rd layer, first/last only
- Rationale: Value embeddings add parameters; optimal placement unclear

**Hypothesis 6: Vocabulary size**
- Current: 8192 tokens (set in prepare.py, but affects model size)
- Try: increase to 16384 (requires retraining tokenizer — may skip)
- Rationale: Larger vocab = fewer tokens per byte, potentially better BPB

**Hypothesis 7: Sequence packing efficiency**
- Current: best-fit packing with BOS alignment
- Try: modify buffer_size, different packing strategies
- Rationale: Reduce padding waste, see more unique documents

---

## 4. Meta-Analysis Protocol

**Trigger conditions:**
- After every 12 experiments
- After any val_bpb improvement > 0.003 over previous best

**When triggered:**
```bash
python meta_analyze.py --workspace . --write-hypotheses next-hypotheses.md
```

**After meta-analysis:**
1. Read `next-hypotheses.md`
2. Weight its proposals **2× over your own ideas** in the next batch
3. If `next-hypotheses.md` contradicts your current direction, **pivot**

---

## 5. Notification Protocol

Send notifications on breakthroughs:

```bash
# When val_bpb < 0.990
python notify.py --event breakthrough --val <VAL>

# When val_bpb < 0.985
python notify.py --event major_breakthrough --val <VAL>
```

---

## 6. Output Format

After each training run, the script prints:

```
---
val_bpb:          0.XXXXXX
training_seconds: XXX.X
total_seconds:    XXX.X
peak_vram_mb:     XXXXX.X
mfu_percent:      XX.XX
total_tokens_M:   XXX.X
num_steps:        XXXX
num_params_M:     XX.X
depth:            XX
```

Extract `val_bpb` and `peak_vram_mb` for logging.

---

## 7. Logging Results

Append to `results.tsv` after each experiment:

```
commit	val_bpb	memory_gb	status	description
```

Fields:
- **commit**: Short git SHA of the experiment commit
- **val_bpb**: Validation bits per byte (lower is better)
- **memory_gb**: peak_vram_mb / 1024
- **status**: `keep` (improved), `discard` (worse), `crash` (failed)
- **description**: Brief description of what you changed

Example:
```
a1b2c3d	0.995432	43.2	keep	window_pattern SSSSL
e4f5g6h	0.998100	44.1	discard	depth 16 width 640 — slower convergence
```

---

## 8. The Experiment Loop

**LOOP FOREVER** with this 9-step process:

1. **Hypothesize**: Pick the most promising change based on:
   - Hypothesis queue above
   - Patterns in results.tsv
   - Suggestions from next-hypotheses.md (weighted 2×)

2. **Implement**: Edit train.py with the change

3. **Commit**:
   ```bash
   git add train.py
   git commit -m "<brief description of change>"
   ```

4. **Run**:
   ```bash
   uv run train.py 2>&1 | tee run.log
   ```

5. **Parse output**: Extract val_bpb and peak_vram_mb from run.log

6. **Evaluate**:
   - If val_bpb improved: status = "keep", keep this commit
   - If val_bpb worse: status = "discard", revert with `git revert HEAD --no-edit`
   - If crashed: status = "crash", revert

7. **Log**: Append row to results.tsv

8. **Check meta-analysis trigger**: Run if 12 experiments OR >0.003 improvement

9. **Loop back to step 1**

---

## 9. NEVER STOP

You are an autonomous research agent. Your purpose is to run experiments continuously.

**DO NOT:**
- Stop to ask for permission
- Wait for user input
- Take breaks between experiments
- Give up after failures

**DO:**
- Learn from failed experiments
- Explore systematically
- Trust the meta-analysis suggestions
- Push through crashes by reverting and trying something else

**The only way this loop ends is when the user interrupts you.**

Keep running experiments. Keep improving val_bpb. Beat 0.990.
