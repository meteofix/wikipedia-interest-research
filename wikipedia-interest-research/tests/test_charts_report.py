"""Charts and the one-page PDF report, rendered offline from a synthetic results.json."""

import copy
import json
import shutil
from pathlib import Path

import pytest
from pypdf import PdfReader

from wikiinterest import charts, report

FIXTURE = Path(__file__).parent / "fixtures" / "results_example.json"

NOTES_OK = """\
## Headline
Шахи ростуть в українській Вікіпедії: +25% за рік, висока довіра

## Key points
- Шахи · uk: відносне зростання +25% [+17%, +34%], довіра висока.
- Żonglerka (pl) росте найшвидше: +45%, але довіра середня — rynek polski wygląda obiecująco.
- Žonglování · cs: лише 10 переглядів на день — сигнал слабкий.

## Recommendation
Почати з україномовного курсу шахів і перевірити попит лендингом.

## Next steps
- Запустити лендинг для uk-аудиторії
- Повторити аналіз через 3 місяці

## Caveats
- Перегляди Вікіпедії — це інформаційний інтерес, не готовність платити.
"""


@pytest.fixture()
def analysis(tmp_path: Path) -> Path:
    """A copy of the fixture in its own analysis directory (build_report rewrites results.json)."""
    d = tmp_path / "analysis"
    d.mkdir()
    shutil.copy(FIXTURE, d / "results.json")
    return d / "results.json"


