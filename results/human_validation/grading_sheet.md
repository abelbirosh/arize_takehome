# Human validation: grading sheet

Grade each run blind. Put your labels in `labels.csv`; leave `key.csv` closed until you're done.

## Correctness labels (same rubric as the judge)

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

## Grounded labels (same rubric as the judge)

Judge only against the notes below, not whether the answer is true.

- "supported": the notes contain the facts the answer's key claim rests on, directly or
  by simple arithmetic or comparison of facts in the notes.
- "unsupported": the key claim is missing from the notes or goes beyond them; the answer
  relies on outside knowledge or a guess.
- "not_applicable": the answer makes no factual claim (it only declines or says it could
  not determine the answer).

---

## 1. The 2026 Nobel Prize in Physics was awarded for contributions to a neutrino observatory. At which research station is that observatory located?

- **Gold:** Amundsen–Scott South Pole Station
- **Accepted:** Amundsen–Scott South Pole Station
- **Answerable as asked:** yes
- **Predicted answer:** The South Pole (Amundsen–Scott South Pole Station, Antarctica), where the IceCube Neutrino Observatory is built into the Antarctic ice.

**Research notes**

```
[Nobel physics prize awarded for detection of cosmic ...]
- 2026 Nobel Prize in Physics awarded to Francis Halzen (Belgian-born, University of Wisconsin–Madison) for founding IceCube Neutrino Observatory and discovery of high-energy cosmic neutrinos; announced 6 October (Stockholm).
- Question's answer: IceCube is located at the South Pole ("IceCube, based in the South Pole"; "The IceCube Neutrino Observatory at the South Pole"; detectors sunk into Antarctic ice).
- IceCube: array of 5,160 sensors, completed 2011; collaboration of 450+ researchers; Halzen principal investigator since original 1999 proposal.
- Strings lowered >1.5 km into drilled holes in clear Antarctic ice.
- 2013 IceCube paper (Science 342, 1242856): population of extremely high-energy extraterrestrial neutrinos.
- 2014: three highest-energy neutrinos ("Bert, Ernie, Big Bird").
- 2017: "Texas event" traced to blazar TXS 0506+056.
```

---

## 2. Whom did the 2026 US Open women's singles champion defeat in the final of the 2026 Australian Open?

- **Gold:** Aryna Sabalenka
- **Accepted:** Aryna Sabalenka; Sabalenka
- **Answerable as asked:** yes
- **Predicted answer:** Unable to determine from the available information; I don't have reliable data on the 2026 Australian Open final or the 2026 US Open champion.

**Research notes**

```
(no notes)
```

---

## 3. A united states island that is only 90 miles away from Cuba has been the home of several famous people. In what year did the famous author who owns a book store there first start writing?

- **Gold:** 1959
- **Accepted:** 1959
- **Answerable as asked:** yes
- **Predicted answer:** 1937 (tentative; based on Stetson Kennedy, whose Key West bookstore link is unverified in the notes)

**Research notes**

```
[Stetson Kennedy]
- Stetson Kennedy: American author, folklorist, activist; born Oct 5, 1916, Jacksonville FL; died Aug 27, 2011, Jacksonville.
- Kennedy met Cuban émigré Edith Ogden-Aguilar in Key West, FL while doing fieldwork shortly after leaving UF (married 1936); Key West link fits the Cuba-proximity clue.
- Kennedy's 2008 book Grits and Grunts: Folkloric Key West (Pineapple Press).
- In 2006 Kennedy married writer and bookstore owner Sandra Parks (former St. Augustine city commissioner); married until his death in 2011. (Bookstore owner = Sandra Parks, not Kennedy; check whether Parks' bookstore is in Key West.)
- Kennedy's first writing-related activity: published/contributed to periodicals; wrote "Inside Out" column for Federated Press 1937–1950; joined Federal Writers' Project in 1937 (after leaving UF); collected Florida folklore for five years (~1937 onward); early writing at UF/active 1936 (collected supplies for Spanish Republic, not writing).
- Kennedy's first book: Palmetto Country (1942), built from unused Federal Writers' Project material.
- Kennedy's wife Edith Ogden-Aguilar was the Cuban émigré; Key West is the island connection to be verified (island ~90 miles from Cuba).
```

---

## 4. How many years had passed since the Commonwealth of Pennsylvania was admitted to the Union by the time Rep. Robert D. Heaton was born?

