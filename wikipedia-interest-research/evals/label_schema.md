# Label schema for eval questions

One JSON object per line (JSONL). Labels describe **what a competent analyst would accept**,
not what this skill's implementation happens to output. Where several behaviors are
reasonable, the labels must accept all of them.

```json
{
  "id": "dev-001",
  "set": "dev",
  "source": "generated | public-example | blind",
  "persona": "short description of the asking founder/product",
  "turns": ["first user message", "optional follow-up message", "..."],
  "user_language": "uk",
  "taxonomy": {
    "intent": "compare_languages",
    "topic_kind": "skill/hobby",
    "ambiguity": "none",
    "coverage_trap": "none",
    "lang_naming": "uk_names",
    "scripts": ["latin"],
    "time_spec": "none",
    "output": ["answer"],
    "criteria": "implicit",
    "scope": "full | partial | out"
  },
  "expected": {
    "must_clarify": false,
    "clarify_acceptable": false,
    "topics": [{"label": "chess", "acceptable_qids": ["Q718"], "notes": ""}],
    "wikis": ["trwiki", "viwiki", "idwiki"],
    "behaviors": ["states the time window it used", "gives growth with an uncertainty range for each language"],
    "forbidden": ["cites numbers that are not in the tool outputs", "claims country-level conclusions without a caveat"],
    "artifacts": []
  },
  "verified_facts": [
    {"fact": "Q718 has sitelinks in trwiki, viwiki, idwiki", "how": "Wikidata wbgetentities, 2026-09-27"}
  ],
  "notes": "free text for graders"
}
```

## Field rules

- `turns`: one element = single-turn question; 2–4 elements = dialogue (later turns are sent
  after the agent answered the previous one).
- `expected.must_clarify`: `true` only if a competent analyst could not reasonably proceed
  (e.g. "our selected languages" with no list). If asking **or** proceeding with an explicitly
  stated assumption are both fine, set `must_clarify: false, clarify_acceptable: true`.
- `expected.topics` / `expected.wikis`: optional; list all acceptable options. Use Wikipedia
  database names (`plwiki`, `zh_yuewiki`, `alswiki`).
- `expected.behaviors`: 2–5 items, each checkable from the final answer or the transcript.
  Behaviors must be method-agnostic ("says the Polish article does not exist", "explains
  Wikipedia views are not purchase intent"), never exact numbers.
- `expected.forbidden`: 1–3 items.
- `expected.artifacts`: `["pdf"]` and/or `["chart"]` when the user explicitly asks for them.
- `verified_facts`: required for every `coverage_trap` ≠ `none` and for any label that depends on
  data facts (existence of articles, codes). Verify with the Wikidata / MediaWiki API.
- The `taxonomy` block is required for generated dev items and optional for blind items.
