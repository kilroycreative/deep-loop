# /status — Show Experiment Progress

Run these commands to summarize the current state of the research loop:

```bash
# Branch and latest commits
git branch --show-current
git log --oneline -8

# Full results table
echo "=== results.tsv ==="
cat results.tsv

# Summary counts
echo ""
echo "=== Summary ==="
TOTAL=$(tail -n +2 results.tsv | grep -v "^baseline" | wc -l | tr -d ' ')
KEPT=$(grep -c "$(printf '\t')keep$(printf '\t')" results.tsv 2>/dev/null || echo 0)
DISC=$(grep -c "$(printf '\t')discard$(printf '\t')" results.tsv 2>/dev/null || echo 0)
CRASH=$(grep -c "$(printf '\t')crash$(printf '\t')" results.tsv 2>/dev/null || echo 0)
echo "Experiments: $TOTAL (kept=$KEPT discarded=$DISC crashed=$CRASH)"

# Best result
echo ""
echo "=== Best val_bpb ==="
sort -t $'\t' -k2 -n results.tsv | head -3
```
