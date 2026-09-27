"""Reason, caveat and warning texts in English and Ukrainian.

Analytics code records *codes with parameters*; English text is rendered for the agent's
summary, and the PDF renders the same codes in the report language, so a Ukrainian report
never mixes in English sentences. Parameters are pre-formatted strings (e.g. "+12%").
"""

from __future__ import annotations

DIRECTIONS = {
    "en": {"growing": "growing", "declining": "declining", "flat": "flat", "uncertain": "uncertain", "n/a": "n/a"},
    "uk": {"growing": "росте", "declining": "падає", "flat": "стабільно", "uncertain": "невизначено", "n/a": "н/д"},
}
VARIANTS = {
    "en": {"ex_spikes": "without spike days", "shifted_6m": "with the window 6 months earlier",
           "no_redirects": "without redirects"},
    "uk": {"ex_spikes": "без днів зі сплесками", "shifted_6m": "якщо зсунути вікно на 6 місяців раніше",
           "no_redirects": "без редиректів"},
}

TEMPLATES: dict[str, dict[str, str]] = {
    "en": {
        # verdict reasons
        "volume_low": "very low volume ({views} views/day): a single link or bot burst can move the numbers",
        "volume_moderate": "moderate volume ({views} views/day): monthly totals are noisy",
        "late_start": "views only start on {start} (new or renamed article): the year-over-year comparison is not reliable",
        "ci_very_wide": "very wide uncertainty range {ci}: growth differs a lot from month to month",
        "ci_wide": "wide uncertainty range {ci}",
        "spikes": "growth depends on short spikes: {g} with spikes vs {g_ex} without (spikes carry {share} of views)",
        "variants_disagree": "conclusion changes {details}",
        "uncertain_range": "the uncertainty range {ci} includes both growth and decline",
        "trend_reversed": "trend reversed: the year before changed by {prior}",
        "platform_shift": "absolute views changed {raw} while the whole language edition changed {proj}",
        "consistent": "consistent: solid volume ({views} views/day), not driven by spikes{variants}",
        "consistent_variants": ", holds in all {n} robustness checks",
        "no_yoy": "no year-over-year comparison possible: no views in the earlier 12 months",
        # comparison notes
        "overlap": "the leader's and runner-up's uncertainty ranges overlap: the difference is not certain",
        "low_conf_series": "series with Low confidence should not drive the decision: {labels}",
        # caveats
        "interest_not_intent": "Wikipedia pageviews measure informational interest, not purchase intent or "
                               "willingness to pay; use them to choose what to validate next.",
        "language_not_country": "A language edition is not a country: its readers can live anywhere, and many "
                                "people read Wikipedia in English instead of their own language.",
        "relative_growth": "Growth is the change of the topic's share of all views of that language edition "
                           "(relative growth), which removes platform-wide shifts such as traffic moving to search "
                           "and AI answers; absolute views are shown alongside.",
        "articles_proxy": "A topic is measured through specific articles and their redirects; interest in other "
                          "articles or other languages is not counted.",
        "human_traffic": "Counts are human (user-agent) views as classified by Wikimedia; undetected automated "
                         "traffic can still show up as spikes.",
        # warnings (report wording: no instructions for the agent)
        "bot_reclass": "Wikimedia re-classified bot traffic for March–August 2025 after improving bot detection; "
                       "comparisons across that period can shift slightly.",
        "missing_article": "{lang}: no article for “{label}” — the topic is not measurable in this edition.",
        "no_data": "{lang}: “{label}” had no views in the window.",
        "redirects_capped": "{lang}: “{title}” has {total} redirects; the {n} most viewed recently are included.",
        "title_redirected": "{lang}: “{title}” redirects to “{target}”; the target article is used.",
        "title_missing": "{lang}: the article “{title}” does not exist.",
        "window_short": "The window has {n} months; year-over-year growth needs 24 months, so only levels are shown.",
        "data_start": "Pageview data starts in {first}; earlier months are not available.",
        "end_incomplete": "The month {end} is not complete yet; the analysis ends in {last}.",
    },
    "uk": {
        "volume_low": "дуже малий обсяг ({views} переглядів/день): одне посилання чи сплеск ботів може зсунути цифри",
        "volume_moderate": "помірний обсяг ({views} переглядів/день): місячні суми шумні",
        "late_start": "перегляди почалися лише {start} (нова або перейменована стаття): порівняння рік до року ненадійне",
        "ci_very_wide": "дуже широкий діапазон невизначеності {ci}: ріст сильно різниться від місяця до місяця",
        "ci_wide": "широкий діапазон невизначеності {ci}",
        "spikes": "ріст залежить від короткочасних сплесків: {g} зі сплесками проти {g_ex} без них "
                  "(сплески дають {share} переглядів)",
        "variants_disagree": "висновок змінюється {details}",
        "uncertain_range": "діапазон {ci} охоплює і ріст, і спад",
        "trend_reversed": "тренд розвернувся: роком раніше зміна становила {prior}",
        "platform_shift": "абсолютні перегляди змінилися на {raw}, а весь мовний розділ — на {proj}",
        "consistent": "висновок стійкий: достатній обсяг ({views} переглядів/день), не залежить від сплесків{variants}",
        "consistent_variants": ", тримається в усіх {n} перевірках стійкості",
        "no_yoy": "порівняння рік до року неможливе: у попередні 12 місяців переглядів не було",
        "overlap": "діапазони лідера й другого місця перетинаються: різниця не гарантована",
        "low_conf_series": "ряди з низькою довірою не мають визначати рішення: {labels}",
        "interest_not_intent": "Перегляди Вікіпедії показують інформаційний інтерес, а не намір купити чи готовність "
                               "платити; це сигнал для вибору, що перевіряти далі.",
        "language_not_country": "Мовний розділ — не країна: його читачі можуть жити будь-де, а багато людей читають "
                                "англійську Вікіпедію замість рідномовної.",
        "relative_growth": "Ріст — це зміна частки теми серед усіх переглядів мовного розділу (відносний ріст); так "
                           "прибирається загальний відплив трафіку до пошуку та AI-відповідей. Абсолютні перегляди "
                           "показано поруч.",
        "articles_proxy": "Тема вимірюється через конкретні статті та їхні редиректи; інтерес до інших статей чи "
                          "мов не враховано.",
        "human_traffic": "Враховано перегляди людей (агент user) за класифікацією Wikimedia; невиявлені боти все ж "
                         "можуть давати сплески.",
        "bot_reclass": "Wikimedia покращила виявлення ботів і перекласифікувала трафік за березень–серпень 2025; "
                       "порівняння через цей період можуть трохи зсуватися.",
        "missing_article": "{lang}: немає статті про «{label}» — у цьому розділі тема напряму не вимірюється.",
        "no_data": "{lang}: «{label}» не мала переглядів у вікні аналізу.",
        "redirects_capped": "{lang}: «{title}» має {total} редиректів; враховано {n} найпопулярніших.",
        "title_redirected": "{lang}: «{title}» перенаправляє на «{target}»; використано цільову статтю.",
        "title_missing": "{lang}: статті «{title}» не існує.",
        "window_short": "Вікно — {n} міс.; для річного росту потрібно 24 місяці, тож показано лише рівні.",
        "data_start": "Дані про перегляди починаються з {first}; раніших місяців немає.",
        "end_incomplete": "Місяць {end} ще не завершився; аналіз закінчується {last}.",
    },
}


def render(code: str, params: dict | None = None, lang: str = "en") -> str:
    table = TEMPLATES.get(lang, TEMPLATES["en"])
    template = table.get(code) or TEMPLATES["en"].get(code) or code
    p = dict(params or {})
    if code == "variants_disagree":
        names, dirs = VARIANTS.get(lang, VARIANTS["en"]), DIRECTIONS.get(lang, DIRECTIONS["en"])
        p["details"] = "; ".join(f"{names.get(v['name'], v['name'])} ({dirs.get(v['direction'], v['direction'])}, "
                                 f"{v['value']})" for v in p.get("items", []))
    if code == "consistent":
        n = p.get("n", 0)
        p["variants"] = render("consistent_variants", {"n": n}, lang) if n else ""
    try:
        return template.format(**p)
    except (KeyError, IndexError):
        return TEMPLATES["en"].get(code, code).format_map(_Default(p))


class _Default(dict):
    def __missing__(self, key):
        return "…"