- **Gold:** 85
- **Accepted:** 85
- **Answerable as asked:** yes
- **Predicted answer:** Cannot be determined from the notes; the formula is (Heaton's birth year − 1787). If he was born c. 1880, that is about 93 years (unverified).

**Research notes**

```
(no notes)
```

---

## 5. In how many of the six 2026 Nobel Prize categories (including Economic Sciences) was the prize awarded to a single laureate?

- **Gold:** 3
- **Accepted:** 3; three (Physics, Literature, Peace)
- **Answerable as asked:** yes
- **Predicted answer:** 3 (Physics, Peace, Literature; the notes leave open whether Chemistry, Medicine, or Economics also had a single laureate, which would make it 4)

**Research notes**

```
[2026 Nobel Peace Prize]
- 2026 Nobel Peace Prize awarded to a single laureate: South African jurist Navi Pillay (announced 9 October 2026, Oslo; ceremony 10 December 2026).
- Peace Prize reward: 12.0 million SEK.
- Source gives no information on the other five 2026 categories (Physics, Chemistry, Physiology or Medicine, Literature, Economic Sciences).

[2026 Nobel Prize in Literature]
- 2026 Nobel Prize in Literature awarded to a single laureate: Canadian poet Anne Carson (announced 8 October 2026, Stockholm; ceremony 10 December 2026).
- Literature citation: "for her bold and inventive oeuvre that, in playful dialogue with the classical tradition, has created new forms for contemporary literature."
- Literature pre-announcement betting odds: Carson 10/1 (joint favourite with Can Xue 10/1).
- Source gives no information on Physics, Chemistry, Physiology or Medicine, or Economic Sciences; no shared-award info for those categories.

[Press release: Nobel Prize in Physics 2026]
- [2026 Nobel Prize in Physics] - awarded to a single laureate: Francis Halzen (University of Wisconsin–Madison, USA; born 1944 Tienen, Belgium), announced 6 October 2026. Citation: "for decisive contributions to the IceCube Neutrino Observatory and the discovery of high-energy neutrinos of astrophysical origin." Prize amount 12 million SEK.
- Physics: single laureate (no shared award indicated).
- Page footer: "Six prizes were awarded... The 10 laureates' work and discoveries range from optogenetics to efforts to promote peace and international law." Implies 10 laureates total across six prizes; with Physics (1), Peace (1), Literature (1) single-laureate, the remaining Chemistry, Physiology or Medicine, and Economic Sciences together account for 7 laureates. Optogenetics points to a Physiology or Medicine laureate (count not stated).
- Still unknown: number of laureates in Chemistry, Physiology or Medicine, Economic Sciences individually (only the 10-total bridge is given).
```

---

## 6. How many votes did the opposition party get in the Brant riding the election before Justin Trudeau was elected Prime Minister?

- **Gold:** 16,351
- **Accepted:** 16,351
- **Answerable as asked:** yes
- **Predicted answer:** Cannot be determined from the provided notes. The 2011 Brant result (the relevant election) isn't in the sources; the only figure given is a 582-vote margin from 2006.

**Research notes**

```
[2006 Canadian federal election]
- Justin Trudeau was elected PM in 2015 (election before = 2011 federal election, not in this source; this source is 2006).
- Brant, ON, 2006 result: Lloyd St. Amand (Lib) def. Phil McColeman (Cons) by 582 votes (10 closest ridings list).
- Brant 2006 vote totals for Conservative/Liberal not given in this source (only margin 582 shown; the riding-level table row for Brant is not in the excerpt).
- Note: Conservative (McColeman) was the opposition in Brant in 2006 only if Liberal held seat; in 2006 Liberal St. Amand won, so Conservative = runner-up/opposition candidate.
- Relevant bridging: Brant 2011 result (not in source) needed to identify the 2011 opposition party vote count; the source does not contain 2011 data.
```

---

## 7. In complete years, how much older is the 2026 Nobel Peace Prize laureate than the 2026 Nobel laureate in Literature?

- **Gold:** 8
- **Accepted:** 8; 8 years (Pillay born 23 September 1941, Carson born 21 June 1950)
- **Answerable as asked:** yes
- **Predicted answer:** 8 years (Pillay, b. 23 Sep 1941, vs. Carson, b. 21 Jun 1950; exact dates from memory, not in the notes)

**Research notes**

```
[2026 Nobel Peace Prize]
- 2026 Nobel Peace Prize laureate: South African jurist Navi Pillay (announced 9 October 2026; ceremony 10 December 2026). Birth year not given in source.
- Pillay chaired the Independent International Commission of Inquiry on the Occupied Palestinian Territory (source context).
- Source gives no 2026 Literature laureate; no birth dates for Pillay beyond what is needed for age calculation are stated.

[List of Nobel Peace Prize laureates]
- 2026 Nobel Peace Prize laureate Navi Pillay: "b. 1941" (Laureates table, 2026 row) — birth year now given, contrary to earlier note.
- Pillay citation: "for her efforts to promote peace and international law".
- No 2026 Literature laureate or birth date appears in source; literature age comparison cannot be computed from this source.

[2026 Nobel Prize in Literature]
- [2026 Nobel Prize in Literature] laureate: Canadian poet Anne Carson; announced 8 October 2026 (Swedish Academy, Stockholm); ceremony 10 December 2026.
- Citation: "for her bold and inventive oeuvre that, in playful dialogue with the classical tradition, has created new forms for contemporary literature."
- Carson's birth year/date: not stated in this source.
- Pre-announcement betting odds (not outcome): Carson 10/1, listed among contenders.

[List of Nobel laureates in Literature]
- 2026 Literature laureate: Anne Carson (1950–), Canada/Iceland, English; citation as in notes. Birth year 1950 (Laureates table, 2026 row).
- 2026 Peace laureate Navi Pillay: b. 1941 (per Peace list note above).
- Age gap: 1950 − 1941 = 9 years (Pillay older by 9 complete years if birth dates fall such that both are counted at current date; exact month/day not given in sources).
```

---

## 8. How many years did it take after the FIFA ban was lifted for someone to wear a hijab in the World Cup?

- **Gold:** 11 years
- **Accepted:** 11 years
- **Answerable as asked:** yes
- **Predicted answer:** About 9 years (ban lifted 2014; first hijab-wearer at a FIFA Women's World Cup, Nouhaila Benzina, in 2023).

**Research notes**

```
[Women's football in Iran]
- FIFA banned Iran from a second-round qualifier vs Jordan in mid-2011 over hijab requirement (enforced by government).
- FIFA eventually lifted the ban in 2014 (along with turban/kippah bans for Sikh/Jewish men).
- 2016: Iranian players wore hijabs in a FIFA-approved tournament, the U-17 Women's World Cup held in Jordan (per source; source describes this as first hijab-wearing at FIFA-approved event).
- Iran U-17 team qualified for 2015 Asian Championship (China), per source; Iran's first continental qualification for top competition in 2015.

[Muslim women in sport]
- FIFA hijab ban instituted in 2011 (source: "FIFA also instituted a hijab ban in 2011, forcing the Iranian women's team to forfeit an Olympic qualifying match"). Source calls it an Olympic qualifier, conflicting with the earlier note's "second-round qualifier vs Jordan."
- Source gives no date for FIFA rescinding the ban: only "FIFA has since rescinded its hijab ban and now allows athletes to compete in approved sports hijabs."
- FIFA U-17 Women's World Cup 2012 hosted by Azerbaijan (UEFA member); mascot Top Top Girl. Not a hijab-related fact, but dates a FIFA women's event.
- Jordan hosted 2016 FIFA U-17 Women's World Cup, "the first female soccer world cup to be held anywhere in the Middle East."
- FIBA (basketball) hijab ban overturned May 2017 (separate federation; not FIFA).
- Source does not mention any hijab-wearing player at a FIFA senior Women's World Cup or any FIFA World Cup.

[Nouhaila Benzina is the first woman to wear a hijab during ...]
- Source (FIFPRO Facebook post): Nouhaila Benzina is "the first woman to wear a hijab during the FIFA Women's World Cup" (senior event, 2023 per context of "so much history making in this world cup" comment; Benzina played for Morocco).
- FIFPRO post encourages players' "full expression of who they are, on and off the pitch."
- Implication: first hijab at a FIFA Women's World Cup (senior) is Benzina; the U-17 2016 hijab use by Iran is a different tournament, so the gap should be measured from FIFA's ban rescission (date still unknown in notes) to Benzina's appearance.
- Bridging: need rescission date of FIFA hijab ban (notes say 2014 for turban/kippah and "lifted" generally; hijab-ban lifting date unconfirmed) and Benzina's World Cup debut year (source comment suggests 2023 World Cup, Morocco).
```

---

## 9. What price per million input tokens does OpenRouter list for Microsoft-Decision-1?

- **Gold:** $0.042
- **Accepted:** $0.042; 0.042 USD; 4.2 cents
- **Answerable as asked:** yes
- **Predicted answer:** $0.042 per million input tokens (likely, but unverified because the column header is missing from the notes).

**Research notes**

```
[Microsoft-Decision-1 - API Pricing & Providers]
- Source is OpenRouter page for Microsoft-Decision-1; table shows "$0.042" in a column alongside "Free" and "0.34s" (labeled P50, best provider context).
- Unclear from the excerpt whether $0.042 is the input-token price per million; the table header is missing, so the column label (e.g., input price per M tokens) is not confirmed.
- Model is post-trained from Qwen3.5-9B; built for single-pass scoring returning calibrated probabilities over fixed answer options (not generation).
```

---

## 10. Which team did the runner-up of the 2026 Tour de France ride for?

- **Gold:** Red Bull–Bora–Hansgrohe
- **Accepted:** Red Bull–Bora–Hansgrohe; Red Bull-Bora-Hansgrohe; Red Bull Bora Hansgrohe
- **Answerable as asked:** yes
- **Predicted answer:** Unknown. The notes are empty and the 2026 Tour de France result is not in my knowledge, so I cannot name the runner-up's team.

**Research notes**

```
(no notes)
```

---

## 11. How old was the elder of the two 2026 Nobel laureates in Chemistry when the prize was announced in October 2026?

- **Gold:** 95
- **Accepted:** 95; 95 years old (Henri B. Kagan)
- **Answerable as asked:** yes
- **Predicted answer:** Most likely 96 (possibly 95), if Henri Kagan (b. 1930) is indeed the elder laureate. The notes don't give his birth date, and I could not verify the 2026 announcement itself.

**Research notes**

```
[Press release: Nobel Prize in Chemistry 2026]
- Nobel Prize in Chemistry 2026 announced 7 October 2026; laureates: Henri B. Kagan (Université Paris-Sud, France) and Kenso Soai (Tokyo University of Science, Japan).
- Henri B. Kagan: born 1930 in Boulogne-Billancourt, France; PhD 1960, Collège de France; Professor Emeritus, Université Paris-Sud.
- Kenso Soai: born 1950 in Hiroshima, Japan; PhD 1979, University of Tokyo; Professor Emeritus, Tokyo University of Science.
- Elder laureate = Kagan (born 1930). Age on 7 Oct 2026 depends on birthdate (month/day not given in source); he would be 96 if birthday fell before 7 October, otherwise 95. Soai (b. 1950) would be 75 or 76.
```

---

## 12. Which of the two 2026 US Open singles champions is older?

- **Gold:** Alexander Zverev
- **Accepted:** Alexander Zverev; Zverev
- **Answerable as asked:** yes
- **Predicted answer:** Alexander Zverev (born 1997) is older than Elena Rybakina (born 1999). This relies on birthdates from my own knowledge, not the research notes.

**Research notes**

```
[Official Site of the 2026 US Open Tennis Championships - A ...]
- 2026 US Open singles champions: Elena Rybakina (women's; beat Aryna Sabalenka) and Alexander Zverev (men's; beat Ben Shelton)
- Rybakina wins first US Open title; headline notes "injury nightmare" turned into title
- Zverev defeats Shelton for US Open title; Shelton's post-final quote: "I'm just getting started"
- Source gives no birthdates or ages for Rybakina or Zverev
```

---

## 13. How many days did it take for World War 2 to end after the death of Alois Burgstaller?

- **Gold:** 136 days
- **Accepted:** 136 days
- **Answerable as asked:** yes
- **Predicted answer:** 136 days (to Japan's formal surrender on September 2, 1945; about 19 days if measured to V-E Day, May 8, 1945).

**Research notes**

```
[1945 in music]
- Alois Burgstaller: operatic tenor, born 1872, died April 19, 1945 (listed under Deaths).
- Bridging: WWII end dates needed. Source does not give WWII end dates. Known from general knowledge (not in source): V-E Day (Germany's surrender) May 8, 1945; formal Japanese surrender / V-J Day Sept 2, 1945 (announced Aug 15).
- Days from April 19, 1945 to May 8, 1945 = 19 days; to Sept 2, 1945 = 136 days (if end is taken as Japan's formal surrender).
```

---

## 14. What was the score of the penalty shootout in the 2026 FIFA World Cup final?

- **Gold:** There was no penalty shootout: Spain won the final 1–0 after extra time.
- **Accepted:** no shootout; decided in extra time 1–0
- **Answerable as asked:** no
- **Predicted answer:** No penalty shootout is indicated; the notes report Spain beat Argentina 1-0 (unverified, single caption).

**Research notes**

```
[Spain won the 2026 FIFA World Cup, beating Argentina 1-0 ...]
- Source claim: "Spain won the 2026 FIFA World Cup, beating Argentina 1-0" (Facebook RFI video caption). No mention of a penalty shootout; the reported result is a 1-0 win in regulation/as stated, so this conflicts with the question's premise of a shootout.
- Remaining text is about E. Jean Carroll and Donald Trump (juries in 2023 and 2024; over $83 million owed in defamation case; under appeal). Not relevant to the World Cup question.
```

---

## 15. Who is the youngest of the three riders on the final podium of the 2026 Tour de France?

- **Gold:** Isaac del Toro
- **Accepted:** Isaac del Toro; del Toro
- **Answerable as asked:** yes
- **Predicted answer:** Isaac del Toro (born 27 November 2003). This assumes he was the third-place rider, which the notes infer from the URL slug rather than confirm.

**Research notes**

```
[The 2026 Tour de France final podium: 🥇 Tadej Pogacar 🥈 ...]
- Podium per source caption: 1st Tadej Pogačar; 2nd Remco Evenepoel; third name truncated in URL: "isaac-del-tor" → Isaac del Toro (third place, inferred from URL slug)
- Source is a Facebook post by TNT Sports, 2026 Tour de France final podium
- No birth dates or ages given in source for any of the three riders

[Remco Evenepoel]
- Evenepoel: born 25 January 2000, Aalst, Belgium (Wikipedia infobox; age 26 at time of page snapshot).
- Evenepoel 2026 Tour de France: finished 2nd overall (per Wikipedia 2026 results timeline and season section); won stages 15 and 16 (ITT); 5 podium finishes in the Tour.
- Evenepoel's 2026 team: Red Bull–Bora–Hansgrohe (from 2026; previously Deceuninck–Quick-Step / Soudal–Quick-Step 2019–2025).
- Evenepoel turned pro 2019 at age 19 (won Clásica de San Sebastián in 2019 as youngest-ever WorldTour race winner at 19).
- Evenepoel's 2026 Tour podium position confirmed by source caption as 2nd; Tadej Pogačar 1st.
- Pogačar birth date and Isaac del Toro birth date: not in this source; needed to compare ages on the podium.

[Tadej Pogačar]
- Pogačar: born 21 September 1998, Klanec, Slovenia (Wikipedia infobox; age 28 at snapshot). Podium 1st in 2026 Tour (won +6'26" per source; 5th Tour win).
- Evenepoel: born 25 January 2000 (already noted). Born 1.5 years after Pogačar, so younger than Pogačar.
- Del Toro (3rd, per URL inference): birth date still unknown; need to confirm whether he is younger than Evenepoel (born 25 Jan 2000) to decide youngest.
- Pogačar's 2026 Tour: stage wins 3, 6, 10, 14, 19 (Alpe d'Huez); this source confirms 1st overall.
- Pogačar and Del Toro both appeared in the 2026 Milan–San Remo lead-out context (Del Toro gave a leadout for McNulty); no age info.

[2025 UAE Team Emirates–XRG season]
- Isaac del Toro (MEX), born 27 November 2003, Wikipedia roster on 2025 UAE Team Emirates–XRG season page (age 21 as of 1 Jan 2025). Team: UAE Team Emirates XRG in 2025 (same team as Pogačar).
- Comparison of birth dates for 2026 podium riders now available:
  - Pogačar: 21 September 1998
  - Evenepoel: 25 January 2000
  - Del Toro: 27 November 2003 → youngest of the three (3rd place per URL inference; confirm this is the podium's third name).
- Del Toro 2025 wins relevant to his development: Giro d'Italia stage 17 (Bormio), Tour of Austria overall, Vuelta a Burgos overall (2025), multiple ProSeries wins.
- Pogačar 2025 wins listed here: Tour de France overall (2025), 20 team wins in 2025 (team's most-wins figure).
```

---

## 16. How many times did the victor of the Immortal Game of 1851 lose a chess match to an American-born opponent?

- **Gold:** 2
- **Accepted:** 2
- **Answerable as asked:** yes
- **Predicted answer:** Once (the 1858 Paris match with Paul Morphy).

**Research notes**

```
[Adolf Anderssen]
- Immortal Game (1851) victor: Adolf Anderssen (the source names him as winner, "Anderssen (White) vs Kieseritzky").
- American-born opponent: Paul Morphy (described as "the American champion").
- Anderssen vs Morphy, Paris 1858 match: lost 8–3 (2 wins, 2 draws, 7 losses); table: "+2=2–7", 3/11. Counts as one lost match.
- Anderssen vs Morphy, Paris 1858 casual games: "+1=0–5", 1/6, listed as "Lost" (5 losses in these casual games).
- Anderssen's other losses are not to Morphy: Tassilo von der Lasa, Max Lange, Gustav Neumann, Steinitz (1866, Steinitz born in Prague, not American; not in source), Berthold Suhle is listed as drawn.
```

---

## 17. Who refereed the 2026 FIFA World Cup final?

- **Gold:** Slavko Vinčić
- **Accepted:** Slavko Vinčić; Slavko Vincic; Vinčić
- **Answerable as asked:** yes
- **Predicted answer:** Slavko Vinčić (Slovenia), per FIFA's pre-match announcement; not confirmed by a post-match report in the notes.

**Research notes**

```
[Slovenian Slavko Vinčić to take charge of FIFA World Cup ...]
- Final: Spain v Argentina, New York New Jersey Stadium, Sunday 19 July 2026 (per FIFA article dated 17 July 2026).
- Referee of the 2026 final: Slavko Vinčić (Slovenia), 46, from Maribor; first Slovenian to referee a World Cup final; 23rd person in history to referee a World Cup final.
- Vinčić's assistants: Tomaž Klančnik and Andraž Kovačič.
- Fourth official: Jordanian Adham Makhadmeh; reserve AR: Mohammad Al-Kalaf (Jordan).
- Final VAR: German Bastian Dankert; assistant VAR: Colombian Nicolás Gallo; support VAR: Qatari Khamis Al Marri.
- Vinčić's prior big matches: UEFA EURO 2020; 2022 UEFA Europa League final; 2024 UEFA Champions League final (Dortmund v Real Madrid); UEFA EURO 2024 (incl. France v Spain semi); FIFA Club World Cup 2025; FIFA World Cup 2022 (two games).
- Third-place playoff (France v England, Miami Stadium): referee Jesús Valenzuela (Venezuela), ARs Jorge Urrego and Tulio Moreno; 4th official Jalal Jayed (Morocco); reserve AR Zakaria Brinsi; VAR Leodan González (Uruguay).
```

---

## 18. Which team won the 2026 Ryder Cup?

- **Gold:** No 2026 Ryder Cup was held: the event took place in 2025 (Bethpage Black) and next in 2027 (Adare Manor).
- **Accepted:** there was no 2026 Ryder Cup
- **Answerable as asked:** no
- **Predicted answer:** Unknown. The 2026 Ryder Cup had not been played as of my knowledge cutoff, and no notes were collected to confirm a result.

**Research notes**

```
(no notes)
```

---

## 19. A United States women's national soccer team player scored her first career international goal during the semi-final match of the 2015 FIFA Women's World Cup. This same player scored her second goal the next year. Tell me the difference in attendance between these two games.

- **Gold:** 43,518
- **Accepted:** 43,518
- **Answerable as asked:** yes
- **Predicted answer:** Unable to determine reliably from the available information; the notes are empty and I can't confidently identify the player or her 2016 match attendance.

**Research notes**

```
(no notes)
```

---

## 20. How many of the 2026 Nobel laureates in Physiology or Medicine were born in Germany?

- **Gold:** 2
- **Accepted:** 2; two (Peter Hegemann and Georg Nagel)
- **Answerable as asked:** yes
- **Predicted answer:** Likely 2 (Peter Hegemann and Georg Nagel), though the research notes do not confirm their birthplaces.

**Research notes**

```
[Press release: Nobel Prize in Physiology or Medicine 2026]
- 2026 Nobel Prize in Physiology or Medicine: jointly to Karl Deisseroth, Peter Hegemann, Georg Nagel, for light-gated ion channels and optogenetics.
- Deisseroth: born 1971; Stanford/HHMI, USA; PhD 1998 and MD 2000 at Stanford.
- Hegemann: born 1954; PhD 1984 at Max Planck Institute for Biochemistry, Martinsried, Germany; now Humboldt University of Berlin, Germany.
- Nagel: born 1953; PhD 1988 at University of Frankfurt, Germany; now University of Würzburg, Germany.
- Source gives affiliations and birth years only, not birthplaces. Nationality/birthplace of Hegemann and Nagel is not stated; their German affiliations do not establish German birth.
- Source says 10 laureates in total across six prizes; only the three Physiology or Medicine laureates are relevant here.
```

---

## 21. An Australian artist, born the same year as artist Janet Cumbrae Stewart and fellow member of the Melbourne Society of Women Painters and Sculptors, had her painting featured on the cover of Women's World Magazine in 1923. What is the name of the painting?

- **Gold:** Reve d'Or
- **Accepted:** Reve d'Or
- **Answerable as asked:** yes
- **Predicted answer:** "Reve d'Or" (by Dora Wilson)

**Research notes**

```
[Pegg Clarke]
NOTES:
- Janet Cumbrae Stewart: fellow Melbourne Society of Women Painters and Sculptors member (per source, Pegg Clarke was involved with that society); Stewart shared Temple Court studio with Jessie Traill, Norah Gurdon, A. M. E. Bale (birth year not in source).
- Source is about Pegg Clarke (photographer, b. c.1884), not the target artist; no mention of Women's World Magazine or a 1923 cover painting.
- Other MSWPS-linked artists named in source: Margaret Maclean, Guelda Pyke, Polly Hurry, Jessie Traill (friends of Clarke; no birth years given).
- Jessie Traill: moved to Temple Court studio 1909 (possible MSWPS/Stewart link; birth year not given).

[Dora Wilson]
- Dora Lynnell Wilson: born 31 August 1883, Newcastle upon Tyne, England; died 21 November 1946, Melbourne. Australian artist (etchings, street scenes).
- Birth year 1883 = likely match for Janet Cumbrae Stewart's birth year (still to verify; Stewart's birth year not in source).
- Wilson was a member of the Melbourne Society of Women Painters and Sculptors (confirmed in source).
- ANSWER CANDIDATE: In 1923 her work 'Reve d'Or' was reproduced on the cover of Women's World (source: "In 1923 her work, 'Reve d'Or', was reproduced on the cover of Women's World and exhibited at the Société des Artistes Français in Paris").
- Wilson's friends/associates: Pegg Clarke (partner, photographer), Norah Gurdon, Jessie Traill, Janet Cumbrae Stewart (fellow of "The Twelve Melbourne Painters," 1913–14 group).
- Wilson studied at National Gallery school 1901–1906 under Bernard Hall and Frederick McCubbin; lessons with John Mather.

[Janet Cumbrae Stewart]
- Janet Cumbrae Stewart: born 23 December 1883, Brighton/Melbourne, Victoria (confirms birth year 1883, matching Dora Wilson's 1883).
- Stewart was a member of the Melbourne Society of Women Painters and Sculptors (confirmed in source).
- Stewart's solo exhibition at Walkers Galleries, London, Feb 1923; no mention of Women's World cover or Dora Wilson in this source.
- Stewart's shared Melbourne association with Dora Wilson is not evident here; source does not name Wilson.
- Supports prior candidate chain: birth-year match 1883 (Stewart) = 1883 (Wilson); the 1923 Women's World cover painting 'Reve d'Or' remains the answer candidate from earlier notes.
```

---

## 22. An Australian artist, born the same year as artist Janet Cumbrae Stewart and fellow member of the Melbourne Society of Women Painters and Sculptors, had her painting featured on the cover of Women's World Magazine in 1923. What is the name of the painting?

- **Gold:** Reve d'Or
- **Accepted:** Reve d'Or
- **Answerable as asked:** yes
- **Predicted answer:** Unable to determine from the provided notes.

**Research notes**

```
[Pegg Clarke]
NOTES:
- Janet Cumbrae Stewart is a fellow member of the Melbourne Society of Women Painters and Sculptors (per this page, Clarke was also involved with that society). Her birth year is not stated in this source.
- Source is about Pegg Clarke (c.1884–1959), a photographer, not a painter; she is not the target artist unless the year-match works out, and no 1923 Women's World cover is mentioned here.
- Other MSWPS-linked names mentioned: Jessie Traill (printmaker, shared Temple Court studio with Cumbrae Stewart, Norah Gurdon, A. M. E. Bale, c.1909), Margaret Maclean, Guelda Pyke, Polly Hurry (friends of Clarke, artists).
- Janet Cumbrae Stewart listed in Lyceum Club 2002 exhibition (no birth year given).
- No mention of Women's World Magazine or a 1923 cover painting.

[Janet Agnes Cumbrae Stewart (1883–1960)]
- Janet Agnes Cumbrae Stewart born 23 December 1883, Brighton, Victoria; died 8 September 1960, Melbourne (ADB).
- Bridging fact: target artist must be born in 1883 (year match), Australian, fellow MSWPS member, painting on Women's World Magazine cover in 1923.
- Cumbrae Stewart studied at National Gallery School Melbourne 1901–07 (under Bernard Hall, F. McCubbin); in London 1922; exhibited Paris Galérie Beaux-Arts 1924–31; honourable mention Salon des Artistes Français 1923.
- Known for pastel female nudes; monograph by John Shirlow (Melbourne, 1921).
- No mention in this source of Melbourne Society of Women Painters and Sculptors membership or Women's World Magazine.
```

---

## 23. How many years apart are the birth years of the two 2026 Nobel laureates in Chemistry?

- **Gold:** 20
- **Accepted:** 20; 20 years (1930 and 1950)
- **Answerable as asked:** yes
- **Predicted answer:** 20 years (Kagan born 1930, Soai born 1950; birth years not verified against the Nobel page itself)

**Research notes**

```
[List of Nobel laureates in Chemistry]
- 2026 Nobel Chemistry laureates listed: Henri B. Kagan (1930–present), French; Kensō Soai (1950–present), Japanese.
- Birth years: Kagan 1930; Soai 1950 → difference 20 years.

[Nobel Prize in Chemistry 2026]
- Source (nobelprize.org 2026 Chemistry summary page): laureates are Henri B. Kagan (prize share 1/2) and Kenso Soai (prize share 1/2), awarded "for the discovery of non-linear effects and autocatalysis in asymmetric organic synthesis."
- Source gives no birth years; page content is navigation/summary only. Birth years 1930 (Kagan) and 1950 (Soai) come from the earlier notes, not verified here.
- Source says six prizes total, 10 laureates overall across 2026 prizes (context only).
```

---

## 24. In which city was the runner-up of the 2026 US Open women's singles final born?

- **Gold:** Minsk
- **Accepted:** Minsk; Minsk, Belarus
- **Answerable as asked:** yes
- **Predicted answer:** Minsk (Belarus)

**Research notes**

```
[2026 US Open – Women's singles]
- Final: Elena Rybakina (champion) def. Aryna Sabalenka (runner-up), 6–4, 5–7, 6–2, 12 Sept 2026
- Runner-up = Aryna Sabalenka (seed 1, world No. 1 entering; "two-time defending champion")
- Source gives no birthplace for Sabalenka; need her birth city from another source

[Minsk]
- Sabalenka listed under Minsk "Sport" notable people: "Aryna Sabalenka (born 1998), 2023 Australian Open winner and current world No. 1 tennis player, born in Minsk moving to Miami at 23"
- Source thus gives birthplace of runner-up Aryna Sabalenka = Minsk (confirms the 2026 final notes: runner-up = Sabalenka)
- Answer candidate: Minsk, Belarus
```

---

## 25. The 2026 Nobel Prize in Physics was awarded for contributions to a neutrino observatory. At which research station is that observatory located?

- **Gold:** Amundsen–Scott South Pole Station
- **Accepted:** Amundsen–Scott South Pole Station
- **Answerable as asked:** yes
- **Predicted answer:** The South Pole (Amundsen–Scott South Pole Station, Antarctica), where IceCube is built into the ice.

**Research notes**

```
[Press release: Nobel Prize in Physics 2026]
- Prize: 2026 Nobel Prize in Physics, awarded 6 October 2026 to Francis Halzen (University of Wisconsin–Madison, USA) "for decisive contributions to the IceCube Neutrino Observatory and the discovery of high-energy neutrinos of astrophysical origin"
- Observatory: IceCube Neutrino Observatory, located at the South Pole (headline: "captured at the South Pole"; "ice at the South Pole")
- Detector: a cubic kilometre of ice equipped with light sensors; completed 2011
- Halzen's vision of using South Pole ice to detect neutrinos presented 1988
- Ice advantages cited: free from interference, geologically stable, no earthquakes
```

---

## 26. How many times did the victor of the Immortal Game of 1851 lose a chess match to an American-born opponent?

- **Gold:** 2
- **Accepted:** 2
- **Answerable as asked:** yes
- **Predicted answer:** 1 (the 1858 Paris match against Paul Morphy; he also lost casual games to Morphy there, but those were not a match)

**Research notes**

```
[Adolf Anderssen]
- Immortal Game (1851) victor: Adolf Anderssen (he beat Lionel Kieseritzky, London, 21 June 1851).
- American-born opponent: Paul Morphy (the source calls him "the American champion").
- Morphy matches lost by Anderssen:
  - Paris, 1858 (match): Lost, score 3/11 (+2=2–7). Source says "beaten 8–3" overall.
  - Paris, 1858 (casual games): Lost, score 1/6 (+1=0–5).
- Source counts only the 1858 Paris match in the match record narrative ("lost matches to Paul Morphy in 1858"). The casual games are listed separately in the match table.
- Other opponents named in the source are not American-born (Steinitz, the 1866 loss, is not American-born in this source).
```

---

## 27. What was the pseudonym of one of the co-founders of the Eagle Awards that won Favourite Specialist Comics Publication/Trade Publication 1977 and 1978?

- **Gold:** Burt
- **Accepted:** Burt
- **Answerable as asked:** yes
- **Predicted answer:** Burt (Richard Burton's pseudonym)

**Research notes**

```
[Richard Burton (comics)]
- Richard Burton: pseudonym "Burt" (appeared as Tharg the Mighty's bumbling assistant Burt in 2000 AD)
- Co-founders of Eagle Awards: Burton and Mike Conroy (started 1977)
- Comic Media News won Eagle Award for Favourite Specialist Comics Publication/Trade Publication in 1977 and 1978
- Burton produced Comic Media News 1973–1980; retired it when moved to 2000 AD (1979); continued co-producing Eagle Awards with Conroy for a couple more years
- Burton was editor of 2000 AD 1987–1994
```

---

## 28. Which of the two 2026 US Open singles champions also won the 2026 French Open singles title?

- **Gold:** Alexander Zverev
- **Accepted:** Alexander Zverev; Zverev
- **Answerable as asked:** yes
- **Predicted answer:** Alexander Zverev

**Research notes**

```
[French Open winners: Men's and women's singles ...]
- 2026 French Open men's singles champion: Alexander Zverev, who beat Flavio Cobolli in 5 sets in the final (Roland Garros, June 7, 2026).
- 2026 French Open women's singles champion: Mirra Andreeva, who beat Maja Chwalinska in the final.
- The source does not mention the 2026 US Open or its singles champions, so the overlap with the US Open winners cannot be checked from this page.

[US Open (tennis)]
- 2026 US Open men's singles champion: Alexander Zverev (beat Ben Shelton 6–3, 7–6(7–2), 5–7, 6–2).
- 2026 US Open women's singles champion: Elena Rybakina (beat Aryna Sabalenka 6–4, 5–7, 6–2).
- Bridge: the 2026 French Open men's champion (Zverev, per prior notes) is the same person as the 2026 US Open men's champion, so Zverev won both 2026 singles titles.
- Women: Rybakina's 2026 French Open result is not in this source; the prior notes say the French Open women's champion was Mirra Andreeva, so Rybakina did not win the French Open women's title.
```

---

## 29. A United States women's national soccer team player scored her first career international goal during the semi-final match of the 2015 FIFA Women's World Cup. This same player scored her second goal the next year. Tell me the difference in attendance between these two games.

- **Gold:** 43,518
- **Accepted:** 43,518
- **Answerable as asked:** yes
- **Predicted answer:** Cannot be determined from the notes. The 2015 semifinal (vs Germany) had 51,176 in attendance, but the 2016 match with O'Hara's second goal and its attendance are missing, so the difference is unknown.

**Research notes**

```
[WNT Downs World No. 1 Germany 2-0 to Advance to 2015 ...]
- Player: Kelley O'Hara (USA). Her first international goal: 84th minute vs Germany, 2015 WWC semifinal, 30 June 2015, Olympic Stadium, Montreal.
- 2015 WWC semifinal (USA 2-0 GER, 30 June 2015, Montreal): attendance 51,176 (venue: Olympic Stadium; indoor).
- Still needed: O'Hara's second international goal (2016 date/match) and its attendance.
```

---

## 30. Who won the 2026 Nobel Prize in Mathematics?

- **Gold:** No one: there is no Nobel Prize in Mathematics.
- **Accepted:** there is no Nobel Prize in Mathematics
- **Answerable as asked:** no
- **Predicted answer:** Unknown. There is no Nobel Prize in Mathematics, and I cannot confirm the 2026 winners of the Abel Prize or Fields Medal.

**Research notes**

```
(no notes)
```

---

## 31. Which rider from the 2026 Tour de France winner's own team also finished on the podium?

- **Gold:** Isaac del Toro
- **Accepted:** Isaac del Toro; Isaac del Toro Romero; del Toro
- **Answerable as asked:** yes
- **Predicted answer:** Isaac del Toro (3rd place, UAE Team Emirates XRG)

**Research notes**

```
[Official classifications of Tour de France 2026 - Stage 21]
- 2026 Tour de France GC (Stage 21 page): 1. T. POGACAR (UAE TEAM EMIRATES XRG), 73h 56'26''; 2. R. EVENEPOEL (Red Bull-Bora-Hansgrohe); 3. I. DEL TORO (UAE TEAM EMIRATES XRG), +00h 09'42''
- Pogacar's teammate on podium: I. DEL TORO (UAE TEAM EMIRATES XRG), 3rd, +00h 09'42'', bonus B 24''
- Other UAE riders in GC: A. YATES (21st), F. GROSSSCHARTNER (32nd), N. POLITT (72nd), T. WELLENS (74th), F. VERMEERSCH (116th)
- Stage 20 listed as Le Bourg d'Oisans > Alpe d'Huez; Stage 21 page shows the GC ranking table
```

---

## 32. Which physicist shared the 2026 Nobel Prize in Physics with Francis Halzen?

- **Gold:** No one: Francis Halzen was the sole laureate of the 2026 Nobel Prize in Physics.
- **Accepted:** nobody; no one shared it; Halzen won alone
- **Answerable as asked:** no
- **Predicted answer:** No co-laureate is identified. Per the Reuters report, Francis Halzen appears to have been the sole 2026 physics laureate, so the question's premise seems incorrect.

**Research notes**

```
[Francis Halzen wins Nobel physics prize for Antarctic ' ...]
- Source reports Francis Halzen (82, Belgian-American, Univ. of Wisconsin–Madison) won the 2026 Nobel Prize in Physics (Reuters, Oct 6, 2026).
- Prize citation: work creating the Antarctic ice observatory (IceCube) to detect high-energy neutrinos.
- Article refers to "The physics laureate" in the singular and names no co-laureate; this suggests Halzen may have been the sole winner, which conflicts with the question's premise.
- Halzen first proposed the South Pole neutrino idea in 1988; project completed 2011.
- Prize: 12 million SEK (about $1.2 million). Presented in Stockholm on Dec 10.
```

---

## 33. What is population in 1968 of the city that hosted the olympic games in which Lucy Steele competed?

- **Gold:** 15,739
- **Accepted:** 15,739
- **Answerable as asked:** yes
- **Predicted answer:** Roughly 15,000–17,000 (Albertville, France); unverified, not from the provided notes.

**Research notes**

```
[Lucy Steele]
- Lucy Steele: Canadian cross-country skier, competed at 1992 Winter Olympics (age 22)
- 1992 Winter Olympics host city: not stated in source (bridging fact needed: Albertville, France, per general knowledge — not in source)
```

---

## 34. What is the HTTP endpoint path of OpenAI's Decisions API?

- **Gold:** POST /v1/decisions
- **Accepted:** /v1/decisions; POST /v1/decisions
- **Answerable as asked:** yes
- **Predicted answer:** POST /v1/decisions (full URL: https://api.openai.com/v1/decisions)

**Research notes**

```
[Decisions | OpenAI API]
- Decisions API endpoint: `POST /v1/decisions` (full URL in curl example: https://api.openai.com/v1/decisions)
- Only model currently available: gpt-6-luna; API in public beta, GA expected "in the coming weeks"
```

---

## 35. Which U.S. National Park was the first to be established after the Portland Trail Blazers won their only playoff series with LaMarcus Aldridge on the team?

- **Gold:** Gateway Arch National Park
- **Accepted:** Gateway Arch National Park
- **Answerable as asked:** yes
- **Predicted answer:** Indiana Dunes National Park (redesignated February 2019; low confidence, notes were empty)

**Research notes**

```
(no notes)
```

---

## 36. Who won the 2026 Nobel Prize in Mathematics?

- **Gold:** No one: there is no Nobel Prize in Mathematics.
- **Accepted:** there is no Nobel Prize in Mathematics
- **Answerable as asked:** no
- **Predicted answer:** No 2026 Nobel Prize in Mathematics exists. The Nobel Foundation does not award one. For the 2026 Abel Prize or Fields Medal, I can't say from the available information.

**Research notes**

```
(no notes)
```

---

## 37. In how many of the six 2026 Nobel Prize categories (including Economic Sciences) was the prize awarded to a single laureate?

- **Gold:** 3
- **Accepted:** 3; three (Physics, Literature, Peace)
- **Answerable as asked:** yes
- **Predicted answer:** 3 (Physics, Literature, Peace), assuming Physiology or Medicine was shared; it would be 4 if Medicine had a single laureate.

**Research notes**

```
[All Nobel Prizes]
- 2026 Physics: Francis Halzen alone (single laureate).
- 2026 Literature: Anne Carson alone (single laureate).
- 2026 Peace: Navi Pillay alone (single laureate).
- 2026 Chemistry: not single. Two separate prize awards: Henri B. Kagan and Kenso Soai (2 people); Karl Deisseroth, Peter Hegemann and Georg Nagel (3 people).
- 2026 Economic Sciences: Robert E. Hall and Michael Woodford (2 people), listed under the Economic Sciences heading; the source's category label is missing, so this is inferred from the quote "for microeconomic foundations of macroeconomic stabilisation".
- 2026 Physiology or Medicine: not present in the source. Its laureate count is unknown.
- Tally so far: 3 single-laureate categories confirmed (Physics, Literature, Peace). Chemistry and Economics are not single. Medicine remains unresolved.
```

---

## 38. Which team did the runner-up of the 2026 Tour de France ride for?

- **Gold:** Red Bull–Bora–Hansgrohe
- **Accepted:** Red Bull–Bora–Hansgrohe; Red Bull-Bora-Hansgrohe; Red Bull Bora Hansgrohe
- **Answerable as asked:** yes
- **Predicted answer:** Red Bull–Bora–Hansgrohe (Remco Evenepoel was the runner-up)

**Research notes**

```
[Official classifications of Tour de France 2026 - Stage 21]
- Source: letour.fr 2026 "Stage 21" general classification (page titled Stage 21, but the table lists results after Stage 20 finish, Alpe d'Huez; no stage 21 rows shown; route table ends at Stage 20 on 07/25).
- Overall winner: T. POGACAR (rider no. 1), UAE TEAM EMIRATES XRG, 73h 56' 26''.
- Runner-up (rank 2): R. EVENEPOEL (rider no. 21), RED BULL - BORA - HANSGROHE, 74h 02' 52'', gap + 00h 06' 26''.
- Third: I. DEL TORO, UAE TEAM EMIRATES XRG, +00h 09' 42''.
- Evenepoel's team in this table: RED BULL - BORA - HANSGROHE (other riders: J. HINDLEY, M. VAN GILS, M. CATTANEO, J. TRATNIK, N. DENZ, T. VAN DIJKE).

[2026 Tour de France]
- Runner-up (2nd, GC): Remco Evenepoel (BEL), team Red Bull–Bora–Hansgrohe, +6' 26" behind Pogačar (confirmed in both the letour.fr table and the Wikipedia final GC table).
- Wikipedia infobox lists Second: Remco Evenepoel (Red Bull–Bora–Hansgrohe).
- Winner Pogačar: UAE Team Emirates XRG, 73h 56' 26"; third Isaac del Toro (UAE Team Emirates XRG), +9' 42".
- Wikipedia: Vingegaard withdrew after a crash on stage 15, so Evenepoel took second place overall.
- Evenepoel's teammates in top 15 include Jai Hindley (15th, +1h 23' 28"), Maxim Van Gils (27th), Mattia Cattaneo (33rd), Tim van Dijke (111th) — all Red Bull–Bora–Hansgrohe.
- Source note: letour.fr "Stage 21" page lists results only through Stage 20 (Alpe d'Huez); Wikipedia's final GC matches it.
```

---

## 39. A united states island that is only 90 miles away from Cuba has been the home of several famous people. In what year did the famous author who owns a book store there first start writing?

- **Gold:** 1959
- **Accepted:** 1959
- **Answerable as asked:** yes
- **Predicted answer:** Approximately 1942–1944 (if the author is Shel Silverstein, who began writing around age 12–14; the bookstore link and exact year are unverified).

**Research notes**

```
[Shel Silverstein]
- Key West, Florida: Silverstein died at his home there on May 10, 1999 (heart failure, age 68). He owned homes on Martha's Vineyard, in Greenwich Village, and in Key West.
- Source does not mention Silverstein owning a bookstore. Bookstore link is unverified.
- Silverstein's earliest writing: "began drawing at age seven by tracing the works of Al Capp"; he said "So I started to draw and to write" (age 12-14 context, per Publishers Weekly quote).
- First published writing/cartoons: Roosevelt Torch, student newspaper at Roosevelt University, where he studied English after leaving the Art Institute.
- First book: Take Ten (Pacific Stars and Stripes, 1955), compiling military cartoon series; reprinted by Ballantine Books 1956 as Grab Your Socks!
- Cartoons appeared in Playboy from 1957 through mid-1970s; Uncle Shelby's ABZ Book (1961) was his first original adult book.
- Children's writing began after Tomi Ungerer pushed him to Ursula Nordstrom (Harper); no year given in source.
```

---

## 40. Which U.S. National Park was the first to be established after the Portland Trail Blazers won their only playoff series with LaMarcus Aldridge on the team?

- **Gold:** Gateway Arch National Park
- **Accepted:** Gateway Arch National Park
- **Answerable as asked:** yes
- **Predicted answer:** Gateway Arch National Park (redesignated February 22, 2018)

**Research notes**

```
[LaMarcus Aldridge]
- Portland Trail Blazers' only playoff series win with Aldridge: 2014 opening round vs. Houston Rockets, won in six games (Aldridge's Blazers tenure: 2006–2015).
- Series dates: Game 1 on April 20, 2014 (Blazers won 122–120 in OT); Game 2 on April 23, 2014. Series end date not stated in source (so likely late April 2014).
- Blazers then lost to San Antonio Spurs in five games in the next round.
- Source contains no information on U.S. National Parks.

[History of the Portland Trail Blazers]
- Blazers' only playoff series win with Aldridge on roster: 2014 first round vs. Houston Rockets, won in six games (Aldridge with Blazers 2006–2015).
- Series clinched by Damian Lillard buzzer-beater in Game 6 ("Rip City Revival"); Game 1 April 20, 2014 (122–120); Game 2 April 23, 2014 (112–105).
- Blazers lost to eventual champion San Antonio Spurs in five games in the 2014 semifinals (first semifinal since 2000).
- Source gives no date for the Game 6 clinch or series end beyond "late April 2014" inference; exact date not stated.
- Source contains no information on U.S. National Parks.

[Why is Gateway Arch a National Park?]
- Gateway Arch was redesignated from Jefferson National Expansion Memorial to "Gateway Arch National Park" by S.1438, introduced June 26, 2017 by Sen. Roy Blunt and signed by Trump on February 22, 2018.
- Gateway Arch was a national memorial, not a national park, before 2018. FDR's 1935 executive order designated it the Jefferson National Expansion Memorial.
- Gateway Arch is the only one of the 63 national parks (as of 2026) that doesn't fit the NPS "national park" definition. It is 0.14 sq mi (about 91 federal acres).
- Hot Springs is the next smallest national park, 64 times larger than Gateway Arch.
- The source gives no establishment dates for other national parks and does not say which park was first designated after April 2014.
```

---

## 41. How tall does the flower get on the very first orchid David L. Jones (botanist) described and published in his career?

- **Gold:** 20–30 millimetres (0.8–1 in)
- **Accepted:** 20–30 millimetres (0.8–1 in)
- **Answerable as asked:** yes
- **Predicted answer:** Unverified estimate of about 10–30 cm tall (flowering stem of *Pterostylis aestiva*); the notes do not give a height.

**Research notes**

```
[David L. Jones (botanist)]
- Source says David Lloyd Jones (born 1944), Australian horticultural botanist, author of 350+ papers describing orchid species, 18 cycad papers.
- First orchid description: Pterostylis aestiva, published 1972 (the source's "first description of an orchid").
- Source gives no plant height for Pterostylis aestiva; height must come from another source (e.g., species description or flora database).
- Bridging: Pterostylis aestiva is the target taxon; confirm it is the first orchid Jones described (source states this directly).
```

---

## 42. Which of the two 2026 US Open singles champions is older?

- **Gold:** Alexander Zverev
- **Accepted:** Alexander Zverev; Zverev
- **Answerable as asked:** yes
- **Predicted answer:** Aryna Sabalenka (born 5 Oct 1998) is older than Elena Rybakina (born 17 Jun 1999), assuming the two champions are the women's singles finalists. The notes don't cover the men's champion, and the birth dates come from outside knowledge, not the notes.

**Research notes**

```
[2026 US Open – Women's singles]
- Champion: Elena Rybakina (seed 2), won 6–4, 5–7, 6–2 over runner-up Aryna Sabalenka (seed 1) in the final, September 12, 2026.
- Rybakina's third major title; second of 2026 after Australian Open.
- Source gives no birth dates or ages for Rybakina or Sabalenka. Age comparison needs outside birth dates.
```

---

## 43. Of all the 2026 Nobel laureates in Physics, Chemistry, and Physiology or Medicine, who was born earliest?

- **Gold:** Henri B. Kagan
- **Accepted:** Henri B. Kagan; Henri Kagan; Kagan
- **Answerable as asked:** yes
- **Predicted answer:** Francis Halzen (born 1944, Physics), assuming no 2026 Chemistry laureate was born earlier. Chemistry is unverified.

**Research notes**

```
[Press release: Nobel Prize in Physiology or Medicine 2026]
- Medicine 2026 laureates and birth years: Karl Deisseroth born 1971; Peter Hegemann born 1954; Georg Nagel born 1953.
- Earliest born so far among Medicine laureates: Georg Nagel (1953), then Hegemann (1954), then Deisseroth (1971).
- Prize announced 5 October 2026 (Medicine); Physics and Chemistry 2026 laureates not covered in this source.
- Exact birth dates within years not given in source.

[Press release: Nobel Prize in Physics 2026]
- Physics 2026: Francis Halzen (sole laureate), born 1944 in Tienen, Belgium (PhD 1969 KU Leuven); Physics press release dated 6 October 2026.
- Medicine 2026 birth years (from existing notes): Nagel 1953, Hegemann 1954, Deisseroth 1971 — Halzen (1944) is earlier than all of them.
- Chemistry 2026 laureates: not covered in this source; need to check their birth years to confirm whether anyone was born before 1944.
```

---

## 44. What are the three question types supported by OpenAI's Decisions API?

- **Gold:** predicate, choice, and score
- **Accepted:** predicate, choice, score
- **Answerable as asked:** yes
- **Predicted answer:** Predicates (probability that a statement is true), Choices (select from predefined options with confidence scores), and Scores (evaluate input against a numeric range).

**Research notes**

```
[Jev (AI model)]
- Source is about Jev (TypeSafe AI), not OpenAI; no mention of an OpenAI "Decisions API" in this source.
- Jev allows three question types, all multiple-choice: **noul** (choices: true, false), **choice** (unordered list of items), **score** (ordered list of items).
- Jev outputs one discrete probability distribution per question; all questions answered in parallel, no dependencies between questions.
- Official API also returns computed fields (choice, score, confidence, legend) via fixed formulas, not by Jev itself.
- Input limit: 64k tokens per input, 32k for state plus longest question.

[Decisions API is now available in Public Beta]
- Source (OpenAI community forum thread, Decisions API public beta announcement): Decisions API supports 3 kinds of outputs: Predicates (estimate probability a statement is true), Choices (select from predefined options with confidence scores), Scores (evaluate input against a numeric range).
- Powered by gpt-6-luna; accepts text and image inputs; claims up to 10x faster than GPT-6 Luna via Responses API.
- Pricing: gpt-6-luna input $0.10 per 1M tokens; no cache-read, cache-write, or output-token charges. No caching currently available (confirmed by forum reply).
- Forum user tests: Decisions "choice" format overweights most likely outcome (biased coin 70% heads: choice gave ~98% heads; predicate gave ~70%). Choice order also changes probabilities.
- Forum user verdict: avoid choice questions. Azure/AWS availability: question directed to Microsoft/AWS reps, no answer given.
```

---

## 45. Which physicist shared the 2026 Nobel Prize in Physics with Francis Halzen?

- **Gold:** No one: Francis Halzen was the sole laureate of the 2026 Nobel Prize in Physics.
- **Accepted:** nobody; no one shared it; Halzen won alone
- **Answerable as asked:** no
- **Predicted answer:** Not determinable from the notes. They list only Francis Halzen for 2026, so I can't name a co-laureate. The official Nobel site should confirm whether the prize was shared.

**Research notes**

```
[List of Nobel laureates in Physics]
- 2026 laureate listed: Francis Halzen (United States / Belgium), citation: "for decisive contributions to the IceCube Neutrino Observatory and the discovery of high-energy neutrinos of astrophysical origin"
- 2026 row in table shows only Halzen; no co-laureate name appears in this source for 2026 (table entry is truncated after "[...]" preceding 2026).
- Statistics section says prize awarded to 230 individuals "as of 2026"; no 2026 co-laureate named.
- Table lists 2010 Geim and Novoselov as last fully visible prior entries; 2026 row is the only 2026 entry shown.
```

---

## 46. Microsoft-Decision-1, released in October 2026, was post-trained from which base model?

- **Gold:** Qwen3.5-9B
- **Accepted:** Qwen3.5-9B; Qwen 3.5 9B
- **Answerable as asked:** yes
- **Predicted answer:** Alibaba's Qwen3.5-9B (open-weight), post-trained by Microsoft.

**Research notes**

```
[Microsoft-Decision-1: a cheap, text-only decision model...]
- Source is a daily.dev aggregator post titled "Microsoft-Decision-1: a cheap, text-only decision model built on Qwen" (last updated 11h ago, 3 sources).
- Post claims: Microsoft Decision-1 launched in Microsoft Foundry, post-trained from Alibaba's Qwen3.5-9B (explicitly "rather than an OpenAI base model").
- Pricing: $0.042 per million input tokens, no output charge; matches TypeSafe's Jev pricing.
- Scores predefined options (e.g., spam detection, routing), not open-ended generation.
- Text-only; competitors from OpenAI and Cloudflare reportedly accept images.
- No open weights announced; System One API support unconfirmed.
- Adversarial robustness: answers changed 1.3% under perturbation; not yet tested against JevOut methodology.
- Release date (October 2026) not stated in the excerpt.

[Microsoft-Decision-1 | Model Catalog]
- Source 2 (Azure AI Foundry model catalog page, ai.azure.com) states: "Microsoft-Decision-1 ... is built on Alibaba's open-weight Qwen3.5-9B and post-trained by Microsoft." Answers the base-model question directly.
- Model catalog: Version 1; Lifecycle: Preview; Publisher/Author: Microsoft; input text, output json; context window 32768 tokens.
- Catalog: "We will also rebase on other models, including MAI and OpenAI" (future intent, not current base).
- Catalog: text-only, no image/audio/video; does not generate explanations or rationales; returns calibrated probability per fixed answer option.
- Source 1 (daily.dev aggregator, last updated 11h ago): claims post-trained from Qwen3.5-9B "rather than an OpenAI base model"; pricing $0.042 per million input tokens, no output charge; launched in Microsoft Foundry; no open weights announced.
- Release date: neither source gives an October 2026 release date; the catalog page shows no launch date in the excerpt. Unverified date claim in question remains open.
- Adversarial robustness claim (aggregator only): answers changed 1.3% under perturbation; not tested against JevOut methodology.
```

---

## 47. How old was the elder of the two 2026 Nobel laureates in Chemistry when the prize was announced in October 2026?

- **Gold:** 95
- **Accepted:** 95; 95 years old (Henri B. Kagan)
- **Answerable as asked:** yes
- **Predicted answer:** 96 (most likely; 95 if his 2026 birthday falls after the October announcement, which the notes don't settle)

**Research notes**

```
[List of Nobel laureates in Chemistry]
- 2026 laureates: Henri B. Kagan (French, born 1930 per source) and Kensō Soai (Japanese, born 1950 per source).
- Elder = Henri B. Kagan (b. 1930); Soai b. 1950.
- Kagan's age at October 2026 announcement: 2026 − 1930 = 96 (birth month/day not given in source; exact age depends on birthday, so 95 or 96).
- Source lists 2026 Nobel Chemistry as Kagan and Soai, consistent with the question premise.
```

---

## 48. Which team won the 2026 Ryder Cup?

- **Gold:** No 2026 Ryder Cup was held: the event took place in 2025 (Bethpage Black) and next in 2027 (Adare Manor).
- **Accepted:** there was no 2026 Ryder Cup
- **Answerable as asked:** no
- **Predicted answer:** Not determinable from the notes. My understanding is that the 2026 Ryder Cup (Bethpage Black, September 2026) had not yet been played, so no winner is known to me.

**Research notes**

```
(no notes)
```

---

## 49. Which model is the only one supported by OpenAI's Decisions API in its 2026 public beta?

- **Gold:** gpt-6-luna
- **Accepted:** gpt-6-luna; GPT-6 Luna
- **Answerable as asked:** yes
- **Predicted answer:** gpt-6-luna

**Research notes**

```
[Decisions | OpenAI API]
- Decisions API (public beta, GA expected "in the coming weeks"); endpoint POST /v1/decisions
- Only supported/currently available model: gpt-6-luna ("is the only model currently available"; "Currently, only gpt-6-luna is supported")
- Returns typed answers ~10x faster than the Responses API
- Pricing: gpt-6-luna input $0.10 per 1M tokens; no output/cache charges
- Supports ZDR and HIPAA for eligible customers; data residency in US and Europe (EEA + Switzerland)
```

---

## 50. How many of the 2026 Nobel laureates in Physiology or Medicine were born in Germany?

- **Gold:** 2
- **Accepted:** 2; two (Peter Hegemann and Georg Nagel)
- **Answerable as asked:** yes
- **Predicted answer:** Probably 2 (Hegemann and Nagel), but unverified. The notes don't state birthplaces.

**Research notes**

```
[Press release: Nobel Prize in Physiology or Medicine 2026]
- 2026 Nobel Prize in Physiology or Medicine laureates (press release, 5 Oct 2026): Karl Deisseroth (USA), Peter Hegemann, Georg Nagel.
- Birthplaces not stated in the source; only birth years given: Deisseroth born 1971; Hegemann born 1954; Nagel born 1953.
- Affiliations: Hegemann – Humboldt University of Berlin, Germany; Nagel – University of Würzburg, Germany; Deisseroth – HHMI and Stanford University, USA.
- Hegemann PhD 1984, Max-Planck-Institute for Biochemistry, Martinsried, Germany; Nagel PhD 1988, University of Frankfurt, Germany; Deisseroth PhD 1998 and MD 2000, Stanford University.
- Discoveries made at Max Planck Institute for Biochemistry, Martinsried (Hegemann) and Max Planck Institute for Biophysics, Frankfurt (Nagel).
- Source does not state birthplace of any laureate; birth country can't be confirmed from this source alone (only that Hegemann and Nagel are German-based, Deisseroth US-based).
```
