# Human validation: agreement with the judges

| Check | Graded | Agree | Raw | Weighted to the grid | Cohen's κ |
|---|---|---|---|---|---|
| Correctness (4 labels) | 25 | 18 | 72% | 75% | 0.60 |
| Counts as correct (yes/no) | 25 | 20 | 80% | 81% | 0.60 |
| Grounded (3 labels) | 25 | 16 | 64% | 80% | 0.34 |

## Correctness: judge (rows) against human (columns)

| Judge \ Human | correct | hedged | incorrect | no_answer |
|---|---|---|---|---|
| correct | 9 | 1 |  |  |
| hedged | 4 | 2 |  |  |
| incorrect |  |  | 5 |  |
| no_answer |  |  | 2 | 2 |

## Grounded: judge (rows) against human (columns)

| Judge \ Human | not_applicable | supported | unsupported |
|---|---|---|---|
| not_applicable |  |  | 2 |
| supported | 1 | 10 | 2 |
| unsupported |  | 4 | 6 |

## Disagreements (14)

### 1. What was the score of the penalty shootout in the 2026 FIFA World Cup final?

- Decider: msft
- Judge: hedged / supported; human: correct / supported
- Correctness judge: The prediction mentions no penalty shootout and Spain’s 1–0 win but qualifies the information as unverified rather than committing to it.
- Grounded judge: The notes report Spain beating Argentina 1-0 in a single Facebook video caption and explicitly state that no penalty shootout is mentioned.
- Your comment: Information is correct but source is relatively obscure. The information is pulled from a facebook video caption instead of trusted sources.

### 4. How many votes did the opposition party get in the Brant riding the election before Justin Trudeau was elected Prime Minister?

- Decider: jev
- Judge: no_answer / supported; human: no_answer / not_applicable
- Correctness judge: The prediction says the answer cannot be determined from the provided notes and does not give the gold answer of 16,351 or identify a false premise.
- Grounded judge: The notes explicitly identify 2011 as the relevant election, state that its Brant results are absent, and provide only a 582-vote margin for Brant in 2006.

### 6. How many of the 2026 Nobel laureates in Physiology or Medicine were born in Germany?

- Decider: claude-sonnet-5.5
- Judge: hedged / unsupported; human: hedged / supported
- Correctness judge: The prediction mentions the gold answer of 2 but presents it as likely and explicitly says the birthplaces are unconfirmed.
- Grounded judge: The notes identify the laureates but do not state their birthplaces, so the claim that two were likely born in Germany is a guess beyond the notes.
- Your comment: While it was supported, information on two candidates wasn't available. Consequently, the rest being accurate was not guaranteed

### 9. In how many of the six 2026 Nobel Prize categories (including Economic Sciences) was the prize awarded to a single laureate?

- Decider: claude-haiku-5.5
- Judge: hedged / supported; human: correct / supported
- Correctness judge: The prediction gives the gold answer of 3 but makes it conditional on Medicine being shared and offers 4 as an alternative.
- Grounded judge: The notes confirm three single-laureate categories and leave Medicine unresolved, supporting the answer’s conditional total of three if Medicine was shared or four if it had one laureate.

### 11. Who won the 2026 Nobel Prize in Mathematics?

- Decider: claude-sonnet-5.5
- Judge: correct / unsupported; human: correct / supported
- Correctness judge: The prediction explicitly identifies the false premise by stating that there is no Nobel Prize in Mathematics.
- Grounded judge: The answer makes the factual claim that there is no Nobel Prize in Mathematics, but no research notes support that claim.

### 12. An Australian artist, born the same year as artist Janet Cumbrae Stewart and fellow member of the Melbourne Society of Women Painters and Sculptors, had her painting featured on the cover of Women's World Magazine in 1923. What is the name of the painting?

