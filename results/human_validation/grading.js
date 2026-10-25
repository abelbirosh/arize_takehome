window.GRADING = {
 "sample_id": "26df6c983bdc",
 "rows": [
  {
   "n": 1,
   "question": "What was the score of the penalty shootout in the 2026 FIFA World Cup final?",
   "gold": "There was no penalty shootout: Spain won the final 1–0 after extra time.",
   "accepted": "no shootout; decided in extra time 1–0",
   "answerable": "no",
   "predicted": "No penalty shootout is indicated; the notes report Spain beat Argentina 1-0 (unverified, single caption).",
   "notes": "[Spain won the 2026 FIFA World Cup, beating Argentina 1-0 ...]\n- Source claim: \"Spain won the 2026 FIFA World Cup, beating Argentina 1-0\" (Facebook RFI video caption). No mention of a penalty shootout; the reported result is a 1-0 win in regulation/as stated, so this conflicts with the question's premise of a shootout.\n- Remaining text is about E. Jean Carroll and Donald Trump (juries in 2023 and 2024; over $83 million owed in defamation case; under appeal). Not relevant to the World Cup question.",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 2,
   "question": "In which city was the runner-up of the 2026 US Open women's singles final born?",
   "gold": "Minsk",
   "accepted": "Minsk; Minsk, Belarus",
   "answerable": "yes",
   "predicted": "Minsk (Belarus)",
   "notes": "[2026 US Open – Women's singles]\n- Final: Elena Rybakina (champion) def. Aryna Sabalenka (runner-up), 6–4, 5–7, 6–2, 12 Sept 2026\n- Runner-up = Aryna Sabalenka (seed 1, world No. 1 entering; \"two-time defending champion\")\n- Source gives no birthplace for Sabalenka; need her birth city from another source\n\n[Minsk]\n- Sabalenka listed under Minsk \"Sport\" notable people: \"Aryna Sabalenka (born 1998), 2023 Australian Open winner and current world No. 1 tennis player, born in Minsk moving to Miami at 23\"\n- Source thus gives birthplace of runner-up Aryna Sabalenka = Minsk (confirms the 2026 final notes: runner-up = Sabalenka)\n- Answer candidate: Minsk, Belarus",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 3,
   "question": "Microsoft-Decision-1, released in October 2026, was post-trained from which base model?",
   "gold": "Qwen3.5-9B",
   "accepted": "Qwen3.5-9B; Qwen 3.5 9B",
   "answerable": "yes",
   "predicted": "Alibaba's Qwen3.5-9B (open-weight), post-trained by Microsoft.",
   "notes": "[Microsoft-Decision-1: a cheap, text-only decision model...]\n- Source is a daily.dev aggregator post titled \"Microsoft-Decision-1: a cheap, text-only decision model built on Qwen\" (last updated 11h ago, 3 sources).\n- Post claims: Microsoft Decision-1 launched in Microsoft Foundry, post-trained from Alibaba's Qwen3.5-9B (explicitly \"rather than an OpenAI base model\").\n- Pricing: $0.042 per million input tokens, no output charge; matches TypeSafe's Jev pricing.\n- Scores predefined options (e.g., spam detection, routing), not open-ended generation.\n- Text-only; competitors from OpenAI and Cloudflare reportedly accept images.\n- No open weights announced; System One API support unconfirmed.\n- Adversarial robustness: answers changed 1.3% under perturbation; not yet tested against JevOut methodology.\n- Release date (October 2026) not stated in the excerpt.\n\n[Microsoft-Decision-1 | Model Catalog]\n- Source 2 (Azure AI Foundry model catalog page, ai.azure.com) states: \"Microsoft-Decision-1 ... is built on Alibaba's open-weight Qwen3.5-9B and post-trained by Microsoft.\" Answers the base-model question directly.\n- Model catalog: Version 1; Lifecycle: Preview; Publisher/Author: Microsoft; input text, output json; context window 32768 tokens.\n- Catalog: \"We will also rebase on other models, including MAI and OpenAI\" (future intent, not current base).\n- Catalog: text-only, no image/audio/video; does not generate explanations or rationales; returns calibrated probability per fixed answer option.\n- Source 1 (daily.dev aggregator, last updated 11h ago): claims post-trained from Qwen3.5-9B \"rather than an OpenAI base model\"; pricing $0.042 per million input tokens, no output charge; launched in Microsoft Foundry; no open weights announced.\n- Release date: neither source gives an October 2026 release date; the catalog page shows no launch date in the excerpt. Unverified date claim in question remains open.\n- Adversarial robustness claim (aggregator only): answers changed 1.3% under perturbation; not tested against JevOut methodology.",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 4,
   "question": "How many votes did the opposition party get in the Brant riding the election before Justin Trudeau was elected Prime Minister?",
   "gold": "16,351",
   "accepted": "16,351",
   "answerable": "yes",
   "predicted": "Cannot be determined from the provided notes. The 2011 Brant result (the relevant election) isn't in the sources; the only figure given is a 582-vote margin from 2006.",
   "notes": "[2006 Canadian federal election]\n- Justin Trudeau was elected PM in 2015 (election before = 2011 federal election, not in this source; this source is 2006).\n- Brant, ON, 2006 result: Lloyd St. Amand (Lib) def. Phil McColeman (Cons) by 582 votes (10 closest ridings list).\n- Brant 2006 vote totals for Conservative/Liberal not given in this source (only margin 582 shown; the riding-level table row for Brant is not in the excerpt).\n- Note: Conservative (McColeman) was the opposition in Brant in 2006 only if Liberal held seat; in 2006 Liberal St. Amand won, so Conservative = runner-up/opposition candidate.\n- Relevant bridging: Brant 2011 result (not in source) needed to identify the 2011 opposition party vote count; the source does not contain 2011 data.",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 5,
   "question": "How many times did the victor of the Immortal Game of 1851 lose a chess match to an American-born opponent?",
   "gold": "2",
   "accepted": "2",
   "answerable": "yes",
   "predicted": "Once (the 1858 Paris match with Paul Morphy).",
   "notes": "[Adolf Anderssen]\n- Immortal Game (1851) victor: Adolf Anderssen (the source names him as winner, \"Anderssen (White) vs Kieseritzky\").\n- American-born opponent: Paul Morphy (described as \"the American champion\").\n- Anderssen vs Morphy, Paris 1858 match: lost 8–3 (2 wins, 2 draws, 7 losses); table: \"+2=2–7\", 3/11. Counts as one lost match.\n- Anderssen vs Morphy, Paris 1858 casual games: \"+1=0–5\", 1/6, listed as \"Lost\" (5 losses in these casual games).\n- Anderssen's other losses are not to Morphy: Tassilo von der Lasa, Max Lange, Gustav Neumann, Steinitz (1866, Steinitz born in Prague, not American; not in source), Berthold Suhle is listed as drawn.",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 6,
   "question": "How many of the 2026 Nobel laureates in Physiology or Medicine were born in Germany?",
   "gold": "2",
   "accepted": "2; two (Peter Hegemann and Georg Nagel)",
   "answerable": "yes",
   "predicted": "Likely 2 (Peter Hegemann and Georg Nagel), though the research notes do not confirm their birthplaces.",
   "notes": "[Press release: Nobel Prize in Physiology or Medicine 2026]\n- 2026 Nobel Prize in Physiology or Medicine: jointly to Karl Deisseroth, Peter Hegemann, Georg Nagel, for light-gated ion channels and optogenetics.\n- Deisseroth: born 1971; Stanford/HHMI, USA; PhD 1998 and MD 2000 at Stanford.\n- Hegemann: born 1954; PhD 1984 at Max Planck Institute for Biochemistry, Martinsried, Germany; now Humboldt University of Berlin, Germany.\n- Nagel: born 1953; PhD 1988 at University of Frankfurt, Germany; now University of Würzburg, Germany.\n- Source gives affiliations and birth years only, not birthplaces. Nationality/birthplace of Hegemann and Nagel is not stated; their German affiliations do not establish German birth.\n- Source says 10 laureates in total across six prizes; only the three Physiology or Medicine laureates are relevant here.",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 7,
   "question": "What is population in 1968 of the city that hosted the olympic games in which Lucy Steele competed?",
   "gold": "15,739",
   "accepted": "15,739",
   "answerable": "yes",
   "predicted": "Roughly 15,000–17,000 (Albertville, France); unverified, not from the provided notes.",
   "notes": "[Lucy Steele]\n- Lucy Steele: Canadian cross-country skier, competed at 1992 Winter Olympics (age 22)\n- 1992 Winter Olympics host city: not stated in source (bridging fact needed: Albertville, France, per general knowledge — not in source)",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 8,
   "question": "Which of the two 2026 US Open singles champions is older?",
   "gold": "Alexander Zverev",
   "accepted": "Alexander Zverev; Zverev",
   "answerable": "yes",
   "predicted": "Alexander Zverev (born 1997) is older than Elena Rybakina (born 1999). This relies on birthdates from my own knowledge, not the research notes.",
   "notes": "[Official Site of the 2026 US Open Tennis Championships - A ...]\n- 2026 US Open singles champions: Elena Rybakina (women's; beat Aryna Sabalenka) and Alexander Zverev (men's; beat Ben Shelton)\n- Rybakina wins first US Open title; headline notes \"injury nightmare\" turned into title\n- Zverev defeats Shelton for US Open title; Shelton's post-final quote: \"I'm just getting started\"\n- Source gives no birthdates or ages for Rybakina or Zverev",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 9,
   "question": "In how many of the six 2026 Nobel Prize categories (including Economic Sciences) was the prize awarded to a single laureate?",
   "gold": "3",
   "accepted": "3; three (Physics, Literature, Peace)",
   "answerable": "yes",
   "predicted": "3 (Physics, Literature, Peace), assuming Physiology or Medicine was shared; it would be 4 if Medicine had a single laureate.",
   "notes": "[All Nobel Prizes]\n- 2026 Physics: Francis Halzen alone (single laureate).\n- 2026 Literature: Anne Carson alone (single laureate).\n- 2026 Peace: Navi Pillay alone (single laureate).\n- 2026 Chemistry: not single. Two separate prize awards: Henri B. Kagan and Kenso Soai (2 people); Karl Deisseroth, Peter Hegemann and Georg Nagel (3 people).\n- 2026 Economic Sciences: Robert E. Hall and Michael Woodford (2 people), listed under the Economic Sciences heading; the source's category label is missing, so this is inferred from the quote \"for microeconomic foundations of macroeconomic stabilisation\".\n- 2026 Physiology or Medicine: not present in the source. Its laureate count is unknown.\n- Tally so far: 3 single-laureate categories confirmed (Physics, Literature, Peace). Chemistry and Economics are not single. Medicine remains unresolved.",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 10,
   "question": "Who refereed the 2026 FIFA World Cup final?",
   "gold": "Slavko Vinčić",
   "accepted": "Slavko Vinčić; Slavko Vincic; Vinčić",
   "answerable": "yes",
   "predicted": "Slavko Vinčić (Slovenia), per FIFA's pre-match announcement; not confirmed by a post-match report in the notes.",
   "notes": "[Slovenian Slavko Vinčić to take charge of FIFA World Cup ...]\n- Final: Spain v Argentina, New York New Jersey Stadium, Sunday 19 July 2026 (per FIFA article dated 17 July 2026).\n- Referee of the 2026 final: Slavko Vinčić (Slovenia), 46, from Maribor; first Slovenian to referee a World Cup final; 23rd person in history to referee a World Cup final.\n- Vinčić's assistants: Tomaž Klančnik and Andraž Kovačič.\n- Fourth official: Jordanian Adham Makhadmeh; reserve AR: Mohammad Al-Kalaf (Jordan).\n- Final VAR: German Bastian Dankert; assistant VAR: Colombian Nicolás Gallo; support VAR: Qatari Khamis Al Marri.\n- Vinčić's prior big matches: UEFA EURO 2020; 2022 UEFA Europa League final; 2024 UEFA Champions League final (Dortmund v Real Madrid); UEFA EURO 2024 (incl. France v Spain semi); FIFA Club World Cup 2025; FIFA World Cup 2022 (two games).\n- Third-place playoff (France v England, Miami Stadium): referee Jesús Valenzuela (Venezuela), ARs Jorge Urrego and Tulio Moreno; 4th official Jalal Jayed (Morocco); reserve AR Zakaria Brinsi; VAR Leodan González (Uruguay).",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 11,
   "question": "Who won the 2026 Nobel Prize in Mathematics?",
   "gold": "No one: there is no Nobel Prize in Mathematics.",
   "accepted": "there is no Nobel Prize in Mathematics",
   "answerable": "no",
   "predicted": "Unknown. There is no Nobel Prize in Mathematics, and I cannot confirm the 2026 winners of the Abel Prize or Fields Medal.",
   "notes": "(no notes)",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 12,
   "question": "An Australian artist, born the same year as artist Janet Cumbrae Stewart and fellow member of the Melbourne Society of Women Painters and Sculptors, had her painting featured on the cover of Women's World Magazine in 1923. What is the name of the painting?",
   "gold": "Reve d'Or",
   "accepted": "Reve d'Or",
   "answerable": "yes",
   "predicted": "Unable to determine from the provided notes.",
   "notes": "[Pegg Clarke]\nNOTES:\n- Janet Cumbrae Stewart is a fellow member of the Melbourne Society of Women Painters and Sculptors (per this page, Clarke was also involved with that society). Her birth year is not stated in this source.\n- Source is about Pegg Clarke (c.1884–1959), a photographer, not a painter; she is not the target artist unless the year-match works out, and no 1923 Women's World cover is mentioned here.\n- Other MSWPS-linked names mentioned: Jessie Traill (printmaker, shared Temple Court studio with Cumbrae Stewart, Norah Gurdon, A. M. E. Bale, c.1909), Margaret Maclean, Guelda Pyke, Polly Hurry (friends of Clarke, artists).\n- Janet Cumbrae Stewart listed in Lyceum Club 2002 exhibition (no birth year given).\n- No mention of Women's World Magazine or a 1923 cover painting.\n\n[Janet Agnes Cumbrae Stewart (1883–1960)]\n- Janet Agnes Cumbrae Stewart born 23 December 1883, Brighton, Victoria; died 8 September 1960, Melbourne (ADB).\n- Bridging fact: target artist must be born in 1883 (year match), Australian, fellow MSWPS member, painting on Women's World Magazine cover in 1923.\n- Cumbrae Stewart studied at National Gallery School Melbourne 1901–07 (under Bernard Hall, F. McCubbin); in London 1922; exhibited Paris Galérie Beaux-Arts 1924–31; honourable mention Salon des Artistes Français 1923.\n- Known for pastel female nudes; monograph by John Shirlow (Melbourne, 1921).\n- No mention in this source of Melbourne Society of Women Painters and Sculptors membership or Women's World Magazine.",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 13,
   "question": "The 2026 Nobel Prize in Physics was awarded for contributions to a neutrino observatory. At which research station is that observatory located?",
   "gold": "Amundsen–Scott South Pole Station",
   "accepted": "Amundsen–Scott South Pole Station",
   "answerable": "yes",
   "predicted": "The South Pole (Amundsen–Scott South Pole Station, Antarctica), where IceCube is built into the ice.",
   "notes": "[Press release: Nobel Prize in Physics 2026]\n- Prize: 2026 Nobel Prize in Physics, awarded 6 October 2026 to Francis Halzen (University of Wisconsin–Madison, USA) \"for decisive contributions to the IceCube Neutrino Observatory and the discovery of high-energy neutrinos of astrophysical origin\"\n- Observatory: IceCube Neutrino Observatory, located at the South Pole (headline: \"captured at the South Pole\"; \"ice at the South Pole\")\n- Detector: a cubic kilometre of ice equipped with light sensors; completed 2011\n- Halzen's vision of using South Pole ice to detect neutrinos presented 1988\n- Ice advantages cited: free from interference, geologically stable, no earthquakes",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 14,
   "question": "How many years apart are the birth years of the two 2026 Nobel laureates in Chemistry?",
   "gold": "20",
   "accepted": "20; 20 years (1930 and 1950)",
   "answerable": "yes",
   "predicted": "20 years (Kagan born 1930, Soai born 1950; birth years not verified against the Nobel page itself)",
   "notes": "[List of Nobel laureates in Chemistry]\n- 2026 Nobel Chemistry laureates listed: Henri B. Kagan (1930–present), French; Kensō Soai (1950–present), Japanese.\n- Birth years: Kagan 1930; Soai 1950 → difference 20 years.\n\n[Nobel Prize in Chemistry 2026]\n- Source (nobelprize.org 2026 Chemistry summary page): laureates are Henri B. Kagan (prize share 1/2) and Kenso Soai (prize share 1/2), awarded \"for the discovery of non-linear effects and autocatalysis in asymmetric organic synthesis.\"\n- Source gives no birth years; page content is navigation/summary only. Birth years 1930 (Kagan) and 1950 (Soai) come from the earlier notes, not verified here.\n- Source says six prizes total, 10 laureates overall across 2026 prizes (context only).",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 15,
   "question": "How many years did it take after the FIFA ban was lifted for someone to wear a hijab in the World Cup?",
   "gold": "11 years",
   "accepted": "11 years",
   "answerable": "yes",
   "predicted": "About 9 years (ban lifted 2014; first hijab-wearer at a FIFA Women's World Cup, Nouhaila Benzina, in 2023).",
   "notes": "[Women's football in Iran]\n- FIFA banned Iran from a second-round qualifier vs Jordan in mid-2011 over hijab requirement (enforced by government).\n- FIFA eventually lifted the ban in 2014 (along with turban/kippah bans for Sikh/Jewish men).\n- 2016: Iranian players wore hijabs in a FIFA-approved tournament, the U-17 Women's World Cup held in Jordan (per source; source describes this as first hijab-wearing at FIFA-approved event).\n- Iran U-17 team qualified for 2015 Asian Championship (China), per source; Iran's first continental qualification for top competition in 2015.\n\n[Muslim women in sport]\n- FIFA hijab ban instituted in 2011 (source: \"FIFA also instituted a hijab ban in 2011, forcing the Iranian women's team to forfeit an Olympic qualifying match\"). Source calls it an Olympic qualifier, conflicting with the earlier note's \"second-round qualifier vs Jordan.\"\n- Source gives no date for FIFA rescinding the ban: only \"FIFA has since rescinded its hijab ban and now allows athletes to compete in approved sports hijabs.\"\n- FIFA U-17 Women's World Cup 2012 hosted by Azerbaijan (UEFA member); mascot Top Top Girl. Not a hijab-related fact, but dates a FIFA women's event.\n- Jordan hosted 2016 FIFA U-17 Women's World Cup, \"the first female soccer world cup to be held anywhere in the Middle East.\"\n- FIBA (basketball) hijab ban overturned May 2017 (separate federation; not FIFA).\n- Source does not mention any hijab-wearing player at a FIFA senior Women's World Cup or any FIFA World Cup.\n\n[Nouhaila Benzina is the first woman to wear a hijab during ...]\n- Source (FIFPRO Facebook post): Nouhaila Benzina is \"the first woman to wear a hijab during the FIFA Women's World Cup\" (senior event, 2023 per context of \"so much history making in this world cup\" comment; Benzina played for Morocco).\n- FIFPRO post encourages players' \"full expression of who they are, on and off the pitch.\"\n- Implication: first hijab at a FIFA Women's World Cup (senior) is Benzina; the U-17 2016 hijab use by Iran is a different tournament, so the gap should be measured from FIFA's ban rescission (date still unknown in notes) to Benzina's appearance.\n- Bridging: need rescission date of FIFA hijab ban (notes say 2014 for turban/kippah and \"lifted\" generally; hijab-ban lifting date unconfirmed) and Benzina's World Cup debut year (source comment suggests 2023 World Cup, Morocco).",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 16,
   "question": "Which U.S. National Park was the first to be established after the Portland Trail Blazers won their only playoff series with LaMarcus Aldridge on the team?",
   "gold": "Gateway Arch National Park",
   "accepted": "Gateway Arch National Park",
   "answerable": "yes",
   "predicted": "Indiana Dunes National Park (redesignated February 2019; low confidence, notes were empty)",
   "notes": "(no notes)",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 17,
   "question": "Whom did the 2026 US Open women's singles champion defeat in the final of the 2026 Australian Open?",
   "gold": "Aryna Sabalenka",
   "accepted": "Aryna Sabalenka; Sabalenka",
   "answerable": "yes",
   "predicted": "Unable to determine from the available information; I don't have reliable data on the 2026 Australian Open final or the 2026 US Open champion.",
   "notes": "(no notes)",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 18,
   "question": "Of all the 2026 Nobel laureates in Physics, Chemistry, and Physiology or Medicine, who was born earliest?",
   "gold": "Henri B. Kagan",
   "accepted": "Henri B. Kagan; Henri Kagan; Kagan",
   "answerable": "yes",
   "predicted": "Francis Halzen (born 1944, Physics), assuming no 2026 Chemistry laureate was born earlier. Chemistry is unverified.",
   "notes": "[Press release: Nobel Prize in Physiology or Medicine 2026]\n- Medicine 2026 laureates and birth years: Karl Deisseroth born 1971; Peter Hegemann born 1954; Georg Nagel born 1953.\n- Earliest born so far among Medicine laureates: Georg Nagel (1953), then Hegemann (1954), then Deisseroth (1971).\n- Prize announced 5 October 2026 (Medicine); Physics and Chemistry 2026 laureates not covered in this source.\n- Exact birth dates within years not given in source.\n\n[Press release: Nobel Prize in Physics 2026]\n- Physics 2026: Francis Halzen (sole laureate), born 1944 in Tienen, Belgium (PhD 1969 KU Leuven); Physics press release dated 6 October 2026.\n- Medicine 2026 birth years (from existing notes): Nagel 1953, Hegemann 1954, Deisseroth 1971 — Halzen (1944) is earlier than all of them.\n- Chemistry 2026 laureates: not covered in this source; need to check their birth years to confirm whether anyone was born before 1944.",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 19,
   "question": "What is the HTTP endpoint path of OpenAI's Decisions API?",
   "gold": "POST /v1/decisions",
   "accepted": "/v1/decisions; POST /v1/decisions",
   "answerable": "yes",
   "predicted": "POST /v1/decisions (full URL: https://api.openai.com/v1/decisions)",
   "notes": "[Decisions | OpenAI API]\n- Decisions API endpoint: `POST /v1/decisions` (full URL in curl example: https://api.openai.com/v1/decisions)\n- Only model currently available: gpt-6-luna; API in public beta, GA expected \"in the coming weeks\"",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 20,
   "question": "Which team won the 2026 Ryder Cup?",
   "gold": "No 2026 Ryder Cup was held: the event took place in 2025 (Bethpage Black) and next in 2027 (Adare Manor).",
   "accepted": "there was no 2026 Ryder Cup",
   "answerable": "no",
   "predicted": "Unknown. The 2026 Ryder Cup had not been played as of my knowledge cutoff, and no notes were collected to confirm a result.",
   "notes": "(no notes)",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 21,
   "question": "Which physicist shared the 2026 Nobel Prize in Physics with Francis Halzen?",
   "gold": "No one: Francis Halzen was the sole laureate of the 2026 Nobel Prize in Physics.",
   "accepted": "nobody; no one shared it; Halzen won alone",
   "answerable": "no",
   "predicted": "The notes do not name a co-laureate; the cited source lists Francis Halzen as the only 2026 Physics laureate, so the question's premise is unsupported by the notes.",
   "notes": "[Nobel Prize in Physics]\n- Source states: Nobel Prize in Physics 2026 awarded to Francis Halzen \"for decisive contributions to the IceCube Neutrino Observatory and the discovery of high-energy neutrinos of astrophysical origin.\" (Royal Swedish Academy of Sciences decision)\n- Source text mentions only Halzen as the 2026 laureate; no co-laureate named in the source.\n- Halzen's role: idea to use glacial ice at South Pole to capture neutrinos; led to IceCube Neutrino Observatory (cubic kilometre of ice with light sensors).\n- Other laureates listed in source (not 2026): Einstein (1921), Röntgen (1901), Andrea Ghez (2020), Leo Esaki (1973), Schrödinger (1933), Anne L'Huillier (2023), J. Michael Kosterlitz (2016), 2014 blue LED laureates, Peter Higgs, Willard Boyle and George Smith, Toshihide Maskawa (photo caption only).",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 22,
   "question": "What price per million input tokens does OpenRouter list for Microsoft-Decision-1?",
   "gold": "$0.042",
   "accepted": "$0.042; 0.042 USD; 4.2 cents",
   "answerable": "yes",
   "predicted": "$0.042 per million input tokens (likely, but unverified because the column header is missing from the notes).",
   "notes": "[Microsoft-Decision-1 - API Pricing & Providers]\n- Source is OpenRouter page for Microsoft-Decision-1; table shows \"$0.042\" in a column alongside \"Free\" and \"0.34s\" (labeled P50, best provider context).\n- Unclear from the excerpt whether $0.042 is the input-token price per million; the table header is missing, so the column label (e.g., input price per M tokens) is not confirmed.\n- Model is post-trained from Qwen3.5-9B; built for single-pass scoring returning calibrated probabilities over fixed answer options (not generation).",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 23,
   "question": "A united states island that is only 90 miles away from Cuba has been the home of several famous people. In what year did the famous author who owns a book store there first start writing?",
   "gold": "1959",
   "accepted": "1959",
   "answerable": "yes",
   "predicted": "1937 (tentative; based on Stetson Kennedy, whose Key West bookstore link is unverified in the notes)",
   "notes": "[Stetson Kennedy]\n- Stetson Kennedy: American author, folklorist, activist; born Oct 5, 1916, Jacksonville FL; died Aug 27, 2011, Jacksonville.\n- Kennedy met Cuban émigré Edith Ogden-Aguilar in Key West, FL while doing fieldwork shortly after leaving UF (married 1936); Key West link fits the Cuba-proximity clue.\n- Kennedy's 2008 book Grits and Grunts: Folkloric Key West (Pineapple Press).\n- In 2006 Kennedy married writer and bookstore owner Sandra Parks (former St. Augustine city commissioner); married until his death in 2011. (Bookstore owner = Sandra Parks, not Kennedy; check whether Parks' bookstore is in Key West.)\n- Kennedy's first writing-related activity: published/contributed to periodicals; wrote \"Inside Out\" column for Federated Press 1937–1950; joined Federal Writers' Project in 1937 (after leaving UF); collected Florida folklore for five years (~1937 onward); early writing at UF/active 1936 (collected supplies for Spanish Republic, not writing).\n- Kennedy's first book: Palmetto Country (1942), built from unused Federal Writers' Project material.\n- Kennedy's wife Edith Ogden-Aguilar was the Cuban émigré; Key West is the island connection to be verified (island ~90 miles from Cuba).",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 24,
   "question": "Which of the two 2026 US Open singles champions also won the 2026 French Open singles title?",
   "gold": "Alexander Zverev",
   "accepted": "Alexander Zverev; Zverev",
   "answerable": "yes",
   "predicted": "Alexander Zverev",
   "notes": "[French Open winners: Men's and women's singles ...]\n- 2026 French Open men's singles champion: Alexander Zverev, who beat Flavio Cobolli in 5 sets in the final (Roland Garros, June 7, 2026).\n- 2026 French Open women's singles champion: Mirra Andreeva, who beat Maja Chwalinska in the final.\n- The source does not mention the 2026 US Open or its singles champions, so the overlap with the US Open winners cannot be checked from this page.\n\n[US Open (tennis)]\n- 2026 US Open men's singles champion: Alexander Zverev (beat Ben Shelton 6–3, 7–6(7–2), 5–7, 6–2).\n- 2026 US Open women's singles champion: Elena Rybakina (beat Aryna Sabalenka 6–4, 5–7, 6–2).\n- Bridge: the 2026 French Open men's champion (Zverev, per prior notes) is the same person as the 2026 US Open men's champion, so Zverev won both 2026 singles titles.\n- Women: Rybakina's 2026 French Open result is not in this source; the prior notes say the French Open women's champion was Mirra Andreeva, so Rybakina did not win the French Open women's title.",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  },
  {
   "n": 25,
   "question": "How old was the elder of the two 2026 Nobel laureates in Chemistry when the prize was announced in October 2026?",
   "gold": "95",
   "accepted": "95; 95 years old (Henri B. Kagan)",
   "answerable": "yes",
   "predicted": "96 (most likely; 95 if his 2026 birthday falls after the October announcement, which the notes don't settle)",
   "notes": "[List of Nobel laureates in Chemistry]\n- 2026 laureates: Henri B. Kagan (French, born 1930 per source) and Kensō Soai (Japanese, born 1950 per source).\n- Elder = Henri B. Kagan (b. 1930); Soai b. 1950.\n- Kagan's age at October 2026 announcement: 2026 − 1930 = 96 (birth month/day not given in source; exact age depends on birthday, so 95 or 96).\n- Source lists 2026 Nobel Chemistry as Kagan and Soai, consistent with the question premise.",
   "human_correctness": "",
   "human_grounded": "",
   "comment": ""
  }
 ],
 "rubric": {
  "correctness": [
   {
    "label": "correct",
    "definition": "the prediction commits to the gold answer or an accepted variant (or a clear equivalent: same entity, number or date; extra context and formatting are fine). If the question cannot be answered as asked, \"correct\" means the prediction says so for the right reason: it identifies the false premise or that no such thing exists."
   },
   {
    "label": "hedged",
    "definition": "the prediction mentions the gold answer but does not commit to it: it offers other candidates alongside it, or presents it as a guess or as unverified."
   },
   {
    "label": "incorrect",
    "definition": "the prediction commits to a different answer. For a question that cannot be answered as asked, inventing an answer is \"incorrect\"."
   },
   {
    "label": "no_answer",
    "definition": "the prediction declines, or says it could not determine the answer, without identifying a false premise."
   }
  ],
  "grounded": [
   {
    "label": "supported",
    "definition": "the notes contain the facts the answer's key claim rests on, directly or by simple arithmetic or comparison of facts in the notes."
   },
   {
    "label": "unsupported",
    "definition": "the key claim is missing from the notes or goes beyond them; the answer relies on outside knowledge or a guess."
   },
   {
    "label": "not_applicable",
    "definition": "the answer makes no factual claim (it only declines or says it could not determine the answer)."
   }
  ]
 }
};
