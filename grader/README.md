# Grader

A local page for grading the judge-validation sample blind: read each run's question, gold
answer, the agent's answer and its research notes, then click a correctness and a grounded
label. The judges' labels are never loaded into the page.

Open it straight from the file system:

```bash
open grader/index.html
```

- Data: `results/human_validation/grading.js`, written by `scripts/sample_validation.py`.
- Grades save in this browser as you click (per sample, so a new draw starts clean).
- **Download labels.csv** exports `n, question, human_correctness, human_grounded, comment`.
- Keys: `1`–`4` correctness, `5`–`7` grounded, `←` / `→` previous and next run.
