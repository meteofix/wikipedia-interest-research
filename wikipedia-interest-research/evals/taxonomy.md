# Question-space taxonomy

The eval sets are generated from this model of the question space, **not** from the three
example questions in the task. Each dimension is an independent axis of variation; generated
sets must cover every value of every dimension and, for the key dimensions (intent, topic kind,
coverage, language naming, scripts), as many value *pairs* as practical (pairwise coverage).

## Dimensions

| Dimension | Values | Why it matters |
|---|---|---|
| `intent` | `trend_single` (is interest in X growing in language L?), `compare_languages` (one topic, several languages), `compare_topics` (several topics, one language), `matrix` (topics × languages), `rank_markets` (which languages/audiences to target next), `seasonality_timing` (when does interest peak / when to launch), `event_spike` (what happened around a spike, did an event matter), `trust_robustness` (how reliable is a signal), `level_size` (how big is interest, relative level), `discovery` (what is popular / related / rising), `methodology` (how numbers are computed), `followup_modify` (dialogue: change period, languages, metric, criteria, exclusions), `report_request` (one-pager / chart of a result), `out_of_scope` (willingness to pay, revenue, pricing, non-Wikipedia data, real-time, personal data, forecasts of sales) | different paths through the skill |
| `topic_kind` | narrow concept, broad field, intent proxy ("learning X", "getting into X"), product category, brand/company, skill/hobby, event, person, profession, medical/health condition | how hard it is to map to articles |
| `ambiguity` | `none`, `polysemy` (Mercury, Python, Java, Jaguar), `cultural` (chess vs xiangqi/shogi, football vs soccer, "gymnastics" meaning different things), `vague` ("wellness", "self-improvement") | ask vs choose-and-state |
| `coverage_trap` | `none`, `missing_in_some` (no article in some requested language), `missing_all`, `en_only`, `merged` (concept only exists as a section of a broader article) | honest "not measurable" handling |
| `volume` | high, medium, low, near-zero (small wikis, niche topics) | noise and confidence |
| `temporal_profile` | stable, rising, declining, seasonal (annual / school year / holidays), spiky (news, deaths, launches, eclipses, sports events), new article, renamed article | metric correctness |
| `lang_naming` | wiki codes (`pl`), English names ("Polish"), native names ("polski", "Deutsch"), Ukrainian names ("польська"), countries instead of languages ("in Brazil", "for Mexico"), regions ("Balkans", "Scandinavia", "Latin America", "Baltics"), "top N languages", unspecified ("our selected languages" without a list) | input normalization, when to ask |
| `wiki_size_and_script` | large / medium / small editions (by readership, not article count — ceb, war, arz are bot-inflated); scripts: Latin, Cyrillic, CJK, Arabic (RTL), Devanagari, Thai, Hebrew, Greek, Georgian/Armenian; special codes (zh-yue, als, be-tarask, zh-min-nan, simple) | fonts, codes, volume |
| `time_spec` | none, relative ("last 2 years", "past 18 months"), absolute ("since 2020", "2019 vs 2024"), event-anchored ("since COVID", "after ChatGPT launch"), pre-2015 (data starts July 2015), future ("next year"), current/partial month ("this month so far") | windows and data limits |
| `output` | quick answer, table, chart, PDF one-pager, ranking, recommendation, explanation | artifacts |
| `criteria` | implicit ("promising"), explicit thresholds ("> 15% growth and > 100 views/day"), weights ("growth matters twice as much as size"), user hypothesis to confirm/refute | parametrization |
| `user_language_style` | Ukrainian, English, other (Polish, German, Spanish, Russian, Czech…); formal, casual with typos, long business context, very terse | understanding |
| `dialogue_position` | first question, refinement, assumption change, pushback ("are you sure?", "Google Trends shows otherwise"), request to redo with a different method | state, reuse |
| `sensitivity` | none; sensitive-but-legitimate market research (mental health, sexual health, addiction recovery, medications) | no unjustified refusals, careful framing |

## Coverage targets for a generated set of ~60 single-turn questions + ~6 dialogues

- Every `intent` value ≥ 3 items; `trend_single`, `compare_languages`, `compare_topics`, `rank_markets` 5–8 each; `out_of_scope` 4–5; partially supported intents (`event_spike`, `discovery`, country-instead-of-language) ≥ 3 each.
- User language: ~45% Ukrainian, ~35% English, ~20% other languages.
- ≥ 6 items with `coverage_trap` ≠ `none` (facts verified against Wikidata; see label schema).
- ≥ 5 items with `ambiguity` ≠ `none`.
- ≥ 10 items involving non-Latin/non-Cyrillic scripts; ≥ 3 items with special wiki codes.
- ≥ 5 items on small wikis or low-volume topics.
- ≥ 3 items with pre-2015, future or partial-month time specs.
- ≥ 10 items explicitly asking for a PDF/one-pager/shareable report; ≥ 5 asking for charts.
- ≥ 5 items with explicit user criteria (thresholds or weights).
- ≥ 3 items with countries/regions instead of languages; ≥ 2 with unspecified "our languages".
- Dialogues: 2–4 user turns each, covering refinement, assumption change, pushback, report request.
- Topic variety across B2C domains: education, language learning, fitness, nutrition, mental health, parenting, hobbies/crafts, games, personal finance, travel, music, programming/tech skills, pets, beauty, sports.
- Do not reuse the three example topics from the task (intermittent fasting, astronomy, learning English); they are included separately as public examples.