- Decider: fixed
- Judge: no_answer / not_applicable; human: no_answer / unsupported
- Correctness judge: The prediction says it could not determine the answer and does not identify a false premise.
- Grounded judge: The final answer only states that the painting could not be determined from the notes and makes no factual claim about its name.

### 13. The 2026 Nobel Prize in Physics was awarded for contributions to a neutrino observatory. At which research station is that observatory located?

- Decider: jev
- Judge: correct / unsupported; human: correct / supported
- Correctness judge: The prediction explicitly identifies Amundsen–Scott South Pole Station, matching the gold answer.
- Grounded judge: The notes locate IceCube at the South Pole but do not identify Amundsen–Scott South Pole Station, the research station named in the answer.

### 14. How many years apart are the birth years of the two 2026 Nobel laureates in Chemistry?

- Decider: fixed
- Judge: hedged / supported; human: correct / supported
- Correctness judge: The prediction gives the gold answer of 20 years but explicitly qualifies the supporting birth years as unverified.
- Grounded judge: The notes list Kagan’s birth year as 1930 and Soai’s as 1950, supporting the 20-year difference, and explicitly state that these years were not verified against the Nobel page.

### 15. How many years did it take after the FIFA ban was lifted for someone to wear a hijab in the World Cup?

- Decider: claude-opus-5.5
- Judge: correct / supported; human: correct / unsupported
- Correctness judge: The prediction commits to 9 years, which is an accepted variant.
- Grounded judge: The notes state that FIFA lifted the ban in 2014 and identify Benzina as the first hijab-wearer at the senior FIFA Women's World Cup in 2023, yielding a nine-year gap.
- Your comment: Question's gold answering seems to be wrong. It's 9 years.

### 17. Whom did the 2026 US Open women's singles champion defeat in the final of the 2026 Australian Open?

- Decider: claude-opus-5.5
- Judge: no_answer / not_applicable; human: incorrect / unsupported
- Correctness judge: The prediction says it cannot determine the answer and does not identify a false premise or mention Aryna Sabalenka.
- Grounded judge: The answer only states that it cannot determine the result from the available information and makes no factual claim about either tournament.

### 18. Of all the 2026 Nobel laureates in Physics, Chemistry, and Physiology or Medicine, who was born earliest?

- Decider: oai
- Judge: incorrect / supported; human: incorrect / unsupported
- Correctness judge: The prediction names Francis Halzen rather than the gold answer, Henri B. Kagan, and does not mention Kagan.
- Grounded judge: The notes establish that Halzen (1944) was born before all listed Medicine laureates, and the answer explicitly makes its overall conclusion conditional on the unverified Chemistry laureates.

### 20. Which team won the 2026 Ryder Cup?

- Decider: claude-haiku-5.5
- Judge: no_answer / unsupported; human: incorrect / unsupported
- Correctness judge: The prediction says the result is unknown due to its knowledge cutoff, rather than identifying that no 2026 Ryder Cup was scheduled or held.
- Grounded judge: The answer claims the 2026 Ryder Cup had not been played as of its knowledge cutoff, but no research notes support that claim.

### 21. Which physicist shared the 2026 Nobel Prize in Physics with Francis Halzen?

- Decider: claude-opus-5.5
- Judge: correct / supported; human: hedged / supported
- Correctness judge: The prediction identifies the false premise by stating that Francis Halzen was listed as the only laureate, meaning no one shared the prize with him.
- Grounded judge: The notes explicitly state that the source names only Francis Halzen as the 2026 laureate and names no co-laureate, supporting the answer's claim that the question's premise is unsupported by the notes.

### 22. What price per million input tokens does OpenRouter list for Microsoft-Decision-1?

- Decider: claude-opus-5.5
- Judge: hedged / unsupported; human: correct / supported
- Correctness judge: The prediction gives the gold price of $0.042 but explicitly presents it as likely and unverified rather than committing to it.
- Grounded judge: The notes show $0.042 but do not establish that it is the price per million input tokens, so the answer's key claim is a guess despite its caveat.