def _write_notes(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def _pdf_text(pdf_path: str) -> tuple[int, str]:
    reader = PdfReader(pdf_path)
    return len(reader.pages), "\n".join(p.extract_text() for p in reader.pages)


def _results() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _fixture_notes_numbers_consistent():
    # the notes above quote values that exist in the fixture (guards against fixture drift)
    r = _results()
    m = {s["key"]: s["metrics"] for s in r["series"] if s["status"] == "ok"}
    assert round(m["t1|uk"]["yoy_rel"] * 100) == 25
    assert round(m["t2|pl"]["yoy_rel"] * 100) == 45
    assert round(m["t2|cs"]["avg_daily_views_12m"]) == 10


def test_fixture_matches_notes():
    _fixture_notes_numbers_consistent()


def test_render_charts_from_fixture(tmp_path: Path):
    out = charts.render_charts(_results(), tmp_path)
    for key in ("trend_png", "growth_png"):
        p = Path(out[key])
        assert p.is_absolute() and p.exists() and p.stat().st_size > 5_000


def test_render_charts_localized(tmp_path: Path):
    out = charts.render_charts(_results(), tmp_path, lang="uk")
    assert out["trend_png"].endswith("trend.uk.png") and Path(out["growth_png"]).exists()


def test_render_charts_single_series(tmp_path: Path):
    r = _results()
    r["series"] = [s for s in r["series"] if s["key"] == "t1|uk"]
    r["comparison"] = None
    out = charts.render_charts(r, tmp_path)
    assert Path(out["trend_png"]).stat().st_size > 5_000


def test_render_charts_without_data_does_not_crash(tmp_path: Path):
    r = _results()
    for s in r["series"]:
        s["status"] = "missing"
        s["monthly"] = []
        s["metrics"] = {"yoy_rel": None}
    r["comparison"] = None
    out = charts.render_charts(r, tmp_path)
    assert Path(out["trend_png"]).exists() and Path(out["growth_png"]).exists()
    empty = {"series": [], "params": {}}
    out = charts.render_charts(empty, tmp_path / "empty")
    assert Path(out["growth_png"]).exists()


def test_render_charts_many_series_caps_lines(tmp_path: Path):
    r = _results()
    base = [s for s in r["series"] if s["status"] == "ok"]
    many = []
    for i in range(4):
        for s in base:
            c = copy.deepcopy(s)
            c["key"] = f"{s['key']}#{i}"
            c["topic_label"] = f"{s['topic_label']} {i}"
            many.append(c)
    r["series"] = many
    r["comparison"] = None
    out = charts.render_charts(r, tmp_path)
    assert Path(out["trend_png"]).exists()


def test_report_one_page_with_unicode(analysis: Path):
    notes = _write_notes(analysis.parent / "notes.md", NOTES_OK)
    res = report.build_report(analysis, notes, lang="uk")
    assert res["pages"] == 1
    pages, text = _pdf_text(res["pdf"])
    assert pages == 1
    assert "Шахи ростуть" in text  # Cyrillic headline
    assert "Žonglování" in text  # Czech diacritics (topic label in the table)
    assert "wygląda" in text  # Polish diacritics from the notes
    assert "Рекомендація" in text  # Ukrainian section label
    assert res["warnings"] == []
    saved = json.loads(analysis.read_text(encoding="utf-8"))
    assert saved["files"]["report_pdf"] == res["pdf"]


def test_report_english_labels(analysis: Path):
    notes = _write_notes(analysis.parent / "notes.md", NOTES_OK)
    res = report.build_report(analysis, notes, lang="xx")  # unknown language -> English labels
    _, text = _pdf_text(res["pdf"])
    assert "Recommendation" in text and "How sure are we" in text


def test_report_one_page_for_long_notes_and_many_series(tmp_path: Path):
    r = _results()
    base = [s for s in r["series"]]
    many = []
    for i in range(7):
        for s in base:
            c = copy.deepcopy(s)
            c["key"] = f"{s['key']}#{i}"
            c["topic_label"] = f"{s['topic_label']} варіант {i}"
            if c["status"] == "ok":
                c["verdict"]["reasons"] = [r + f" (case {i})" for r in c["verdict"]["reasons"]] + [
                    "Direction changes in the shifted window; interpret with care."]
            many.append(c)
    r["series"] = many
    r["warnings"] = r["warnings"] * 5
    d = tmp_path / "big"
    d.mkdir()
    (d / "results.json").write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
    long_point = ("Шахи · uk: відносне зростання +25%, довіра висока; " * 12).strip()
    long_notes = (
        "## Headline\n" + "Дуже довгий заголовок про шахи і жонглювання в трьох мовах " * 4 + "\n\n"
        "## Key points\n" + "".join(f"- {long_point}\n" for _ in range(6)) + "\n"
        "## Recommendation\n" + "Почати з україномовного курсу і перевірити попит. " * 20 + "\n\n"
        "## Next steps\n" + "".join(f"- Крок {i}: перевірити гіпотезу на лендингу\n" for i in range(1, 7)) + "\n"
        "## Caveats\n" + "".join("- Перегляди — не готовність платити, а інформаційний інтерес.\n" for _ in range(6))
    )
    notes = _write_notes(d / "notes.md", long_notes)
    res = report.build_report(d / "results.json", notes, lang="uk")
    pages, text = _pdf_text(res["pdf"])
    assert pages == 1 and res["pages"] == 1
    assert "results.json" in text  # hidden table rows are announced


def test_invented_number_is_rejected(analysis: Path):
    notes = _write_notes(analysis.parent / "notes.md", NOTES_OK.replace("+45%", "+57%"))
    with pytest.raises(report.NotesError) as err:
        report.build_report(analysis, notes)
    msg = str(err.value)
    assert "57%" in msg and "--allow-numbers" in msg
    assert not (analysis.parent / "report.pdf").exists()


def test_allowed_number_passes(analysis: Path):
    notes = _write_notes(analysis.parent / "notes.md",
                         NOTES_OK.replace("+45%", "+57%") + "\n")
    res = report.build_report(analysis, notes, allow_numbers=[57])
    assert res["pages"] == 1


def test_number_present_in_results_passes(analysis: Path):
    r = _results()
    share = next(s for s in r["series"] if s["key"] == "t1|pl")["metrics"]["share_ppm_12m"]
    text = NOTES_OK.replace("- Повторити аналіз через 3 місяці", f"- Частка Szachy: {share:.1f} на млн переглядів")
    notes = _write_notes(analysis.parent / "notes.md", text)
    assert report.build_report(analysis, notes)["pages"] == 1


def test_missing_headline_raises(analysis: Path):
    notes = _write_notes(analysis.parent / "notes.md", NOTES_OK.split("## Key points")[1].join(["## Key points", ""]))
    with pytest.raises(report.NotesError, match="Headline"):
        report.build_report(analysis, notes)


def test_missing_notes_file_explains_template(analysis: Path):
    with pytest.raises(report.NotesError, match="## Headline"):
        report.build_report(analysis, analysis.parent / "nope.md")


def test_cjk_and_rtl_text_does_not_crash(analysis: Path):
    text = NOTES_OK.replace("Запустити лендинг для uk-аудиторії", "国际象棋 курс і שחמט та شطرنج")
    notes = _write_notes(analysis.parent / "notes.md", text)
    res = report.build_report(analysis, notes)
    assert res["pages"] == 1
    assert res["warnings"] and "replaced" in res["warnings"][0]


def test_parse_notes_aliases_and_bullets():
    parsed = report.parse_notes(
        "# Заголовок\n**Головне**: росте\n\n### Ключові висновки:\n1. перший\n* другий\n  продовження\n"
        "## Рекомендація\nРобити X.\n## Наступні кроки\n- a\n- b\n")
    assert parsed["headline"] == "Головне: росте"
    assert parsed["key_points"] == ["перший", "другий продовження"]
    assert parsed["recommendation"] == "Робити X."
    assert parsed["next_steps"] == ["a", "b"]


def test_sanitize_replaces_unsupported_characters():
    clean, bad = charts.sanitize("Шахи 象棋 שחמט ok")
    assert "Шахи" in clean and "ok" in clean
    assert "象" in bad and "ש" in bad and "?" in clean
