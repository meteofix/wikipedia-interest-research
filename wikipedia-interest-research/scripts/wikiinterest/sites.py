"""Language editions: resolve user input (codes, names) to Wikipedia sites via Wikimedia's sitematrix.

Language codes, wiki subdomains and database names differ for some editions
(yue -> zh-yue.wikipedia.org / zh_yuewiki, gsw -> als.wikipedia.org / alswiki,
be-tarask -> be_x_oldwiki), so all three are accepted and normalised here.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass

from . import config
from .http import Http

SITEMATRIX_URL = "https://meta.wikimedia.org/w/api.php"

# Common tags people use that are not Wikipedia codes.
_ALIASES = {
    "nb": "no", "zh-cn": "zh", "zh-hans": "zh", "zh-tw": "zh", "zh-hant": "zh", "zh-hk": "zh", "cmn": "zh",
    "pt-br": "pt", "pt-pt": "pt", "en-us": "en", "en-gb": "en", "es-419": "es", "es-mx": "es",
    "iw": "he", "in": "id", "ji": "yi", "jw": "jv", "sr-latn": "sr", "sr-cyrl": "sr", "fil": "tl",
    "mo": "ro", "arb": "ar", "zsm": "ms", "swh": "sw", "pes": "fa", "ekk": "et", "lvs": "lv", "khk": "mn",
    "cantonese": "zh-yue", "simple english": "simple",
}


class UnknownLanguage(ValueError):
    pass


@dataclass(frozen=True)
class Site:
    code: str  # wiki subdomain, e.g. "zh-yue"
    lang_code: str  # language code used by Wikidata labels, e.g. "yue"
    dbname: str  # e.g. "zh_yuewiki" (Wikidata sitelink key)
    host: str  # e.g. "zh-yue.wikipedia.org"
    name: str  # native name
    english: str  # English name

    @property
    def api(self) -> str:
        return f"https://{self.host}/w/api.php"


def load_sites(http: Http) -> list[Site]:
    data = http.get_json(
        SITEMATRIX_URL,
        {"action": "sitematrix", "smtype": "language", "smsiteprop": "code|dbname|url", "smstate": "all",
         "format": "json", "formatversion": "2"},
        ttl=config.TTL_SITEMATRIX,
    )
    sites = []
    for key, lang in data["sitematrix"].items():
        if key in ("count", "specials"):
            continue
        for s in lang.get("site", []):
            if s.get("code") != "wiki" or s.get("closed"):
                continue
            host = s["url"].split("//", 1)[1]
            sites.append(Site(host.split(".")[0], lang["code"], s["dbname"], host,
                              lang.get("name", ""), lang.get("localname", "")))
    # "simple" (Simple English) is listed under specials, not as a language
    for s in data["sitematrix"].get("specials", []):
        if s.get("dbname") == "simplewiki" and not s.get("closed"):
            sites.append(Site("simple", "en", "simplewiki", "simple.wikipedia.org", "Simple English", "Simple English"))
    return sites


class SiteIndex:
    def __init__(self, sites: list[Site]):
        self.sites = sites
        self._by_key: dict[str, Site] = {}
        for s in sites:
            for k in (s.code, s.lang_code, s.dbname):
                self._by_key.setdefault(k.lower(), s)
        self._by_name: dict[str, Site] = {}
        for s in sites:
            for n in (s.english, s.name):
                if n:
                    self._by_name.setdefault(n.lower(), s)
        self.dbnames = {s.dbname for s in sites}

    def resolve(self, token: str) -> Site:
        t = token.strip().lower().replace("_", "-")
        t = _ALIASES.get(t, t)
        for cand in (t, t.replace("-", "_"), t.replace("wiki", "") if t.endswith("wiki") else None):
            if cand and cand in self._by_key:
                return self._by_key[cand]
        if t in self._by_name:
            return self._by_name[t]
        prefix = [s for n, s in self._by_name.items() if n.startswith(t)] if len(t) >= 3 else []
        if len({s.code for s in prefix}) == 1:
            return prefix[0]
        close = difflib.get_close_matches(t, list(self._by_key) + list(self._by_name), n=5, cutoff=0.75)
        hint = ", ".join(f"{c} ({self._lookup(c).english})" for c in close) if close else "none"
        many = ", ".join(sorted({f'{s.code} ({s.english})' for s in prefix})[:8])
        raise UnknownLanguage(
            f"Unknown Wikipedia language '{token}'. "
            + (f"Several editions match: {many}. " if many else "")
            + f"Closest matches: {hint}. Use the wiki code (e.g. 'pl', 'zh-yue'); a country is not a language — "
            "pick the language(s) its people read."
        )

    def _lookup(self, key: str) -> Site:
        return self._by_key.get(key) or self._by_name[key]

    def resolve_many(self, tokens: list[str]) -> list[Site]:
        out: list[Site] = []
        for tok in tokens:
            s = self.resolve(tok)
            if s not in out:
                out.append(s)
        return out


def split_langs(value: str | None) -> list[str]:
    if not value:
        return []
    return [p.strip() for p in value.replace(";", ",").split(",") if p.strip()]
