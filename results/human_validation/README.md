# Human validation

Grade each row of `grading.csv` blind: fill in `human_correctness`, `human_grounded` and, if useful, `comment`. Leave `key.csv` closed until you're done.

## human_correctness

- "correct": the prediction commits to the gold answer or an accepted variant (or a clear
  equivalent: same entity, number or date; extra context and formatting are fine). If the
  question cannot be answered as asked, "correct" means the prediction says so for the
  right reason: it identifies the false premise or that no such thing exists.
- "hedged": the prediction mentions the gold answer but does not commit to it: it offers
  other candidates alongside it, or presents it as a guess or as unverified.
- "incorrect": the prediction commits to a different answer. For a question that cannot
  be answered as asked, inventing an answer is "incorrect".
- "no_answer": the prediction declines, or says it could not determine the answer,
  without identifying a false premise.

## human_grounded

Judge only against the row's `notes`, not whether the answer is true.

- "supported": the notes contain the facts the answer's key claim rests on, directly or
  by simple arithmetic or comparison of facts in the notes.
- "unsupported": the key claim is missing from the notes or goes beyond them; the answer
  relies on outside knowledge or a guess.
- "not_applicable": the answer makes no factual claim (it only declines or says it could
  not determine the answer).
